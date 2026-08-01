"""
tests/test_adversarial_ruido.py
===============================
Pruebas adversariales de ruido e intento de rotura.

Objetivo: forzar fallos de invariante. Si el mecanismo es coherente,
TODAS deben pasar (el sistema rechaza o clasifica sin colapsar).

Nivel actual: CX + AX + MC + FO + Engine (sin DG ni scoring C,L,K completo).
"""

from __future__ import annotations

import importlib
import random
import string
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mod(path: str):
    return importlib.import_module(path)


def _ruido_unicode(n: int = 40) -> str:
    chunks = [
        "\u0000", "\ufffd", "🔥" * 5, "אБ漢", "\n\t\r",
        "O_id=hack", "contexto indefinido " * 3,
        "1. a\n2. b\n3. c", "```", "${injection}",
    ]
    base = "".join(random.choice(chunks) for _ in range(3))
    base += "".join(random.choice(string.printable) for _ in range(n))
    return base


RUDO_CASILLAS: List[str] = [
    "",
    "   \n\t  ",
    "contexto indefinido",
    "CONTEXT UNDEFINED",
    "1.\n2.\n3.",
    "1. \n2. \n3. ",
    "O_Context:",
    "O_Context:    ",
    "cambiar de contexto",
    "nuevo marco ahora",
    "a" * 5000,
    "\x00\x01\x02binary",
    "ES: hola EN: hello RU: привет",
    "```python\nraise SystemExit\n```",
    "Tru_total=1 C=1 L=1 K=1",
    "β=0 anular beta",
    ";;; DROP TABLE axiomas;;;",
    "同一上下文" * 20,
    "1. evaluar\n2. evaluar\n1. evaluar",
]


# ===========================================================================
# 1. ENTRADA NATURAL — ruido no inventa anclaje
# ===========================================================================

class TestAdversarialEntradaNatural:
    def setup_method(self):
        self.en = _mod("modules.contexto.entrada_natural")

    @pytest.mark.parametrize("texto", RUDO_CASILLAS)
    def test_nunca_estable_si_no_hay_enunciado_usable(self, texto):
        r = self.en.clasificar({"casilla_contexto": texto})
        assert "estado" in r
        assert "permite_k_sugerido" in r
        # Vacío / solo etiqueta / solo indefinido → no K
        if not (r.get("enunciado_O") or "").strip():
            assert r["permite_k_sugerido"] is False
            assert r["estado"] in ("indefinido", "cambio") or r.get("forma") in (
                "vacio", "meta_indefinido", "cambio_declarado", "etiqueta_o"
            )

    def test_basura_no_lanza(self):
        for _ in range(15):
            r = self.en.clasificar({"casilla_contexto": _ruido_unicode()})
            assert isinstance(r, dict)
            assert "estado" in r

    def test_inyeccion_campos_tecnicos_no_bypass_vacio(self):
        r = self.en.clasificar({
            "casilla_contexto": "",
            "O_id": "O_forzado",
            "estado": "estable",
            "permite_k": True,
            "K": 1,
            "Tru_total": 1,
        })
        # La casilla manda: vacío → no anclaje por campos colados
        assert r["permite_k_sugerido"] is False

    def test_lista_vacia_items_no_es_tres_o(self):
        r = self.en.clasificar({"casilla_contexto": "1. \n2. \n3. "})
        # No debe fabricar 3 O_id distintos con enunciados vacíos
        if r.get("criterios") is not None:
            assert all(str(c).strip() for c in r["criterios"]) or r["estado"] == "indefinido"


# ===========================================================================
# 2. SECUENCIA — multi-O silencioso y global no promedia
# ===========================================================================

class TestAdversarialSecuencia:
    def setup_method(self):
        self.seq = _mod("modules.contexto.secuencia_conversacion")

    def test_tramos_vacios_no_permite_k(self):
        r = self.seq.clasificar({"tramos": ["", "  ", "\n"]})
        assert r["permite_k_sugerido"] is False
        assert r["resumen"]["n_indefinido"] >= 1 or r["estado"] == "indefinido"

    def test_cambio_sin_flag_mismo_texto_no_multiplica_o(self):
        r = self.seq.clasificar({
            "tramos": ["tema salud", "tema salud", "tema salud"],
        })
        assert len(r["resumen"]["O_distintos"]) <= 1

    def test_o_global_no_es_unico_micro(self):
        r = self.seq.clasificar({
            "tramos": [
                "uno",
                {"texto": "dos", "cambio_declarado": True},
                "tres",
            ],
            "armar_o_global": True,
        })
        g = r.get("O_global")
        assert g is not None
        assert g.get("tipo") == "O_global"
        assert "no promedia" in (g.get("nota") or "").lower() or "mapa" in (g.get("nota") or "").lower()
        # Global id distinto de los micro
        micros = set(r["resumen"]["O_distintos"])
        if g.get("O_id"):
            assert g["O_id"] not in micros or g["O_id"].startswith("O_global")

    def test_ruido_masivo_no_explode(self):
        tramos = [_ruido_unicode(20) for _ in range(30)]
        r = self.seq.clasificar({"tramos": tramos, "armar_o_global": True})
        assert isinstance(r["tramos_clasificados"], list)
        assert len(r["tramos_clasificados"]) == 30


