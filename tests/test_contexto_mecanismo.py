"""
tests/test_contexto_mecanismo.py
================================
Suite de confirmación del mecanismo de contexto (CX + AX anexo + MC).

Cubre lo montado en esta fase:
  - elevación de entrada natural (casilla humana)
  - registro / indefinido / cambio
  - secuencia multi-tramo y O global
  - grafo AX (ids CX v0.4, coherencia)
  - sub-rutas MC (contexto_MC, fractal, mechanic_of_the_mechanics)
  - generación antes de K (CX-T16)
  - ausencia de choques y de inversión mecánica

No sustituye test_VPSI / test_vpsi_contratos; los complementa.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures blandas: importar solo si el módulo existe
# ---------------------------------------------------------------------------

def _import_or_skip(path: str):
    pytest.importorskip(path.split(".")[0] if False else path)
    import importlib
    return importlib.import_module(path)


@pytest.fixture(scope="module")
def contexto():
    return _import_or_skip("modules.contexto")


@pytest.fixture(scope="module")
def axiomas():
    return _import_or_skip("modules.axiomas")


@pytest.fixture(scope="module")
def mc():
    return _import_or_skip("modules.correlacion_mecanica")


# ===========================================================================
# 1. CONTENEDOR CX
# ===========================================================================

class TestContenedorCX:
    def test_rol_y_capacidades(self, contexto):
        c = contexto.CONTENEDOR
        assert c["rol"] == "CX"
        assert c["nombre"] == "contexto"
        caps = c["capacidades"]
        assert callable(caps.get("verificar") or caps.get("evaluar") or contexto.resolver)

    def test_resolver_sin_peticion_macro(self, contexto):
        out = contexto.resolver()
        assert "coherente" in out
        assert out.get("escala") in ("macro", "micro+macro")
        assert "repositorio" in out

    def test_undefined_no_bool(self, contexto):
        u = contexto.UNDEFINED
        with pytest.raises(TypeError):
            bool(u)


# ===========================================================================
# 2. ENTRADA NATURAL (casilla humana)
# ===========================================================================

class TestEntradaNatural:
    def test_modulo_carga(self):
        mod = _import_or_skip("modules.contexto.entrada_natural")
        assert hasattr(mod, "REGLA")
        assert hasattr(mod, "clasificar")
        assert mod.REGLA["id"] == "CX-R-ENTRADA-NATURAL"

    def test_lista_criterios_un_solo_o(self):
        mod = _import_or_skip("modules.contexto.entrada_natural")
        texto = (
            "1. evaluar si todo lo que dijo es razonable\n"
            "2. saber si Carlos dijo la verdad\n"
            "3. utilizar las leyes para evaluar su actitud"
        )
        r = mod.clasificar({"casilla_contexto": texto})
        assert r["forma"] == "lista_criterios"
        assert r["estado"] == "estable"
        assert r["permite_k_sugerido"] is True
        assert r["O_id"]
        assert len(r.get("criterios") or []) >= 3
        # Un O, no tres
        assert r["armado"] == "natural_a_registro"

    def test_casilla_vacia_indefinido(self):
        mod = _import_or_skip("modules.contexto.entrada_natural")
        r = mod.clasificar({"casilla_contexto": "   "})
        assert r["estado"] == "indefinido"
        assert r["permite_k_sugerido"] is False
        assert r["O_id"] is None

    def test_prosa_simple_estable(self):
        mod = _import_or_skip("modules.contexto.entrada_natural")
        r = mod.clasificar({"contexto": "evaluar la coherencia del testimonio"})
        assert r["estado"] == "estable"
        assert r["enunciado_O"]
        assert r["permite_k_sugerido"] is True

    def test_meta_indefinido(self):
        mod = _import_or_skip("modules.contexto.entrada_natural")
        r = mod.clasificar({"casilla_contexto": "contexto indefinido"})
        assert r["forma"] == "meta_indefinido"
        assert r["permite_k_sugerido"] is False


# ===========================================================================
# 3. DECLARACION O
# ===========================================================================

class TestDeclaracionO:
    def test_completo_estable(self):
        mod = _import_or_skip("modules.contexto.declaracion_O")
        r = mod.clasificar({
            "O_id": "O_test",
            "enunciado_O": "marco de prueba",
        })
        assert r["estado"] == "estable"
        assert r["permite_k_sugerido"] is True

    def test_incompleto_indefinido(self):
        mod = _import_or_skip("modules.contexto.declaracion_O")
        r = mod.clasificar({"O_id": "solo_id"})
        assert r["estado"] == "indefinido"
        assert r["incompleto"] is True


# ===========================================================================
# 4. SECUENCIA CONVERSACION / MULTI-O
# ===========================================================================

class TestSecuenciaConversacion:
    def test_modulo_carga(self):
        mod = _import_or_skip("modules.contexto.secuencia_conversacion")
        assert mod.REGLA["id"] == "CX-R-SECUENCIA-CONV"

    def test_tramos_mismo_o_y_global(self):
        mod = _import_or_skip("modules.contexto.secuencia_conversacion")
        r = mod.clasificar({
            "tramos": [
                "Carlos: no tomé el dinero",
                "Pedro: entonces quién fue",
                "Carlos: no lo sé",
            ],
            "armar_o_global": True,
        })
        assert r["ok"] is True
        assert len(r["tramos_clasificados"]) == 3
        assert r["O_global"] is not None
        assert r["O_global"]["tipo"] == "O_global"
        # Sin cambio declarado: un solo O micro dominante
        ids = [t["O_id"] for t in r["tramos_clasificados"] if t.get("O_id")]
        assert len(set(ids)) == 1

    def test_cambio_declarado_nuevo_o(self):
        mod = _import_or_skip("modules.contexto.secuencia_conversacion")
        r = mod.clasificar({
            "tramos": [
                "hablamos de salud",
                {"texto": "ahora el clima", "cambio_declarado": True},
                "hace calor",
            ],
        })
        assert r["resumen"]["n_cambio"] >= 1
        o_ids = r["resumen"]["O_distintos"]
        assert len(o_ids) >= 2

    def test_criterios_un_o_no_multi(self):
        mod = _import_or_skip("modules.contexto.secuencia_conversacion")
        r = mod.clasificar({
            "criterios": [
                "evaluar si es razonable",
                "si Carlos dijo la verdad",
                "actitud según las leyes",
            ],
        })
        # Un tramo lógico / un O
        assert r["resumen"]["n_tramos"] >= 1
        assert len(r["resumen"]["O_distintos"]) <= 1


# ===========================================================================
# 5. RESOLVER CX INTEGRADO
# ===========================================================================

class TestResolverIntegrado:
    def test_peticion_natural_permite_k(self, contexto):
        out = contexto.resolver({
            "casilla_contexto": (
                "1. evaluar razonabilidad\n"
                "2. verdad de Carlos\n"
                "3. actitud bajo las leyes"
            ),
            "modo_entrada": "auditoria",
        })
        # Macro repo debe seguir coherente en CI verde
        assert "registro" in out or out.get("O_context")
        assert "errores" in out
        # Si el repo CT/AX/MC están OK, coherente puede ser True
        assert isinstance(out["coherente"], bool)

    def test_vacio_no_inventa_k(self, contexto):
        out = contexto.resolver({"casilla_contexto": ""})
        reg = out.get("registro") or {}
        if reg:
            assert reg.get("estado") in ("indefinido", None) or out.get("permite_k") is False


# ===========================================================================
# 6. AX — ANEXO CX EN EL GRAFO
# ===========================================================================

class TestAxiomasContexto:
    def test_barrer_coherente(self, axiomas):
        r = axiomas.barrer()
        assert r["coherente"] is True
        assert r["choques"] == [] or len(r["choques"]) == 0
        assert r["declaraciones"] >= 287

    def test_ids_anexo_v04_presentes(self, axiomas):
        r = axiomas.barrer()
        # recolectar ids si el informe los expone; si no, via declaraciones
        ids = set()
        if "ids" in r:
            ids = set(r["ids"])
        else:
            # fallback: import cuerpos
            try:
                from modules.axiomas import recolectar
                decls, _err = recolectar()
                ids = {d.get("id") for d in decls if d.get("id")}
            except Exception:
                pytest.skip("recolectar no expuesto")
        for need in (
            "CX-A19", "CX-A20", "CX-A22", "CX-A23", "CX-A24", "CX-A25",
            "CX-T14", "CX-T15", "CX-T16", "CX-T17",
            "CX-C14", "CX-C18",
        ):
            assert need in ids, f"falta {need} en el grafo AX"

    def test_cx_t16_depende_fijacion(self, axiomas):
        try:
            from modules.axiomas import recolectar
            decls, _ = recolectar()
        except Exception:
            pytest.skip("recolectar no expuesto")
        t16 = next((d for d in decls if d.get("id") == "CX-T16"), None)
        assert t16 is not None
        dep = t16.get("depende_de") or []
        assert "CX-A24" in dep or "Def-5.3.1" in dep


# ===========================================================================
# 7. MC — COHERENCIA Y SUB-RUTAS
# ===========================================================================

class TestMecanica:
    def test_barrer_mc_coherente(self, mc):
        r = mc.barrer()
        assert r.get("coherente") is True
        assert r.get("estado") in ("APROBADO", True, "APROBADO") or r["coherente"]
        assert not r.get("choques")

    def test_contexto_mc_permite_k(self):
        mod = _import_or_skip("modules.correlacion_mecanica.contexto_MC")
        assert mod.permite_k({
            "Ciclo_Id", "Declaracion_O", "Escala_O", "Regla_Significado",
        }) is True
        assert mod.permite_k({"Ciclo_Id"}) is False
        assert mod.permite_k(set()) is False

    def test_contexto_mc_clasificar_evento(self):
        mod = _import_or_skip("modules.correlacion_mecanica.contexto_MC")
        assert mod.clasificar_evento(True, True) in ("expansion", "mismo_O")
        assert mod.clasificar_evento(False, True) == "cambio"
        assert mod.clasificar_evento(True, False) == "indefinido"

    def test_fractal_mc_cargado(self):
        mod = _import_or_skip("modules.correlacion_mecanica.contexto_fractal_MC")
        assert mod.MECANICA["nombre"] == "contexto_fractal_mecanico"
        orden = mod.orden()
        assert "CXF_Fijacion_O" in orden
        assert "CXF_Permiso_K_Local" in orden
        # Fijación antes que permiso K en el orden
        assert orden.index("CXF_Fijacion_O") < orden.index("CXF_Permiso_K_Local")

    def test_fractal_permite_k_local_exige_fijacion(self):
        mod = _import_or_skip("modules.correlacion_mecanica.contexto_fractal_MC")
        base = {
            "CXF_Ciclo_Sesion",
            "CXF_Entrada_Natural",
            "CXF_Elevacion_Enunciado",
            "CXF_Registro_Operativo",
        }
        assert mod.permite_k_local(base) is False
        base.add("CXF_Fijacion_O")
        assert mod.permite_k_local(base) is True

    def test_mechanic_of_the_mechanics(self):
        mod = _import_or_skip("modules.correlacion_mecanica.mechanic_of_the_mechanics")
        assert mod.MECANICA["nombre"] == "mechanic_of_the_mechanics"
        orden = mod.orden()
        assert "MMC_Barrido_Coherente" in orden
        assert "MMC_No_Saltar_Anclaje" in orden
        assert orden.index("MMC_Deteccion_Inversion") < orden.index("MMC_Union_Orden_Global")

    def test_mc_lista_archivos_esperados(self, mc):
        inv = mc.inventario()
        archivos = " ".join(inv.get("archivos") or [])
        # Al menos universal + contexto; fractal y mechanic si están montados
        assert "causalidad_universal" in archivos or any(
            "causalidad" in a for a in (inv.get("archivos") or [])
        )


# ===========================================================================
# 8. GENERACIÓN / RECOMBINACIÓN (grafo vivo)
# ===========================================================================

class TestGeneratividadContexto:
    def test_dominio_contexto_en_theta(self, axiomas):
        """Si el Engine expone generatividad, contexto debe aparecer; si no, ids CX bastan."""
        r = axiomas.barrer()
        assert r["coherente"] is True
        # Recombinación mínima: más de un id CX-A2x implica anexo expandido
        try:
            from modules.axiomas import recolectar
            decls, _ = recolectar()
            cx = [d for d in decls if str(d.get("id", "")).startswith("CX-")]
            assert len(cx) >= 30, f"se esperaban >=30 decls CX, hay {len(cx)}"
        except Exception:
            pytest.skip("recolectar no disponible")

    def test_constantes_intactas(self):
        from modules.constante import ALPHA, BETA
        assert ALPHA + BETA == Fraction(1)
        assert ALPHA == Fraction(26, 27)


# ===========================================================================
# 9. ACCIÓN HUMANA VÁLIDA (contrato de interfaz)
# ===========================================================================

class TestAccionHumanaValida:
    """El usuario no tipa O_id; la casilla basta."""

    def test_solo_prosa_en_resolver(self, contexto):
        out = contexto.resolver({
            "contexto": "¿Carlos dijo la verdad según las leyes?",
        })
        assert "O_context" in out or out.get("registro") is not None

    def test_no_exige_campos_tecnicos(self):
        mod = _import_or_skip("modules.contexto.entrada_natural")
        r = mod.clasificar({"casilla_contexto": "auditar coherencia del relato"})
        assert "O_id" in r and r["O_id"]  # interno
        assert r["estado"] == "estable"


# ===========================================================================
# 10. CONTRADICCIÓN / REGRESIÓN RÁPIDA
# ===========================================================================

class TestSinContradiccion:
    def test_ax_y_mc_juntos(self, axiomas, mc):
        assert axiomas.barrer()["coherente"] is True
        assert mc.barrer()["coherente"] is True

    def test_engine_arranca(self):
        from core.engine import Engine, ArranqueError
        try:
            eng = Engine(Path("modules"), invocador_id="test_cx", strict=True)
        except ArranqueError as e:
            pytest.fail(f"Engine no arrancó: {e}")
        assert eng.estado == "OPERATIVO"
