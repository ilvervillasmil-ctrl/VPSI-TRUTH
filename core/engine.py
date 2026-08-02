"""
VPSI-TRUTH --- core/engine.py

Engine central.

Principio:
  - Conoce la arquitectura (módulos, roles, contratos, capacidades).
  - Actúa solo por lo que cada CONTENEDOR declara.
  - No inventa operaciones.
  - No interpreta resultados de los módulos.
  - No sustituye la lógica interna de un módulo.
  - CT es ancla de constantes (ALPHA/BETA), no un calculador.
  - CA calcula C/L/K; FO aplica Tru_Ri / Tru_total.
  - Sin O_context → K indefinido (Def-5.3.1).
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional
from fractions import Fraction


# ===============================================================
# UNDEFINED
# ===============================================================
class _Undefined:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, other):
        return isinstance(other, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")


UNDEFINED = _Undefined()


def es_undefined(v: Any) -> bool:
    return v is UNDEFINED or isinstance(v, _Undefined)


# ===============================================================
# EXCEPCIONES
# ===============================================================
class ArranqueError(Exception):
    """Incoherencia axiomática, mecánica o dependencias faltantes."""


class EvaluacionError(Exception):
    """Error en el camino de evaluación."""


class DominioError(Exception):
    """Error de dominio / O_context."""


class ContratoError(Exception):
    """Contrato CONTENEDOR inválido o capacidad no resoluble."""


# ===============================================================
# ROLES
# ===============================================================
ROLES = ("CT", "AX", "FO", "MC", "SF", "DG", "CA", "CX", "RE", "VX", "TX", "CH", "UI")
OBLIGATORIOS = ("CT", "AX", "FO", "MC", "SF")


# ===============================================================
# CONTENEDOR
# ===============================================================
class Contenedor:
    def __init__(self, nombre: str, rol: str, version: str, modulo: Any, ruta: Path, meta: Dict):
        self.nombre = nombre
        self.rol = rol
        self.version = version
        self.modulo = modulo
        self.ruta = ruta
        self.requiere: List[str] = list(meta.get("requiere") or [])
        self.descripcion: str = str(meta.get("descripcion") or "")
        # capacidades: nombre → callable | str (nombre de función en el módulo)
        raw = meta.get("capacidades") or {}
        if not isinstance(raw, dict):
            raw = {}
        self.capacidades: Dict[str, Any] = dict(raw)

    def fn(self, nombre: str):
        """Resuelve capacidad del contrato. Nunca inventa nombres."""
        ref = self.capacidades.get(nombre)
        if ref is None:
            return None
        if callable(ref):
            return ref
        if isinstance(ref, str):
            return getattr(self.modulo, ref, None)
        return None

    def tiene(self, nombre: str) -> bool:
        return callable(self.fn(nombre))

    def como_dict(self) -> Dict:
        caps = {}
        for k, v in self.capacidades.items():
            if callable(v):
                caps[k] = getattr(v, "__name__", "callable")
            else:
                caps[k] = str(v)
        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "version": self.version,
            "requiere": list(self.requiere),
            "ruta": str(self.ruta),
            "descripcion": self.descripcion,
            "capacidades": caps,
        }


# ===============================================================
# REGISTRO
# ===============================================================
class Registro:
    def __init__(self):
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {r: [] for r in ROLES}
        self.rechazados: List[Dict] = []

    def registrar(self, cont: Contenedor) -> None:
        if cont.nombre in self.contenedores:
            self.rechazados.append({
                "ruta": str(cont.ruta),
                "razon": f"nombre duplicado: {cont.nombre}",
            })
            return
        self.contenedores[cont.nombre] = cont
        if cont.rol in self.por_rol:
            self.por_rol[cont.rol].append(cont)

    def primero(self, rol: str) -> Optional[Contenedor]:
        lista = self.por_rol.get(rol) or []
        return lista[0] if lista else None

    def resumen(self) -> Dict:
        return {
            "roles": {r: [c.nombre for c in self.por_rol[r]] for r in ROLES},
            "roles_vacios": [r for r in ROLES if not self.por_rol[r]],
            "rechazados": list(self.rechazados),
            "cargados": [c.como_dict() for c in self.contenedores.values()],
            "total": len(self.contenedores),
        }


# ===============================================================
# ENGINE
# ===============================================================
class Engine:
    def __init__(
        self,
        raiz_modulos: str | Path,
        invocador_id: str = "core",
        verificar_axiomas: bool = True,
        strict: bool = True,
    ):
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id = invocador_id
        self.verificar_axiomas = verificar_axiomas
        self.strict = strict

        self.registro = Registro()
        self.informe_axiomas: Optional[Dict] = None
        self.informe_mecanica: Optional[Dict] = None
        self.estado = "NO_INICIADO"
        self.errores_arranque: List[str] = []
        self.fallos: List[Dict] = []

        self._descubrir()
        self._resolver_dependencias()

        if self.verificar_axiomas:
            self._ejecutar_compuertas()

        if self.errores_arranque:
            self.estado = "RECHAZADO"
            if self.strict:
                raise ArranqueError(
                    "Engine no pudo arrancar:\n  - "
                    + "\n  - ".join(self.errores_arranque)
                )
        else:
            self.estado = "OPERATIVO"

    # -----------------------------------------------------------
    # Descubrimiento
    # -----------------------------------------------------------
    def _descubrir(self) -> None:
        if not self.raiz.exists():
            self.errores_arranque.append(f"Raíz de módulos no existe: {self.raiz}")
            return

        for path in sorted(self.raiz.rglob("__init__.py")):
            # solo paquetes de primer nivel bajo modules/
            if path.parent == self.raiz:
                continue
            # modules/nombre/__init__.py
            if path.parent.parent != self.raiz and self.raiz not in path.parents:
                continue
            # evitar subpaquetes profundos no contenedores
            rel = path.relative_to(self.raiz)
            if len(rel.parts) != 2:
                continue

            try:
                cont = self._cargar_modulo(path)
                if cont:
                    self.registro.registrar(cont)
            except Exception as e:
                self.registro.rechazados.append({
                    "ruta": str(path),
                    "razon": f"{type(e).__name__}: {e}",
                })

    def _cargar_modulo(self, path: Path) -> Optional[Contenedor]:
        directorio = path.parent
        nombre_mod = f"vpsi_{directorio.name}"
        spec = importlib.util.spec_from_file_location(
            nombre_mod,
            path,
            submodule_search_locations=[str(directorio)],
        )
        if spec is None or spec.loader is None:
            return None

        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre_mod] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            self.registro.rechazados.append({
                "ruta": str(path),
                "razon": f"import: {type(e).__name__}: {e}",
            })
            return None

        meta = getattr(mod, "CONTENEDOR", None)
        if not isinstance(meta, dict):
            self.registro.rechazados.append({
                "ruta": str(path),
                "razon": "sin CONTENEDOR dict",
            })
            return None

        nombre = meta.get("nombre")
        rol = meta.get("rol")
        version = str(meta.get("version", "0.0"))

        if not nombre or not rol:
            self.registro.rechazados.append({
                "ruta": str(path),
                "razon": "CONTENEDOR sin nombre o rol",
            })
            return None

        if rol not in ROLES:
            self.registro.rechazados.append({
                "ruta": str(path),
                "razon": f"rol desconocido: {rol}",
            })
            return None

        return Contenedor(
            nombre=str(nombre),
            rol=str(rol),
            version=version,
            modulo=mod,
            ruta=path,
            meta=meta,
        )

    # -----------------------------------------------------------
    def _resolver_dependencias(self) -> None:
        for cont in list(self.registro.contenedores.values()):
            faltan = []
            for req in cont.requiere:
                if req in ROLES:
                    if not self.registro.por_rol.get(req):
                        faltan.append(f"rol:{req}")
                else:
                    if req not in self.registro.contenedores:
                        faltan.append(f"modulo:{req}")
            if faltan:
                self.errores_arranque.append(
                    f"{cont.nombre} ({cont.rol}) requiere {faltan} y no están disponibles"
                )

    # -----------------------------------------------------------
    def _ejecutar_capacidad(
        self,
        cont: Contenedor,
        capacidad: str,
        *args,
        **kwargs,
    ) -> Any:
        fn = cont.fn(capacidad)
        if not callable(fn):
            self.fallos.append({
                "contenedor": cont.nombre,
                "rol": cont.rol,
                "capacidad": capacidad,
                "razon": "no declarada o no callable",
            })
            return UNDEFINED
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.fallos.append({
                "contenedor": cont.nombre,
                "rol": cont.rol,
                "capacidad": capacidad,
                "razon": f"{type(e).__name__}: {e}",
                "traza": traceback.format_exc(limit=3),
            })
            return UNDEFINED

    def _ejecutar_compuertas(self) -> None:
        # Obligatorios presentes
        for rol in OBLIGATORIOS:
            if not self.registro.por_rol.get(rol):
                self.errores_arranque.append(f"Falta rol obligatorio {rol}")

        # MC
        for cont in self.registro.por_rol.get("MC", []):
            for cap in ("verificar", "barrer", "evaluar"):
                if cont.tiene(cap):
                    informe = self._ejecutar_capacidad(cont, cap)
                    if es_undefined(informe):
                        self.errores_arranque.append(f"MC/{cont.nombre}: fallo {cap}")
                    elif isinstance(informe, dict):
                        self.informe_mecanica = informe
                        if not informe.get("coherente", True):
                            self.errores_arranque.append(f"MC/{cont.nombre}: incoherente")
                    break

        # AX
        for cont in self.registro.por_rol.get("AX", []):
            for cap in ("verificar", "barrer", "evaluar"):
                if cont.tiene(cap):
                    informe = self._ejecutar_capacidad(cont, cap)
                    if es_undefined(informe):
                        self.errores_arranque.append(f"AX/{cont.nombre}: fallo {cap}")
                    elif isinstance(informe, dict):
                        self.informe_axiomas = informe
                        if not informe.get("coherente", True):
                            self.errores_arranque.append(f"AX/{cont.nombre}: incoherente")
                    break

        # CT ancla: debe poder leer ALPHA/BETA del módulo
        try:
            self.get_constantes()
        except ArranqueError as e:
            self.errores_arranque.append(str(e))

        # -----------------------------------------------------------
    # Ancla CT
    # -----------------------------------------------------------
    def get_constantes(self) -> Dict[str, Fraction]:
        for cont in self.registro.por_rol.get("CT", []):
            mod = cont.modulo
            alpha = getattr(mod, "ALPHA", None)
            beta = getattr(mod, "BETA", None)
            if isinstance(alpha, Fraction) and isinstance(beta, Fraction):
                return {"ALPHA": alpha, "BETA": beta}
            a_fn, b_fn = cont.fn("alpha"), cont.fn("beta")
            if callable(a_fn) and callable(b_fn):
                return {"ALPHA": a_fn(), "BETA": b_fn()}
        raise ArranqueError("Constantes ALPHA/BETA no disponibles (ancla CT)")

    def get_formulas(self):
        for cont in self.registro.por_rol.get("FO", []):
            mod = cont.modulo
            tru_ri = getattr(mod, "tru_ri", None)
            tru_total = getattr(mod, "tru_total", None)
            if callable(tru_ri) and callable(tru_total):
                return tru_ri, tru_total
            ri_fn = cont.fn("tru_ri")
            tt_fn = cont.fn("tru_total")
            if callable(ri_fn) and callable(tt_fn):
                return ri_fn, tt_fn
        try:
            from modules.formulas.truth import tru_ri, tru_total
            return tru_ri, tru_total
        except ImportError as e:
            raise ArranqueError(
                "Fórmulas tru_ri/tru_total no disponibles: {0}".format(e)
            )

    # -----------------------------------------------------------
    # Evaluación (orquesta; no interpreta)
    # -----------------------------------------------------------
    def ejecutar_capacidad(self, rol: str, capacidad: str, *args, **kwargs) -> Any:
        cont = self.registro.primero(rol)
        if cont is None:
            return UNDEFINED
        return self._ejecutar_capacidad(cont, capacidad, *args, **kwargs)

    def get_resultados_evaluacion(self) -> List[Dict[str, Any]]:
        return list(self.resultados_evaluacion)

    def evaluar(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        self.fallos = []
        peticion = dict(peticion or {})

        def _emit(resultado: Dict[str, Any]) -> Dict[str, Any]:
            registro = {
                "secuencia": len(self.resultados_evaluacion) + 1,
                "entrada": {
                    "contexto": (
                        peticion.get("contexto")
                        or peticion.get("O_context")
                        or peticion.get("Octx")
                    ),
                    "tiene_C": ("C" in peticion and peticion.get("C") is not None),
                    "tiene_L": ("L" in peticion and peticion.get("L") is not None),
                    "tiene_K": ("K" in peticion and peticion.get("K") is not None),
                },
                "resultado": dict(resultado),
            }
            self.resultados_evaluacion.append(registro)
            return resultado

        if self.estado != "OPERATIVO":
            return _emit({
                "estado": "RECHAZADO",
                "razon": "Engine no operativo",
                "errores_arranque": list(self.errores_arranque),
                "fallos": list(self.fallos),
            })

        o_ctx = (
            peticion.get("contexto")
            or peticion.get("O_context")
            or peticion.get("Octx")
        )
        if not o_ctx:
            return _emit({
                "estado": "UNDEFINED",
                "razon": "K indefinido: falta O_context (Corolario Def-5.3.1)",
                "factores": {"C": None, "L": None, "K": "UNDEFINED"},
                "tru_ri": "UNDEFINED",
                "tru_total": "UNDEFINED",
                "fallos": list(self.fallos),
            })

        C = L = K = None
        ca = self.registro.primero("CA")
        if ca and ca.tiene("calcular"):
            calc = self._ejecutar_capacidad(ca, "calcular", peticion)
            if not es_undefined(calc) and isinstance(calc, dict):
                C = calc.get("C")
                L = calc.get("L")
                K = calc.get("K")

        try:
            if "C" in peticion and peticion["C"] is not None:
                C = Fraction(str(peticion["C"]))
            if "L" in peticion and peticion["L"] is not None:
                L = Fraction(str(peticion["L"]))
            if "K" in peticion and peticion["K"] is not None:
                K = Fraction(str(peticion["K"]))
        except Exception as e:
            return _emit({
                "estado": "ERROR",
                "razon": "C, L o K inválidos: {0}".format(e),
                "contexto": o_ctx,
                "fallos": list(self.fallos),
            })

        if C is None or L is None or K is None:
            return _emit({
                "estado": "PARCIAL",
                "razon": (
                    "Faltan factores C/L/K "
                    "(CA no los entregó o no vinieron en la petición)"
                ),
                "contexto": o_ctx,
                "factores": {
                    "C": str(C) if C is not None else None,
                    "L": str(L) if L is not None else None,
                    "K": str(K) if K is not None else None,
                },
                "fallos": list(self.fallos),
            })

        try:
            tru_ri_fn, tru_total_fn = self.get_formulas()
            constantes = self.get_constantes()
            ri = tru_ri_fn(C, L, K)
            tt = tru_total_fn(C, L, K)
        except Exception as e:
            return _emit({
                "estado": "ERROR",
                "razon": "cálculo Tru: {0}: {1}".format(type(e).__name__, e),
                "contexto": o_ctx,
                "fallos": list(self.fallos),
            })

        return _emit({
            "estado": "OK",
            "contexto": o_ctx,
            "factores": {"C": str(C), "L": str(L), "K": str(K)},
            "tru_ri": str(ri),
            "tru_total": str(tt),
            "alpha": str(constantes["ALPHA"]),
            "beta": str(constantes["BETA"]),
            "R_i_equals_R": False,
            "fuentes_usadas": ["X", "O_context"],
            "fallos": list(self.fallos),
        })

    def censar(self) -> Dict:
        return self.registro.resumen()

    def inventario(self) -> Dict:
        contenido = {}
        for cont in self.registro.contenedores.values():
            if cont.tiene("inventario"):
                out = self._ejecutar_capacidad(cont, "inventario")
                if es_undefined(out):
                    contenido[cont.nombre] = {"error": "inventario falló"}
                else:
                    contenido[cont.nombre] = out
        return {
            "estado": self.estado,
            "errores_arranque": list(self.errores_arranque),
            "registro": self.registro.resumen(),
            "contenido": contenido,
            "informe_axiomas": self.informe_axiomas,
            "informe_mecanica": self.informe_mecanica,
            "resultados_evaluacion": list(self.resultados_evaluacion),
            "resultados_evaluacion_n": len(self.resultados_evaluacion),
        }

    def censar_generatividad(self) -> Dict:
        out = self.ejecutar_capacidad("AX", "generatividad")

        try:
            resumen = self.censar() if hasattr(self, "censar") else {}
        except Exception:
            resumen = {}

        roles_vacios = list(resumen.get("roles_vacios") or [])
        rechazados = list(resumen.get("rechazados") or [])

        if es_undefined(out) or not isinstance(out, dict):
            return {
                "estado": "UNDEFINED",
                "razon": "AX.generatividad no disponible o falló",
                "roles_vacios": roles_vacios,
                "rechazados": rechazados,
                "u1_estado": "NO_STAGNANT" if roles_vacios else "REVISAR",
                "nota": "Sin medición TR1; residual de roles usado como proxy U1.",
            }

        resultado = dict(out)
        resultado["roles_vacios"] = roles_vacios
        resultado["rechazados_n"] = len(rechazados)
        if roles_vacios or resultado.get("pares_novedosos", 0) > 0:
            resultado["u1_estado"] = "NO_STAGNANT"
        else:
            resultado["u1_estado"] = resultado.get("u1_proxy", "REVISAR")
        resultado["estado"] = "OK"
        return resultado

    # -----------------------------------------------------------
    # Introspección (sin actuar de más)
    # -----------------------------------------------------------
    def censar(self) -> Dict:
        return self.registro.resumen()

    def inventario(self) -> Dict:
        contenido = {}
        for cont in self.registro.contenedores.values():
            if cont.tiene("inventario"):
                out = self._ejecutar_capacidad(cont, "inventario")
                if es_undefined(out):
                    contenido[cont.nombre] = {"error": "inventario falló"}
                else:
                    contenido[cont.nombre] = out
        return {
            "estado": self.estado,
            "errores_arranque": list(self.errores_arranque),
            "registro": self.registro.resumen(),
            "contenido": contenido,
            "informe_axiomas": self.informe_axiomas,
            "informe_mecanica": self.informe_mecanica,
            "resultados_evaluacion": list(self.resultados_evaluacion),
            "resultados_evaluacion_n": len(self.resultados_evaluacion),
        }

    def get_resultados_evaluacion(self) -> List[Dict[str, Any]]:
        return list(self.resultados_evaluacion)

    def censar_generatividad(self) -> Dict:
        out = self.ejecutar_capacidad("AX", "generatividad")

        try:
            resumen = self.censar() if hasattr(self, "censar") else {}
        except Exception:
            resumen = {}

        roles_vacios = list(resumen.get("roles_vacios") or [])
        rechazados = list(resumen.get("rechazados") or [])

        if es_undefined(out) or not isinstance(out, dict):
            return {
                "estado": "UNDEFINED",
                "razon": "AX.generatividad no disponible o falló",
                "roles_vacios": roles_vacios,
                "rechazados": rechazados,
                "u1_estado": "NO_STAGNANT" if roles_vacios else "REVISAR",
                "nota": "Sin medición TR1; residual de roles usado como proxy U1.",
            }

        resultado = dict(out)
        resultado["roles_vacios"] = roles_vacios
        resultado["rechazados_n"] = len(rechazados)
        if roles_vacios or resultado.get("pares_novedosos", 0) > 0:
            resultado["u1_estado"] = "NO_STAGNANT"
        else:
            resultado["u1_estado"] = resultado.get("u1_proxy", "REVISAR")
        resultado["estado"] = "OK"
        return resultado


__all__ = [
    "Engine",
    "Contenedor",
    "Registro",
    "ROLES",
    "OBLIGATORIOS",
    "UNDEFINED",
    "es_undefined",
    "ArranqueError",
    "EvaluacionError",
    "DominioError",
    "ContratoError",
]
