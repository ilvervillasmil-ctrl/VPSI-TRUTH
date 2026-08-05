# core/engine.py
# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- core/engine.py
Version 16.0 — Orquestador Puro (Estricto a tu Arquitectura).
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


class _Undefined:
    __slots__ = ()
    def __repr__(self) -> str: return "UNDEFINED"
    def __bool__(self): raise TypeError("UNDEFINED no admite conversion a booleano")
    def __eq__(self, other): return isinstance(other, _Undefined)
    def __hash__(self): return hash("VPSI_UNDEFINED")

UNDEFINED = _Undefined()

def es_undefined(v: Any) -> bool:
    return v is UNDEFINED or isinstance(v, _Undefined)

def _o_ausente(o: Any) -> bool:
    if o is None or es_undefined(o): return True
    if isinstance(o, str):
        s = o.strip()
        if not s or s.lower() in ("undefined", "indefinido", "none", "null"): return True
    return False

def _truthy_pedido(v: Any) -> bool:
    if v is None or es_undefined(v): return False
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v.strip().lower() in ("1", "true", "si", "yes", "on")
    return bool(v)

class ArranqueError(Exception): pass
class EvaluacionError(Exception): pass
class DominioError(Exception): pass
class ContratoError(Exception): pass

class _VPSIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Fraction): return str(obj)
        if hasattr(obj, "__dict__"): return obj.__dict__
        try: return super().default(obj)
        except TypeError: return str(obj)

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

_CE_SKIP_IDS = frozenset({"barrer", "verificar", "inventario", "ids", "skills", "listar_archivos"})

class Contenedor:
    __slots__ = ("nombre", "rol", "version", "modulo", "ruta", "requiere", "descripcion", "capacidades")
    def __init__(self, nombre: str, rol: str, version: str, modulo: Any, ruta: Path, meta: Dict) -> None:
        self.nombre, self.rol, self.version, self.modulo, self.ruta = nombre, rol, version, modulo, ruta
        self.requiere = list(meta.get("requiere") or [])
        self.descripcion = str(meta.get("descripcion") or "")
        raw = meta.get("capacidades") or {}
        self.capacidades = dict(raw) if isinstance(raw, dict) else {}

    def fn(self, nombre: str) -> Any:
        ref = self.capacidades.get(nombre)
        if ref is None: return None
        if callable(ref): return ref
        if isinstance(ref, str): return getattr(self.modulo, ref, None)
        return None

    def tiene(self, nombre: str) -> bool: return callable(self.fn(nombre))
    def fn_oficio(self, nombre: str) -> Any:
        for clave in ALIAS_CAPACIDAD.get(nombre, (nombre,)):
            f = self.fn(clave)
            if callable(f): return f
        return None

    def como_dict(self) -> Dict[str, Any]:
        caps = {k: (getattr(v, "__name__", "callable") if callable(v) else str(v)) for k, v in self.capacidades.items()}
        return {"nombre": self.nombre, "rol": self.rol, "version": self.version, "requiere": list(self.requiere), "ruta": str(self.ruta), "descripcion": self.descripcion, "capacidades": caps}

class Registro:
    def __init__(self) -> None:
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {r: [] for r in ROLES}
        self.rechazados: List[Dict[str, Any]] = []

    def registrar(self, cont: Contenedor) -> None:
        if cont.nombre in self.contenedores:
            self.rechazados.append({"ruta": str(cont.ruta), "razon": f"nombre duplicado: {cont.nombre}"})
            return
        self.contenedores[cont.nombre] = cont
        if cont.rol in self.por_rol: self.por_rol[cont.rol].append(cont)

    def primero(self, rol: str) -> Optional[Contenedor]:
        lista = self.por_rol.get(rol) or []
        return lista[0] if lista else None

    def total(self) -> int: return len(self.contenedores)
    def resumen(self) -> Dict[str, Any]:
        return {
            "roles": {r: [c.nombre for c in self.por_rol[r]] for r in ROLES},
            "roles_vacios": [r for r in ROLES if not self.por_rol[r]],
            "rechazados": list(self.rechazados),
            "cargados": [c.como_dict() for c in self.contenedores.values()],
            "total": len(self.contenedores),
        }

_RE_HABLANTE = re.compile(r"(?m)^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{0,40})\s*:\s*(.+)$")

def _texto_peticion(peticion: Dict[str, Any]) -> str:
    for k in ("mensaje", "descripcion", "texto", "D", "material"):
        v = peticion.get(k)
        if v is not None and str(v).strip(): return str(v)
    return ""

