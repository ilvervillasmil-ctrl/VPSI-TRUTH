# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/capacidades_engine/__init__.py

Rol CE — capacidades del Engine (extension del propio Engine).

CONTRATO (exclusivo de Engine)
  Este modulo ES del Engine. No es un servicio externo.
  El INIT es el contrato: solo Engine lo consume.
  Todo archivo .py del directorio (salvo _*) que declare
  SKILL / SKILLS es un miembro del Engine.
  Tambien se exponen bloques de contrato del directorio
  (PUENTE_DEPOSITO, DEFINICION_SUJETO, etc.) cuando existan.
  Engine los lee todos, a disposicion, cuando quiera y como quiera.
  CE no filtra el uso: expone lo que hay; Engine decide.

OFICIO DE ESTE INIT
  - Descubrir automaticamente todos los *.py del directorio
  - Exponer ids, skills, inventario, puente de deposito y
    definicion de sujeto a Engine
  - Aceptar un archivo con SKILLS = [ ... ] (varios mandatos)
  - No calcular, no depositar, no orquestar el ciclo

SUJETO (termino del ciclo, no gramatica)
  En este rol, "sujeto" NO es el sujeto gramatical de la oracion.
  Sujeto = hablante etiquetado en el material con la forma
  "Nombre: mensaje" (ej. Carlo:, Maria:, Juan:).
  Ver DEFINICION_SUJETO cuando el archivo de mandatos lo declare.

REQUISITO
  "CE" debe figurar en ROLES de core/engine.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_DIR = Path(__file__).resolve().parent
_CAP = _DIR


