"""
modules/taxonomia/__init__.py
=============================

Rol TX — Taxonomía metodológica.

No interpreta.
No calcula Tru_total.
Define reglas deterministas de estructura para medir cada táctica (T1–T15).

El Engine aplica la taxonomía sobre un O_context cuando el contrato
y la correlación mecánica lo autorizan.

Los archivos dentro de taxonomia/ declaran:
  - TACTICA  (dict)  → una táctica
  - TACTICAS (list)  → varias tácticas (p. ej. manipulation_TX.py)

El init audita cada declaración. Si no pasa el filtro, no sale.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from core.diagnostico import DiagnosticoGlobal
except Exception:
    class DiagnosticoGlobal:
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass

_DIR = Path(__file__).parent
CLAVES_TACTICA = ("id", "nombre", "degrada", "enunciado")


# ===============================================================
# VALIDACIÓN DE UNA TÁCTICA (filtro interno)
# ===============================================================
def _validar_tactica(meta: Dict[str, Any], origen: str) -> List[str]:
    """
    Audita una declaración de táctica.
    Si hay errores, esa táctica no sale.
    """
    errores: List[str] = []
    if not isinstance(meta, dict):
        return [f"{origen}: TACTICA no es dict"]

    for clave in CLAVES_TACTICA:
        val = meta.get(clave)
        if val is None or val == "" or val == []:
            errores.append(f"{origen}: falta o vacío '{clave}'")

    tid = meta.get("id")
    if tid is not None and not isinstance(tid, str):
        errores.append(f"{origen}: 'id' debe ser str")

    nombre = meta.get("nombre")
    if nombre is not None and not isinstance(nombre, str):
        errores.append(f"{origen}: 'nombre' debe ser str")

    degrada = meta.get("degrada")
    if degrada is not None:
        if not isinstance(degrada, (list, tuple)):
            errores.append(f"{origen}: 'degrada' debe ser lista")
        else:
            permitidos = {"C", "L", "K", "A"}
            for d in degrada:
                if d not in permitidos:
                    errores.append(f"{origen}: factor '{d}' no permitido en degrada")

    estructura = meta.get("estructura")
    if estructura is not None and not isinstance(estructura, dict):
        errores.append(f"{origen}: 'estructura' debe ser dict")

    return errores


# ===============================================================
# DESCUBRIMIENTO + AUDITORÍA
# ===============================================================
def _descubrir() -> Dict[str, Dict[str, Any]]:
    """
    Recorre la carpeta.
    Acepta TACTICAS (lista) o TACTICA (dict).
    Cada táctica se audita; si no pasa, se registra con error y no participa
    en aplicar() ni en el inventario limpio.
    """
    registro: Dict[str, Dict[str, Any]] = {}

    for f in sorted(_DIR.glob("*.py")):
        if f.name.startswith("_") or f.name == "__init__.py":
            continue

        clave = f"taxonomia_{f.stem}"
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue

        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            registro[f.name] = {
                "archivo": f.name,
                "error": f"{type(e).__name__}: {e}",
            }
            continue

        # --- Lista de tácticas ---
        lista = getattr(mod, "TACTICAS", None)
        if isinstance(lista, list):
            for i, item in enumerate(lista):
                origen = f"{f.name}[{i}]"
                errs = _validar_tactica(item if isinstance(item, dict) else {}, origen)
                if errs:
                    registro[f"{f.name}#{i}"] = {
                        "archivo": f.name,
                        "error": "; ".join(errs),
                    }
                    continue
                tid = str(item.get("id"))
                registro[f"{f.name}#{tid}"] = {
                    "archivo": f.name,
                    "id": tid,
                    "nombre": item.get("nombre"),
                    "degrada": list(item.get("degrada", [])),
                    "enunciado": item.get("enunciado"),
                    "estructura": item.get("estructura") or {},
                }
            continue

        # --- Una sola táctica ---
        meta = getattr(mod, "TACTICA", None)
        if meta is None:
            registro[f.name] = {
                "archivo": f.name,
                "error": "sin TACTICA ni TACTICAS",
            }
            continue

        errs = _validar_tactica(meta if isinstance(meta, dict) else {}, f.name)
        if errs:
            registro[f.name] = {
                "archivo": f.name,
                "error": "; ".join(errs),
            }
            continue

        registro[f.name] = {
            "archivo": f.name,
            "id": str(meta.get("id")),
            "nombre": meta.get("nombre"),
            "degrada": list(meta.get("degrada", [])),
            "enunciado": meta.get("enunciado"),
            "estructura": meta.get("estructura") or {},
        }

    return registro


def _detectar_choques(hallado: Dict[str, Dict[str, Any]]) -> List[str]:
    choques: List[str] = []
    por_id: Dict[str, List[str]] = {}
    por_nombre: Dict[str, List[str]] = {}

    for clave, meta in hallado.items():
        if "error" in meta:
            continue
        tid = str(meta.get("id") or "").strip()
        nom = str(meta.get("nombre") or "").strip()
        if tid:
            por_id.setdefault(tid, []).append(clave)
        if nom:
            por_nombre.setdefault(nom, []).append(clave)

    for tid, archivos in por_id.items():
        if len(archivos) > 1:
            choques.append(f"id de táctica '{tid}' repetido en {archivos}")
    for nom, archivos in por_nombre.items():
        if len(archivos) > 1:
            choques.append(f"nombre de táctica '{nom}' repetido en {archivos}")
    return choques


def _solo_validas(hallado: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Solo tácticas que pasaron el filtro (sin error, con id)."""
    return {
        k: v
        for k, v in hallado.items()
        if "error" not in v and v.get("id")
    }