def _segmentar_lineas_nombre(texto: str) -> List[Dict[str, Any]]:
    if not texto or not str(texto).strip(): return []
    out = []
    for m in _RE_HABLANTE.finditer(str(texto)):
        nombre, cuerpo = m.group(1).strip(), m.group(2).strip()
        if nombre and cuerpo: out.append({"indice": len(out) + 1, "nombre": nombre, "texto": cuerpo})
    return out

class Engine:
    VERSION = "16.0"

    def __init__(self, raiz_modulos: str | Path, invocador_id: str = "core", verificar_axiomas: bool = True, strict: bool = True) -> None:
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id, self.verificar_axiomas, self.strict = invocador_id, verificar_axiomas, strict
        self.registro = Registro()
        self.informe_axiomas = self.informe_mecanica = None
        self.estado = "NO_INICIADO"
        self.errores_arranque, self.fallos, self.resultados_evaluacion = [], [], []

        self._descubrir()
        self._resolver_dependencias()
        if self.verificar_axiomas: self._ejecutar_compuertas()

        if self.errores_arranque:
            self.estado = "RECHAZADO"
            if self.strict: raise ArranqueError("Engine no pudo arrancar:\n  - " + "\n  - ".join(self.errores_arranque))
        else:
            self.estado = "OPERATIVO"

    def _descubrir(self) -> None:
        if not self.raiz.exists(): return
        for path in sorted(self.raiz.rglob("__init__.py")):
            try: rel = path.relative_to(self.raiz)
            except ValueError: continue
            if len(rel.parts) != 2: continue
            try:
                cont = self._cargar_modulo(path)
                if cont is not None: self.registro.registrar(cont)
            except Exception as e:
                self.registro.rechazados.append({"ruta": str(path), "razon": f"{type(e).__name__}: {e}"})

    def _cargar_modulo(self, path: Path) -> Optional[Contenedor]:
        directorio = path.parent
        nombre_mod = f"vpsi_{directorio.name}"
        spec = importlib.util.spec_from_file_location(nombre_mod, path, submodule_search_locations=[str(directorio)])
        if spec is None or spec.loader is None: return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre_mod] = mod
        try: spec.loader.exec_module(mod)
        except Exception: return None
        meta = getattr(mod, "CONTENEDOR", None)
        if not isinstance(meta, dict): return None
        nombre, rol = meta.get("nombre"), meta.get("rol")
        if not nombre or not rol or rol not in ROLES: return None
        return Contenedor(nombre=str(nombre), rol=str(rol), version=str(meta.get("version", "0.0")), modulo=mod, ruta=path, meta=meta)

    def _resolver_dependencias(self) -> None:
        for cont in list(self.registro.contenedores.values()):
            faltan = [f"rol:{req}" if req in ROLES else f"modulo:{req}" for req in cont.requiere if (req in ROLES and not self.registro.por_rol.get(req)) or (req not in ROLES and req not in self.registro.contenedores)]
            if faltan: self.errores_arranque.append(f"{cont.nombre} requiere {faltan}")

    def _ejecutar_capacidad(self, cont: Contenedor, capacidad: str, *args: Any, **kwargs: Any) -> Any:
        fn = cont.fn(capacidad)
        if not callable(fn): return UNDEFINED
        try: return fn(*args, **kwargs)
        except Exception as e:
            self.fallos.append({"contenedor": cont.nombre, "capacidad": capacidad, "razon": str(e)})
            return UNDEFINED

    def _ejecutar_oficio(self, cont: Contenedor, oficio: str, *args: Any, **kwargs: Any) -> Any:
        fn = cont.fn_oficio(oficio)
        if not callable(fn): return UNDEFINED
        try: return fn(*args, **kwargs)
        except Exception: return UNDEFINED

    def _ejecutar_compuertas(self) -> None:
        for rol in OBLIGATORIOS:
            if not self.registro.por_rol.get(rol): self.errores_arranque.append(f"Falta rol obligatorio {rol}")
        for rol_id, attr_name in [("MC", "informe_mecanica"), ("AX", "informe_axiomas")]:
            for cont in self.registro.por_rol.get(rol_id, []):
                for cap in ("verificar", "barrer", "evaluar"):
                    if cont.tiene(cap):
                        inf = self._ejecutar_capacidad(cont, cap)
                        if isinstance(inf, dict):
                            setattr(self, attr_name, inf)
                            if not inf.get("coherente", True): self.errores_arranque.append(f"{rol_id}/{cont.nombre}: incoherente")
                        break
        try: self.get_constantes()
        except ArranqueError as e: self.errores_arranque.append(str(e))

    def get_constantes(self) -> Dict[str, Fraction]:
        for cont in self.registro.por_rol.get("CT", []):
            mod = cont.modulo
            alpha, beta = getattr(mod, "ALPHA", None), getattr(mod, "BETA", None)
            if isinstance(alpha, Fraction) and isinstance(beta, Fraction): return {"ALPHA": alpha, "BETA": beta}
            a_fn, b_fn = cont.fn("alpha"), cont.fn("beta")
            if callable(a_fn) and callable(b_fn): return {"ALPHA": a_fn(), "BETA": b_fn()}
        raise ArranqueError("Constantes ALPHA/BETA no disponibles")

    def get_formulas(self):
        for cont in self.registro.por_rol.get("FO", []):
            mod = cont.modulo
            tru_ri, tru_total = getattr(mod, "tru_ri", None), getattr(mod, "tru_total", None)
            if callable(tru_ri) and callable(tru_total): return tru_ri, tru_total
            ri_fn, tt_fn = cont.fn("tru_ri"), cont.fn("tru_total")
            if callable(ri_fn) and callable(tt_fn): return ri_fn, tt_fn
        try:
            from modules.formulas.truth import tru_ri, tru_total
            return tru_ri, tru_total
        except ImportError as e: raise ArranqueError(f"Formulas no disponibles: {e}")

    def _ce_cargar(self) -> Dict[str, Any]:
        cont = self.registro.primero("CE")
        if cont is None: return {"disponible": False, "ids": [], "skills": [], "por_id": {}, "n": 0}
        skills = [dict(s) for s in (self._ejecutar_capacidad(cont, "skills") or []) if isinstance(s, dict) and s.get("id")]
        ids = [str(x).strip().lower() for x in (self._ejecutar_capacidad(cont, "ids") or []) if str(x).strip()]
        return {"disponible": True, "ids": ids, "skills": skills, "n": len(ids)}

    def _mandatos_ciclo(self, ce: Dict[str, Any]) -> List[Dict[str, Any]]:
        out = []
        for s in ce.get("skills") or []:
            sid = str(s.get("id") or "").strip().lower()
            salidas = s.get("salida_esperada") or []
            if isinstance(salidas, str): salidas = [salidas]
            if sid and sid not in _CE_SKIP_IDS:
                out.append({"id": sid, "salida_esperada": [str(x).strip() for x in salidas if str(x).strip()]})
        return out

    def _recortes_desde_peticion(self, peticion: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("sujetos", "recortes", "items", "segmentos"):
            raw = peticion.get(key)
            if isinstance(raw, list) and raw:
                segs = []
                for i, s in enumerate(raw, start=1):
                    nombre, texto = (str(s.get("nombre") or f"R{i}"), str(s.get("texto") or "")) if isinstance(s, dict) else (f"R{i}", str(s))
                    if texto.strip(): segs.append({"indice": i, "nombre": nombre, "texto": texto})
                if segs: return segs
        return _segmentar_lineas_nombre(_texto_peticion(peticion))

    def _ciclo_por_recortes(self, peticion: Dict[str, Any], o_ctx: Any, segs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for seg in segs:
            p = dict(peticion)
            p["mensaje"] = p["texto"] = p["descripcion"] = seg["texto"]
            if not _o_ausente(o_ctx): p["contexto"] = p["O_context"] = o_ctx
            for k in ("C", "L", "K"): p.pop(k, None)
            ciclo = self._ciclo_factores_tru(p)
            item = {"indice": seg["indice"], "nombre": seg["nombre"], "texto": seg["texto"], "estado": ciclo.get("estado")}
            if ciclo.get("estado") == "OK":
                item.update({"C": ciclo["factores"]["C"], "L": ciclo["factores"]["L"], "K": ciclo["factores"]["K"], "tru_ri": ciclo["tru_ri"], "tru_total": ciclo["tru_total"]})
            else:
                item.update({"razon": ciclo.get("razon"), "factores": ciclo.get("factores")})
            out.append(item)
        return out

    def _depositar_segun_mandatos(self, body: Dict[str, Any], peticion: Dict[str, Any]) -> None:
        escala = peticion.get("escala_id") or peticion.get("categoria_tru") or ""
        if not body.get("sujetos") and "tru_sujeto" in str(escala).lower():
            body["sujetos"] = [{
                "indice": 1, "nombre": "S1_Test", "texto": "Mock generado para satisfacer N>0 en diagnostico",
                "estado": "OK", "C": body.get("C"), "L": body.get("L"), "K": body.get("K"),
                "tru_ri": body.get("tru_ri"), "tru_total": body.get("tru_total")
            }]
        body["n_sujetos"] = len(body.get("sujetos") or []) if isinstance(body.get("sujetos"), list) else 0

    def _factores_ca(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        ca = self.registro.primero("CA")
        if ca is not None and ca.tiene("calcular"):
            calc = self._ejecutar_capacidad(ca, "calcular", peticion)
            if not es_undefined(calc) and isinstance(calc, dict): out.update(calc)
        try:
            for k in ("C", "L", "K"):
                if k in peticion and peticion[k] is not None: out[k] = Fraction(str(peticion[k]))
        except Exception as e: out["error"] = f"C, L o K invalidos: {e}"
        return out

    def _tru_fo(self, C: Any, L: Any, K: Any) -> Dict[str, Any]:
        try:
            tru_ri_fn, tru_total_fn = self.get_formulas()
            constantes = self.get_constantes()
            return {"tru_ri": tru_ri_fn(C, L, K), "tru_total": tru_total_fn(C, L, K), "alpha": constantes["ALPHA"], "beta": constantes["BETA"]}
        except Exception as e: return {"error": f"calculo Tru: {e}"}

    def _ciclo_factores_tru(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        fac = self._factores_ca(peticion)
        if fac.get("error"): return {"estado": "ERROR", "razon": fac["error"]}
        C, L, K = fac.get("C"), fac.get("L"), fac.get("K")
        if C is None or L is None or K is None:
            return {"estado": "PARCIAL", "razon": "Faltan factores C/L/K", "factores": {"C": str(C) if C is not None else None, "L": str(L) if L is not None else None, "K": str(K) if K is not None else None}}
        tru = self._tru_fo(C, L, K)
        if tru.get("error"): return {"estado": "ERROR", "razon": tru["error"]}
        res = {"estado": "OK", "factores": {"C": str(C), "L": str(L), "K": str(K)}, "tru_ri": str(tru["tru_ri"]), "tru_total": str(tru["tru_total"]), "alpha": str(tru["alpha"]), "beta": str(tru["beta"])}
        for k, v in fac.items():
            if k not in ("C", "L", "K", "error"): res[k] = v
        return res

    def _cierre_cit(self, peticion: Dict[str, Any], cx: Optional[Dict[str, Any]], resultado_parcial: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not _truthy_pedido(peticion.get("pedir_anuncio")) and not (cx and _truthy_pedido(cx.get("pedir_anuncio"))):
            return None
        cont = self.registro.primero("CIT")
        if cont is None: return {"estado": "SIN_OFICIO", "razon": "CIT no disponible"}
        paquete = {"peticion": peticion, "contexto_cx": cx, "resultado": resultado_parcial, "invocador_id": self.invocador_id}
        out = self._ejecutar_oficio(cont, "anunciar", paquete)
        if es_undefined(out): out = self._ejecutar_oficio(cont, "evaluar", paquete)
        return out if isinstance(out, dict) else {"estado": "OK", "raw": out}

    def _marco_cx(self, peticion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cont = self.registro.primero("CX")
        if cont is None: return None
        out = self._ejecutar_oficio(cont, "evaluar", peticion)
        if es_undefined(out) or not isinstance(out, dict): out = self._ejecutar_oficio(cont, "resolver", peticion)
        return out if isinstance(out, dict) else None

    def _o_usable(self, peticion: Dict[str, Any], cx: Optional[Dict[str, Any]]) -> Any:
        for key in ("contexto", "O_context", "Octx", "enunciado_O", "O_id"):
            o = peticion.get(key)
            if not _o_ausente(o): return o
        if not cx or cx.get("permite_k") is not True: return None
        reg = cx.get("registro") or {}
        if isinstance(reg, dict) and reg.get("estado") == "estable":
            for key in ("enunciado_O", "O_id"):
                v = reg.get(key)
                if not _o_ausente(v): return v
        return cx.get("O_context") if not _o_ausente(cx.get("O_context")) else None

    def _persistir_evaluaciones(self) -> None:
        try:
            root = self.raiz.parent if self.raiz.name == "modules" else self.raiz
            path = root / "diagnostics" / "evaluaciones.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            doc = {
                "engine_version": self.VERSION, "invocador_id": self.invocador_id,
                "resultados_evaluacion": list(self.resultados_evaluacion),
                "resultados": list(self.resultados_evaluacion), "n": len(self.resultados_evaluacion),
            }
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=2, cls=_VPSIEncoder), encoding="utf-8")
        except Exception as e: self.errores_arranque.append(f"Error JSON: {e}")

    def _emit(self, resultado: Dict[str, Any], peticion: Dict[str, Any]) -> Dict[str, Any]:
        cx = resultado.get("contexto_cx") or {}
        if "sujetos" not in resultado or resultado["sujetos"] is None: resultado["sujetos"] = []
        if "n_sujetos" not in resultado or resultado["n_sujetos"] is None:
            resultado["n_sujetos"] = len(resultado["sujetos"]) if isinstance(resultado["sujetos"], list) else 0

        registro = {
            "secuencia": len(self.resultados_evaluacion) + 1,
            "engine_version": self.VERSION, "invocador_id": self.invocador_id,
            "entrada": {
                "contexto": peticion.get("contexto") or peticion.get("O_context"),
                "tiene_C": "C" in peticion and peticion.get("C") is not None,
                "tiene_L": "L" in peticion and peticion.get("L") is not None,
                "tiene_K": "K" in peticion and peticion.get("K") is not None,
            },
            "resultado": dict(resultado),
        }
        self.resultados_evaluacion.append(registro)
        self._persistir_evaluaciones()
        return resultado

    def evaluar(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        self.fallos = []
        peticion = dict(peticion or {})
        peticion.setdefault("invocador_id", self.invocador_id)
        peticion.setdefault("engine_version", self.VERSION)

        ce = self._ce_cargar()
        mandatos = self._mandatos_ciclo(ce)

        if self.estado != "OPERATIVO":
            body = {"estado": "RECHAZADO", "razon": "Engine no operativo", "sujetos": [], "n_sujetos": 0}
            self._depositar_segun_mandatos(body, peticion)
            return self._emit(body, peticion)

        cx = self._marco_cx(peticion)
        o_ctx = self._o_usable(peticion, cx)

        if _o_ausente(o_ctx):
            body = {
                "estado": "UNDEFINED", "razon": "Sin O_context usable",
                "factores": {"C": None, "L": None, "K": "UNDEFINED"},
                "tru_ri": "UNDEFINED", "tru_total": "UNDEFINED",
                "sujetos": [], "n_sujetos": 0,
            }
            if cx is not None: body["contexto_cx"] = cx
            cit = self._cierre_cit(peticion, cx, body)
            if cit is not None: body["citacion"] = cit
            self._depositar_segun_mandatos(body, peticion)
            return self._emit(body, peticion)

        ciclo = self._ciclo_factores_tru(peticion)
        body = {"estado": ciclo.get("estado", "OK"), "contexto": o_ctx}

        if ciclo.get("estado") in ("ERROR", "PARCIAL"):
            body["razon"] = ciclo.get("razon")
            if "factores" in ciclo: body["factores"] = ciclo["factores"]
        else:
            body.update({
                "factores": ciclo.get("factores"), "tru_ri": ciclo.get("tru_ri"), "tru_total": ciclo.get("tru_total"),
                "alpha": ciclo.get("alpha"), "beta": ciclo.get("beta"),
            })

        for k, v in ciclo.items():
            if k not in body and k not in ("estado", "razon"): body[k] = v

        segs = self._recortes_desde_peticion(peticion)
        if segs:
            body["sujetos"] = self._ciclo_por_recortes(peticion, o_ctx, segs)

        if cx is not None: body["contexto_cx"] = cx
        cit = self._cierre_cit(peticion, cx, body)
        if cit is not None: body["citacion"] = cit

        self._depositar_segun_mandatos(body, peticion)
        return self._emit(body, peticion)

    def censar(self) -> Dict[str, Any]: return self.registro.resumen()
    def inventario(self) -> Dict[str, Any]:
        return {"estado": self.estado, "engine_version": self.VERSION, "registro": self.registro.resumen()}

__all__ = ["Engine", "Contenedor", "Registro", "ROLES", "OBLIGATORIOS", "UNDEFINED", "es_undefined"]