def _normalizar_meta(meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    sid = str(meta.get("id") or "").strip().lower()
    if not sid:
        return None
    meta = dict(meta)
    if not str(meta.get("descripcion") or "").strip():
        for alt in ("enunciado", "descripcion_larga", "nota", "notas"):
            if str(meta.get(alt) or "").strip():
                meta["descripcion"] = str(meta[alt]).strip()
                break
    if not str(meta.get("nombre") or "").strip():
        meta["nombre"] = sid
    if not str(meta.get("version") or "").strip():
        meta["version"] = "1.0"
    if not str(meta.get("descripcion") or "").strip():
        meta["descripcion"] = "capacidad del Engine: {0}".format(sid)
    return meta


def _extraer_metas(mod: Any) -> List[Dict[str, Any]]:
    """
    Acepta SKILL / CAPACIDAD (dict) o SKILLS / CAPACIDADES (list).
    Devuelve TODOS los skills validos del modulo.
    """
    out: List[Dict[str, Any]] = []
    vistos = set()
    for attr in ("SKILL", "CAPACIDAD", "SKILLS", "CAPACIDADES"):
        raw = getattr(mod, attr, None)
        candidatos: List[Dict[str, Any]] = []
        if isinstance(raw, dict):
            candidatos = [raw]
        elif isinstance(raw, list):
            candidatos = [x for x in raw if isinstance(x, dict)]
        for meta in candidatos:
            norm = _normalizar_meta(meta)
            if norm is None:
                continue
            sid = str(norm["id"]).strip().lower()
            if sid in vistos:
                continue
            vistos.add(sid)
            out.append(norm)
    return out


def _cargar_modulos_ce() -> List[Any]:
    """Carga todos los *.py del directorio (salvo _*) una vez por barrido."""
    mods: List[Any] = []
    if not _CAP.is_dir():
        return mods
    for f in sorted(_CAP.glob("*.py")):
        if f.name.startswith("_"):
            continue
        clave = "ce_skill_{0}".format(f.stem)
        spec = importlib.util.spec_from_file_location(clave, str(f))
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            continue
        mods.append(mod)
    return mods


def _cargar_skills() -> Dict[str, Dict[str, Any]]:
    hallado: Dict[str, Dict[str, Any]] = {}
    if not _CAP.is_dir():
        return hallado

    for f in sorted(_CAP.glob("*.py")):
        if f.name.startswith("_"):
            continue
        clave = "ce_skill_{0}".format(f.stem)
        spec = importlib.util.spec_from_file_location(clave, str(f))
        if spec is None or spec.loader is None:
            hallado[f.stem] = {"archivo": f.name, "error": "spec_invalido"}
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            hallado[f.stem] = {
                "archivo": f.name,
                "error": "{0}: {1}".format(type(e).__name__, e),
            }
            continue

        metas = _extraer_metas(mod)
        if not metas:
            # Archivo sin SKILL puede ser solo puente/definicion; no es error duro
            hallado[f.stem] = {
                "archivo": f.name,
                "error": "sin SKILL/CAPACIDAD con id",
            }
            continue

        for meta in metas:
            sid = str(meta["id"]).strip().lower()
            hallado[sid] = {
                "archivo": f.name,
                "id": sid,
                "nombre": meta.get("nombre"),
                "version": str(meta.get("version") or "1.0"),
                "descripcion": str(meta.get("descripcion") or ""),
                "oficio": meta.get("oficio"),
                "material": meta.get("material"),
                "requiere_catalogo": meta.get("requiere_catalogo"),
                "salida_esperada": meta.get("salida_esperada"),
                "entrada": meta.get("entrada"),
                "requiere_roles": meta.get("requiere_roles"),
                "raw": meta,
            }
    return hallado


def _validar_skills(hallado: Dict[str, Dict[str, Any]]) -> List[str]:
    errores: List[str] = []
    por_id: Dict[str, List[str]] = {}
    for sid, meta in sorted(hallado.items()):
        if meta.get("error"):
            if "sin SKILL" not in str(meta.get("error")):
                errores.append("{0}: {1}".format(sid, meta["error"]))
            continue
        for k in ("id", "nombre", "version", "descripcion"):
            if not str(meta.get(k) or "").strip():
                errores.append("skill '{0}': falta '{1}'".format(sid, k))
        por_id.setdefault(sid, []).append(meta.get("archivo") or sid)
    for sid, archivos in por_id.items():
        if len(archivos) > 1:
            errores.append("id '{0}' repetido en {1}".format(sid, archivos))
    return errores


def skills() -> List[Dict[str, Any]]:
    hallado = _cargar_skills()
    out: List[Dict[str, Any]] = []
    for sid, meta in sorted(hallado.items()):
        if meta.get("error"):
            continue
        out.append({
            "id": meta.get("id"),
            "nombre": meta.get("nombre"),
            "version": meta.get("version"),
            "descripcion": meta.get("descripcion"),
            "archivo": meta.get("archivo"),
            "oficio": meta.get("oficio"),
            "material": meta.get("material"),
            "salida_esperada": meta.get("salida_esperada"),
            "entrada": meta.get("entrada"),
            "requiere_roles": meta.get("requiere_roles"),
            "raw": meta.get("raw"),
        })
    return out


def ids() -> List[str]:
    return [s["id"] for s in skills() if s.get("id")]


def por_id(skill_id: str) -> Optional[Dict[str, Any]]:
    if not skill_id:
        return None
    clave = str(skill_id).strip().lower()
    for s in skills():
        if s.get("id") == clave:
            return s
    return None


def listar_archivos() -> List[str]:
    if not _CAP.is_dir():
        return []
    return [
        p.name for p in sorted(_CAP.glob("*.py"))
        if not p.name.startswith("_")
    ]


def puente_deposito() -> Dict[str, Any]:
    """
    Contrato de extension: bornes que Engine debe depositar al cerrar el ciclo.
    Se lee de cualquier *.py del directorio que exporte PUENTE_DEPOSITO
    o puente_deposito().
    """
    for mod in _cargar_modulos_ce():
        fn = getattr(mod, "puente_deposito", None)
        if callable(fn):
            try:
                out = fn()
                if isinstance(out, dict) and out:
                    return dict(out)
            except Exception:
                pass
        raw = getattr(mod, "PUENTE_DEPOSITO", None)
        if isinstance(raw, dict) and raw:
            return dict(raw)
    return {}


def definicion_sujeto() -> Dict[str, Any]:
    """
    Semantica fija para Angie:
    sujeto = hablante 'Nombre: mensaje', NO sujeto gramatical.
    """
    for mod in _cargar_modulos_ce():
        fn = getattr(mod, "definicion_sujeto", None)
        if callable(fn):
            try:
                out = fn()
                if isinstance(out, dict) and out:
                    return dict(out)
            except Exception:
                pass
        raw = getattr(mod, "DEFINICION_SUJETO", None)
        if isinstance(raw, dict) and raw:
            return dict(raw)
    return {
        "id": "ce_definicion_sujeto",
        "termino": "sujeto",
        "significa": (
            "Hablante etiquetado en el material con la forma "
            "'Nombre: mensaje'. No es sujeto gramatical."
        ),
        "bornes": ["sujetos", "n_sujetos"],
    }


def bornes_deposito_por_skill(skill_id: str) -> List[str]:
    for mod in _cargar_modulos_ce():
        fn = getattr(mod, "bornes_deposito_por_skill", None)
        if callable(fn):
            try:
                out = fn(skill_id)
                if isinstance(out, list):
                    return list(out)
            except Exception:
                pass
    puente = puente_deposito()
    key = str(skill_id or "").strip().lower()
    for item in puente.get("skills_con_deposito") or []:
        if str(item.get("skill_id") or "").strip().lower() == key:
            return list(item.get("bornes") or [])
    return []


def barrer() -> Dict[str, Any]:
    hallado = _cargar_skills()
    errores = _validar_skills(hallado)
    lista_ids = [sid for sid, m in sorted(hallado.items()) if not m.get("error")]
    archivos = listar_archivos()
    notas: List[str] = []
    if not _CAP.is_dir():
        notas.append("directorio CE no existe")
    elif not lista_ids:
        notas.append(
            "ningun skill valido; archivos: {0}".format(archivos or "(ninguno)")
        )
        for sid, m in hallado.items():
            if m.get("error"):
                notas.append("  {0}: {1}".format(sid, m["error"]))

    puente = puente_deposito()
    def_suj = definicion_sujeto()

    return {
        "contenedor": "capacidades_engine",
        "rol": "CE",
        "coherente": not errores,
        "errores": errores,
        "choques": [],
        "ids": lista_ids,
        "n": len(lista_ids),
        "archivos": archivos,
        "notas": notas,
        "ruta_capacidades": str(_CAP),
        "puente_deposito_presente": bool(puente),
        "definicion_sujeto_presente": bool(def_suj),
        "nota": (
            "CE es extension del Engine. Todo skill y bloque de contrato "
            "del directorio esta a disposicion del orquestador. "
            "Sujeto = hablante Nombre: (no gramatica). "
            "Este init no calcula ni deposita."
        ),
    }


def verificar() -> Dict[str, Any]:
    return barrer()


def inventario(peticion: Any = None) -> Dict[str, Any]:
    b = barrer()
    return {
        "contenedor": "capacidades_engine",
        "rol": "CE",
        "version": "1.1",
        "ids": b.get("ids"),
        "n": b.get("n"),
        "archivos": b.get("archivos"),
        "coherente": b.get("coherente"),
        "skills": skills(),
        "puente_deposito": puente_deposito(),
        "definicion_sujeto": definicion_sujeto(),
        "notas": b.get("notas"),
        "funcion": (
            "Cuerpo de capacidades del Engine (extension). "
            "Cada archivo .py con SKILL/SKILLS es un mandato legible. "
            "PUENTE_DEPOSITO y DEFINICION_SUJETO orientan el deposito "
            "de bornes (sujetos = hablantes Nombre:). "
            "Engine los usa a voluntad. CE no calcula ni deposita."
        ),
    }


def verificar_salida(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    return "coherente" in salida or "ids" in salida


CONTENEDOR = {
    "nombre": "capacidades_engine",
    "rol": "CE",
    "version": "1.1",
    "requiere": [],
    "descripcion": (
        "Capacidades del propio Engine (extension, no modulo ajeno). "
        "El INIT es el contrato exclusivo de Engine. "
        "Todo archivo .py del directorio se lee automaticamente: "
        "SKILL/SKILLS, PUENTE_DEPOSITO, DEFINICION_SUJETO. "
        "Sujeto = hablante 'Nombre: mensaje', no sujeto gramatical. "
        "CE no calcula, no deposita, no restringe el uso. "
        "Requisito: 'CE' en ROLES de core/engine.py."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "skills": skills,
        "ids": ids,
        "por_id": por_id,
        "listar_archivos": listar_archivos,
        "puente_deposito": puente_deposito,
        "definicion_sujeto": definicion_sujeto,
        "bornes_deposito_por_skill": bornes_deposito_por_skill,
    },
}


__all__ = [
    "CONTENEDOR",
    "barrer",
    "verificar",
    "inventario",
    "skills",
    "ids",
    "por_id",
    "listar_archivos",
    "puente_deposito",
    "definicion_sujeto",
    "bornes_deposito_por_skill",
    "verificar_salida",
]
