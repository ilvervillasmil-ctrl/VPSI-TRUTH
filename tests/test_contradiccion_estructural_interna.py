"""
Test de contradicción estructural interna.

Objetivo:
Verificar que el sistema detecta una contradicción entre
dos compromisos asumidos por el mismo hablante y degrade
la coherencia estructural.

No fija valores exactos de C, L o K, porque éstos pertenecen
al mecanismo del VPSI. El test únicamente verifica propiedades
estructurales esperadas.
"""

from core.engine import Engine


def test_contradiccion_estructural_interna():

    engine = Engine()

    texto = """
    Yo soy una persona sumamente inteligente porque desarrollé un
    sistema capaz de realizar auditorías estructurales complejas.

    Sin embargo, yo no soy una persona inteligente.
    """

    peticion = {
        "descripcion": texto,
        "modo": "auditoria",
    }

    resultado = engine.evaluar(peticion)

    assert resultado is not None

    # Deben existir factores
    assert "C" in resultado
    assert "L" in resultado
    assert "K" in resultado

    # Debe existir Tru
    assert "Tru_Ri" in resultado
    assert "Tru_total" in resultado

    # Debe detectarse pérdida de coherencia
    assert resultado["C"] < 1

    # El resultado final no debe ser máximo
    assert resultado["Tru_total"] < 1
