"""
VPSI-TRUTH --- tests/test_ep_correlacion.py

Test de Protocolo Epistémico (EP Test) para verificar la precisión
y trazabilidad de la correlación y conteos operacionales.
"""

from __future__ import annotations

import pytest
from fractions import Fraction
from modules.calculator.conteos import extraer_conteos


def test_ep_correlacion_convergencia_beta() -> None:
    """
    Verifica que un texto con alta concordancia respecto a O_context
    alcance una correlación K óptima tendiendo a la unidad,
    evitando caídas de precisión espurias.
    """
    texto = "El sistema opera bajo principios deterministas y mantiene afirmaciones estables."
    o_context = "El sistema opera bajo principios deterministas y mantiene afirmaciones estables y verificadas."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    assert resultado["c"] > 0, "Debe haber afirmaciones detectadas."
    assert resultado["afirmaciones_falsas"] == Fraction(0), "No debe haber divergencias falsas con alta coincidencia."
    
    k_val = Fraction(1) - (resultado["afirmaciones_falsas"] / Fraction(resultado["c"]))
    assert k_val == Fraction(1), f"La correlación K esperada era 1, se obtuvo {k_val}"


def test_ep_correlacion_divergencia_trazable() -> None:
    """
    Verifica que ante una divergencia explícita, el sistema desglose
    la falla y permita auditar el motivo exacto en el detalle.
    """
    texto = "El sistema es totalmente estocástico y no determinista."
    o_context = "El sistema opera bajo principios estrictamente deterministas."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    assert resultado["o_presente"] is True
    assert resultado["afirmaciones_falsas"] > 0, "Debe registrar divergencia léxica."
    assert len(resultado["f_detalle"]) > 0, "El detalle de f debe contener la trazabilidad del fallo."
