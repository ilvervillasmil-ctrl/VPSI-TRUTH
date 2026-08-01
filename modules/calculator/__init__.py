from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Any
from core.diagnostico import DiagnosticoGlobal


# ===============================================================
# ENGINE
# ===============================================================
def calcular(peticion: Dict[str, Any]) -> Dict[str, Optional[Fraction]]:
    """
    Calcula C, L, K. Devuelve None si falta información.
    Las implementaciones concretas viven en archivos dentro de calculator/.
    No calcula Tru_total (eso es FO).
    """
    errores = []
    C = L = K = None
    metodo = peticion.get("metodo", "operacional")

    # --- Calcular C ---
    try:
        if metodo == "teorico":
            C = _calcular_c_teorico(peticion.get("mensaje")) if peticion.get("mensaje") else None
        else:
            C = _calcular_c_operacional(peticion.get("compromisos"), peticion.get("contradicciones"))
    except Exception as e:
        errores.append(f"Error en C: {str(e)}")
        C = None

    # --- Calcular L ---
    try:
        if metodo == "teorico":
            L = _calcular_l_teorico(peticion.get("mensaje")) if peticion.get("mensaje") else None
        else:
            L = _calcular_l_operacional(peticion.get("posturas"), peticion.get("reversiones"))
    except Exception as e:
        errores.append(f"Error en L: {str(e)}")
        L = None

    # --- Calcular K ---
    try:
        if peticion.get("contexto") is None:
            K = None  # Sin O_context, K no puede calcularse
        else:
            if metodo == "teorico":
                K = (
                    _calcular_k_teorico(peticion.get("mensaje"), peticion.get("contexto"))
                    if peticion.get("mensaje")
                    else None
                )
            else:
                K = _calcular_k_operacional(
                    peticion.get("afirmaciones"),
                    peticion.get("afirmaciones_falsas"),
                    peticion.get("contexto"),
                )
    except Exception as e:
        errores.append(f"Error en K: {str(e)}")
        K = None

    # Enviar reporte si hay errores
    if errores:
        DiagnosticoGlobal.recibir_reporte(
            modulo="calculator",
            errores=[{"tipo": "error_calculo", "detalle": error} for error in errores],
        )

    return {"C": C, "L": L, "K": K}


# ===============================================================
# CENTINELA
# ===============================================================
def verificar_salida(salida: Dict[str, Optional[Fraction]]) -> bool:
    """
    Valida la forma de la salida.
    None en un factor es dato ausente legítimo (sobre todo K sin contexto),
    no implica que el módulo esté roto.
    """
    if not isinstance(salida, dict):
        return False
    return all(k in salida for k in ("C", "L", "K"))


# ===============================================================
# CONTENEDOR (Contrato del módulo — al final)
# ===============================================================
# Contrato literal para el Engine:
# conoce este mapa y solo actúa según lo que aquí se declara.
CONTENEDOR = {
    "nombre": "calculator",
    "rol": "CA",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Calcula C, L, K. Usa None para valores no disponibles. "
        "Sin O_context, K queda None (Def-5.3.1). "
        "No calcula Tru_total (eso es FO). "
        "El Engine solo ejecuta lo que este contrato declara."
    ),
    "capacidades": {
        "verificar": calcular,
        "calcular": calcular,
    },
}


# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "calcular",
    "verificar_salida",
]
