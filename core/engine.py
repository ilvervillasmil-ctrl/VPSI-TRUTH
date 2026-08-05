# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- core/engine.py
Version 12.2 — orquestador por contrato; CE = extension del Engine.

Principio
  - Descubre modulos por CONTENEDOR (roles y capacidades).
  - Actua solo por lo que cada contrato declara.
  - CE no es un modulo ajeno: es extension del propio Engine.
  - Todo archivo/mandato bajo CE se lee automaticamente.
  - Engine no hardcodea "sujeto", "objeto" ni nombres de mandato:
    deposita lo que cada skill declara en salida_esperada (u homologos).
  - Nuevos mandatos en CE no exigen tocar este archivo.
  - CT: ALPHA/BETA. CA: C/L/K. FO: Tru. CX: marco. CIT: anuncio.
  - Sin O usable → UNDEFINED. Nunca bool(UNDEFINED). No fabrica K/O.
"""

from __future__ import annotations

import importlib.util
import json
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
    if o is None or es_undefined(o):
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
    pass


class EvaluacionError(Exception):
    pass


class DominioError(Exception):
    pass


class ContratoError(Exception):
    pass


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
    "ids": ("ids",),
    "skills": ("skills",),
    "por_id": ("por_id",),
}

# Claves de skill que no son mandatos de ciclo (introspeccion)
_CE_SKIP_IDS = frozenset({
    "barrer", "verificar", "inventario", "ids", "skills", "listar_archivos",
})


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
# Material / recortes (determinista; sin semantica libre)
# ===============================================================
_RE_HABLANTE = re.compile(
    r"(?m)^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{0,40})\s*:\s*(.+)$"
)


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


def _segmentar_lineas_nombre(texto: str) -> List[Dict[str, Any]]:
    if not texto or not str(texto).strip():
        return []
    out: List[Dict[str, Any]] = []
    for m in _RE_HABLANTE.finditer(str(texto)):
        nombre = m.group(1).strip()
        cuerpo = m.group(2).strip()
        if nombre and cuerpo:
            out.append({
                "indice": len(out) + 1,
                "nombre": nombre,
                "texto": cuerpo,
            })
    return out


def _default_para_clave(clave: str) -> Any:
    k = str(clave).strip().lower()
    if k.startswith("n_") or k.endswith("_n") or k in ("n", "count"):
        return 0
    if k in ("sujetos", "por_sujeto", "items", "recortes", "lista"):
        return [] if k != "por_sujeto" else {}
    if k.startswith("por_"):
        return {}
    if k in ("tru_ri", "tru_total", "c", "l", "k"):
        return None
    return None


# ===============================================================
# ENGINE
# ===============================================================
class Engine:
    """
    Orquestador v12.1

    CE es extension del Engine: lee todos los mandatos y deposita
    segun salida_esperada de cada skill. No hardcodea nombres.
    """

    VERSION = "12.2"

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
    # Descubrimiento
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
    # Ejecucion por contrato
    # -----------------------------------------------------------
    def _ejecutar_capacidad(
        self, cont: Contenedor, capacidad: str, *args: Any, **kwargs: Any
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
        self, cont: Contenedor, oficio: str, *args: Any, **kwargs: Any
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
                "Formulas tru_ri/tru_total no disponibles: {0}".format(e)
            )

    # -----------------------------------------------------------
    # CE = extension del Engine (lee TODO automaticamente)
    # -----------------------------------------------------------
    def _ce_cargar(self) -> Dict[str, Any]:
        """
        Carga ids + skills completos desde el contrato CE.
        No filtra por nombre de mandato. Todo lo valido queda a disposicion.
        """
        cont = self.registro.primero("CE")
        if cont is None:
            return {
                "disponible": False,
                "ids": [],
                "skills": [],
                "por_id": {},
                "n": 0,
            }
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
        # dedup ids
        vistos = set()
        ids_u: List[str] = []
        for i in ids:
            if i not in vistos:
                vistos.add(i)
                ids_u.append(i)
        if not ids_u and skills:
            for s in skills:
                sid = str(s.get("id") or "").strip().lower()
                if sid and sid not in vistos:
                    vistos.add(sid)
                    ids_u.append(sid)
        por_id: Dict[str, Dict[str, Any]] = {}
        for s in skills:
            sid = str(s.get("id") or "").strip().lower()
            if not sid:
                continue
            # enriquecer con raw si CE lo expuso via por_id
            if cont.tiene("por_id") and "raw" not in s:
                extra = self._ejecutar_capacidad(cont, "por_id", sid)
                if isinstance(extra, dict):
                    merged = dict(extra)
                    merged.update(s)
                    s = merged
            por_id[sid] = s
        return {
            "disponible": True,
            "ids": ids_u,
            "skills": list(por_id.values()) if por_id else skills,
            "por_id": por_id,
            "n": len(ids_u),
        }

    def _skill_meta(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza campos del contrato del skill sin imponer nombres."""
        raw = skill.get("raw") if isinstance(skill.get("raw"), dict) else {}
        base = dict(raw)
        base.update({k: v for k, v in skill.items() if k != "raw"})
        sid = str(base.get("id") or "").strip().lower()
        salidas = (
            base.get("salida_esperada")
            or base.get("produce")
            or base.get("salidas")
            or []
        )
        if isinstance(salidas, str):
            salidas = [salidas]
        salidas = [str(x).strip() for x in salidas if str(x).strip()]
        entradas = base.get("entrada") or base.get("requiere") or []
        if isinstance(entradas, str):
            entradas = [entradas]
        entradas = [str(x).strip() for x in entradas if str(x).strip()]
        return {
            "id": sid,
            "salida_esperada": salidas,
            "entrada": entradas,
            "nombre": base.get("nombre"),
            "version": base.get("version"),
            "raw": base,
        }

    def _mandatos_ciclo(self, ce: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Todos los skills CE que son mandatos de ciclo (no introspeccion)."""
        out: List[Dict[str, Any]] = []
        for s in ce.get("skills") or []:
            meta = self._skill_meta(s)
            if not meta["id"] or meta["id"] in _CE_SKIP_IDS:
                continue
            out.append(meta)
        # skills solo como id sin detalle
        known = {m["id"] for m in out}
        for sid in ce.get("ids") or []:
            if sid in _CE_SKIP_IDS or sid in known:
                continue
            por = (ce.get("por_id") or {}).get(sid) or {"id": sid}
            out.append(self._skill_meta(por))
        return out

    def _depositar_segun_mandatos(
        self,
        body: Dict[str, Any],
        mandatos: List[Dict[str, Any]],
        relleno: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Deposita en body lo que cada mandato CE declara en salida_esperada.
        Siempre escribe la clave (lista vacia / 0 / {} si no hay datos).
        """
        relleno = dict(relleno or {})

        # 1) volcar relleno calculado (forzoso)
        for k, v in relleno.items():
            body[k] = v

        # 2) asegurar cada salida_esperada
        for m in mandatos:
            for clave in m.get("salida_esperada") or []:
                key = str(clave).strip()
                if not key:
                    continue
                if key in body and body[key] not in (None,):
                    continue
                if key in relleno:
                    body[key] = relleno[key]
                else:
                    body[key] = _default_para_clave(key)
            sal = [str(x).strip() for x in (m.get("salida_esperada") or [])]
            sal_l = [x.lower() for x in sal]
            for k, kl in zip(sal, sal_l):
                if kl.startswith("n_"):
                    base = k[2:] if k.lower().startswith("n_") else kl[2:]
                    if base and base not in body:
                        body[base] = relleno.get(base, [])
                    if k not in body or body[k] is None:
                        base_val = body.get(base)
                        body[k] = (
                            len(base_val)
                            if isinstance(base_val, list)
                            else relleno.get(k, 0)
                        )
                if kl.startswith("por_") and (k not in body or body[k] is None):
                    body[k] = relleno.get(k, {})

    def _recortes_desde_peticion(
        self, peticion: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recortes de material si la peticion o el texto los traen.
        Generico: lista 'sujetos'/'recortes'/'items' o lineas Nombre:.
        """
        for key in ("sujetos", "recortes", "items", "segmentos"):
            raw = peticion.get(key)
            if isinstance(raw, list) and raw:
                segs: List[Dict[str, Any]] = []
                for i, s in enumerate(raw, start=1):
                    if isinstance(s, dict):
                        nombre = str(
                            s.get("nombre") or s.get("id") or "R{0}".format(i)
                        )
                        texto = str(
                            s.get("texto") or s.get("mensaje") or s.get("D") or ""
                        )
                    else:
                        nombre = "R{0}".format(i)
                        texto = str(s)
                    if texto.strip():
                        segs.append({
                            "indice": i,
                            "nombre": nombre,
                            "texto": texto,
                        })
                if segs:
                    return segs
        return _segmentar_lineas_nombre(_texto_peticion(peticion))

    def _ciclo_por_recortes(
        self,
        peticion: Dict[str, Any],
        o_ctx: Any,
        segs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for seg in segs:
            p = dict(peticion)
            p["mensaje"] = seg["texto"]
            p["texto"] = seg["texto"]
            p["descripcion"] = seg["texto"]
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

    def _relleno_desde_recortes(
        self,
        mandatos: List[Dict[str, Any]],
        recortes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Mapea recortes a claves de salida_esperada de cada mandato CE.
        Si el skill pide 'sujetos' u otra lista, se rellena sin hardcodear.
        """
        relleno: Dict[str, Any] = {}
        por = {
            (r.get("nombre") or "R{0}".format(r.get("indice"))): r
            for r in recortes
        }
        skip = {
            "tru_ri", "tru_total", "c", "l", "k", "resultado_ciclo",
            "categoria_tru", "escala_id", "citacion", "ids_tt",
            "escalas_disponibles",
        }
        for m in mandatos:
            sal = [str(x).strip() for x in (m.get("salida_esperada") or [])]
            sal_l = [x.lower() for x in sal]
            lista_key = None
            for k, kl in zip(sal, sal_l):
                if kl.startswith("n_") or kl.startswith("por_"):
                    continue
                if kl in skip:
                    continue
                lista_key = k
                break
            if lista_key is None:
                for k, kl in zip(sal, sal_l):
                    if (
                        not kl.startswith("n_")
                        and not kl.startswith("por_")
                        and kl not in skip
                    ):
                        lista_key = k
                        break
            if lista_key:
                relleno[lista_key] = list(recortes)
                relleno["n_" + str(lista_key)] = len(recortes)
            # Solo generar n_/por_ si el mandato lo declaro en salida_esperada
            for k, kl in zip(sal, sal_l):
                if kl.startswith("n_"):
                    relleno[k] = len(recortes)
                if kl.startswith("por_"):
                    relleno[k] = dict(por)
        return relleno

    # -----------------------------------------------------------
    # API
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

    def get_resultados_evaluacion(self) -> List[Dict[str, Any]]:
        return list(self.resultados_evaluacion)

    def _persistir_evaluaciones(self) -> None:
        """
        Escribe diagnostics/evaluaciones.json con el historial de ciclos.
        Permite a Omega / diagnostico leer el deposito.
        """
        try:
            # raiz del repo = padre de modules/
            root = self.raiz.parent if self.raiz.name == "modules" else self.raiz
            path = root / "diagnostics" / "evaluaciones.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            doc = {
                "engine_version": self.VERSION,
                "invocador_id": self.invocador_id,
                "resultados_evaluacion": list(self.resultados_evaluacion),
                "resultados": list(self.resultados_evaluacion),
                "n": len(self.resultados_evaluacion),
            }
            path.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception:
            pass

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
        self._persistir_evaluaciones()
        return resultado

    def _peticion_con_meta(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
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

    def _tru_fo(self, C: Any, L: Any, K: Any) -> Dict[str, Any]:
        try:
            tru_ri_fn, tru_total_fn = self.get_formulas()
            constantes = self.get_constantes()
            return {
                "tru_ri": tru_ri_fn(C, L, K),
                "tru_total": tru_total_fn(C, L, K),
                "alpha": constantes["ALPHA"],
                "beta": constantes["BETA"],
            }
        except Exception as e:
            return {"error": "calculo Tru: {0}: {1}".format(type(e).__name__, e)}

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
        }

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
        Ciclo por contratos + extension CE.
        CE se lee entero; el deposito sigue salida_esperada de cada mandato.
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

        # --- CE: extension completa ---
        ce = self._ce_cargar()
        mandatos = self._mandatos_ciclo(ce)
        mandatos_ids = [m["id"] for m in mandatos]

        cx = self._marco_cx(peticion)
        o_ctx = self._o_usable(peticion, cx)

        # Recortes de material (si hay)
        segs = self._recortes_desde_peticion(peticion)
        recortes_calc: List[Dict[str, Any]] = []
        if segs and not _o_ausente(o_ctx):
            recortes_calc = self._ciclo_por_recortes(peticion, o_ctx, segs)
        relleno = self._relleno_desde_recortes(mandatos, recortes_calc)

        if _o_ausente(o_ctx):
            ids_cx = list((cx or {}).get("ids_cx_relevantes") or [])
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
                "mandatos_ce": mandatos_ids,
                "valuacion": {
                    "capa_objeto": "indefinido",
                    "capa_meta": "anuncio_de_indefinido",
                    "es_error_sistema": False,
                    "ids": [
                        "Def-5.3.1", "IND-D1", "IND-A1", "IND-A2", "IND-A4",
                        "IND-A5", "IND-L1", "IND-T1", "IND-C2", "IND-C3",
                    ] + ids_cx,
                    "nota": (
                        "Resultado de ciclo, no rechazo de arranque. "
                        "No se fabrica O ni K=0."
                    ),
                },
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            # deposito segun contratos CE aunque el ciclo sea UNDEFINED
            self._depositar_segun_mandatos(body, mandatos, relleno)
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

        ciclo = self._ciclo_factores_tru(peticion)

        if ciclo.get("estado") == "ERROR":
            body = {
                "estado": "ERROR",
                "razon": ciclo.get("razon"),
                "contexto": o_ctx,
                "ce_ids": ce.get("ids") or [],
                "mandatos_ce": mandatos_ids,
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            self._depositar_segun_mandatos(body, mandatos, relleno)
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
                "mandatos_ce": mandatos_ids,
                "fallos": list(self.fallos),
                "engine_version": self.VERSION,
            }
            self._depositar_segun_mandatos(body, mandatos, relleno)
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
            "mandatos_ce": mandatos_ids,
            "fallos": list(self.fallos),
            "engine_version": self.VERSION,
        }
        self._depositar_segun_mandatos(body, mandatos, relleno)
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
            "ce": self._ce_cargar() if self.estado == "OPERATIVO" else {},
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
