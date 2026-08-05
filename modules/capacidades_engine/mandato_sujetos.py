# modules/capacidades_engine/ce_mandato_sujetos.py
# -*- coding: utf-8 -*-
"""
Skill CE — extensión ejecutable del Engine.

Mandato de sincronización: Tru total por sujeto S_1…S_N.
Incluye la lógica de recorte para detectar a los hablantes (ej. "Carlos: hola").
"""

import re
from typing import Dict, Any, List

# El motor de recorte ahora vive dentro del propio mandato
_RE_HABLANTE = re.compile(
    r"(?m)^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{0,40})\s*:\s*(.+)$"
)

def extraer_sujetos(peticion: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Inyección de lógica para el Engine: 
    Busca sujetos explícitos o segmenta el texto usando la expresión regular.
    """
    for key in ("sujetos", "recortes", "items", "segmentos"):
        raw = peticion.get(key)
        if isinstance(raw, list) and raw:
            segs: List[Dict[str, Any]] = []
            for i, s in enumerate(raw, start=1):
                if isinstance(s, dict):
                    nombre = str(s.get("nombre") or s.get("id") or f"S{i}")
                    texto = str(s.get("texto") or s.get("mensaje") or s.get("D") or "")
                else:
                    nombre = f"S{i}"
                    texto = str(s)
                if texto.strip():
                    segs.append({
                        "indice": i,
                        "nombre": nombre,
                        "texto": texto,
                    })
            if segs:
                return segs

    # Si no vienen en lista, aplicamos la magia de la expresión regular al texto
    texto_raw = ""
    for k in ("mensaje", "descripcion", "texto", "D", "material"):
        if peticion.get(k) and str(peticion.get(k)).strip():
            texto_raw = str(peticion.get(k))
            break
            
    out: List[Dict[str, Any]] = []
    for m in _RE_HABLANTE.finditer(texto_raw):
        nombre = m.group(1).strip()
        cuerpo = m.group(2).strip()
        if nombre and cuerpo:
            out.append({
                "indice": len(out) + 1,
                "nombre": nombre,
                "texto": cuerpo,
            })
    return out


# El contrato declarativo que lee el Engine
SKILL = {
    "id": "ce_mandato_sujetos",
    "nombre": "Mandato: Tru total por sujeto S_1…S_N",
    "enunciado": (
        "Mandato del Engine a los módulos de oficio: "
        "se pide valuación por sujeto (escala tru_sujeto del catálogo TT). "
        "Engine deposita resultado.sujetos = [{indice, nombre, C, L, K...}]."
    ),
    "version": "1.1",
    "modulos_objetivo": [
        "tru_totales", "contexto", "correlacion_mecanica", "calculator",
        "formulas", "citacion", "cache", "taxonomia", "axiomas"
    ],
    "requiere_roles": ["TT", "CX", "MC", "CA", "FO", "CIT", "CH", "TX", "AX"],
    "entrada": ["categoria_tru=tru_sujeto", "O_id", "enunciado_O", "material_multi_hablante"],
    "salida_esperada": ["sujetos", "n_sujetos", "por_sujeto"],
    "sincroniza_con": ["ce_mandato_escala_tt"],
    "prioridad": 20,
    "notas": "Este mandato exporta la función extraer_sujetos para inyectarla al Engine.",
    "ejecutor": extraer_sujetos  # Pasamos la función directamente al diccionario
}
