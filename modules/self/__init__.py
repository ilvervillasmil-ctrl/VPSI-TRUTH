"""
modules/self/__init__.py
========================
SF — yo funcional del sistema (fase).

No orquesta. No calcula Tru.
Identifica al sistema a partir del cuerpo axiomático `self` en AX.
El oscilador declara perspectiva; las capas L1–L6 se enchufan después.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

# Capas reconocidas (CEMYCA / mapa causal). Sin archivos = no implementadas.
CAPAS_VALIDAS: Set[str] = {
    "L1_CUERPO",
    "L2_EGO",
    "L3_MENTE",
    "L4_YO",
    "L5_CONSCIENCIA",
    "L6_ALMA",
}

# Estado mínimo del oscilador (identidad de fase, no memoria persistente de negocio)
_estado_oscilador: Dict[str, Any] = {
    "capa_activa": "L4_YO",
    "historial": [],  # últimos N cambios de perspectiva
}


def _recolectar_self_ax() -> Dict[str, Any]:
    """
    Lee declaraciones del cuerpo `self` vía AX.
    Fail-closed: si AX no responde, SF no inventa identidad.
    """
    try:
        from modules.axiomas import recolectar
    except Exception as e:
        return {
            "ok": False,
            "razon": f"AX.recolectar no disponible: {type(e).__name__}: {e}",
            "declaraciones": [],
        }

    try:
        decls, errores = recolectar()
    except Exception as e:
        return {
            "ok": False,
            "razon": f"recolectar falló: {type(e).__name__}: {e}",
            "declaraciones": [],
        }

    self_decls = []
    for d in decls or []:
        cuerpo = str(d.get("cuerpo") or d.get("fuente") or "").lower()
        # etiquetas frecuentes del cuerpo self en el repo
        if cuerpo == "self" or str(d.get("id", "")).upper().startswith("SF"):
            self_decls.append({
                "id": d.get("id"),
                "tipo": d.get("tipo"),
                "gobierna": list(d.get("gobierna") or []),
                "enunciado": d.get("enunciado") or d.get("sujeto"),
            })

    return {
        "ok": True,
        "razon": None,
        "declaraciones": self_decls,
        "n": len(self_decls),
        "errores_recoleccion": len(errores or []),
    }


def yo_funcional() -> Dict[str, Any]:
    """
    Identidad del sistema = proyección del cuerpo axiomático self.
    Engine la consulta; no la modifica.
    """
    ax = _recolectar_self_ax()
    return {
        "contenedor": "self",
        "rol": "SF",
        "tipo": "yo_funcional",
        "capa_activa": _estado_oscilador.get("capa_activa"),
        "ax_self": ax,
        "identidad_disponible": bool(ax.get("ok") and ax.get("n", 0) > 0),
        "nota": (
            "Yo funcional de fase: anclado en AX.self. "
            "No implica capas CEMYCA implementadas."
        ),
    }


def oscilar(
    hacia: Optional[str] = None,
    contexto: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Cambia (o reporta) la perspectiva activa del sistema.
    Fase: solo valida nombre de capa y registra el intento.
    Sin fricción/pesos hasta que existan archivos de capa.
    """
    actual = _estado_oscilador.get("capa_activa")
    if hacia is None:
        return {
            "ok": True,
            "capa_activa": actual,
            "cambio": False,
            "capas_validas": sorted(CAPAS_VALIDAS),
            "contexto": contexto or {},
        }

    clave = str(hacia).strip().upper()
    # admite "L4" o "L4_YO"
    if clave in CAPAS_VALIDAS:
        destino = clave
    else:
        destino = None
        for c in CAPAS_VALIDAS:
            if c.startswith(clave + "_") or c == clave:
                destino = c
                break

    if destino is None:
        return {
            "ok": False,
            "capa_activa": actual,
            "cambio": False,
            "error": f"capa no válida: {hacia}",
            "capas_validas": sorted(CAPAS_VALIDAS),
        }

    if destino != actual:
        hist = list(_estado_oscilador.get("historial") or [])
        hist.append({"desde": actual, "hacia": destino})
        _estado_oscilador["historial"] = hist[-20:]
        _estado_oscilador["capa_activa"] = destino

    return {
        "ok": True,
        "capa_activa": _estado_oscilador["capa_activa"],
        "cambio": destino != actual,
        "desde": actual,
        "hacia": destino,
        "contexto": contexto or {},
        "nota": "oscilación de fase sin pesos de capa",
    }


def barrer() -> Dict[str, Any]:
    """Centinela de SF: identidad legible solo si AX.self responde."""
    yo = yo_funcional()
    ax = yo.get("ax_self") or {}
    coherente = bool(ax.get("ok")) and (
        ax.get("errores_recoleccion", 1) == 0
    )
    # identidad vacía no tumba el módulo: es fase; sí se reporta
    return {
        "contenedor": "self",
        "rol": "SF",
        "coherente": coherente,
        "identidad_disponible": yo.get("identidad_disponible"),
        "capa_activa": yo.get("capa_activa"),
        "n_declaraciones_self": ax.get("n", 0),
        "capas_implementadas": [],  # se llenará cuando existan archivos
        "capas_validas": sorted(CAPAS_VALIDAS),
        "errores": [] if coherente else [ax.get("razon") or "AX.self no legible"],
    }


def verificar() -> Dict[str, Any]:
    return barrer()


def verificar_salida(salida: Dict[str, Any]) -> bool:
    if not isinstance(salida, dict):
        return False
    return "coherente" in salida or "capa_activa" in salida or "ax_self" in salida


CONTENEDOR = {
    "nombre": "self",
    "rol": "SF",
    "version": "0.1-fase",
    "requiere": [],   # <-- vacío; AX se resuelve al invocar yo_funcional/barrer
    "descripcion": (
        "Yo funcional del sistema. Identidad desde el cuerpo axiomático self. "
        "No orquesta. No calcula Tru. Oscilador de perspectiva (fase). "
        "Dependencia AX en runtime, no en arranque."
    ),
    "capacidades": {
        "verificar": verificar,
        "barrer": barrer,
        "yo_funcional": yo_funcional,
        "oscilar": oscilar,
    },
}
   

__all__ = [
    "CONTENEDOR",
    "verificar",
    "barrer",
    "yo_funcional",
    "oscilar",
    "verificar_salida",
    "CAPAS_VALIDAS",
]
