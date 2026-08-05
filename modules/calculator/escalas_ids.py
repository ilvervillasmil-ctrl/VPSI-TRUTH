# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/calculator/escalas_ids.py

Mapa de ids de escala para conteos.

NO es un módulo nuevo. NO tiene CONTENEDOR. NO sustituye conteos.py.
Calculator ya tiene su INIT. Conteos ya sabe contar.

Este archivo solo declara:
  cuando pidan este id → el material a contar es este recorte
  (misma lógica de extraer_conteos; cambia el texto de entrada).

Conteos / CA lo consultan si el pedido trae un id de escala.
Si no traen id, conteos sigue igual que siempre.

Alineado a TT (tru_atomo, tru_frase, tru_sujeto, …).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

VERSION = "1.0"

# id → descriptor de recorte (sin calcular C/L/K/Tru)
ESCALAS: Dict[str, Dict[str, Any]] = {
    "tru_atomo": {
        "nombre": "átomo / unidad mínima",
        "material": "una unidad mínima del texto (cláusula / átomo de discurso)",
        "repetir_por": "por_unidad",
        "entrada": ("unidad", "O_context"),
        "notas": "Un ciclo de extraer_conteos por unidad pedida.",
    },
    "tru_frase": {
        "nombre": "frase / afirmación",
        "material": "una frase o afirmación del texto",
        "repetir_por": "por_frase",
        "entrada": ("frase", "O_context"),
        "notas": "Un ciclo de extraer_conteos por frase pedida.",
    },
    "tru_sujeto": {
        "nombre": "sujeto S_1…S_N",
        "material": "texto atribuido a un sujeto S_i (i = 1…N)",
        "repetir_por": "por_sujeto",
        "entrada": ("texto_sujeto", "nombre_sujeto", "indice_sujeto", "O_context"),
        "notas": (
            "Repetir extraer_conteos una vez por sujeto. "
            "Quien prepara el texto de cada S_i es la orquestación; "
            "aquí solo está el id del recorte."
        ),
    },
    "tru_conversacion": {
        "nombre": "conversación completa",
        "material": "texto completo de la conversación / diálogo",
        "repetir_por": "una_vez",
        "entrada": ("texto", "O_context"),
        "notas": "Un ciclo de extraer_conteos sobre el diálogo íntegro.",
    },
    "tru_repositorio": {
        "nombre": "repositorio como objeto",
        "material": "texto / enunciado del repositorio como objeto (auditoría VPSI)",
        "repetir_por": "una_vez",
        "entrada": ("texto", "O_context", "enunciado_O"),
        "notas": "Un ciclo de extraer_conteos sobre el material de auto-auditoría.",
    },
}


def ids() -> List[str]:
    return list(ESCALAS.keys())


def por_id(escala_id: str) -> Optional[Dict[str, Any]]:
    key = str(escala_id or "").strip().lower()
    if key not in ESCALAS:
        return None
    out = dict(ESCALAS[key])
    out["id"] = key
    return out


def tiene(escala_id: str) -> bool:
    return str(escala_id or "").strip().lower() in ESCALAS


__all__ = [
    "ESCALAS",
    "VERSION",
    "ids",
    "por_id",
    "tiene",
]
