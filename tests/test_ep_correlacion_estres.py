"""
VPSI-TRUTH --- tests/test_ep_correlacion_estres.py

Test de Protocolo Epistémico de Estrés (EP Stress Test) para presionar
los límites de cálculo, umbrales de solape y pesos en la correlación (K).
"""

from __future__ import annotations

import pytest
from fractions import Fraction
from modules.calculator.conteos import extraer_conteos


def test_estres_divergencia_total_disjunta() -> None:
    """
    Presiona el sistema con contextos y afirmaciones totalmente disjuntos
    para verificar que la divergencia alcance la saturación máxima (f = c, K = 0).
    """
    texto = "El motor cuántico procesa ondas gravitacionales estelares."
    o_context = "La economía financiera global depende de tasas de interés bancarias."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    assert resultado["c"] > 0, "Debe registrar proposiciones."
    assert resultado["afirmaciones_falsas"] == Fraction(resultado["c"]), \
        "Con vocabulario totalmente disjunto, todas las afirmaciones deben ser falsas (f = c)."
    
    k_val = Fraction(1) - (resultado["afirmaciones_falsas"] / Fraction(resultado["c"]))
    assert k_val == Fraction(0), f"La correlación K esperada era 0, se obtuvo {k_val}"


def test_estres_fronteras_solape_lexico() -> None:
    """
    Presiona los umbrales de transición en _divergencia_peso (frontera del 60% y 50%)
    para evaluar si los pesos de penalización responden con precisión exacta sin saltos erráticos.
    """
    # Contexto base rico en tokens deterministas
    o_context = "sistema operativo determinista verifica calculos exactos mediante axiomas formales."
    
    # Caso 1: Solape alto pero imperfecto (por debajo del 60%, cae en tramo intermedio de roce)
    texto_parcial = "sistema operativo procesa calculos generales."
    res_parcial = extraer_conteos(texto=texto_parcial, o_context=o_context)
    
    assert res_parcial["afirmaciones_falsas"] > Fraction(0), "Debe registrar divergencia parcial."
    assert res_parcial["afirmaciones_falsas"] < Fraction(res_parcial["c"]), \
        "La divergencia no debe saturar totalmente con un solape intermedio."


def test_estres_saturacion_stoplist_extrema() -> None:
    """
    Presiona el comportamiento del sistema cuando el texto está compuesto
    principalmente por stopwords y artículos, evaluando la resistencia del denominador.
    """
    texto = "El de la los en con para por y o un una."
    o_context = "El sistema operativo."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    # Unidades muy cortas sin contenido mínimo de tokens no proposicionales deben descartarse o dar base nula
    assert resultado["c"] == 0 or resultado["tokens_restados"] > 0, \
        "El sistema debe filtrar adecuadamente el ruido masivo de stopwords."


def test_estres_multi_clausula_disonante() -> None:
    """
    Presiona textos complejos con múltiples cláusulas combinadas,
    verificando que la acumulación de f detalle cada fricción de forma independiente.
    """
    texto = "El sistema es determinista; sin embargo, opera de forma estocástica y aleatoria."
    o_context = "El sistema opera bajo principios estrictamente deterministas."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    assert resultado["o_presente"] is True
    assert resultado["afirmaciones_falsas"] > Fraction(0), "Debe detectar la disonancia en las cláusulas."
    assert len(resultado["f_detalle"]) > 0, "El detalle de f debe listar las unidades con fricción."