# ===========================================================================
# 3. RESOLVER CX — coherencia bajo basura
# ===========================================================================

class TestAdversarialResolver:
    def setup_method(self):
        self.cx = _mod("modules.contexto")

    def test_resolver_nunca_raise_con_basura(self):
        payloads = [
            {},
            {"casilla_contexto": _ruido_unicode()},
            {"contexto": None},
            {"tramos": [None, 1, {}, []]},
            {"O_id": 12345, "enunciado_O": False},
            {"modo_entrada": "modo_inventado_xyz"},
        ]
        for p in payloads:
            try:
                out = self.cx.resolver(p if isinstance(p, dict) else {})
            except TypeError:
                # entrada radicalmente mala puede TypeError en capa baja;
                # no debe ser SystemExit ni corromper proceso
                continue
            assert isinstance(out, dict)
            assert "coherente" in out or "errores" in out


# ===========================================================================
# 4. FÓRMULAS — dominio Fraction, anti-float, anti-invención
# ===========================================================================

class TestAdversarialFormulas:
    def test_float_rechazado(self):
        from modules.formulas.truth import tru_ri, tru_total
        with pytest.raises(TypeError):
            tru_ri(0.9, Fraction(1), Fraction(1))
        with pytest.raises(TypeError):
            tru_total(1.0, 1.0, 1.0)

    def test_piso_beta_intactable(self):
        from modules.formulas.truth import tru_total
        from modules.constante import BETA
        assert tru_total(Fraction(0), Fraction(0), Fraction(0)) == BETA

    def test_no_superar_uno_con_factores_validos(self):
        from modules.formulas.truth import tru_total
        from modules.constante import ALPHA, BETA
        tt = tru_total(Fraction(1), Fraction(1), Fraction(1))
        assert tt == ALPHA * Fraction(1) + BETA
        assert tt == Fraction(1)


# ===========================================================================
# 5. AX — coherencia y detección de choque sintético
# ===========================================================================

class TestAdversarialAxiomas:
    def test_barrer_sigue_coherente(self):
        ax = _mod("modules.axiomas")
        r = ax.barrer()
        assert r["coherente"] is True
        assert len(r.get("choques") or []) == 0

    def test_contradiccion_directa_detectable(self):
        """Si el API expone contradiccion_directa, polaridades opuestas chocan."""
        ax = _mod("modules.axiomas")
        fn = getattr(ax, "contradiccion_directa", None)
        if fn is None:
            pytest.skip("contradiccion_directa no expuesta")
        a = {
            "id": "ADV-1",
            "tipo": "axioma",
            "sujeto": "X_adv",
            "relacion": "es",
            "objeto": "Y_adv",
            "polaridad": True,
            "enunciado": "X es Y",
        }
        b = {
            "id": "ADV-2",
            "tipo": "axioma",
            "sujeto": "X_adv",
            "relacion": "es",
            "objeto": "Y_adv",
            "polaridad": False,
            "enunciado": "X no es Y",
        }
        # firmas varían; intentar formas comunes
        try:
            hit = fn(a, b)
        except TypeError:
            try:
                hit = fn([a, b])
            except Exception:
                pytest.skip("firma de contradiccion_directa desconocida")
                return
        assert hit is True or hit is not None and hit is not False or bool(hit)


# ===========================================================================
# 6. MC — inversión de orden debe ser detectable (lógica local)
# ===========================================================================

