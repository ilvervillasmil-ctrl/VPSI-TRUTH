"""
VPSI-TRUTH --- core/engine.py
Versión 11.1 — orquestador por contrato.

Principio (no cambia)
  - Conoce la arquitectura (módulos, roles, contratos, capacidades).
  - Actúa solo por lo que cada CONTENEDOR declara.
  - No inventa operaciones ni interpreta resultados.
  - No sustituye la lógica interna de un módulo.
  - No re-enuncia teoremas (IND-T1 / Def-5.3.1 / TR1 viven en AX).
  - CT: ancla ALPHA/BETA. CA: C/L/K. FO: Tru_Ri / Tru_total.
  - CX: clasifica O / permite_k / pedir_anuncio (no calcula Tru).
  - CIT: anuncia cadena si el marco lo pide (no calcula Tru).
  - MC: coherencia de orden en compuerta.

Lo que 11.1 corrige (sin “imponer” teoría al orquestador)
  - O de contenido solo si viene en la petición o si CX declara
    permite_k is True y aporta O estable. Si no, no hay dominio.
  - Sin O usable → resultado de ciclo UNDEFINED (no crash, no OK).
  - Nunca bool(UNDEFINED). Nunca fabricar K=0 ni O fantasma.
  - Eso es cumplir el contrato de CX + el grafo que AX ya carga;
    no es interpretar el meta-teorema dentro de Engine.

Esquema del ciclo:
  Sustrato → Marco (CX) → Factores (CA) → Fórmula (FO)
  → Cierre (CIT si pedir_anuncio) → Evidencia.
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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


def _o_ausente(o: Any) -> bool:
    """
    True si no hay O usable como dominio de contenido.
    Nunca evalúa bool(UNDEFINED).
    Rótulos de estado ("undefined", "indefinido") no son dominio.
    """
    if o is None:
        return True
    if es_undefined(o):
        return True
    if isinstance(o, str):
        s = o.strip()
        if not s:
            return True
        if s.lower() in ("undefined", "indefinido", "∅", "none", "null"):
            return True
    return False


def _truthy_pedido(v: Any) -> bool:
    """Pedido de anuncio sin bool(UNDEFINED)."""
    if v is None or es_undefined(v):
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "si", "sí", "yes", "on")
    return bool(v)


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
ROLES: Tuple[str, ...] = (
    "CT", "AX", "FO", "MC", "SF", "DG", "CA", "CX", "DI",
    "RE", "VX", "TX", "CH", "CIT", "UI", "GL", "TT", "CC", "CE",
)
OBLIGATORIOS: Tuple[str, ...] = ("CT", "AX", "FO", "MC", "SF")


ALIAS_CAPACIDAD: Dict[str, Tuple[str, ...]] = {
    "barrer": ("barrer", "verificar", "evaluar"),
    "verificar": ("verificar", "barrer", "evaluar"),
    "evaluar": ("evaluar", "verificar", "barrer", "resolver"),
    "resolver": ("resolver", "evaluar", "verificar"),
    "componer": ("componer", "verificar"),
    "inventario": ("inventario",),
    "calcular": ("calcular",),
    "generatividad": ("generatividad",),
    "censo": ("censo", "verificar", "barrer"),
    "reportar": ("reportar",),
    "anunciar": ("anunciar", "registrar", "evaluar", "verificar"),
    "registrar": ("registrar", "anunciar", "evaluar"),
}


# ===============================================================
# CONTENEDOR
# ===============================================================
class Contenedor:
    __slots__ = (
        "nombre", "rol", "version", "modulo", "ruta",
        "requiere", "descripcion", "capacidades",
    )

    def __init__(
        self,
        nombre: str,
        rol: str,
        version: str,
        modulo: Any,
        ruta: Path,
        meta: Dict,
    ) -> None:
        self.nombre = nombre
        self.rol = rol
        self.version = version
        self.modulo = modulo
        self.ruta = ruta
        self.requiere: List[str] = list(meta.get("requiere") or [])
        self.descripcion: str = str(meta.get("descripcion") or "")
        raw = meta.get("capacidades") or {}
        self.capacidades: Dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}

    def fn(self, nombre: str) -> Any:
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

    def fn_oficio(self, nombre: str) -> Any:
        for clave in ALIAS_CAPACIDAD.get(nombre, (nombre,)):
            f = self.fn(clave)
            if callable(f):
                return f
        return None

    def tiene_oficio(self, nombre: str) -> bool:
        return callable(self.fn_oficio(nombre))

    def como_dict(self) -> Dict[str, Any]:
        caps: Dict[str, str] = {}
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
    def __init__(self) -> None:
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {r: [] for r in ROLES}
        self.rechazados: List[Dict[str, Any]] = []

    def registrar(self, cont: Contenedor) -> None:
        if cont.nombre in self.contenedores:
            self.rechazados.append({
                "ruta": str(cont.ruta),
                "razon": "nombre duplicado: {0}".format(cont.nombre),
            })
            return
        self.contenedores[cont.nombre] = cont
        if cont.rol in self.por_rol:
            self.por_rol[cont.rol].append(cont)

    def primero(self, rol: str) -> Optional[Contenedor]:
        lista = self.por_rol.get(rol) or []
        return lista[0] if lista else None

    def total(self) -> int:
        return len(self.contenedores)

    def resumen(self) -> Dict[str, Any]:
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
    """
    Orquestador v11.1

    No interpreta IND-T1 ni Def-5.3.1.
    Solo: contratos, oficios, permite_k de CX, no fabricar O/K.
    """

    VERSION = "11.1"

    def __init__(
        self,
        raiz_modulos: str | Path,
        invocador_id: str = "core",
        verificar_axiomas: bool = True,
        strict: bool = True,
    ) -> None:
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id = invocador_id
        self.verificar_axiomas = verificar_axiomas
        self.strict = strict

        self.registro = Registro()
        self.informe_axiomas: Optional[Dict[str, Any]] = None
        self.informe_mecanica: Optional[Dict[str, Any]] = None
        self.estado = "NO_INICIADO"
        self.errores_arranque: List[str] = []
        self.fallos: List[Dict[str, Any]] = []
        self.resultados_evaluacion: List[Dict[str, Any]] = []

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
    # Sustrato
    # -----------------------------------------------------------
    def _descubrir(self) -> None:
        if not self.raiz.exists():
            self.errores_arranque.append(
                "Raíz de módulos no existe: {0}".format(self.raiz)
            )
            return

        for path in sorted(self.raiz.rglob("__init__.py")):
            try:
                rel = path.relative_to(self.raiz)
            except ValueError:
                continue
            if len(rel.parts) != 2:
                continue
            try:
                cont = self._cargar_modulo(path)
                if cont is not None:
                    self.registro.registrar(cont)
            except Exception as e:
                self.registro.rechazados.append({
                    "ruta": str(path),
                    "razon": "{0}: {1}".format(type(e).__name__, e),
                })

    def _cargar_modulo(self, path: Path) -> Optional[Contenedor]:
        directorio = path.parent
        nombre_mod = "vpsi_{0}".format(directorio.name)
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
                "razon": "import: {0}: {1}".format(type(e).__name__, e),
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
                "razon": "rol desconocido: {0}".format(rol),
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

    def _resolver_dependencias(self) -> None:
        for cont in list(self.registro.contenedores.values()):
            faltan: List[str] = []
            for req in cont.requiere:
                if req in ROLES:
                    if not self.registro.por_rol.get(req):
                        faltan.append("rol:{0}".format(req))
                else:
                    if req not in self.registro.contenedores:
                        faltan.append("modulo:{0}".format(req))
            if faltan:
                self.errores_arranque.append(
                    "{0} ({1}) requiere {2} y no están disponibles".format(
                        cont.nombre, cont.rol, faltan
                    )
                )

    # -----------------------------------------------------------
    # Ejecución fail-closed
    # -----------------------------------------------------------
    def _ejecutar_capacidad(
        self,
        cont: Contenedor,
        capacidad: str,
        *args: Any,
        **kwargs: Any,
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
                "razon": "{0}: {1}".format(type(e).__name__, e),
                "traza": traceback.format_exc(limit=3),
            })
            return UNDEFINED

    def _ejecutar_oficio(
        self,
        cont: Contenedor,
        oficio: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        fn = cont.fn_oficio(oficio)
        if not callable(fn):
            self.fallos.append({
                "contenedor": cont.nombre,
                "rol": cont.rol,
                "oficio": oficio,
                "razon": "oficio no resoluble en contrato",
            })
            return UNDEFINED
        try:
            return fn(*args, **kwargs)
        except TypeError:
            try:
                return fn()
            except Exception as e:
                self.fallos.append({
                    "contenedor": cont.nombre,
                    "rol": cont.rol,
                    "oficio": oficio,
                    "razon": "{0}: {1}".format(type(e).__name__, e),
                    "traza": traceback.format_exc(limit=3),
                })
                return UNDEFINED
        except Exception as e:
            self.fallos.append({
                "contenedor": cont.nombre,
                "rol": cont.rol,
                "oficio": oficio,
                "razon": "{0}: {1}".format(type(e).__name__, e),
                "traza": traceback.format_exc(limit=3),
            })
            return UNDEFINED

    def _ejecutar_compuertas(self) -> None:
        for rol in OBLIGATORIOS:
            if not self.registro.por_rol.get(rol):
                self.errores_arranque.append(
                    "Falta rol obligatorio {0}".format(rol)
                )

        for cont in self.registro.por_rol.get("MC", []):
            for cap in ("verificar", "barrer", "evaluar"):
                if cont.tiene(cap):
                    informe = self._ejecutar_capacidad(cont, cap)
                    if es_undefined(informe):
                        self.errores_arranque.append(
                            "MC/{0}: fallo {1}".format(cont.nombre, cap)
                        )
                    elif isinstance(informe, dict):
                        self.informe_mecanica = informe
                        if not informe.get("coherente", True):
                            self.errores_arranque.append(
                                "MC/{0}: incoherente".format(cont.nombre)
                            )
                    break

        for cont in self.registro.por_rol.get("AX", []):
            for cap in ("verificar", "barrer", "evaluar"):
                if cont.tiene(cap):
                    informe = self._ejecutar_capacidad(cont, cap)
                    if es_undefined(informe):
                        self.errores_arranque.append(
                            "AX/{0}: fallo {1}".format(cont.nombre, cap)
                        )
                    elif isinstance(informe, dict):
                        self.informe_axiomas = informe
                        if not informe.get("coherente", True):
                            self.errores_arranque.append(
                                "AX/{0}: incoherente".format(cont.nombre)
                            )
                    break

        try:
            self.get_constantes()
        except ArranqueError as e:
            self.errores_arranque.append(str(e))

    # -----------------------------------------------------------
    # Anclas CT / FO
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
        raise ArranqueError(
            "Constantes ALPHA/BETA no disponibles (ancla CT)"
        )

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
    # API de oficio
    # -----------------------------------------------------------
    def ejecutar_capacidad(
        self, rol: str, capacidad: str, *args: Any, **kwargs: Any
    ) -> Any:
        cont = self.registro.primero(rol)
        if cont is None:
            return UNDEFINED
        return self._ejecutar_capacidad(cont, capacidad, *args, **kwargs)

    def ejecutar_oficio(
        self, rol: str, oficio: str, *args: Any, **kwargs: Any
    ) -> Any:
        cont = self.registro.primero(rol)
        if cont is None:
            return UNDEFINED
        return self._ejecutar_oficio(cont, oficio, *args, **kwargs)

    # -----------------------------------------------------------
    # Evidencia
    # -----------------------------------------------------------
    def get_resultados_evaluacion(self) -> List[Dict[str, Any]]:
        return list(self.resultados_evaluacion)

    def _emit(
        self,
        resultado: Dict[str, Any],
        peticion: Dict[str, Any],
    ) -> Dict[str, Any]:
        cx = resultado.get("contexto_cx") or {}
        registro = {
            "secuencia": len(self.resultados_evaluacion) + 1,
            "engine_version": self.VERSION,
            "invocador_id": self.invocador_id,
            "entrada": {
                "contexto": (
                    peticion.get("contexto")
                    or peticion.get("O_context")
                    or peticion.get("Octx")
                ),
                "tiene_C": "C" in peticion and peticion.get("C") is not None,
                "tiene_L": "L" in peticion and peticion.get("L") is not None,
                "tiene_K": "K" in peticion and peticion.get("K") is not None,
                "pedir_anuncio": _truthy_pedido(
                    peticion.get("pedir_anuncio")
                ) or _truthy_pedido(cx.get("pedir_anuncio")),
            },
            "resultado": dict(resultado),
        }
        self.resultados_evaluacion.append(registro)
        return resultado

    # -----------------------------------------------------------
    # Ciclo
    # -----------------------------------------------------------
    def _peticion_con_meta(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        """Meta de acto (invocador, versión). No es O de contenido."""
        p = dict(peticion or {})
        p.setdefault("invocador_id", self.invocador_id)
        p.setdefault("engine_version", self.VERSION)
        return p

    def _marco_cx(self, peticion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cont = self.registro.primero("CX")
        if cont is None:
            return None
        out = self._ejecutar_oficio(cont, "evaluar", peticion)
        if es_undefined(out) or not isinstance(out, dict):
            out = self._ejecutar_oficio(cont, "resolver", peticion)
        if es_undefined(out) or not isinstance(out, dict):
            return None
        return out

    def _o_usable(
        self,
        peticion: Dict[str, Any],
        cx: Optional[Dict[str, Any]],
    ) -> Any:
        """
        Dominio O para reclamar K / Tru de contenido.

        Regla de orquestación (contrato, no teorema embebido):
          1) O explícito en la petición.
          2) Si no, solo lo que CX autorice con permite_k is True
             y O/registro estable.
          3) C, L, K, invocador_id, engine_version NUNCA son O.

        Si CX no autoriza K, no hay dominio evaluable → el ciclo
        reporta UNDEFINED (resultado), no inventa camino OK.
        """
        for key in ("contexto", "O_context", "Octx", "enunciado_O", "O_id"):
            o = peticion.get(key)
            if not _o_ausente(o):
                return o

        if not cx:
            return None

        # Contrato CX: sin permite_k no hay dominio de contenido
        if cx.get("permite_k") is not True:
            return None

        reg = cx.get("registro") or {}
        if isinstance(reg, dict):
            if reg.get("estado") and reg.get("estado") != "estable":
                return None
            for key in ("enunciado_O", "O_id"):
                v = reg.get(key)
                if not _o_ausente(v):
                    return v

        o_cx = cx.get("O_context")
        if not _o_ausente(o_cx):
            return o_cx

        return None

    def _cierre_cit(
        self,
        peticion: Dict[str, Any],
        cx: Optional[Dict[str, Any]],
        resultado_parcial: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        pedir = _truthy_pedido(peticion.get("pedir_anuncio"))
        tipos: List[str] = list(peticion.get("tipos_peticion") or [])

        if cx:
            pedir = pedir or _truthy_pedido(cx.get("pedir_anuncio"))
            if not tipos:
                tipos = list(cx.get("tipos_peticion") or [])
            reg = cx.get("registro") or {}
            if isinstance(reg, dict):
                pedir = pedir or _truthy_pedido(reg.get("pedir_anuncio"))
                if not tipos:
                    tipos = list(reg.get("tipos_peticion") or [])

        if not pedir:
            return None

        cont = self.registro.primero("CIT")
        if cont is None:
            self.fallos.append({
                "rol": "CIT",
                "razon": "pedir_anuncio=True pero rol CIT no cargado",
            })
            return {
                "estado": "SIN_OFICIO",
                "razon": "CIT no disponible",
                "pedir_anuncio": True,
                "tipos_peticion": tipos,
            }

        paquete = {
            "peticion": peticion,
            "contexto_cx": cx,
            "resultado": resultado_parcial,
            "tipos_peticion": tipos,
            "invocador_id": self.invocador_id,
            "engine_version": self.VERSION,
        }
        out = self._ejecutar_oficio(cont, "anunciar", paquete)
        if es_undefined(out):
            out = self._ejecutar_oficio(cont, "evaluar", paquete)
        if es_undefined(out):
            return {
                "estado": "FALLO_OFICIO",
                "razon": "CIT sin capacidad anunciar/evaluar resoluble",
                "pedir_anuncio": True,
                "tipos_peticion": tipos,
            }
        if isinstance(out, dict):
            return out
        return {"estado": "OK", "raw": out, "tipos_peticion": tipos}

    def evaluar(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta un ciclo.
        No interpreta Tru. No inventa O ni factores. No embebe teoremas.
        """
        self.fallos = []
        peticion = self._peticion_con_meta(peticion)

        if self.estado != "OPERATIVO":
            return self._emit({
                "estado": "RECHAZADO",
                "razon": "Engine no operativo",
                "errores_arranque": list(self.errores_arranque),
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }, peticion)

        # 1. Marco CX (clasifica; no calcula Tru)
        cx = self._marco_cx(peticion)
        o_ctx = self._o_usable(peticion, cx)

        # 2. Sin O usable → resultado UNDEFINED (ciclo completo, no crash)
        if _o_ausente(o_ctx):
            ids_cx = []
            if cx is not None:
                ids_cx = list(cx.get("ids_cx_relevantes") or [])
            body: Dict[str, Any] = {
                "estado": "UNDEFINED",
                "razon": (
                    "Sin O_context usable: K de contenido no reclamable "
                    "(contrato CX permite_k / Def-5.3.1 en grafo AX)"
                ),
                "factores": {"C": None, "L": None, "K": "UNDEFINED"},
                "tru_ri": "UNDEFINED",
                "tru_total": "UNDEFINED",
                "valuacion": {
                    "capa_objeto": "indefinido",
                    "capa_meta": "anuncio_de_indefinido",
                    "es_error_sistema": False,
                    "ids": [
                        "Def-5.3.1",
                        "IND-D1",
                        "IND-A1",
                        "IND-A2",
                        "IND-A4",
                        "IND-A5",
                        "IND-L1",
                        "IND-T1",
                        "IND-C2",
                        "IND-C3",
                    ] + ids_cx,
                    "nota": (
                        "Resultado de ciclo, no rechazo de arranque. "
                        "Engine permanece OPERATIVO. "
                        "No se fabrica O ni K=0."
                    ),
                },
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            if cx is not None:
                body["contexto_cx"] = {
                    "permite_k": cx.get("permite_k"),
                    "pedir_anuncio": cx.get("pedir_anuncio"),
                    "tipos_peticion": cx.get("tipos_peticion"),
                    "modo_entrada": cx.get("modo_entrada"),
                    "coherente": cx.get("coherente"),
                    "ids_cx_relevantes": cx.get("ids_cx_relevantes"),
                }
            cit = self._cierre_cit(peticion, cx, body)
            if cit is not None:
                body["citacion"] = cit
            return self._emit(body, peticion)

        # 3. Factores (CA y/o petición explícita)
        C = L = K = None
        ca = self.registro.primero("CA")
        if ca is not None and ca.tiene("calcular"):
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
            body = {
                "estado": "ERROR",
                "razon": "C, L o K inválidos: {0}".format(e),
                "contexto": o_ctx,
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            if cx is not None:
                body["contexto_cx"] = {
                    "permite_k": cx.get("permite_k"),
                    "pedir_anuncio": cx.get("pedir_anuncio"),
                }
            return self._emit(body, peticion)

        if C is None or L is None or K is None:
            body = {
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
                "engine_version": self.VERSION,
            }
            if cx is not None:
                body["contexto_cx"] = {
                    "permite_k": cx.get("permite_k"),
                    "pedir_anuncio": cx.get("pedir_anuncio"),
                    "tipos_peticion": cx.get("tipos_peticion"),
                }
            cit = self._cierre_cit(peticion, cx, body)
            if cit is not None:
                body["citacion"] = cit
            return self._emit(body, peticion)

        # 4. Fórmula FO
        try:
            tru_ri_fn, tru_total_fn = self.get_formulas()
            constantes = self.get_constantes()
            ri = tru_ri_fn(C, L, K)
            tt = tru_total_fn(C, L, K)
        except Exception as e:
            body = {
                "estado": "ERROR",
                "razon": "cálculo Tru: {0}: {1}".format(type(e).__name__, e),
                "contexto": o_ctx,
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            if cx is not None:
                body["contexto_cx"] = {"permite_k": cx.get("permite_k")}
            return self._emit(body, peticion)

        body = {
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
            "engine_version": self.VERSION,
        }
        if cx is not None:
            body["contexto_cx"] = {
                "permite_k": cx.get("permite_k"),
                "pedir_anuncio": cx.get("pedir_anuncio"),
                "tipos_peticion": cx.get("tipos_peticion"),
                "modo_entrada": cx.get("modo_entrada"),
                "ids_cx_relevantes": cx.get("ids_cx_relevantes"),
                "coherente": cx.get("coherente"),
            }

        # 5. Cierre CIT
        cit = self._cierre_cit(peticion, cx, body)
        if cit is not None:
            body["citacion"] = cit
            body["fallos"] = list(self.fallos)

        # 6. Evidencia
        return self._emit(body, peticion)

    # -----------------------------------------------------------
    # Introspección
    # -----------------------------------------------------------
    def censar(self) -> Dict[str, Any]:
        return self.registro.resumen()

    def inventario(self) -> Dict[str, Any]:
        contenido: Dict[str, Any] = {}
        for cont in self.registro.contenedores.values():
            if cont.tiene("inventario"):
                out = self._ejecutar_capacidad(cont, "inventario")
                if es_undefined(out):
                    contenido[cont.nombre] = {"error": "inventario falló"}
                else:
                    contenido[cont.nombre] = out
        return {
            "estado": self.estado,
            "engine_version": self.VERSION,
            "invocador_id": self.invocador_id,
            "errores_arranque": list(self.errores_arranque),
            "registro": self.registro.resumen(),
            "contenido": contenido,
            "informe_axiomas": self.informe_axiomas,
            "informe_mecanica": self.informe_mecanica,
            "resultados_evaluacion": list(self.resultados_evaluacion),
            "resultados_evaluacion_n": len(self.resultados_evaluacion),
        }

    def censar_generatividad(self) -> Dict[str, Any]:
        """Solo oficio AX.generatividad si el contrato lo expone."""
        out = self.ejecutar_capacidad("AX", "generatividad")
        try:
            resumen = self.censar()
        except Exception:
            resumen = {}

        roles_vacios = list(resumen.get("roles_vacios") or [])
        rechazados = list(resumen.get("rechazados") or [])

        if es_undefined(out) or not isinstance(out, dict):
            return {
                "estado": "UNDEFINED",
                "razon": "AX.generatividad no disponible o falló",
                "engine_version": self.VERSION,
                "roles_vacios": roles_vacios,
                "rechazados": rechazados,
                "u1_estado": "NO_STAGNANT" if roles_vacios else "REVISAR",
                "nota": (
                    "Sin medición TR1 desde AX; residual de roles como proxy U1. "
                    "TR1 vive en AX, no en Engine."
                ),
            }

        resultado = dict(out)
        resultado["roles_vacios"] = roles_vacios
        resultado["rechazados_n"] = len(rechazados)
        resultado["engine_version"] = self.VERSION
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
    "ALIAS_CAPACIDAD",
    "UNDEFINED",
    "es_undefined",
    "_o_ausente",
    "ArranqueError",
    "EvaluacionError",
    "DominioError",
    "ContratoError",
]
