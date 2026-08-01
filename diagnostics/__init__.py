"""
VPSI-TRUTH --- modules/diagnostics/__init__.py

Contenedor de diagnóstico. Rol DG.

Omega Report no calcula. Solo recibe los informes reales que el Engine
ya obtuvo de cada módulo y los presenta de forma objetiva.

Contrato:
  - No recalcula C, L, K, Tru_Ri ni Tru_total.
  - No vuelve a barrer axiomas ni mecánica.
  - Solo valida que los datos recibidos sean completos y consistentes
    con lo que el sistema ya produjo.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime, timezone


# ===============================================================
# CONTENEDOR (Contrato del módulo)
# ===============================================================
CONTENEDOR = {
    "nombre": "diagnostics",
    "rol": "DG",
    "version": "1.0",
    "requiere": ["CT", "AX", "FO"],  # Mínimo necesario para un reporte válido
    "descripcion": (
        "Contenedor de diagnóstico. Rol DG. "
        "Recibe los informes reales producidos por el Engine y los módulos "
        "y genera el Omega Report sin recalcular nada."
    ),
    "capacidades": {
        "verificar": "verificar",
        "inventario": "inventario",
        "generar_reporte": "generar_reporte",
        "validar_entrada": "validar_entrada",
    },
}


# ===============================================================
# ERRORES
# ===============================================================
class DiagnosticoError(Exception):
    """Error en la capa de diagnóstico."""
    pass


class EntradaIncompletaError(DiagnosticoError):
    """Faltan informes obligatorios para generar el reporte."""
    pass


# ===============================================================
# LO QUE EL MÓDULO EXIGE RECIBIR DEL ENGINE
# ===============================================================
CAMPOS_OBLIGATORIOS = (
    "estado_engine",          # "OPERATIVO" | "RECHAZADO"
    "constantes",             # {"ALPHA": ..., "BETA": ...}
    "informe_axiomas",        # salida de axiomas.barrer()
    "informe_formulas",       # salida de formulas.barrer() (opcional pero recomendado)
    "resultados_evaluacion",  # lista de llamadas a engine.evaluar() si las hubo
)

CAMPOS_OPCIONALES = (
    "informe_mecanica",
    "informe_self",
    "errores_arranque",
    "registro_modulos",
    "tests",
)


def validar_entrada(datos: Dict[str, Any]) -> List[str]:
    """
    Verifica que el Engine haya pasado la información mínima real.
    No recalcula nada. Solo comprueba presencia y forma.
    """
    faltas = []

    if not isinstance(datos, dict):
        return ["entrada no es dict"]

    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos:
            faltas.append(f"falta campo obligatorio: {campo}")

    # Validaciones de forma (sin recalcular)
    if "constantes" in datos:
        c = datos["constantes"]
        if not isinstance(c, dict) or "ALPHA" not in c or "BETA" not in c:
            faltas.append("constantes debe contener ALPHA y BETA")

    if "informe_axiomas" in datos:
        ia = datos["informe_axiomas"]
        if not isinstance(ia, dict):
            faltas.append("informe_axiomas debe ser dict")
        elif "coherente" not in ia:
            faltas.append("informe_axiomas sin clave 'coherente'")

    if "estado_engine" in datos:
        if datos["estado_engine"] not in ("OPERATIVO", "RECHAZADO", "NO_INICIADO"):
            faltas.append(f"estado_engine inválido: {datos['estado_engine']}")

    return faltas


# ===============================================================
# GENERACIÓN DEL REPORTE (solo presentación)
# ===============================================================
def generar_reporte(datos: Dict[str, Any], salida: Optional[Path] = None) -> Dict[str, Any]:
    """
    Genera el Omega Report a partir de los datos reales que entrega el Engine.

    No ejecuta barrer(), no llama a tru_ri/tru_total, no recalcula nada.
    Solo lee y formatea.
    """
    faltas = validar_entrada(datos)
    if faltas:
        raise EntradaIncompletaError(
            "No se puede generar Omega Report. Faltan datos reales del sistema:\n  - "
            + "\n  - ".join(faltas)
        )

    reporte = {
        "titulo": "OMEGA REPORT - VPSI-TRUTH",
        "generado": datetime.now(timezone.utc).isoformat(),
        "estado_engine": datos["estado_engine"],
        "constantes": datos["constantes"],
        "axiomas": {
            "coherente": datos["informe_axiomas"].get("coherente"),
            "declaraciones": datos["informe_axiomas"].get("declaraciones"),
            "choques": len(datos["informe_axiomas"].get("choques", [])),
            "errores": len(datos["informe_axiomas"].get("errores", [])),
        },
        "formulas": datos.get("informe_formulas"),
        "mecanica": datos.get("informe_mecanica"),
        "evaluaciones": datos.get("resultados_evaluacion", []),
        "errores_arranque": datos.get("errores_arranque", []),
        "modulos": datos.get("registro_modulos"),
        "tests": datos.get("tests"),
        "valido": len(faltas) == 0 and datos["estado_engine"] == "OPERATIVO",
    }

    if salida is not None:
        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")

    return reporte


# ===============================================================
# VERIFICACIÓN DEL MÓDULO (contrato)
# ===============================================================
def verificar(datos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Capacidad de verificación del contenedor DG.
    Si se pasan datos, valida que sean suficientes para un reporte objetivo.
    """
    if datos is None:
        return {
            "contenedor": CONTENEDOR["nombre"],
            "estado": "APROBADO",
            "coherente": True,
            "mensaje": "Módulo DG listo. Esperando datos reales del Engine.",
        }

    faltas = validar_entrada(datos)
    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": "APROBADO" if not faltas else "RECHAZADO",
        "coherente": not faltas,
        "faltas": faltas,
    }


def inventario(peticion=None) -> Dict[str, Any]:
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "rol": CONTENEDOR["rol"],
        "requiere": CONTENEDOR["requiere"],
        "campos_obligatorios": list(CAMPOS_OBLIGATORIOS),
        "campos_opcionales": list(CAMPOS_OPCIONALES),
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
    }


# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "verificar",
    "inventario",
    "generar_reporte",
    "validar_entrada",
    "DiagnosticoError",
    "EntradaIncompletaError",
    "CAMPOS_OBLIGATORIOS",
    "CAMPOS_OPCIONALES",
]
