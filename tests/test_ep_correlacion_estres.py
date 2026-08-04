"""
VPSI-TRUTH --- tests/test_ep_correlacion_estres.py

Test de Protocolo Epistémico de Estrés (EP Stress Test) robusto para presionar
los límites de cálculo, contradicciones explícitas y separación semántica.
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


def test_estres_contradiccion_explicita() -> None:
    """
    Presiona al sistema con una contradicción semántica clara e inequívoca,
    garantizando que la divergencia se active por oposición directa de significado
    y no por mera ambigüedad de solape léxico.
    """
    o_context = "El sistema es completamente determinista y nunca utiliza aleatoriedad."
    texto = "El sistema utiliza aleatoriedad para producir resultados diferentes en cada ejecución."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    assert resultado["o_presente"] is True
    assert resultado["c"] > 0, "Debe registrar proposiciones evaluables."
    assert resultado["afirmaciones_falsas"] > Fraction(0), \
        "Una contradicción explícita debe activar necesariamente afirmaciones falsas (f > 0)."
    assert len(resultado["f_detalle"]) > 0, "El detalle de f debe registrar la fricción."


def test_estres_informacion_adicional_no_contradictoria() -> None:
    """
    Valida que información adicional o complementaria que comparte tokens nucleares
    pero aporta datos nuevos no sea castigada indebidamente como afirmación falsa,
    respetando la evolución del correlador.
    """
    o_context = "sistema operativo determinista verifica calculos exactos mediante axiomas formales."
    texto = "sistema operativo procesa calculos generales."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
    assert resultado["c"] > 0, "Debe registrar afirmaciones."
    # El correlador avanzado tolera solapes estables sin disparar falsedad estructural
    assert resultado["afirmaciones_falsas"] == Fraction(0), \
        "La información complementaria no contradictoria debe mantener f = 0 bajo el nuevo criterio."


def test_estres_saturacion_stoplist_extrema() -> None:
    """
    Presiona el comportamiento del sistema cuando el texto está compuesto
    principalmente por stopwords y artículos, evaluando la resistencia del denominador.
    """
    texto = "El de la los en con para por y o un una."
    o_context = "El sistema operativo."
    
    resultado = extraer_conteos(texto=texto, o_context=o_context)
    
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
