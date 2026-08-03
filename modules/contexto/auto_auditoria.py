"""
modules/contexto/auto_auditoria.py
==================================

REGLA CX — Contexto de auto-auditoría del sistema (VPSI-TRUTH).

QUÉ ES
------
Clasifica cuándo la entrada pide que el *propio sistema* se mire a sí mismo:
  - módulos y contratos CONTENEDOR
  - grafo axiomático (AX / cuerpos)
  - coherencia MC
  - constantes CT
  - resultados de ciclo / evidencia
  - cadena anunciable (para CIT, no aquí)

No es CIT (CIT anuncia después).
No es AX (AX juzga el grafo).
No es Engine (Engine orquesta).
No calcula Tru ni asigna K numérico.

CONTEXTO DE DOMINIO
-------------------
O típico (cuando la entrada lo fija):
  "Auto-auditoría interna de VPSI-TRUTH: módulos, contratos,
   coherencia axiomática y mecánica, evidencia de ciclo."

modo_entrada canónico: "auditoria" (ya admitido en MODOS_ENTRADA del init).

Si la entrada pide auto-auditoría pero no fija enunciado/O usable
→ estado indefinido (Def-5.3.1 / IND-*); no se fabrica dominio.

TIPOS DE PETICIÓN (solo los del contrato CX)
--------------------------------------------
  dame_cadena_completa  — anuncio completo del ciclo / módulos tocados
  dame_evidencia        — qué se midió / qué se cargó
  dame_normas           — ids / contratos que gobiernan
  dame_limites          — qué CX/CIT/Engine no pueden hacer
  dame_O                — enunciado del dominio de auditoría
  por_que_valor         — por qué un estado (p.ej. UNDEFINED) salió así

Anclas: CX-OP-*, PA-*, IND-*, Def-5.3.1, CX-A14.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# REGLA (campos obligatorios del centinela)
# ---------------------------------------------------------------------------
REGLA: Dict[str, Any] = {
    "id": "CX-R-AUTO-AUDITORIA",
    "nombre": "auto_auditoria_sistema",
    "version": "1.0",
    "descripcion": (
        "Clasifica el contexto de auto-auditoría interna del sistema: "
        "módulos, contratos CONTENEDOR, coherencia AX/MC, constantes CT "
        "y evidencia de ciclo. Activa pedir_anuncio y tipos de cadena "
        "cuando la entrada pide que el sistema se anuncie a sí mismo. "
        "No calcula Tru. No asigna K numérico. No emite la cadena (eso es CIT)."
    ),
    "anclas_cx": [
        "CX-OP-1",
        "CX-OP-2",
        "CX-OP-4",
        "CX-A14",
        "CX-C4",
        "Def-5.3.1",
        "IND-D1",
        "IND-A1",
        "IND-A5",
        "IND-T1",
        "PA-A1",
        "PA-A2",
        "PA-T1",
        "PA-C2",
    ],
}

# Señales de que el *dominio* es auto-auditoría del sistema (no de un texto externo).
_SENALES_AUTO: tuple = (
    "auto auditoria",
    "auto-auditoria",
    "autoauditoria",
    "auto-auditoría",
    "auto auditoría",
    "auditoria interna",
    "auditoría interna",
    "auditar el sistema",
    "auditar sistema",
    "auditar modulos",
    "auditar módulos",
    "auditar el repo",
    "auditar repositorio",
    "auditoria del sistema",
    "auditoría del sistema",
    "auditoria del repo",
    "coherencia del sistema",
    "coherencia del repo",
    "estado de los modulos",
    "estado de los módulos",
    "contratos del sistema",
    "verificar contratos",
    "censo de modulos",
    "censo de módulos",
    "inventario del sistema",
    "self audit",
    "system audit",
    "audit modules",
    "audit the system",
)

# Tipos admitidos por el INIT de CX (no inventar otros: el centinela los rechaza).
_TIPOS_AUTO: List[str] = [
    "dame_cadena_completa",
    "dame_evidencia",
    "dame_normas",
    "dame_limites",
    "dame_O",
    "por_que_valor",
]

_ENUNCIADO_CANONICO = (
    "Auto-auditoría interna de VPSI-TRUTH: módulos, contratos CONTENEDOR, "
    "coherencia axiomática (AX), mecánica (MC), constantes (CT) y evidencia "
    "de ciclo; el sistema anuncia su propio estado sin calcular Tru en CX."
)

_O_ID_CANONICO = "O_auto_auditoria_VPSI"


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
    ):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            partes.append(str(v).strip())
    modo = peticion.get("modo_entrada") or peticion.get("modo")
    if modo:
        partes.append(str(modo).strip())
    return " ".join(partes).lower()


def _es_pedido_auto(peticion: Dict[str, Any], texto: str) -> bool:
    """
    True si el marco de la petición es auto-auditoría del sistema.
    No basta con modo=auditoria de un texto externo: hace falta señal
    de que el *objeto* a auditar es el propio repo/módulos/contratos.
    """
    modo = str(
        peticion.get("modo_entrada") or peticion.get("modo") or ""
    ).strip().lower()

    if modo == "auditoria":
        # modo auditoría + (señal de sistema O flags explícitos)
        if any(s in texto for s in _SENALES_AUTO):
            return True
        if peticion.get("auto_auditoria") is True:
            return True
        if peticion.get("auditar_sistema") is True:
            return True
        if str(peticion.get("objeto_auditoria", "")).strip().lower() in (
            "sistema",
            "repo",
            "repositorio",
            "modulos",
            "módulos",
            "self",
            "vpsi",
            "vpsi-truth",
        ):
            return True
        # modo auditoria sin ancla de *qué* se audita → no forzar este dominio
        return False

    if peticion.get("auto_auditoria") is True:
        return True
    if peticion.get("auditar_sistema") is True:
        return True
    if any(s in texto for s in _SENALES_AUTO):
        return True
    return False


def _enunciado_usable(peticion: Dict[str, Any], texto: str) -> Optional[str]:
    """
    Enunciado O de la auto-auditoría.
    Si la petición ya trae enunciado claro, se respeta.
    Si solo hay señales de auto-auditoría sin prosa, se ofrece el canónico
    (dominio del sistema, no de un texto externo vacío).
    """
    for k in ("enunciado_O", "enunciado", "contexto", "O_context", "Octx"):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            s = str(v).strip()
            # Rótulos de estado no son dominio
            if s.lower() in ("undefined", "indefinido", "none", "null", "∅"):
                continue
            return s
    # Pedido explícito de auto-auditoría sin prosa: dominio canónico del sistema
    if _es_pedido_auto(peticion, texto):
        return _ENUNCIADO_CANONICO
    return None


def clasificar(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clasifica si aplica el contexto de auto-auditoría del sistema.

    Salida solo con claves de dominio CX (whitelist del init).
    No emite Tru_Ri / Tru_total / C / L / K numérico.
    """
    peticion = dict(peticion or {})
    texto = _texto_entrada(peticion)
    aplica = _es_pedido_auto(peticion, texto)

    if not aplica:
        # No impone estado: otras reglas pueden clasificar.
        return {
            "ok": True,
            "oficio": "auto_auditoria",
            "aplica": False,
            "ids_cx": list(REGLA["anclas_cx"]),
        }

    enunciado = _enunciado_usable(peticion, texto)
    o_id = peticion.get("O_id") or peticion.get("o_id")
    if o_id is not None and str(o_id).strip():
        o_id = str(o_id).strip()
    else:
        o_id = _O_ID_CANONICO if enunciado else None

    if not enunciado or not o_id:
        # Auto-auditoría pedida pero sin dominio usable → indefinido (no fabricar).
        return {
            "ok": True,
            "oficio": "auto_auditoria",
            "aplica": True,
            "estado": "indefinido",
            "evento": "indefinido",
            "incompleto": True,
            "O_id": o_id,
            "enunciado_O": enunciado,
            "modo_entrada": "auditoria",
            "pedir_anuncio": True,
            "tipos_peticion": list(_TIPOS_AUTO),
            "permite_k_sugerido": False,
            "ids_cx": [
                "CX-R-AUTO-AUDITORIA",
                "Def-5.3.1",
                "IND-D1",
                "IND-A5",
                "CX-A14",
                "CX-C4",
                "PA-A1",
            ],
            "mensajes": [
                "Auto-auditoría solicitada sin O_id/enunciado_O usable: "
                "estado indefinido; K no reclamable; CX no fabrica dominio."
            ],
        }

    # Dominio de auto-auditoría fijado → estable; anuncio pedido por naturaleza del oficio.
    tipos = list(_TIPOS_AUTO)
    # Si la petición ya traía tipos válidos, el init fusiona; aquí sugerimos el juego completo.
    return {
        "ok": True,
        "oficio": "auto_auditoria",
        "aplica": True,
        "estado": "estable",
        "evento": "mismo_O",
        "incompleto": False,
        "O_id": o_id,
        "enunciado_O": enunciado,
        "modo_entrada": "auditoria",
        "escala": "macro",
        "pedir_anuncio": True,
        "tipos_peticion": tipos,
        "permite_k_sugerido": True,
        "ids_cx": [
            "CX-R-AUTO-AUDITORIA",
            "CX-OP-1",
            "CX-OP-4",
            "PA-A1",
            "PA-A2",
            "PA-T1",
            "IND-A1",
            "IND-T1",
        ],
        "mensajes": [
            "Contexto de auto-auditoría del sistema fijado. "
            "CX clasifica; Engine orquesta; AX/MC ya cargados en repositorio; "
            "CIT anuncia la cadena si el ciclo lo cierra. "
            "No se calcula Tru en esta regla."
        ],
    }


__all__ = ["REGLA", "clasificar"]
