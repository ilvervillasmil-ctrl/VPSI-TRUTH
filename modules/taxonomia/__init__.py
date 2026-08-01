"""
modules/taxonomia/__init__.py
=============================

Rol TX — Taxonomía metodológica.

No interpreta.
No calcula Tru_total.
Define reglas deterministas de estructura para medir cada táctica (T1–T15).

El Engine aplica la taxonomía sobre un O_context cuando el contrato
y la correlación mecánica lo autorizan.
Los archivos dentro de taxonomia/ declaran cada táctica (TACTICA).
El init filtra coherencia interna y expone la capacidad de aplicar.
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
# DESCUBRIMIENTO DE TÁCTICAS
# ===============================================================
def _descubrir() -> Dict[str, Dict[str, Any]]:
    """
    Cada archivo .py (excepto __init__ y _*) puede declarar TACTICA: dict.
    Sin TACTICA → no participa.
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
            registro[f.name] = {"archivo": f.name, "error": f"{type(e).__name__}: {e}"}
            continue

        meta = getattr(mod, "TACTICA", None)
        if not isinstance(meta, dict):
            continue

        registro[f.name] = {
            "archivo": f.name,
            "id": meta.get("id"),
            "nombre": meta.get("nombre"),
            "degrada": list(meta.get("degrada", [])),  # C, L, K, A, ...
            "enunciado": meta.get("enunciado"),
            "estructura": meta.get("estructura"),  # criterios estructurales, no interpretativos
        }
    return registro


def _detectar_choques(hallado: Dict[str, Dict[str, Any]]) -> List[str]:
    choques: List[str] = []
    por_id: Dict[str, List[str]] = {}
    por_nombre: Dict[str, List[str]] = {}

    for archivo, meta in hallado.items():
        if "error" in meta:
            continue
        tid = str(meta.get("id") or "").strip()
        nom = str(meta.get("nombre") or "").strip()
        if tid:
            por_id.setdefault(tid, []).append(archivo)
        if nom:
            por_nombre.setdefault(nom, []).append(archivo)

    for tid, archivos in por_id.items():
        if len(archivos) > 1:
            choques.append(f"id de táctica '{tid}' repetido en {archivos}")
    for nom, archivos in por_nombre.items():
        if len(archivos) > 1:
            choques.append(f"nombre de táctica '{nom}' repetido en {archivos}")
    return choques


# ===============================================================
# FILTRO / CENTINELA
# ===============================================================
def barrer() -> Dict[str, Any]:
    """
    Coherencia interna de la taxonomía.
    Carpeta vacía = vacío legítimo (aún no hay tácticas montadas).
    """
    hallado = _descubrir()
    errores: List[str] = []
    notas: List[str] = []

    for archivo, meta in sorted(hallado.items()):
        if "error" in meta:
            errores.append(f"{archivo}: {meta['error']}")
            continue
        for clave in CLAVES_TACTICA:
            if not meta.get(clave):
                errores.append(f"{archivo}: TACTICA sin '{clave}'")

    choques = _detectar_choques(hallado)
    if not hallado:
        notas.append("sin tácticas internas (vacío legítimo)")

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
        "tacticas": sorted(
            str(m.get("id"))
            for m in hallado.values()
            if m.get("id") and "error" not in m
        ),
        "notas": notas,
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return bool(salida.get("coherente", False))


# ===============================================================
# APLICACIÓN ESTRUCTURAL (sin interpretación)
# ===============================================================
def aplicar(
    descripcion: Dict[str, Any],
    contexto: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Aplica la taxonomía por estructura, no por opinión.

    Entrada esperada (mínima):
      descripcion: hechos estructurales ya medidos o declarados
        (p. ej. polaridades, cambios de marco, rol declarado vs ejecutado)
      contexto: O_context bajo el cual se evalúa (si no hay, K no aplica)

    Salida:
      lista de tácticas cuya estructura coincide con la descripción,
      factores que degradan (C, L, K, A) y evidencia estructural citada.
    No emite Tru_total.
    """
    hallado = _descubrir()
    contexto = contexto or {}
    o_ctx = contexto.get("O_context") or contexto.get("contexto")

    coincidencias: List[Dict[str, Any]] = []
    for archivo, meta in sorted(hallado.items()):
        if "error" in meta or not meta.get("id"):
            continue
        estructura = meta.get("estructura") or {}
        # Criterio determinista: todas las claves de estructura presentes
        # en descripcion con el valor exigido (si se declara).
        ok = True
        evidencia: List[str] = []
        if isinstance(estructura, dict) and estructura:
            for k, esperado in estructura.items():
                actual = descripcion.get(k)
                if actual is None:
                    ok = False
                    break
                if actual != esperado:
                    ok = False
                    break
                evidencia.append(f"{k}={actual}")
        else:
            # Sin estructura formal en el archivo → no se aplica por defecto
            ok = False

        if ok:
            coincidencias.append({
                "id": meta.get("id"),
                "nombre": meta.get("nombre"),
                "degrada": meta.get("degrada", []),
                "enunciado": meta.get("enunciado"),
                "evidencia": evidencia,
                "archivo": archivo,
            })

    return {
        "contenedor": "taxonomia",
        "O_context": o_ctx,
        "aplicadas": coincidencias,
        "total": len(coincidencias),
        "nota": (
            "Medición estructural. Sin interpretación. "
            "Tru_total lo calculan CA/FO bajo el mismo O_context."
        ),
    }


def inventario() -> Dict[str, Any]:
    hallado = _descubrir()
    return {
        "contenedor": "taxonomia",
        "version": "1.0",
        "rol": "TX",
        "tacticas": {
            str(m.get("id")): {
                "nombre": m.get("nombre"),
                "degrada": m.get("degrada"),
            }
            for m in hallado.values()
            if m.get("id") and "error" not in m
        },
        "funcion": (
            "Taxonomía metodológica determinista. "
            "Mide tácticas por estructura, no por interpretación. "
            "El Engine la aplica cuando el contrato y MC lo autorizan."
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
