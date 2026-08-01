"""
tests/test_vpsi_contratos.py
============================
Medición real del Engine y del núcleo VPSI-TRUTH.
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


def _engine(strict: bool = True, verificar_axiomas: bool = True):
    from core.engine import Engine
    return Engine(
        str(MODULOS),
        invocador_id="core",
        verificar_axiomas=verificar_axiomas,
        strict=strict,
    )


# ===============================================================
# CT — ancla
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


# ===============================================================
# FO — fórmulas
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
# ENGINE — arranque y contrato
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

    def test_roles_sin_duplicar(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        nombres = [c.nombre for c in eng.registro.contenedores.values()]
        assert len(nombres) == len(set(nombres))

    def test_tx_en_roles(self):
        from core.engine import ROLES
        assert "TX" in ROLES

    def test_capacidades_resolubles(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        for c in eng.registro.contenedores.values():
            for cap in c.capacidades:
                fn = c.fn(cap)
                if fn is not None:
                    assert callable(fn), f"{c.nombre}.{cap} no callable: {fn!r}"


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
        out = eng.ejecutar_capacidad("AX", "capacidad_inventada_xyz")
        assert es_undefined(out)


# ===============================================================
# EVALUAR
# ===============================================================
class TestEvaluar:
    def test_sin_contexto_k_indefinido(self):
        eng = _engine(verificar_axiomas=True, strict=True)
        out = eng.evaluar({"C": "1", "L": "1", "K": "1"})
        assert out["estado"] == "UNDEFINED"
        assert out["factores"]["K"] == "UNDEFINED"

    def test_con_contexto_y_factores(self):
        eng = _engine(verificar_axiomas=True, strict=True)
        out = eng.evaluar({
            "O_context": "test",
            "C": "1",
            "L": "1",
            "K": "1",
        })
        assert out["estado"] == "OK"
        assert out["tru_total"] == "1"
        assert out["tru_ri"] == "1"

    def test_piso_beta_via_engine(self):
        from modules.constante import BETA
        eng = _engine(verificar_axiomas=True, strict=True)
        out = eng.evaluar({
            "contexto": "test",
            "C": "0",
            "L": "0",
            "K": "0",
        })
        assert out["estado"] == "OK"
        assert out["tru_total"] == str(BETA)

    def test_engine_no_inventa_sin_factores(self):
        eng = _engine(verificar_axiomas=True, strict=True)
        out = eng.evaluar({"O_context": "test"})
        assert out["estado"] in ("PARCIAL", "OK", "ERROR")
        if out["estado"] == "PARCIAL":
            assert "tru_total" not in out or out.get("tru_total") is None


# ===============================================================
# AX / MC
# ===============================================================
class TestCompuertas:
    def test_ax_coherente(self):
        from core.engine import es_undefined
        eng = _engine(verificar_axiomas=False, strict=False)
        assert eng.registro.primero("AX") is not None
        out = eng.ejecutar_capacidad("AX", "verificar")
        if es_undefined(out):
            out = eng.ejecutar_capacidad("AX", "barrer")
        assert not es_undefined(out)
        assert isinstance(out, dict)
        assert out.get("coherente") is True

    def test_mc_coherente(self):
        from core.engine import es_undefined
        eng = _engine(verificar_axiomas=False, strict=False)
        assert eng.registro.primero("MC") is not None
        out = eng.ejecutar_capacidad("MC", "verificar")
        if es_undefined(out):
            out = eng.ejecutar_capacidad("MC", "barrer")
        assert not es_undefined(out)
        assert isinstance(out, dict)
        assert "coherente" in out


# ===============================================================
# TAXONOMÍA
# ===============================================================
class TestTaxonomia:
    def test_barrer_y_filtro(self):
        if not (MODULOS / "taxonomia" / "__init__.py").exists():
            pytest.skip("taxonomia no montada")
        from modules.taxonomia import barrer, aplicar
        estado = barrer()
        assert "coherente" in estado
        res = aplicar({}, contexto={"O_context": "test"})
        ids_ok = set(estado.get("tacticas", []))
        for a in res.get("aplicadas", []):
            assert a["id"] in ids_ok


# ===============================================================
# CALCULATOR
# ===============================================================
class TestCalculator:
    def test_k_sin_contexto_none(self):
        if not (MODULOS / "calculator" / "__init__.py").exists():
            pytest.skip("calculator no montado")
        from modules.calculator import calcular
        out = calcular({"metodo": "operacional"})
        assert out.get("K") is None


# ===============================================================
# INTROSPECCIÓN
# ===============================================================
class TestIntrospeccion:
    def test_censar(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        r = eng.censar()
        assert "roles" in r
        assert "rechazados" in r
        assert "total" in r

    def test_inventario(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        inv = eng.inventario()
        assert inv["estado"] in ("OPERATIVO", "RECHAZADO", "NO_INICIADO")
        assert "registro" in inv


# ===============================================================
# CT vía Engine
# ===============================================================
class TestAnclaViaEngine:
    def test_get_constantes(self):
        eng = _engine(verificar_axiomas=False, strict=False)
        c = eng.get_constantes()
        assert c["ALPHA"] == Fraction(26, 27)
        assert c["BETA"] == Fraction(1, 27)


# ===============================================================
# TR1 / U1 — generatividad (fase actual)
# ===============================================================
class TestGeneratividad:
    def test_contrato_ax(self):
        from modules.axiomas import CONTENEDOR, generatividad
        assert CONTENEDOR.get("rol") == "AX"
        caps = CONTENEDOR.get("capacidades") or {}
        assert "generatividad" in caps
        assert callable(caps["generatividad"])
        assert callable(generatividad)

    def test_capas_y_canonica_completa(self):
        from modules.axiomas import generatividad
        g = generatividad()
        assert isinstance(g, dict)
        assert "theta_n" in g
        assert "pares_novedosos" in g
        assert "im_vs_theta" in g
        assert g["im_vs_theta"] in ("GENERATIVO", "ESTANCADO", "SIN_DATOS")

        can = g.get("canonica")
        assert isinstance(can, dict), "falta capa canónica"
        assert can.get("theta_n") == 24
        assert can.get("ids_faltantes") == []
        assert can.get("ids_sin_dominio") == []
        assert g["theta_n"] >= can["theta_n"]

    def test_generativo_minimo(self):
        """Umbral de fase: >0 y >|Θ|. No exige 153 (repo incompleto)."""
        from modules.axiomas import generatividad
        g = generatividad()
        can = g["canonica"]
        assert can["pares_novedosos"] > 0
        assert can["im_vs_theta"] == "GENERATIVO"
        assert can["pares_novedosos"] > can["theta_n"]

    def test_via_engine(self):
        from core.engine import es_undefined
        eng = _engine(verificar_axiomas=False, strict=False)
        if hasattr(eng, "censar_generatividad"):
            out = eng.censar_generatividad()
        else:
            out = eng.ejecutar_capacidad("AX", "generatividad")
        assert not es_undefined(out)
        assert isinstance(out, dict)
        assert "canonica" in out or out.get("theta_n") is not None
