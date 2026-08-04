# -*- coding: utf-8 -*-
"""
modules/contexto/entendimiento_fractal.py
========================================

REGLA CX — Clasificación de contexto bajo el cuerpo EF
(Entendimiento y Fractalidad operativa).

QUÉ ES
------
Clasifica cuándo la entrada activa el *marco de estabilización operativa*
formalizado en AX (EF-D*, EF-A*, EF-T*):

  - expansión de material correlacional bajo O (bucle B(D,O))
  - saturación / ruptura cuando Corr deja de crecer
  - multi-O (micro / global) sin promedio silencioso
  - interrupción jurisdiccional cuando el objeto salta al propio sistema
  - distinción ruptura ≠ indefinido de dominio

No es AX (AX declara y vigila el grafo EF).
No es CA / FO (no calcula Tru, C, L, K ni E numérico).
No es Engine (no orquesta el bucle).
No es CIT (no emite la cadena).
No es conteos (no produce m,k,p,r,c,f).

CONTEXTO DE DOMINIO
-------------------
O típico (cuando la entrada lo fija):
  "Estabilización operativa bajo O: expansión de correlaciones,
   saturación de material, multi-marco y límites de jurisdicción."

Si la entrada invoca entendimiento/fractalidad pero no fija
enunciado/O usable → estado indefinido (Def-5.3.1 / IND-*);
CX no fabrica dominio (EF-C1, IND-C3).

ANCLAS
------
  EF-D1…D8, EF-A1…A8, EF-T1…T7, EF-C1…C7
  CX-A1, CX-A10, CX-A14, CX-A23, CX-A25, CX-T6, CX-T15
  Def-5.3.1, IND-D1, IND-A1, IND-A5, SM-D10, SM-T13, TA4
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# REGLA (campos obligatorios del centinela CX)
# ---------------------------------------------------------------------------
REGLA: Dict[str, Any] = {
    "id": "CX-R-EF-ESTABILIZACION",
    "nombre": "entendimiento_fractal",
    "version": "1.1",
    "descripcion": (
        "Clasifica el marco de estabilización operativa (cuerpo EF): "
        "expansión de correlaciones bajo O, saturación/ruptura de material, "
        "coexistencia micro/global sin colapso, e interrupción jurisdiccional "
        "cuando el objeto de evaluación salta al propio sistema. "
        "No calcula Tru. No asigna K numérico. No implementa el bucle E."
    ),
    "anclas_cx": [
        "EF-D1",
        "EF-D3",
        "EF-D5",
        "EF-D8",
        "EF-A1",
        "EF-A3",
        "EF-A4",
        "EF-A5",
        "EF-A8",
        "EF-T1",
        "EF-T2",
        "EF-T7",
        "EF-C1",
        "EF-C5",
        "EF-C7",
        "CX-A1",
        "CX-A10",
        "CX-A14",
        "CX-A23",
        "CX-A25",
        "CX-T6",
        "CX-T15",
        "Def-5.3.1",
        "IND-D1",
        "IND-A1",
        "IND-A5",
        "SM-D10",
        "SM-T13",
        "TA4",
    ],
}

# Señales de que el *dominio* es estabilización operativa / bucle de correlación
# (no basta una palabra suelta: se exige marco de proceso bajo O).
_SENALES_EF: tuple = (
    # ES
    "entendimiento operativo",
    "estabilizacion operativa",
    "estabilización operativa",
    "bucle de correlacion",
    "bucle de correlación",
    "bucle de entendimiento",
    "expansion de correlaciones",
    "expansión de correlaciones",
    "saturacion de material",
    "saturación de material",
    "ruptura de bucle",
    "corr(d)",
    "ciclo de correlaciones",
    "fractal semantico",
    "fractal semántico",
    "recursion estructural",
    "recursión estructural",
    "recursion cognitiva",
    "recursión cognitiva",
    "contexto micro",
    "contexto global",
    "o_micro",
    "o_global",
    "multi-contexto",
    "multi contexto",
    "interrupcion jurisdiccional",
    "interrupción jurisdiccional",
    "salto al self",
    "salto al sistema",
    "material correlacional",
    # EN (señales cortas de dominio, no de relleno)
    "operational understanding",
    "correlation loop",
    "saturation of material",
    "jurisdictional interrupt",
)

# Señales de que el objeto evaluable es el *propio sistema* (activa EF-A5 en clasificación)
_SENALES_SALTO_SELF: tuple = (
    "que piensas",
    "qué piensas",
    "que piensas tu",
    "qué piensas tú",
    "como funciona el motor",
    "cómo funciona el motor",
    "estado interno del sistema",
    "auditar el propio sistema",
    "auto referencia del motor",
    "autorreferencia del motor",
    "self del sistema",
    "what do you think",
    "how does the engine work",
)

_TIPOS_EF: List[str] = [
    "dame_O",
    "dame_limites",
    "dame_normas",
    "por_que_valor",
    "dame_cadena_completa",
]

_ENUNCIADO_CANONICO = (
    "Estabilización operativa bajo O (cuerpo EF): expansión de material "
    "correlacional, saturación/ruptura cuando Corr deja de crecer, "
    "coexistencia de O micro y O global sin promedio silencioso, e "
    "interrupción jurisdiccional si el objeto salta al propio sistema; "
    "CX clasifica el marco, no calcula Tru ni E."
)

_O_ID_CANONICO = "O_ef_estabilizacion_VPSI"


def _texto_entrada(peticion: Dict[str, Any]) -> str:
    partes: List[str] = []
    for k in (
        "contexto",
        "O_context",
        "Octx",
        "enunciado_O",
        "enunciado",
        "texto",
        "descripcion",
        "objetivo",
        "tarea",
        "mensaje",
    ):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            partes.append(str(v).strip())
    modo = peticion.get("modo_entrada") or peticion.get("modo")
    if modo:
        partes.append(str(modo).strip())
    # flags explícitos
    for flag in ("ef_activo", "estabilizacion_operativa", "bucle_correlacion"):
        if peticion.get(flag) is True:
            partes.append(flag.replace("_", " "))
    return " ".join(partes).lower()


def _es_pedido_ef(peticion: Dict[str, Any], texto: str) -> bool:
    """
    True si el marco de la petición activa el dominio EF.
    No fuerza EF por modo genérico: hace falta señal de estabilización
    operativa / correlación bajo O / multi-marco / salto de jurisdicción.
    """
    if peticion.get("ef_activo") is True:
        return True
    if peticion.get("estabilizacion_operativa") is True:
        return True
    if peticion.get("bucle_correlacion") is True:
        return True
    if str(peticion.get("cuerpo_ax", "")).strip().lower() in (
        "ef",
        "entendimiento_fractal",
        "entendimiento-fractal",
    ):
        return True
    if any(s in texto for s in _SENALES_EF):
        return True
    if any(s in texto for s in _SENALES_SALTO_SELF):
        # salto al self es señal EF-A5 solo si hay marco de evaluación
        return True
    return False


def _hay_salto_self(texto: str, peticion: Dict[str, Any]) -> bool:
    if peticion.get("salto_self") is True:
        return True
    if peticion.get("jurisdiccion_sistema") is True:
        return True
    return any(s in texto for s in _SENALES_SALTO_SELF)


def _enunciado_usable(peticion: Dict[str, Any], texto: str) -> Optional[str]:
    for k in ("enunciado_O", "enunciado", "contexto", "O_context", "Octx"):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            s = str(v).strip()
            if s.lower() in ("undefined", "indefinido", "none", "null", "∅"):
                continue
            return s
    if _es_pedido_ef(peticion, texto):
        return _ENUNCIADO_CANONICO
    return None


def validar() -> Dict[str, Any]:
    """Auto-chequeo de la regla (sin petición)."""
    return {
        "ok": True,
        "regla": REGLA["id"],
        "nombre": REGLA["nombre"],
        "version": REGLA["version"],
        "exige_para_estable": ["O_id", "enunciado_O"],
        "estados": ["estable", "cambio", "indefinido"],
        "oficios_prohibidos": [
            "calcular Tru",
            "asignar K numérico",
            "implementar bucle E",
            "depositar traza τ",
        ],
        "anclas": list(REGLA["anclas_cx"]),
    }


def clasificar(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clasifica si aplica el contexto de estabilización operativa (EF).

    Salida solo con claves de dominio CX (whitelist del init).
    No emite Tru_Ri / Tru_total / C / L / K numérico.
    No implementa expansión de Corr ni umbrales numéricos.
    """
    peticion = dict(peticion or {})
    texto = _texto_entrada(peticion)
    aplica = _es_pedido_ef(peticion, texto)

    if not aplica:
        return {
            "ok": True,
            "oficio": "entendimiento_fractal",
            "aplica": False,
            "ids_cx": list(REGLA["anclas_cx"]),
        }

    enunciado = _enunciado_usable(peticion, texto)
    o_id = peticion.get("O_id") or peticion.get("o_id")
    if o_id is not None and str(o_id).strip():
        o_id = str(o_id).strip()
    else:
        o_id = _O_ID_CANONICO if enunciado else None

    salto = _hay_salto_self(texto, peticion)

    # --- sin dominio usable → indefinido (no fabricar) ---
    if not enunciado or not o_id:
        return {
            "ok": True,
            "oficio": "entendimiento_fractal",
            "aplica": True,
            "estado": "indefinido",
            "evento": "indefinido",
            "incompleto": True,
            "O_id": o_id,
            "enunciado_O": enunciado,
            "pedir_anuncio": True,
            "tipos_peticion": list(_TIPOS_EF),
            "permite_k_sugerido": False,
            "ids_cx": [
                "CX-R-EF-ESTABILIZACION",
                "EF-C1",
                "Def-5.3.1",
                "IND-D1",
                "IND-A5",
                "CX-A14",
                "CX-A10",
                "EF-L3",
            ],
            "mensajes": [
                "Marco EF solicitado sin O_id/enunciado_O usable: "
                "estado indefinido; K no reclamable; CX no fabrica dominio "
                "(EF-C1, Def-5.3.1). Ruptura de bucle no aplica sin O."
            ],
        }

    # --- salto jurisdiccional al sistema (EF-A5) ---
    if salto:
        return {
            "ok": True,
            "oficio": "entendimiento_fractal",
            "aplica": True,
            "estado": "cambio",
            "evento": "cambio",
            "incompleto": False,
            "O_id": o_id,
            "enunciado_O": enunciado,
            "escala": "meta",
            "pedir_anuncio": True,
            "tipos_peticion": [
                "dame_O",
                "dame_limites",
                "dame_normas",
                "por_que_valor",
                "dame_cadena_completa",
            ],
            "permite_k_sugerido": False,
            "ids_cx": [
                "CX-R-EF-ESTABILIZACION",
                "EF-A5",
                "EF-C3",
                "CX-A23",
                "SF-T1",
                "RE-A8",
                "TA4",
                "PA-A1",
            ],
            "mensajes": [
                "Clasificación EF-A5: el objeto evaluable desplaza hacia el propio "
                "sistema → bucle externo Suspendido (cambio de jurisdicción). "
                "CX no trata el estado interno como X de R. "
                "Engine/SF atienden el marco; CIT anuncia límites si se pide cadena."
            ],
        }

    # --- dominio EF estable ---
    # Evento: si la petición declara multi-O o cambio explícito, se respeta.
    estado_decl = peticion.get("estado")
    evento_decl = peticion.get("evento")

    if estado_decl == "cambio" or evento_decl in ("cambio", "expansion"):
        estado = "cambio"
        evento = evento_decl if evento_decl in ("cambio", "expansion") else "cambio"
        ids = [
            "CX-R-EF-ESTABILIZACION",
            "EF-A4",
            "EF-T2",
            "EF-T5",
            "CX-A8",
            "CX-A25",
            "CX-T6",
            "CX-T15",
        ]
        mensajes = [
            "Marco EF con evento de cambio/expansión declarado. "
            "O_global, si existe, no borra micro (EF-A4 / CX-A25). "
            "Sin regla de agregación declarada no hay Tru único del discurso (EF-T2)."
        ]
        permite = False  # cambio: K del tramo previo no se arrastra en silencio
    else:
        estado = "estable"
        evento = "mismo_O" if evento_decl not in ("mismo_O", "expansion") else evento_decl
        ids = [
            "CX-R-EF-ESTABILIZACION",
            "EF-A1",
            "EF-A3",
            "EF-T1",
            "EF-A8",
            "EF-C5",
            "EF-C7",
            "CX-A1",
            "CX-A14",
            "SM-D10",
            "Def-5.3.1",
        ]
        mensajes = [
            "Contexto de estabilización operativa (EF) fijado bajo O usable. "
            "CX clasifica el marco: expansión/saturación de Corr es oficio de "
            "Engine bajo AX; conteos/CA no implementan E (EF-C5). "
            "Sin constante 25/27 (EF-C7). No se calcula Tru en esta regla."
        ]
        permite = True

    return {
        "ok": True,
        "oficio": "entendimiento_fractal",
        "aplica": True,
        "estado": estado,
        "evento": evento,
        "incompleto": False,
        "O_id": o_id,
        "enunciado_O": enunciado,
        "modo_entrada": peticion.get("modo_entrada") or peticion.get("modo") or "texto_libre",
        "escala": peticion.get("escala") or "macro",
        "pedir_anuncio": bool(peticion.get("pedir_anuncio"))
        or bool(peticion.get("tipos_peticion")),
        "tipos_peticion": list(_TIPOS_EF)
        if peticion.get("pedir_anuncio") or peticion.get("tipos_peticion")
        else [],
        "permite_k_sugerido": permite,
        "ids_cx": ids,
        "mensajes": mensajes,
    }


__all__ = ["REGLA", "clasificar", "validar"]
