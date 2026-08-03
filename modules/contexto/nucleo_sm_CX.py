# -*- coding: utf-8 -*-
"""
modules/contexto/nucleo_sm_CX.py
=============================
Regla interna CX — contexto del núcleo SM
(mapa de legibilidad, memoria operativa, precisión del mecanismo).

FUNCIÓN (única)
  Clasificar cuándo la entrada opera en el dominio del núcleo semántico-
  operativo formalizado en SM_MAPA, SM_MEMORIA y SM_PRECISION:
    - legibilidad / celdas [w]_Π / invarianza de significado
    - lucha de correlaciones / ancla de error
    - traza τ / memoria operativa M / reapertura solo bajo Clash
    - precisión del mecanismo μ / frontera del diseñador ∂D
    - subordinación de la probabilidad al mapa

  No calcula Tru_Ri ni Tru_total.
  No asigna C, L, K numéricos.
  No deposita τ (eso es CH + Engine).
  No ejecuta Res (eso es CA/FO bajo MC).
  Solo arma el marco O y señala las anclas SM relevantes.

Anclas:
  SM-D9..SM-D19, SM-A11..SM-A19, SM-T12..SM-T23,
  SM-C11..SM-C22, CX-A1, CX-A14, Def-5.3.1, TA4, T14.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

REGLA = {
    "id": "CX-R-NUCLEO-SM",
    "nombre": "nucleo_sm",
    "version": "1.0",
    "descripcion": (
        "Clasifica el contexto del núcleo SM: mapa de legibilidad, "
        "memoria operativa (traza τ), precisión del mecanismo y "
        "frontera del diseñador. Activa ids_cx/SM cuando la entrada "
        "pide evaluar significado, correlaciones, error sin ancla, "
        "re-confirmación o límite de anclas suministradas. "
        "No calcula Tru. No asigna K numérico."
    ),
    "anclas_cx": [
        "CX-A1",
        "CX-A14",
        "Def-5.3.1",
        "SM-D9",
        "SM-D11",
        "SM-D14",
        "SM-D16",
        "SM-D18",
        "SM-A11",
        "SM-A12",
        "SM-A14",
        "SM-A17",
        "SM-T12",
        "SM-T14",
        "SM-T16",
        "SM-T20",
        "SM-T23",
    ],
}

# Señales de dominio SM (deterministas, sin NLP opaco)
_SENALES_MAPA = (
    "mapa de legibilidad",
    "celda de significado",
    "celdas invariantes",
    "invarianza de significado",
    "particion de contrastes",
    "partición de contrastes",
    "sin celda",
    "celda flotante",
    "legibilidad",
    "entendimiento operativo",
    "ancla de error",
    "predicado de error",
    "lucha de correlaciones",
    "argmax tru_ri",
    "correlaciones candidatas",
)

_SENALES_MEMORIA = (
    "memoria operativa",
    "traza de resolucion",
    "traza de resolución",
    "re-confirmacion",
    "reconfirmacion",
    "ciclo de re-confirmacion",
    "reapertura legítima",
    "reapertura legitima",
    "clash con anclas",
    "depositar traza",
    "correccion acumulativa",
    "corrección acumulativa",
    "ya resuelto",
    "configuracion resuelta",
    "configuración resuelta",
)

_SENALES_PRECISION = (
    "precision del mecanismo",
    "precisión del mecanismo",
    "mecanismo causal preciso",
    "prec(μ)",
    "prec(mu)",
    "anclas suministradas",
    "frontera del diseñador",
    "frontera del disenador",
    "parcial_d",
    "∂d",
    "origen de la distorsion",
    "origen de la distorsión",
    "subordinacion de la probabilidad",
    "subordinación de la probabilidad",
    "probabilidad no genera invariante",
)

_SENALES_GENERAL = (
    "nucleo sm",
    "núcleo sm",
    "sm_mapa",
    "sm_memoria",
    "sm_precision",
    "sm-mapa",
    "sm-memoria",
    "sm-precision",
    "sin contacto con r",
    "maquina sin r",
    "máquina sin r",
)

_ENUNCIADO_CANONICO = (
    "Núcleo SM: mapa de legibilidad (Π, celdas), lucha de correlaciones "
    "(argmax Tru_Ri), memoria operativa (traza τ, evación de ciclo), "
    "precisión del mecanismo (Prec(μ)) y frontera del diseñador (∂D). "
    "Evaluación bajo anclas SM_MAPA + SM_MEMORIA + SM_PRECISION."
)

_O_ID_CANONICO = "O_nucleo_SM"


def _texto_entrada(peticion: Dict[str, Any]) -> str:
    partes: List[str] = []
    for k in (
        "contexto",
        "O_context",
        "Octx",
        "enunciado_O",
        "enunciado",
        "texto",
        "casilla_contexto",
        "descripcion",
        "objetivo",
        "tarea",
        "dominio",
    ):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            partes.append(str(v).strip())
    modo = peticion.get("modo_entrada") or peticion.get("modo")
    if modo:
        partes.append(str(modo).strip())
    return " ".join(partes).lower()


def _capa_detectada(texto: str) -> List[str]:
    """Devuelve capas SM activas según señales en el texto."""
    capas: List[str] = []
    if any(s in texto for s in _SENALES_MAPA):
        capas.append("mapa")
    if any(s in texto for s in _SENALES_MEMORIA):
        capas.append("memoria")
    if any(s in texto for s in _SENALES_PRECISION):
        capas.append("precision")
    if any(s in texto for s in _SENALES_GENERAL):
        if "mapa" not in capas:
            capas.append("mapa")
        if "memoria" not in capas:
            capas.append("memoria")
        if "precision" not in capas:
            capas.append("precision")
    return capas


def _es_pedido_nucleo(peticion: Dict[str, Any], texto: str) -> bool:
    if peticion.get("nucleo_sm") is True:
        return True
    if peticion.get("dominio_sm") is True:
        return True
    if str(peticion.get("objeto_auditoria", "")).strip().lower() in (
        "sm",
        "nucleo_sm",
        "mapa",
        "memoria_operativa",
        "precision",
        "significado",
    ):
        return True
    if _capa_detectada(texto):
        return True
    return False


def _enunciado_usable(peticion: Dict[str, Any], texto: str, capas: List[str]) -> Optional[str]:
    for k in ("enunciado_O", "enunciado", "contexto", "O_context", "Octx", "casilla_contexto"):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            s = str(v).strip()
            if s.lower() in ("undefined", "indefinido", "none", "null", "∅"):
                continue
            return s
    if capas:
        return _ENUNCIADO_CANONICO
    return None


def validar() -> Dict[str, Any]:
    return {
        "ok": True,
        "regla": REGLA["id"],
        "capas": ["mapa", "memoria", "precision"],
        "produce": ["estado", "evento", "capas_sm", "ids_cx", "permite_k_sugerido"],
        "prohibe": [
            "calcular Tru_Ri o Tru_total",
            "asignar C/L/K numérico",
            "depositar traza (oficio CH/Engine)",
            "ejecutar Res (oficio CA/FO bajo MC)",
        ],
        "principio": (
            "CX clasifica el marco del núcleo SM; "
            "MC ordena la cadena sm_nucleo_MC; "
            "CA/FO calculan; CH deposita τ; CIT anuncia."
        ),
    }


def clasificar(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clasifica si aplica el contexto del núcleo SM.

    Entrada típica:
      { "contexto": "evaluar si hay celda flotante y re-confirmación" }
      { "nucleo_sm": true, "casilla_contexto": "..." }
      { "objeto_auditoria": "memoria_operativa" }

    Salida: solo claves de dominio CX (whitelist del init).
    """
    peticion = dict(peticion or {})
    texto = _texto_entrada(peticion)
    capas = _capa_detectada(texto)
    aplica = _es_pedido_nucleo(peticion, texto)

    if not aplica:
        return {
            "ok": True,
            "oficio": "nucleo_sm",
            "aplica": False,
            "ids_cx": list(REGLA["anclas_cx"]),
        }

    enunciado = _enunciado_usable(peticion, texto, capas)
    o_id = peticion.get("O_id") or peticion.get("o_id")
    if o_id is not None and str(o_id).strip():
        o_id = str(o_id).strip()
    else:
        o_id = _O_ID_CANONICO if enunciado else None

    ids: List[str] = ["CX-R-NUCLEO-SM", "CX-A1", "CX-A14"]
    mensajes: List[str] = []

    if "mapa" in capas:
        ids.extend(["SM-D9", "SM-A11", "SM-A12", "SM-T12", "SM-T14", "SM-C11"])
        mensajes.append(
            "capa mapa activa: legibilidad, celdas invariantes, "
            "ancla de error, lucha de correlaciones (SM_MAPA)"
        )
    if "memoria" in capas:
        ids.extend(["SM-D14", "SM-A14", "SM-T16", "SM-T17", "SM-T18", "SM-C15"])
        mensajes.append(
            "capa memoria activa: traza τ, evación de ciclo, "
            "reapertura solo bajo Clash (SM_MEMORIA)"
        )
    if "precision" in capas:
        ids.extend(["SM-D16", "SM-D18", "SM-A17", "SM-T20", "SM-T23", "SM-C22"])
        mensajes.append(
            "capa precisión activa: Prec(μ), A_sum, ∂D, "
            "origen de la distorsión (SM_PRECISION)"
        )
    if not capas:
        # Pedido explícito sin señales finas → núcleo completo
        capas = ["mapa", "memoria", "precision"]
        ids.extend([
            "SM-D9", "SM-D14", "SM-D16", "SM-T12", "SM-T16", "SM-T20", "SM-T23",
        ])
        mensajes.append(
            "núcleo SM completo (mapa + memoria + precisión) por bandera explícita"
        )

    if not enunciado or not o_id:
        mensajes.append(
            "núcleo SM solicitado sin O_id/enunciado_O usable: "
            "estado indefinido; K no reclamable (Def-5.3.1, CX-A14)"
        )
        return {
            "ok": True,
            "oficio": "nucleo_sm",
            "aplica": True,
            "estado": "indefinido",
            "evento": "indefinido",
            "incompleto": True,
            "O_id": o_id,
            "enunciado_O": enunciado,
            "modo_entrada": peticion.get("modo_entrada") or "auditoria",
            "capas_sm": capas,
            "permite_k_sugerido": False,
            "ids_cx": sorted(set(ids + ["Def-5.3.1", "CX-C4", "SM-A11"])),
            "mensajes": mensajes,
        }

    mensajes.append(
        "contexto del núcleo SM fijado. "
        "CX clasifica; sm_nucleo_MC ordena la cadena; "
        "CA/FO calculan bajo anclas; CH deposita τ; CIT anuncia. "
        "No se calcula Tru en esta regla."
    )

    return {
        "ok": True,
        "oficio": "nucleo_sm",
        "aplica": True,
        "estado": "estable",
        "evento": "mismo_O",
        "incompleto": False,
        "O_id": o_id,
        "enunciado_O": enunciado,
        "modo_entrada": peticion.get("modo_entrada") or "auditoria",
        "escala": "macro",
        "capas_sm": capas,
        "permite_k_sugerido": True,
        "ids_cx": sorted(set(ids)),
        "mensajes": mensajes,
        "nota_mecanica": (
            "Cadena recomendada: sm_nucleo_MC "
            "(Precision_Mecanismo → Particion_Pi → Maximizacion_Tru_Ri → "
            "Deposito_en_M → Evaluacion_Clash → Marca_Localidad_parcial_D)."
        ),
    }


__all__ = ["REGLA", "clasificar", "validar"]