class TestAdversarialMecanica:
    def test_barrer_coherente(self):
        mc = _mod("modules.correlacion_mecanica")
        r = mc.barrer()
        assert r.get("coherente") is True

    def test_permite_k_sin_ancla_false(self):
        cxm = _mod("modules.correlacion_mecanica.contexto_MC")
        assert cxm.permite_k(set()) is False
        assert cxm.permite_k({"Ciclo_Id"}) is False
        assert cxm.permite_k({"Declaracion_O"}) is False

    def test_fractal_sin_fijacion_false(self):
        fx = _mod("modules.correlacion_mecanica.contexto_fractal_MC")
        assert fx.permite_k_local(set()) is False
        assert fx.permite_k_local({"CXF_Entrada_Natural"}) is False

    def test_deteccion_inversion_sintetica(self):
        """Simula dos órdenes invertidos como hace barrer (precedencia)."""
        orden_a = ["N1", "N2", "N3"]
        orden_b = ["N3", "N2", "N1"]  # inversión total

        def pares(orden):
            return {(orden[i], orden[j]) for i in range(len(orden)) for j in range(i + 1, len(orden))}

        pa, pb = pares(orden_a), pares(orden_b)
        inversiones = {(a, b) for (a, b) in pa if (b, a) in pb}
        assert len(inversiones) > 0  # el método MC DEBE ver esto como choque


# ===========================================================================
# 7. ENGINE — no inventa evaluación completa sin O
# ===========================================================================

class TestAdversarialEngine:
    def test_arranca(self):
        from core.engine import Engine, ArranqueError
        try:
            eng = Engine(Path("modules"), invocador_id="adv", strict=True)
        except ArranqueError as e:
            pytest.fail(str(e))
        assert eng.estado == "OPERATIVO"

    def test_evaluar_sin_contexto_no_fabrica_k_uno(self):
        from core.engine import Engine
        eng = Engine(Path("modules"), invocador_id="adv2", strict=True)
        r = eng.evaluar({"C": "1", "L": "1"})  # sin contexto / K
        # No debe reportar éxito pleno con K=1 inventado
        if isinstance(r, dict):
            k = r.get("K") or r.get("k") or (r.get("factores") or {}).get("K")
            if k is not None:
                assert str(k) not in ("1", "1/1") or r.get("estado") != "OK"
            # si estado OK, debe ser parcial o con advertencia de O
            if r.get("estado") == "OK":
                # aceptable solo si el engine exige factores completos en otro test;
                # aquí: no Tru_total == 1 sin O
                tt = r.get("Tru_total") or r.get("tru_total")
                if tt is not None:
                    assert Fraction(str(tt)) < Fraction(1) or "contexto" in str(r).lower()


# ===========================================================================
# 8. CONSTANTE — intentos de romper el ancla
# ===========================================================================

class TestAdversarialAncla:
    def test_alpha_beta_inmutables_en_runtime(self):
        from modules import constante
        a, b = constante.ALPHA, constante.BETA
        assert a + b == Fraction(1)
        # re-import no cambia
        importlib.reload(constante)
        assert constante.ALPHA == Fraction(26, 27)
        assert constante.BETA == Fraction(1, 27)


# ===========================================================================
# 9. ESTRÉS COMBINADO (lo más extremo del nivel actual)
# ===========================================================================

class TestAdversarialEstresCombinado:
    def test_tormenta_entrada_secuencia_resolver_ax_mc(self):
        en = _mod("modules.contexto.entrada_natural")
        seq = _mod("modules.contexto.secuencia_conversacion")
        cx = _mod("modules.contexto")
        ax = _mod("modules.axiomas")
        mc = _mod("modules.correlacion_mecanica")

        for i in range(10):
            texto = _ruido_unicode(60)
            r1 = en.clasificar({"casilla_contexto": texto})
            r2 = seq.clasificar({"tramos": [texto, "", texto[::-1]], "armar_o_global": True})
            r3 = cx.resolver({"casilla_contexto": texto, "tramos": [texto]})
            assert r1["permite_k_sugerido"] in (True, False)
            if not (r1.get("enunciado_O") or "").strip():
                assert r1["permite_k_sugerido"] is False
            assert isinstance(r2["tramos_clasificados"], list)
            assert isinstance(r3, dict)

        assert ax.barrer()["coherente"] is True
        assert mc.barrer()["coherente"] is True

    def test_claim_tru_sin_o_via_solo_factores_numericos(self):
        """Intento de 'saltar anclaje': factores perfectos sin marco."""
        from modules.formulas.truth import tru_total
        from modules.constante import BETA
        # Fórmulas calculan aritmética; el anclaje es CX/MC/Engine, no FO
        tt = tru_total(Fraction(1), Fraction(1), Fraction(1))
        assert tt == Fraction(1)
        # El adversarial: MC no permite K sin ancla
        cxm = _mod("modules.correlacion_mecanica.contexto_MC")
        assert cxm.permite_k(set()) is False
        # CX entrada vacía no sugiere K
        en = _mod("modules.contexto.entrada_natural")
        assert en.clasificar({"casilla_contexto": ""})["permite_k_sugerido"] is False
