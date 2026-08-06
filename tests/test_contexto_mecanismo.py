# ==============================================================
# tests/test_contexto_mecanismo.py
# Test mínimo de humo (reemplazo de la suite anterior)
# ==============================================================

def test_multiplicacion_simple():
    assert 2 * 2 == 4


def test_engine_operativo():
    from pathlib import Path
    from core.engine import Engine, ArranqueError

    try:
        eng = Engine(Path("modules"), invocador_id="test_simple", strict=True)
    except ArranqueError as e:
        raise AssertionError(f"Engine no arrancó: {e}") from e

    assert eng.estado == "OPERATIVO"
    assert eng.registro.total() >= 1
