"""
modules/diccionario/clasificacion.py
====================================

Esquema de clasificación léxica (desglose de una palabra).

Archivo del módulo diccionario — no es un init ni un subpaquete.
El init de DI descubre fuentes; este archivo fija el formato con el
que se desglosa una entrada para que Engine y todos los módulos
la lean igual.

FUNCIÓN
  Organizar: palabra, definición, significado (+ tipificación opcional).

NO HACE
  - Elegir qué significado aplica según contexto (ciclo CX + correlación).
  - Calcular Tru / C / L / K.
  - Escribir frases ni rellenar el diccionario.

CAMPOS
  obligatorios:  palabra, definicion
  recomendados:  significado
  opcionales:    tipo, idioma, fuente, dominio, notas
  prohibidos:    C, L, K, Tru_*, O_context, permite_k, estado, evento
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

VERSION = "1.0"

CAMPOS_OBLIGATORIOS: Tuple[str, ...] = (
    "palabra",
    "definicion",
)

CAMPOS_RECOMENDADOS: Tuple[str, ...] = (
    "significado",
)

CAMPOS_OPCIONALES: Tuple[str, ...] = (
    "tipo",
    "idioma",
    "fuente",
    "dominio",
    "notas",
)

CAMPOS_PROHIBIDOS: Tuple[str, ...] = (
    "C", "L", "K",
    "Tru_Ri", "Tru_total", "tru_ri", "tru_total",
    "O_context", "o_context", "permite_k",
    "estado", "evento",
)

def plantilla() -> Dict[str, Any]:
    """Forma vacía de desglose. Sin contenido inventado."""
    return {
        "palabra": None,
        "definicion": None,
        "significado": None,
        "tipo": None,
        "idioma": None,
        "fuente": None,
        "dominio": None,
        "notas": None,
    }

def desglosar(entrada: Any, *, palabra: Optional[str] = None) -> Dict[str, Any]:
    """
    Normaliza una entrada de diccionario al esquema de clasificación.
    No elige entre significados contextuales. No calcula Tru.
    """
    out = plantilla()

    if palabra is not None and str(palabra).strip():
        out["palabra"] = str(palabra).strip().lower()

    if entrada is None:
        out["notas"] = "entrada vacía"
        return out

    if isinstance(entrada, str):
        out["definicion"] = entrada.strip() or None
        out["significado"] = out["definicion"]
        return out

    if not isinstance(entrada, dict):
        out["notas"] = "entrada no dict ni str; no desglosable"
        return out

    if out["palabra"] is None:
        for k in ("palabra", "lema", "term", "termino", "término"):
            v = entrada.get(k)
            if v is not None and str(v).strip():
                out["palabra"] = str(v).strip().lower()
                break

    for k in ("definicion", "definición", "def", "definition"):
        v = entrada.get(k)
        if v is not None and str(v).strip():
            out["definicion"] = str(v).strip()
            break

    for k in ("significado", "meaning", "interpretacion", "interpretación"):
        v = entrada.get(k)
        if v is not None and str(v).strip():
            out["significado"] = str(v).strip()
            break
    if out["significado"] is None and out["definicion"] is not None:
        out["significado"] = out["definicion"]

    for k in ("tipo", "idioma", "fuente", "dominio", "notas"):
        v = entrada.get(k)
        if v is not None and str(v).strip():
            out[k] = str(v).strip()

    return out

def validar(desglose: Dict[str, Any]) -> List[str]:
    """Comprueba forma del desglose. Informa; no lanza."""
    errores: List[str] = []
    if not isinstance(desglose, dict):
        return ["desglose debe ser dict"]

    for k in CAMPOS_OBLIGATORIOS:
        v = desglose.get(k)
        if v is None or not str(v).strip():
            errores.append("falta campo obligatorio: {0}".format(k))

    for k in CAMPOS_PROHIBIDOS:
        if k in desglose and desglose[k] is not None:
            errores.append(
                "campo prohibido en clasificación léxica: {0} "
                "(oficio de otro módulo)".format(k)
            )

    return errores

def es_forma_valida(desglose: Dict[str, Any]) -> bool:
    return not validar(desglose)

def inventario() -> Dict[str, Any]:
    return {
        "archivo": "clasificacion.py",
        "version": VERSION,
        "campos_obligatorios": list(CAMPOS_OBLIGATORIOS),
        "campos_recomendados": list(CAMPOS_RECOMENDADOS),
        "campos_opcionales": list(CAMPOS_OPCIONALES),
        "campos_prohibidos": list(CAMPOS_PROHIBIDOS),
        "funcion": (
            "Formato de desglose de una palabra: "
            "palabra, definicion, significado (+ tipificación opcional). "
            "Archivo del módulo DI. No elige significado contextual. No calcula Tru."
        ),
    }
