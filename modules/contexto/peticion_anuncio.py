"""
modules/contexto/peticion_anuncio.py
====================================
Regla interna CX — petición de anuncio / cadena auditable.

Anclas: PA-D1, PA-A1, PA-A2, PA-T1, PA-C2,
        CX-A1, Def-5.3.1, citacion_MC

No calcula Tru.
No genera la cadena (eso es CIT).
Solo clasifica si la petición micro exige anuncio y de qué tipo.
La entrada de "cítame / dame el porqué" vive en el O/petición;
CIT responde según PA-A2.
"""

from __future__ import annotations

from typing import Any, Dict, List

REGLA = {
    "id": "CX-R-PETICION-ANUNCIO",
    "nombre": "peticion_anuncio",
    "version": "1.0",
    "descripcion": (
        "Detecta y normaliza la solicitud de cadena auditable en la entrada "
        "de contexto (pedir_anuncio / tipos_peticion / modo). "
        "No calcula Tru ni emite citas; clasifica el marco para Engine/CIT."
    ),
    "anclas": [
        "PA-D1", "PA-A1", "PA-A2", "PA-T1", "PA-C2",
        "CX-A1", "Def-5.3.1",
    ],
}

# Alineado a correlacion_mecanica/citacion_MC.tipos_peticion
TIPOS_PETICION = (
    "por_que_valor",
    "dame_O",
    "dame_evidencia",
    "dame_normas",
    "dame_limites",
    "dame_cadena_completa",
)

# Claves de petición que activan anuncio (deterministas)
_CLAVES_ACTIVACION = (
    "pedir_anuncio",
    "pedir_cita",
    "anuncio",
    "citar",
    "cadena_auditable",
    "dame_por_que",
)


def validar() -> Dict[str, Any]:
    return {
        "ok": True,
        "regla": REGLA["id"],
        "tipos_peticion": list(TIPOS_PETICION),
        "claves_activacion": list(_CLAVES_ACTIVACION),
        "oficio": "clasificar petición de anuncio; no calcular Tru",
    }


def _truthy(v: Any) -> bool:
    if v is True:
        return True
    if v is False or v is None:
        return False
    if isinstance(v, (int, float)):
        return v != 0
    s = str(v).strip().lower()
    return s in ("1", "true", "si", "sí", "yes", "on", "citar", "anuncio")


def _normalizar_tipos(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        partes = [p.strip() for p in raw.replace(";", ",").split(",")]
        return [p for p in partes if p in TIPOS_PETICION]
    if isinstance(raw, (list, tuple, set)):
        return [str(x).strip() for x in raw if str(x).strip() in TIPOS_PETICION]
    return []


def clasificar(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clasifica flags de petición de anuncio en la entrada.

    Entrada típica (opcionales):
      pedir_anuncio | pedir_cita | anuncio | citar | cadena_auditable
      tipos_peticion | tipo_peticion  (str | list)
      modo_entrada (si es auditoria puede implicar cadena)

    Salida:
      pedir_anuncio, tipos_peticion, mensajes, ids, permite_k_sugerido (None)
    """
    peticion = peticion or {}
    mensajes: List[str] = []
    ids = ["PA-A1", "PA-C2"]

    activado = False
    for k in _CLAVES_ACTIVACION:
        if k in peticion and _truthy(peticion.get(k)):
            activado = True
            break

    tipos = _normalizar_tipos(
        peticion.get("tipos_peticion") or peticion.get("tipo_peticion")
    )

    # modo auditoria sin tipos → cadena completa por defecto de forma
    modo = (
        peticion.get("modo_entrada") or peticion.get("modo") or ""
    )
    modo = str(modo).strip().lower()
    if modo == "auditoria" and not activado and not tipos:
        # no fuerza anuncio solo por modo; solo si el caller lo pide
        pass

    if tipos and not activado:
        activado = True
        mensajes.append(
            "tipos_peticion presentes → pedir_anuncio=True"
        )

    if activado and not tipos:
        tipos = ["dame_cadena_completa"]
        mensajes.append(
            "pedir_anuncio sin tipos → default dame_cadena_completa"
        )

    if activado:
        mensajes.append(
            "petición de anuncio clasificada; CIT empaqueta, CX no calcula Tru"
        )
        ids.extend(["PA-A2", "PA-T1"])
    else:
        mensajes.append("sin petición de anuncio en esta entrada")

    invalidos = []
    raw = peticion.get("tipos_peticion") or peticion.get("tipo_peticion")
    if isinstance(raw, str) and raw.strip():
        for p in raw.replace(";", ",").split(","):
            p = p.strip()
            if p and p not in TIPOS_PETICION:
                invalidos.append(p)
    elif isinstance(raw, (list, tuple)):
        for x in raw:
            s = str(x).strip()
            if s and s not in TIPOS_PETICION:
                invalidos.append(s)
    if invalidos:
        mensajes.append(
            "tipos_peticion no admitidos ignorados: {0}".format(invalidos)
        )

    return {
        "ok": True,
        "pedir_anuncio": activado,
        "tipos_peticion": tipos,
        "tipos_invalidos": invalidos,
        "mensajes": mensajes,
        "ids": ids,
        # no sugiere permite_k: eso sigue siendo oficio de O estable
        "permite_k_sugerido": None,
        "oficio": "clasificacion_peticion_anuncio",
    }
