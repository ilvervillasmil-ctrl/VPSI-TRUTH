# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- core/engine.py
Version 12.0 — orquestador por contrato + extension CE.

Principio
  - Conoce la arquitectura solo por CONTENEDOR (roles, capacidades).
  - Actua solo por lo que cada contrato declara.
  - No inventa operaciones ni interpreta resultados de oficio ajeno.
  - No sustituye la logica interna de un modulo.
  - CT: ALPHA/BETA. CA: C/L/K. FO: Tru_Ri / Tru_total.
  - CX: clasifica O / permite_k / pedir_anuncio (no calcula Tru).
  - CIT: anuncia cadena si el marco lo pide (no calcula Tru).
  - CE: extension del Engine (mandatos). CE no calcula.
  - TT / CC / demas: se usan si el contrato y el mandato lo permiten.

12.0
  - Lee CE (ids/skills) en el ciclo.
  - Recombina ciclos de oficio ya permitido (p. ej. por sujeto).
  - Deposita resultado.sujetos / n_sujetos cuando aplica.
  - Nuevos modulos/roles con CONTENEDOR valido se descubren al arrancar.
  - La secuencia no es una jaula: el esqueleto seguro se mantiene;
    los mandatos CE abren recortes adicionales dentro del contrato.
"""

from __future__ import annotations

import importlib.util
import re
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
        raise TypeError("UNDEFINED no admite conversion a booleano")

    def __eq__(self, other):
        return isinstance(other, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")


UNDEFINED = _Undefined()


def es_undefined(v: Any) -> bool:
    return v is UNDEFINED or isinstance(v, _Undefined)


def _o_ausente(o: Any) -> bool:
    if o is None:
        return True
    if es_undefined(o):
        return True
    if isinstance(o, str):
        s = o.strip()
        if not s:
            return True
        if s.lower() in ("undefined", "indefinido", "none", "null"):
            return True
    return False


def _truthy_pedido(v: Any) -> bool:
    if v is None or es_undefined(v):
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "si", "yes", "on")
    return bool(v)


# ===============================================================
# EXCEPCIONES
# ===============================================================
class ArranqueError(Exception):
    """Incoherencia axiomatica, mecanica o dependencias faltantes."""


class EvaluacionError(Exception):
    """Error en el camino de evaluacion."""


class DominioError(Exception):
    """Error de dominio / O_context."""


class ContratoError(Exception):
    """Contrato CONTENEDOR invalido o capacidad no resoluble."""


# ===============================================================
# ROLES (admitidos al registrar; nuevos se agregan aqui cuando existan)
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
    "ids": ("ids",),
    "skills": ("skills",),
    "por_id": ("por_id",),
}


# ===============================================================
# CONTENEDOR / REGISTRO
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
# SEGMENTACION DETERMINISTA DE SUJETOS (recorte de material)
# ===============================================================
_RE_HABLANTE = re.compile(
    r"(?m)^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{0,40})\s*:\s*(.+)$"
)


def _segmentar_sujetos(texto: str) -> List[Dict[str, Any]]:
    """
    Recorte determinista. No es semantica libre:
    lineas 'Nombre: enunciado'. Si no hay, lista vacia.
    """
    if not texto or not str(texto).strip():
        return []
    hallados: List[Dict[str, Any]] = []
    for m in _RE_HABLANTE.finditer(str(texto)):
        nombre = m.group(1).strip()
        cuerpo = m.group(2).strip()
        if not nombre or not cuerpo:
            continue
        hallados.append({
            "nombre": nombre,
            "texto": cuerpo,
            "indice": len(hallados) + 1,
        })
    return hallados


def _texto_peticion(peticion: Dict[str, Any]) -> str:
    for k in ("mensaje", "descripcion", "texto", "D", "material"):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            return str(v)
    entrada = peticion.get("entrada")
    if isinstance(entrada, dict):
        for k in ("mensaje", "descripcion", "texto"):
            v = entrada.get(k)
            if v is not None and str(v).strip():
                return str(v)
    elif entrada is not None and str(entrada).strip():
        return str(entrada)
    return ""


# ===============================================================
# ENGINE
# ===============================================================
class Engine:
    """
    Orquestador v12.0

    Descubre modulos por CONTENEDOR.
    Consulta CE (mandatos) y recombina ciclos de oficio permitido.
    No interpreta teoremas. No fabrica O/K.
    """

    VERSION = "12.0"

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
    # Descubrimiento de modulos (todos los CONTENEDOR validos)
    # -----------------------------------------------------------
    def _descubrir(self) -> None:
        if not self.raiz.exists():
            self.errores_arranque.append(
                "Raiz de modulos no existe: {0}".format(self.raiz)
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
                    "{0} ({1}) requiere {2} y no estan disponibles".format(
                        cont.nombre, cont.rol, faltan
                    )
                )

    # -----------------------------------------------------------
    # Ejecucion fail-closed por contrato
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
                "Formulas tru_ri/tru_total no disponibles: {0}".format(e)
            )

    # -----------------------------------------------------------
    # CE — brazo del Engine (solo lectura de mandatos)
    # -----------------------------------------------------------
    def _ce_ids_skills(self) -> Dict[str, Any]:
        cont = self.registro.primero("CE")
        if cont is None:
            return {"ids": [], "skills": [], "disponible": False}
        ids: List[str] = []
        skills: List[Dict[str, Any]] = []
        if cont.tiene("ids"):
            out = self._ejecutar_capacidad(cont, "ids")
            if isinstance(out, list):
                ids = [str(x).strip().lower() for x in out if str(x).strip()]
        if cont.tiene("skills"):
            out = self._ejecutar_capacidad(cont, "skills")
            if isinstance(out, list):
                for s in out:
                    if isinstance(s, dict) and s.get("id"):
                        skills.append(dict(s))
        if not ids and skills:
            ids = [str(s["id"]).strip().lower() for s in skills if s.get("id")]
        # dedup estable
        vistos = set()
        ids_u = []
        for i in ids:
            if i not in vistos:
                vistos.add(i)
                ids_u.append(i)
        return {
            "ids": ids_u,
            "skills": skills,
            "disponible": True,
            "n": len(ids_u),
        }

    def _mandatos_aplicables(
        self,
        peticion: Dict[str, Any],
        ce: Dict[str, Any],
    ) -> List[str]:
        """
        Que mandatos CE aplican a esta peticion.
        No ejecuta skills: solo selecciona ids declarados.
        """
        ids = set(ce.get("ids") or [])
        if not ids:
            return []
        aplicables: List[str] = []
        escala = None
        for k in ("escala_id", "categoria_tru", "id_escala", "escala"):
            v = peticion.get(k)
            if v is not None and str(v).strip():
                escala = str(v).strip().lower()
                break
        pedido = peticion.get("mandatos") or peticion.get("ce_mandatos") or []
        if isinstance(pedido, str):
            pedido = [pedido]
        pedido_l = {str(x).strip().lower() for x in pedido if str(x).strip()}

        # explicitos
        for mid in pedido_l:
            if mid in ids and mid not in aplicables:
                aplicables.append(mid)

        # por escala / material
        if "ce_mandato_catalogo" in ids and "ce_mandato_catalogo" not in aplicables:
            aplicables.append("ce_mandato_catalogo")
        if escala and "ce_mandato_escala_tt" in ids and "ce_mandato_escala_tt" not in aplicables:
            aplicables.append("ce_mandato_escala_tt")
        if escala and "ce_mandato_aplicar_escala" in ids and "ce_mandato_aplicar_escala" not in aplicables:
            aplicables.append("ce_mandato_aplicar_escala")

        texto = _texto_peticion(peticion)
        segs = _segmentar_sujetos(texto)
        sujetos_en_pet = peticion.get("sujetos")
        multi = bool(segs) or (
            isinstance(sujetos_en_pet, list) and len(sujetos_en_pet) > 0
        )
        if multi or escala == "tru_sujeto":
            if "ce_mandato_sujetos" in ids and "ce_mandato_sujetos" not in aplicables:
                aplicables.append("ce_mandato_sujetos")
            if "ce_mandato_aplicar_escala" in ids and "ce_mandato_aplicar_escala" not in aplicables:
                aplicables.append("ce_mandato_aplicar_escala")

        return aplicables

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

        # ===========================================================
    # CICLO
    # ===========================================================

    # -----------------------------------------------------------
    # peticion + meta
    # -----------------------------------------------------------
    def _peticion_con_meta(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        p = dict(peticion or {})
        p.setdefault("invocador_id", self.invocador_id)
        p.setdefault("engine_version", self.VERSION)
        return p

    # -----------------------------------------------------------
    # marco CX
    # -----------------------------------------------------------
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

    # -----------------------------------------------------------
    # O usable
    # -----------------------------------------------------------
    def _o_usable(
        self,
        peticion: Dict[str, Any],
        cx: Optional[Dict[str, Any]],
    ) -> Any:
        for key in ("contexto", "O_context", "Octx", "enunciado_O", "O_id"):
            o = peticion.get(key)
            if not _o_ausente(o):
                return o
        if not cx:
            return None
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

    # -----------------------------------------------------------
    # factores CA (C L K)
    # -----------------------------------------------------------
    def _factores_ca(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
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
            return {"error": "C, L o K invalidos: {0}".format(e)}
        return {"C": C, "L": L, "K": K}

    # -----------------------------------------------------------
    # Tru FO (Tru_Ri / Tru_total)
    # -----------------------------------------------------------
    def _tru_fo(self, C: Any, L: Any, K: Any) -> Dict[str, Any]:
        try:
            tru_ri_fn, tru_total_fn = self.get_formulas()
            constantes = self.get_constantes()
            ri = tru_ri_fn(C, L, K)
            tt = tru_total_fn(C, L, K)
            return {
                "tru_ri": ri,
                "tru_total": tt,
                "alpha": constantes["ALPHA"],
                "beta": constantes["BETA"],
            }
        except Exception as e:
            return {"error": "calculo Tru: {0}: {1}".format(type(e).__name__, e)}

    # -----------------------------------------------------------
    # ciclo factores + Tru
    # -----------------------------------------------------------
    def _ciclo_factores_tru(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        fac = self._factores_ca(peticion)
        if fac.get("error"):
            return {"estado": "ERROR", "razon": fac["error"]}
        C, L, K = fac.get("C"), fac.get("L"), fac.get("K")
        if C is None or L is None or K is None:
            return {
                "estado": "PARCIAL",
                "razon": (
                    "Faltan factores C/L/K "
                    "(CA no los entrego o no vinieron en la peticion)"
                ),
                "factores": {
                    "C": str(C) if C is not None else None,
                    "L": str(L) if L is not None else None,
                    "K": str(K) if K is not None else None,
                },
            }
        tru = self._tru_fo(C, L, K)
        if tru.get("error"):
            return {"estado": "ERROR", "razon": tru["error"]}
        return {
            "estado": "OK",
            "factores": {"C": str(C), "L": str(L), "K": str(K)},
            "tru_ri": str(tru["tru_ri"]),
            "tru_total": str(tru["tru_total"]),
            "alpha": str(tru["alpha"]),
            "beta": str(tru["beta"]),
            "C": C,
            "L": L,
            "K": K,
        }

    # -----------------------------------------------------------
    # ciclo por sujetos (hablante Nombre:)
    # -----------------------------------------------------------
    def _ciclo_por_sujetos(
        self,
        peticion: Dict[str, Any],
        o_ctx: Any,
    ) -> List[Dict[str, Any]]:
        """
        Recombina: un ciclo CA+FO por sujeto.
        Segmentacion determinista o lista en peticion['sujetos'].
        """
        sujetos_in = peticion.get("sujetos")
        segs: List[Dict[str, Any]] = []
        if isinstance(sujetos_in, list) and sujetos_in:
            for i, s in enumerate(sujetos_in, start=1):
                if isinstance(s, dict):
                    nombre = str(s.get("nombre") or s.get("id") or "S{0}".format(i))
                    texto = str(s.get("texto") or s.get("mensaje") or "")
                else:
                    nombre = "S{0}".format(i)
                    texto = str(s)
                if texto.strip():
                    segs.append({"indice": i, "nombre": nombre, "texto": texto})
        if not segs:
            segs = _segmentar_sujetos(_texto_peticion(peticion))

        out: List[Dict[str, Any]] = []
        for seg in segs:
            p = dict(peticion)
            p["mensaje"] = seg["texto"]
            p["texto"] = seg["texto"]
            p["descripcion"] = seg["texto"]
            p.setdefault("escala_id", "tru_sujeto")
            p.setdefault("categoria_tru", "tru_sujeto")
            if not _o_ausente(o_ctx):
                p.setdefault("contexto", o_ctx)
                p.setdefault("O_context", o_ctx)
            for k in ("C", "L", "K"):
                p.pop(k, None)
            ciclo = self._ciclo_factores_tru(p)
            item = {
                "indice": seg["indice"],
                "nombre": seg["nombre"],
                "texto": seg["texto"],
                "estado": ciclo.get("estado"),
            }
            if ciclo.get("estado") == "OK":
                item["C"] = ciclo["factores"]["C"]
                item["L"] = ciclo["factores"]["L"]
                item["K"] = ciclo["factores"]["K"]
                item["tru_ri"] = ciclo["tru_ri"]
                item["tru_total"] = ciclo["tru_total"]
            else:
                item["razon"] = ciclo.get("razon")
                item["factores"] = ciclo.get("factores")
            out.append(item)
        return out

    # -----------------------------------------------------------
    # cierre CIT
    # -----------------------------------------------------------
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

    # -----------------------------------------------------------
    # evaluar (orquestacion)
    # -----------------------------------------------------------
    def evaluar(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta un ciclo por contratos disponibles + mandatos CE.
        No interpreta Tru. No inventa O ni factores.
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

        # --- CE: extension (mandatos a disposicion) ---
        ce = self._ce_ids_skills()
        mandatos = self._mandatos_aplicables(peticion, ce)

        # 1. Marco CX
        cx = self._marco_cx(peticion)
        o_ctx = self._o_usable(peticion, cx)

        # 2. Sin O usable
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
                "ce_ids": ce.get("ids") or [],
                "mandatos_aplicados": mandatos,
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

        # 3. Recombinacion por mandato de sujetos (si aplica)
        sujetos: List[Dict[str, Any]] = []
        if "ce_mandato_sujetos" in mandatos or (
            str(peticion.get("escala_id") or peticion.get("categoria_tru") or "")
            .strip()
            .lower()
            == "tru_sujeto"
        ):
            sujetos = self._ciclo_por_sujetos(peticion, o_ctx)

        # 4. Ciclo principal CA + FO
        ciclo = self._ciclo_factores_tru(peticion)
        if ciclo.get("estado") == "ERROR":
            body = {
                "estado": "ERROR",
                "razon": ciclo.get("razon"),
                "contexto": o_ctx,
                "ce_ids": ce.get("ids") or [],
                "mandatos_aplicados": mandatos,
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            if sujetos:
                body["sujetos"] = sujetos
                body["n_sujetos"] = len(sujetos)
                body["por_sujeto"] = {
                    s.get("nombre") or "S{0}".format(s.get("indice")): s
                    for s in sujetos
                }
            if cx is not None:
                body["contexto_cx"] = {
                    "permite_k": cx.get("permite_k"),
                    "pedir_anuncio": cx.get("pedir_anuncio"),
                }
            return self._emit(body, peticion)

        if ciclo.get("estado") == "PARCIAL":
            body = {
                "estado": "PARCIAL",
                "razon": ciclo.get("razon"),
                "contexto": o_ctx,
                "factores": ciclo.get("factores"),
                "ce_ids": ce.get("ids") or [],
                "mandatos_aplicados": mandatos,
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            if sujetos:
                body["sujetos"] = sujetos
                body["n_sujetos"] = len(sujetos)
                body["por_sujeto"] = {
                    s.get("nombre") or "S{0}".format(s.get("indice")): s
                    for s in sujetos
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

        body = {
            "estado": "OK",
            "contexto": o_ctx,
            "factores": ciclo["factores"],
            "tru_ri": ciclo["tru_ri"],
            "tru_total": ciclo["tru_total"],
            "alpha": ciclo["alpha"],
            "beta": ciclo["beta"],
            "R_i_equals_R": False,
            "fuentes_usadas": ["X", "O_context"],
            "ce_ids": ce.get("ids") or [],
            "mandatos_aplicados": mandatos,
            "fallos": list(self.fallos),
            "engine_version": self.VERSION,
        }
        if sujetos:
            body["sujetos"] = sujetos
            body["n_sujetos"] = len(sujetos)
            body["por_sujeto"] = {
                s.get("nombre") or "S{0}".format(s.get("indice")): s
                for s in sujetos
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

        cit = self._cierre_cit(peticion, cx, body)
        if cit is not None:
            body["citacion"] = cit
            body["fallos"] = list(self.fallos)

        return self._emit(body, peticion)

    # -----------------------------------------------------------
    # Introspeccion
    # -----------------------------------------------------------
    def censar(self) -> Dict[str, Any]:
        return self.registro.resumen()

    def inventario(self) -> Dict[str, Any]:
        contenido: Dict[str, Any] = {}
        for cont in self.registro.contenedores.values():
            if cont.tiene("inventario"):
                out = self._ejecutar_capacidad(cont, "inventario")
                if es_undefined(out):
                    contenido[cont.nombre] = {"error": "inventario fallo"}
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
            "ce": self._ce_ids_skills() if self.estado == "OPERATIVO" else {},
        }

    def censar_generatividad(self) -> Dict[str, Any]:
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
                "razon": "AX.generatividad no disponible o fallo",
                "engine_version": self.VERSION,
                "roles_vacios": roles_vacios,
                "rechazados": rechazados,
                "u1_estado": "NO_STAGNANT" if roles_vacios else "REVISAR",
                "nota": (
                    "Sin medicion TR1 desde AX; residual de roles como proxy U1. "
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
