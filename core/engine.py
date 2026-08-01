"""
VPSI-TRUTH --- core/engine.py

#El Engine es el ejecutor universal de contratos del framework VPSI-TRUTH.

Principio fundamental:
- Posee conocimiento completo de la arquitectura (módulos, contratos, dependencias,
  estados, capacidades, variables, archivos internos y estructura de cada módulo).
- Su capacidad de actuación está estrictamente limitada por lo que cada contrato
  declara explícitamente en CONTENEDOR["capacidades"].
- Nunca inventa operaciones.
- Nunca modifica resultados.
- Nunca sustituye la lógica de un módulo.
- Nunca interpreta la información producida por un módulo.
- Todo comportamiento de acción proviene exclusivamente de los contratos.
"""

from __future__ import annotations
import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ===============================================================
# CONSTANTES GLOBALES: ROLES DE MÓDULOS
# ===============================================================
# Nota: Los roles son parte de la arquitectura, no de la lógica de negocio.
ROL_AXIOMAS = "AX"
ROL_CONSTANTE = "CT"
ROL_FORMULAS = "FO"
ROL_CALCULATOR = "CA"
ROL_CONTEXTO = "CX"
ROL_TAXONOMIA = "TX"
ROL_REALIDAD = "RE"
ROL_VERIFICACION = "VX"
ROL_CORRELACION_MECANICA = "MC"

ROLES = (
    ROL_AXIOMAS,
    ROL_CONSTANTE,
    ROL_FORMULAS,
    ROL_CALCULATOR,
    ROL_CONTEXTO,
    ROL_TAXONOMIA,
    ROL_REALIDAD,
    ROL_VERIFICACION,
    ROL_CORRELACION_MECANICA,
)

# Módulos obligatorios para el arranque (parte de la arquitectura)
OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS, ROL_CORRELACION_MECANICA)

# ===============================================================
# EJECUCIÓN UNIVERSAL DE CONTRATOS
# ===============================================================

def ejecutar_contratos(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    El Engine únicamente lee los contratos declarados por los módulos
    y ejecuta las capacidades autorizadas por dichos contratos.

    No interpreta resultados.
    No modifica resultados.
    No inventa operaciones.
    """

    self.invocador.reiniciar()

    for contenedor in self.registro.contenedores.values():
        self.invocador.ejecutar_desde_contrato(
            contenedor,
            peticion,
        )

    return self.invocador.resultado()


# ===============================================================
# EVALUACIÓN
# ===============================================================

def evaluar(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Punto único de entrada del Engine.
    """
    return self.ejecutar_contratos(peticion)
