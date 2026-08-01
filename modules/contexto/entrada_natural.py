"""
modules/contexto/entrada_natural.py
===================================
Regla interna CX — entrada natural de contexto (casilla de interfaz).

FUNCIÓN (única)
  Velar y armar el registro operativo a partir de cualquier forma
  en que un humano (o un sistema) declare el contexto en prosa,
  lista, conversación o meta-auditoría.

  Contexto no calcula Tru_Ri ni Tru_total.
  Contexto no puntúa C, L, K.
  Contexto no etiqueta tácticas TX.
  Contexto es la llave maestra que arma el marco O para que
  el resto del mecanismo pueda operar sin ambigüedad.

Anclas: CX-A1, CX-A8, CX-A10, CX-A14, CX-A15, CX-C4, CX-C10,
        CX-T4, CX-T6, CX-T13, Def-5.3.1, Lema de Indeterminación (protocolo).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple

REGLA = {
    "id": "CX-R-ENTRADA-NATURAL",
    "nombre": "entrada_natural",
    "version": "1.0",
    "descripcion": (
        "Convierte cualquier declaración natural de contexto (casilla de UI, "
        "lista de criterios, prosa, conversación) en registro operativo formal. "
        "No exige vocabulario técnico al usuario. No calcula Tru."
    ),
    "anclas_cx": [
        "CX-A1", "CX-A8", "CX-A10", "CX-A14", "CX-A15",
        "CX-C4", "CX-C10", "CX-T4", "CX-T6", "CX-T13", "Def-5.3.1",
    ],
}


# ---------------------------------------------------------------------------
# Formas admisibles de material en la casilla
# ---------------------------------------------------------------------------
FORMAS = (
    "vacio",              # casilla vacía → indefinido
    "prosa",              # un párrafo / frase libre
    "lista_criterios",    # 1. ... 2. ... 3. ... bajo un mismo O
    "etiqueta_o",         # "O_Context: ..." / "contexto: ..."
    "meta_indefinido",    # declara explícitamente que el contexto es indefinido
    "cambio_declarado",   # declara cambio de marco / nuevo tema
    "multi_bloque",       # varios bloques separados (posible multi-O)
)

MODOS_INFERIDOS = (
    "auditoria",
    "afirmacion",
    "conversacion",
    "teorema",
    "texto_libre",
    "repositorio",
)


def validar() -> Dict[str, Any]:
    return {
        "ok": True,
        "regla": REGLA["id"],
        "formas": list(FORMAS),
        "modos_inferidos": list(MODOS_INFERIDOS),
        "principio": (
            "La casilla humana entrega significado; el módulo arma el registro. "
            "Sin texto usable → indefinido (K no reclamable). "
            "Con texto usable → O estable interno sin pedir O_id al usuario."
        ),
    }


# ---------------------------------------------------------------------------
# Utilidades de detección (deterministas, sin NLP opaco)
# ---------------------------------------------------------------------------
_RE_LISTA = re.compile(
    r"(?m)^\s*(?:(?:\d+[\.\)]\s+)|(?:[\-\*•]\s+))(.+)$"
)
_RE_ETIQUETA = re.compile(
    r"(?i)^\s*(?:o[_\s\-]?context|octx|contexto|context)\s*[:=]\s*(.*)$",
    re.DOTALL,
)
_RE_INDEFINIDO = re.compile(
    r"(?i)\b(contexto\s+indefinido|sin\s+contexto|no\s+hay\s+contexto|"
    r"undefined\s+context|context\s+undefined|o\s+indefinido)\b"
)
_RE_CAMBIO = re.compile(
    r"(?i)\b(cambiar\s+de\s+(?:tema|contexto|marco)|nuevo\s+contexto|"
    r"otro\s+marco|cerrar\s+contexto|change\s+context)\b"
)
_RE_AUDITORIA = re.compile(
    r"(?i)\b(evaluar|evaluaci[oó]n|auditar|auditor[ií]a|verificar|"
    r"si\s+(?:es\s+)?verdad|razonable|contradec|coheren)\b"
)
_RE_CONVERSACION = re.compile(
    r"(?i)\b(dijo|dijo\s+que|conversaci[oó]n|di[aá]logo|turno|"
    r"carlos|mar[ií]a|pedro|[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s*:)\b"
)


def _texto_fuente(peticion: Dict[str, Any]) -> str:
    """Prioridad: campos de UI naturales, luego formales."""
    for k in (
        "casilla_contexto",
        "texto_contexto",
        "contexto",
        "O_context",
        "enunciado_O",
        "enunciado",
        "input",
        "texto",
    ):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _oid_interno(texto: str, sesion_id: Optional[str] = None) -> str:
    base = (sesion_id or "") + "||" + texto.strip()
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]
    return f"O_auto_{digest}"


def _extraer_criterios(texto: str) -> List[str]:
    items = [m.group(1).strip() for m in _RE_LISTA.finditer(texto)]
    return [x for x in items if x]


def _detectar_forma(texto: str) -> str:
    if not texto.strip():
        return "vacio"
    if _RE_INDEFINIDO.search(texto) and len(texto.strip()) < 120:
        # Declaración corta de indefinición (no un ensayo que mencione la palabra)
        return "meta_indefinido"
    if _RE_CAMBIO.search(texto):
        return "cambio_declarado"
    if _RE_ETIQUETA.match(texto):
        return "etiqueta_o"
    criterios = _extraer_criterios(texto)
    if len(criterios) >= 2:
        return "lista_criterios"
    # Bloques separados por líneas en blanco dobles → multi posible
    bloques = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
    if len(bloques) >= 2 and all(len(b) > 15 for b in bloques):
        return "multi_bloque"
    return "prosa"


def _inferir_modo(texto: str, forma: str, peticion: Dict[str, Any]) -> str:
    if peticion.get("modo_entrada") in MODOS_INFERIDOS:
        return str(peticion["modo_entrada"])
    if forma == "meta_indefinido":
        return "auditoria"
    if forma == "lista_criterios" or _RE_AUDITORIA.search(texto):
        return "auditoria"
    if _RE_CONVERSACION.search(texto) or peticion.get("grano") == "conversacion":
        return "conversacion"
    if peticion.get("grano") == "teorema" or "teorema" in texto.lower():
        return "teorema"
    if forma in ("prosa", "etiqueta_o") and len(texto) < 80:
        return "afirmacion"
    return "texto_libre"


def _normalizar_etiqueta(texto: str) -> str:
    m = _RE_ETIQUETA.match(texto)
    if m:
        resto = m.group(1).strip()
        return resto if resto else texto
    return texto


def _enunciado_canonico(texto: str, forma: str, criterios: List[str]) -> str:
    if forma == "etiqueta_o":
        return _normalizar_etiqueta(texto)
    if forma == "lista_criterios" and criterios:
        return " | ".join(f"({i+1}) {c}" for i, c in enumerate(criterios))
    return texto.strip()


# ---------------------------------------------------------------------------
# Clasificación principal
# ---------------------------------------------------------------------------
def clasificar(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Armado del registro desde entrada natural.

    Entrada típica de UI (cualquiera basta):
      { "casilla_contexto": "1. evaluar si... 2. saber si Carlos..." }
      { "contexto": "evaluar la actitud según las leyes" }
      { "texto_contexto": "", "sesion_id": "abc" }

    Campos técnicos opcionales (si el Engine los aporta):
      sesion_id, O_id, estado, evento, modo_entrada, grano, ligaduras

    Salida: estado, evento, O_id, enunciado_O, criterios, forma,
            modo_entrada, permite_k_sugerido, mensajes, ids_cx
    """
    peticion = dict(peticion or {})
    texto = _texto_fuente(peticion)
    forma = _detectar_forma(texto)
    criterios = _extraer_criterios(texto) if forma in (
        "lista_criterios", "etiqueta_o", "prosa", "multi_bloque"
    ) else []
    # Si vino etiqueta + lista dentro
    if forma == "etiqueta_o":
        cuerpo = _normalizar_etiqueta(texto)
        criterios = _extraer_criterios(cuerpo) or criterios

    modo = _inferir_modo(texto, forma, peticion)
    sesion_id = peticion.get("sesion_id") or peticion.get("session_id")
    mensajes: List[str] = []
    ids_cx: List[str] = ["CX-A14", "CX-C10"]

    # --- Caso vacío ---
    if forma == "vacio":
        mensajes.append(
            "casilla vacía → registro indefinido; K no reclamable "
            "(CX-A10, CX-C4, Def-5.3.1)"
        )
        return {
            "ok": True,
            "forma": forma,
            "estado": "indefinido",
            "evento": "indefinido",
            "O_id": None,
            "enunciado_O": None,
            "criterios": [],
            "modo_entrada": modo if modo != "texto_libre" else "texto_libre",
            "grano": peticion.get("grano") or "ninguno",
            "permite_k_sugerido": False,
            "sesion_id": sesion_id,
            "mensajes": mensajes,
            "ids_cx": ids_cx + ["CX-A10", "CX-C4", "CX-T13", "Def-5.3.1"],
            "armado": "ninguno",
        }

    # --- Meta: declara contexto indefinido ---
    if forma == "meta_indefinido":
        enunciado = texto.strip()
        oid = peticion.get("O_id") or _oid_interno(
            "META_INDEFINIDO::" + enunciado, sesion_id
        )
        mensajes.append(
            "declaración meta de contexto indefinido: el tramo auditado "
            "no aporta K; esta D se evalúa bajo O meta de auditoría, "
            "no se rellena el agujero (CX-A10, CX-T13)"
        )
        return {
            "ok": True,
            "forma": forma,
            "estado": "indefinido",
            "evento": "indefinido",
            "O_id": oid,
            "enunciado_O": enunciado,
            "criterios": [],
            "modo_entrada": "auditoria",
            "grano": "meta",
            "permite_k_sugerido": False,
            "meta": True,
            "sesion_id": sesion_id,
            "mensajes": mensajes,
            "ids_cx": ids_cx + ["CX-A10", "CX-T13", "Def-5.3.1"],
            "armado": "meta_indefinido",
        }

    # --- Cambio declarado de marco ---
    if forma == "cambio_declarado":
        enunciado = _enunciado_canonico(texto, forma, criterios)
        oid = peticion.get("O_id") or _oid_interno(enunciado, sesion_id)
        mensajes.append(
            "cambio de contexto declarado: cerrar evaluación anterior y "
            "abrir proceso nuevo con este O (CX-A8, CX-T6; protocolo Octx)"
        )
        return {
            "ok": True,
            "forma": forma,
            "estado": "cambio",
            "evento": "cambio",
            "O_id": oid,
            "enunciado_O": enunciado,
            "criterios": criterios,
            "modo_entrada": modo,
            "grano": peticion.get("grano") or "frase",
            "permite_k_sugerido": bool(enunciado),
            "sesion_id": sesion_id,
            "mensajes": mensajes,
            "ids_cx": ids_cx + ["CX-A8", "CX-T6"],
            "armado": "cambio_sesion",
        }

    # --- Multi-bloque: un O por bloque solo si el usuario separó temas;
    #     por defecto un solo O con criterios = bloques (no inventar multi-O) ---
    if forma == "multi_bloque":
        bloques = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
        enunciado = " | ".join(f"({i+1}) {b}" for i, b in enumerate(bloques))
        oid = peticion.get("O_id") or _oid_interno(enunciado, sesion_id)
        mensajes.append(
            "varios bloques en la casilla: se arman como criterios de un "
            "mismo O (no se inventan O distintos sin declaración de cambio)"
        )
        ids_cx = ids_cx + ["CX-A1", "CX-T4"]
        return {
            "ok": True,
            "forma": forma,
            "estado": "estable",
            "evento": "mismo_O",
            "O_id": oid,
            "enunciado_O": enunciado,
            "criterios": bloques,
            "modo_entrada": modo,
            "grano": peticion.get("grano") or "conversacion",
            "permite_k_sugerido": True,
            "sesion_id": sesion_id,
            "mensajes": mensajes,
            "ids_cx": ids_cx,
            "armado": "multi_bloque_un_O",
        }

    # --- Lista de criterios / prosa / etiqueta (caso normal de UI) ---
    enunciado = _enunciado_canonico(texto, forma, criterios)
    if not enunciado.strip():
        mensajes.append("texto tras normalizar quedó vacío → indefinido")
        return {
            "ok": True,
            "forma": forma,
            "estado": "indefinido",
            "evento": "indefinido",
            "O_id": None,
            "enunciado_O": None,
            "criterios": [],
            "modo_entrada": modo,
            "grano": peticion.get("grano") or "ninguno",
            "permite_k_sugerido": False,
            "sesion_id": sesion_id,
            "mensajes": mensajes,
            "ids_cx": ids_cx + ["CX-A10", "CX-C4"],
            "armado": "fallido_vacio",
        }

    oid = peticion.get("O_id") or _oid_interno(enunciado, sesion_id)
    estado_decl = peticion.get("estado")
    if estado_decl in ("cambio", "indefinido"):
        estado = estado_decl
        evento = "cambio" if estado_decl == "cambio" else "indefinido"
        permite = False if estado == "indefinido" else bool(enunciado)
    else:
        estado = "estable"
        evento = "mismo_O"
        permite = True

    if forma == "lista_criterios":
        mensajes.append(
            f"lista de {len(criterios)} criterios bajo un único O de sesión; "
            "el usuario no necesita O_id técnico"
        )
        ids_cx = ids_cx + ["CX-A1", "CX-A14", "CX-T4"]
        grano = peticion.get("grano") or "frase"
    elif forma == "etiqueta_o":
        mensajes.append("etiqueta O_Context/contexto detectada; cuerpo usado como enunciado_O")
        ids_cx = ids_cx + ["CX-A1", "CX-A14"]
        grano = peticion.get("grano") or "frase"
    else:
        mensajes.append(
            "prosa de casilla elevada a enunciado_O estable; "
            "marco listo para CA/FO sin campos técnicos del usuario"
        )
        ids_cx = ids_cx + ["CX-A1", "CX-A14"]
        grano = peticion.get("grano") or ("palabra" if len(enunciado.split()) <= 3 else "frase")

    return {
        "ok": True,
        "forma": forma,
        "estado": estado,
        "evento": evento,
        "O_id": oid,
        "enunciado_O": enunciado,
        "criterios": criterios,
        "modo_entrada": modo,
        "grano": grano,
        "permite_k_sugerido": permite and estado == "estable",
        "sesion_id": sesion_id,
        "mensajes": mensajes,
        "ids_cx": ids_cx,
        "armado": "natural_a_registro",
        # Eco de ejemplo de UI (documentación operativa)
        "nota_interfaz": (
            "La casilla puede contener solo: "
            "'1. evaluar si todo lo que dijo es razonable "
            "2. saber si Carlos dijo la verdad "
            "3. utilizar las leyes para evaluar su actitud'. "
            "Eso basta: un O, tres criterios, modo auditoría inferido."
        ),
    }
