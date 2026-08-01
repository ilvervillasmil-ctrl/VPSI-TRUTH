"""
tests/test_vpsi_contratos.py
============================
Adaptado al Engine operativo (verificar_axiomas / strict / ROLES / UNDEFINED).
No usa símbolos que el Engine ya no exporta.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULOS = ROOT / "modules"


def _engine(*, strict: bool = True, verificar_axiomas: bool = True):
    from core.engine import Engine
    return Engine(
        str(MODULOS),
        invocador_id="core",
        verificar_axiomas=verificar_axiomas,
        strict=strict,
    )


# ===============================================================
# CT — ancla (no capacidades alpha/beta)
# ===============================================================
class TestConstantesAncla:
    def test_fraction_y_valores(self):
        from modules.constante import ALPHA, BETA
        assert isinstance(ALPHA, Fraction)
        assert isinstance(BETA, Fraction)
        assert ALPHA == Fraction(26, 27)
        assert BETA == Fraction(1, 27)
        assert ALPHA + BETA == Fraction(1)
        assert BETA > 0

    def test_ancla_via_engine(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        c = eng.get_constantes()
        assert c["ALPHA"] == Fraction(26, 27)
        assert c["BETA"] == Fraction(1, 27)


# ===============================================================
# FO
# ===============================================================
class TestFormulas:
    def test_rechaza_float(self):
        from modules.formulas.truth import tru_ri, tru_total
        with pytest.raises(TypeError):
            tru_ri(0.5, Fraction(1), Fraction(1))
        with pytest.raises(TypeError):
            tru_total(0.5, Fraction(1), Fraction(1))

    def test_piso_y_techo(self):
        from modules.formulas.truth import tru_ri, tru_total
        from modules.constante import BETA
        assert tru_ri(Fraction(1), Fraction(1), Fraction(1)) == Fraction(1)
        assert tru_total(Fraction(0), Fraction(0), Fraction(0)) == BETA
        assert tru_total(Fraction(1), Fraction(1), Fraction(1)) == Fraction(1)


# ===============================================================
# ENGINE — arranque
# ===============================================================
class TestEngineArranque:
    def test_arranca_operativo(self):
        eng = _engine(strict=True, verificar_axiomas=True)
        assert eng.estado == "OPERATIVO"

    def test_obligatorios_presentes(self):
        from core.engine import OBLIGATORIOS
        eng = _engine(verificar_axiomas=False, strict=False)
        for rol in OBLIGATORIOS:
            assert eng.registro.por_rol.get(rol), f"falta {rol}"

    def test_roles_admitidos(self):
        from core.engine import ROLES
        for r in ("CT", "AX", "FO", "MC", "CA", "CX", "RE", "VX", "TX", "SF", "DG"):
            assert r in ROLES

    def test_sin_nombres_duplicados(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        nombres = list(eng.registro.contenedores)
        assert len(nombres) == len(set(nombres))

    def test_capacidades_resolubles(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        for c in eng.registro.contenedores.values():
            for cap in c.capacidades:
                fn = c.fn(cap)
                if fn is not None:
                    assert callable(fn), f"{c.nombre}.{cap} = {fn!r}"


# ===============================================================
# UNDEFINED
# ===============================================================
class TestUndefined:
    def test_no_bool(self):
        from core.engine import UNDEFINED
        with pytest.raises(TypeError):
            bool(UNDEFINED)

    def test_capacidad_inexistente(self):
        from core.engine import es_undefined
        eng = _engine(verificar_axiomas=False, strict=False)
        assert es_undefined(eng.ejecutar_capacidad("AX", "no_existe_xyz"))


# ===============================================================
# EVALUAR
# ===============================================================
class TestEvaluar:
    def test_sin_o_context(self):
        eng = _engine(strict=True, verificar_axiomas=True)
        out = eng.evaluar({"C": "1", "L": "1", "K": "1"})
        assert out["estado"] == "UNDEFINED"
        assert out["factores"]["K"] == "UNDEFINED"

    def test_ok_con_factores(self):
        eng = _engine(strict=True, verificar_axiomas=True)
        out = eng.evaluar({"O_context": "test", "C": "1", "L": "1", "K": "1"})
        assert out["estado"] == "OK"
        assert out["tru_ri"] == "1"
        assert out["tru_total"] == "1"

    def test_piso_beta(self):
        from modules.constante import BETA
        eng = _engine(strict=True, verificar_axiomas=True)
        out = eng.evaluar({"contexto": "test", "C": "0", "L": "0", "K": "0"})
        assert out["estado"] == "OK"
        assert out["tru_total"] == str(BETA)

    def test_parcial_sin_factores(self):
        eng = _engine(strict=True, verificar_axiomas=True)
        out = eng.evaluar({"O_context": "test"})
        assert out["estado"] in ("PARCIAL", "OK", "ERROR")
        if out["estado"] == "PARCIAL":
            assert "tru_total" not in out or out.get("tru_total") in (None, "UNDEFINED")


# ===============================================================
# COMPUERTAS AX / MC
# ===============================================================
class TestCompuertas:
    def test_ax(self):
        from core.engine import es_undefined
        eng = _engine(verificar_axiomas=False, strict=False)
        assert eng.registro.primero("AX") is not None
        out = eng.ejecutar_capacidad("AX", "verificar")
        if es_undefined(out):
            out = eng.ejecutar_capacidad("AX", "barrer")
        assert not es_undefined(out)
        assert out.get("coherente") is True

    def test_mc(self):
        from core.engine import es_undefined
        eng = _engine(verificar_axiomas=False, strict=False)
        assert eng.registro.primero("MC") is not None
        out = eng.ejecutar_capacidad("MC", "verificar")
        if es_undefined(out):
            out = eng.ejecutar_capacidad("MC", "barrer")
        assert not es_undefined(out)
        assert "coherente" in out


# ===============================================================
# TX / CA
# ===============================================================
class TestTaxonomia:
    def test_filtro(self):
        if not (MODULOS / "taxonomia" / "__init__.py").exists():
            pytest.skip("sin taxonomia")
        from modules.taxonomia import barrer, aplicar
        estado = barrer()
        res = aplicar({}, contexto={"O_context": "t"})
        ids_ok = set(estado.get("tacticas", []))
        for a in res.get("aplicadas", []):
            assert a["id"] in ids_ok


class TestCalculator:
    def test_k_sin_contexto(self):
        if not (MODULOS / "calculator" / "__init__.py").exists():
            pytest.skip("sin calculator")
        from modules.calculator import calcular
        assert calcular({"metodo": "operacional"}).get("K") is None


# ===============================================================
# INTROSPECCIÓN
# ===============================================================
class TestIntrospeccion:
    def test_censar(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        r = eng.censar()
        assert "roles" in r and "rechazados" in r

    def test_inventario(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        inv = eng.inventario()
        assert "estado" in inv and "registro" in inv