# ===============================================================
# FILTRO / CENTINELA DEL MÓDULO
# ===============================================================
def barrer() -> Dict[str, Any]:
    """
    Coherencia interna de la taxonomía.
    - Audita cada táctica de cada archivo.
    - Si no pasa, no sale.
    - Carpeta vacía = vacío legítimo.
    """
    hallado = _descubrir()
    errores: List[str] = []
    notas: List[str] = []

    for clave, meta in sorted(hallado.items()):
        if "error" in meta:
            errores.append(f"{clave}: {meta['error']}")

    choques = _detectar_choques(hallado)
    validas = _solo_validas(hallado)

    if not hallado:
        notas.append("sin archivos de táctica (vacío legítimo)")
    elif not validas and hallado:
        notas.append("hay archivos pero ninguna táctica pasó el filtro")

    if choques or errores:
        DiagnosticoGlobal.recibir_reporte(
            modulo="taxonomia",
            errores=(
                [{"tipo": "choque", "detalle": c} for c in choques]
                + [{"tipo": "error", "detalle": e} for e in errores]
            ),
        )

    return {
        "contenedor": "taxonomia",
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "tacticas": sorted(str(m.get("id")) for m in validas.values()),
        "total_declaradas": len(hallado),
        "total_validas": len(validas),
        "notas": notas,
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return bool(salida.get("coherente", False))


# ===============================================================
# APLICACIÓN ESTRUCTURAL (solo tácticas que pasaron el filtro)
# ===============================================================
def aplicar(
    descripcion: Dict[str, Any],
    contexto: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Aplica la taxonomía por estructura, no por opinión.
    Solo usa tácticas que pasaron la auditoría del init.
    No emite Tru_total.
    """
    hallado = _descubrir()
    validas = _solo_validas(hallado)
    contexto = contexto or {}
    o_ctx = contexto.get("O_context") or contexto.get("contexto")

    coincidencias: List[Dict[str, Any]] = []
    for clave, meta in sorted(validas.items()):
        estructura = meta.get("estructura") or {}
        ok = True
        evidencia: List[str] = []

        if isinstance(estructura, dict) and estructura:
            for k, esperado in estructura.items():
                actual = descripcion.get(k)
                if actual is None or actual != esperado:
                    ok = False
                    break
                evidencia.append(f"{k}={actual}")
        else:
            # Sin criterios estructurales → no se aplica
            ok = False

        if ok:
            coincidencias.append({
                "id": meta.get("id"),
                "nombre": meta.get("nombre"),
                "degrada": meta.get("degrada", []),
                "enunciado": meta.get("enunciado"),
                "evidencia": evidencia,
                "archivo": meta.get("archivo"),
            })

    return {
        "contenedor": "taxonomia",
        "O_context": o_ctx,
        "aplicadas": coincidencias,
        "total": len(coincidencias),
        "tacticas_disponibles": len(validas),
        "nota": (
            "Medición estructural. Sin interpretación. "
            "Solo tácticas que pasaron el filtro del init. "
            "Tru_total lo calculan CA/FO bajo el mismo O_context."
        ),
    }


def inventario() -> Dict[str, Any]:
    hallado = _descubrir()
    validas = _solo_validas(hallado)
    return {
        "contenedor": "taxonomia",
        "version": "1.0",
        "rol": "TX",
        "tacticas": {
            str(m.get("id")): {
                "nombre": m.get("nombre"),
                "degrada": m.get("degrada"),
            }
            for m in validas.values()
        },
        "total_validas": len(validas),
        "funcion": (
            "Taxonomía metodológica determinista. "
            "Mide tácticas por estructura, no por interpretación. "
            "El Engine la aplica cuando el contrato y MC lo autorizan. "
            "Si una táctica no pasa el filtro del init, no sale."
        ),
    }


def axiomas() -> List[Dict[str, Any]]:
    return [
        {
            "id": "TX-1",
            "tipo": "axioma",
            "sujeto": "taxonomia",
            "relacion": "mide_por",
            "objeto": "estructura",
            "polaridad": True,
            "enunciado": (
                "Cada táctica se reconoce por criterios estructurales "
                "explícitos, no por interpretación libre."
            ),
            "depende_de": [],
            "gobierna": ["taxonomia"],
        },
        {
            "id": "TX-2",
            "tipo": "axioma",
            "sujeto": "taxonomia",
            "relacion": "no_calcula",
            "objeto": "Tru_total",
            "polaridad": True,
            "enunciado": (
                "TX no calcula Tru_total. Degrada factores (C, L, K, A) "
                "cuando la estructura de la táctica coincide; "
                "CA/FO calculan bajo el O_context."
            ),
            "depende_de": [],
            "gobierna": ["taxonomia"],
        },
        {
            "id": "TX-3",
            "tipo": "axioma",
            "sujeto": "init_taxonomia",
            "relacion": "filtra",
            "objeto": "tacticas_internas",
            "polaridad": True,
            "enunciado": (
                "Toda táctica declarada en archivos internos se audita. "
                "Si no pasa el filtro, no sale ni se aplica."
            ),
            "depende_de": [],
            "gobierna": ["taxonomia"],
        },
    ]


# ===============================================================
# CONTENEDOR (contrato literal para el Engine — al final)
# ===============================================================
CONTENEDOR = {
    "nombre": "taxonomia",
    "rol": "TX",
    "version": "1.0",
    "requiere": ["CX", "MC"],
    "descripcion": (
        "Taxonomía metodológica. Rol TX. "
        "Reglas deterministas de estructura para medir tácticas (T1–T15). "
        "Sin interpretación. No calcula Tru_total. "
        "El init audita cada táctica interna; si no pasa, no sale. "
        "El Engine aplica esta taxonomía sobre un O_context "
        "cuando el contrato y la correlación mecánica lo autorizan."
    ),
    "capacidades": {
        "verificar": barrer,
        "aplicar": aplicar,
        "inventario": inventario,
        "axiomas": axiomas,
    },
}

__all__ = [
    "CONTENEDOR",
    "barrer",
    "aplicar",
    "inventario",
    "verificar_salida",
    "axiomas",
]
