"""
modules/contexto/__init__.py
============================

Rol CX — Contenedor de Contexto.

No calcula Tru_Ri ni Tru_total.
Define y vela las reglas del juego contextual.

Dos escalas:
  1. Micro  — reglas para O_context de una petición / frase / dominio.
  2. Macro  — coherencia contextual del repositorio completo
             (módulos, contratos, reportes como Omega Report).

El Engine dirige.
Este módulo solo entrega el marco y garantiza que las reglas
internas de contexto no se contradigan entre sí.

Dependencia causal: MC (correlación mecánica) marca el momento
en que el contexto puede definirse o ejecutarse.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from core.diagnostico import DiagnosticoGlobal
except Exception:
    class DiagnosticoGlobal:  # fallback silencioso
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass


_DIR = Path(__file__).parent


# ===============================================================
# UNDEFINED (valor sin evidencia contextual)
# ===============================================================
class _Undefined:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, other):
        return isinstance(other, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")


UNDEFINED = _Undefined()


def es_undefined(v: Any) -> bool:
    return v is UNDEFINED or isinstance(v, _Undefined)


class ContextoError(Exception):
    """Error de coherencia o de regla contextual."""
    pass


# ===============================================================
# CARGA DE REGLAS INTERNAS (archivos dentro de contexto/)
# ===============================================================
def _cargar_reglas() -> Dict[str, Any]:
    """
    Cada archivo .py (excepto __init__ y _*) puede declarar:
      - REGLA: dict con metadatos de la regla
      - validar(): callable que devuelve dict o lanza
    El init solo comprueba que no se contradigan entre sí.
    """
    registro: Dict[str, Any] = {}
    for archivo in sorted(_DIR.glob("*.py")):
        if archivo.name == "__init__.py" or archivo.name.startswith("_"):
            continue
        nombre = f"contexto_regla_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(nombre, archivo)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            registro[archivo.stem] = {"error": f"{type(e).__name__}: {e}"}
            continue

        meta = getattr(mod, "REGLA", None)
        validador = getattr(mod, "validar", None)

        entrada: Dict[str, Any] = {"archivo": archivo.name}
        if isinstance(meta, dict):
            entrada["regla"] = meta
        if callable(validador):
            try:
                entrada["resultado"] = validador()
            except Exception as e:
                entrada["error"] = str(e)
        if "regla" not in entrada and "resultado" not in entrada and "error" not in entrada:
            entrada["error"] = "sin REGLA ni validar()"

        registro[archivo.stem] = entrada
    return registro


def _detectar_choques_reglas(reglas: Dict[str, Any]) -> List[str]:
    """
    Choque simple: dos reglas con el mismo id o el mismo nombre
    y polaridades / enunciados incompatibles.
    Extensible cuando existan más archivos de regla.
    """
    choques: List[str] = []
    por_id: Dict[str, List[str]] = {}
    por_nombre: Dict[str, List[str]] = {}

    for clave, datos in reglas.items():
        if "error" in datos:
            continue
        regla = datos.get("regla") or {}
        rid = str(regla.get("id", "")).strip()
        nom = str(regla.get("nombre", "")).strip()
        if rid:
            por_id.setdefault(rid, []).append(clave)
        if nom:
            por_nombre.setdefault(nom, []).append(clave)

    for rid, archivos in por_id.items():
        if len(archivos) > 1:
            choques.append(f"id de regla '{rid}' repetido en {archivos}")
    for nom, archivos in por_nombre.items():
        if len(archivos) > 1:
            choques.append(f"nombre de regla '{nom}' repetido en {archivos}")

    return choques


# ===============================================================
# CONTEXTO DE REPOSITORIO (macro)
# ===============================================================
def _contexto_repositorio() -> Dict[str, Any]:
    """
    El propio repositorio es un contexto.
    Coherencia de contratos, roles y ausencia de contradicción
    entre módulos es parte del marco contextual global.
    Omega Report es un artefacto de ese contexto.
    """
    info: Dict[str, Any] = {
        "O_context": "VPSI-TRUTH / repositorio",
        "descripcion": (
            "Contexto macro: coherencia del sistema de módulos, "
            "contratos CONTENEDOR y reportes de diagnóstico."
        ),
    }

    # Constantes (CT)
    try:
        from fractions import Fraction
        from modules.constante import ALPHA, BETA
        info["constantes"] = {
            "ALPHA": str(ALPHA),
            "BETA": str(BETA),
            "valido": ALPHA + BETA == Fraction(1),
        }
    except Exception as e:
        info["constantes"] = {"error": str(e), "valido": False}

    # Axiomas (AX)
    try:
        from modules.axiomas import barrer as barrer_ax
        ia = barrer_ax()
        info["axiomas"] = {
            "coherente": ia.get("coherente", False),
            "declaraciones": ia.get("declaraciones", 0),
            "choques": len(ia.get("choques", [])),
        }
    except Exception as e:
        info["axiomas"] = {"coherente": False, "error": str(e)}

    # Mecánica (MC) — dependencia causal
    try:
        from modules.correlacion_mecanica import barrer as barrer_mc
        im = barrer_mc()
        info["mecanica"] = {
            "coherente": im.get("coherente", False),
            "choques": im.get("choques", []),
        }
    except Exception as e:
        info["mecanica"] = {"coherente": False, "error": str(e)}

    coherente = (
        info.get("constantes", {}).get("valido", False)
        and info.get("axiomas", {}).get("coherente", False)
        and info.get("mecanica", {}).get("coherente", False)
    )
    info["coherente"] = coherente
    return info


# ===============================================================
# API PRINCIPAL
# ===============================================================
def resolver(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Resuelve el contexto aplicable.

    - Sin petición → contexto de repositorio (macro).
    - Con petición → adjunta O_context declarado y valida reglas internas.

    No calcula Tru. Solo entrega el marco y su coherencia.
    """
    peticion = peticion or {}
    reglas = _cargar_reglas()
    choques_reglas = _detectar_choques_reglas(reglas)
    repo = _contexto_repositorio()

    o_ctx = peticion.get("contexto") or peticion.get("O_context") or repo.get("O_context")

    errores: List[str] = []
    if choques_reglas:
        errores.extend(choques_reglas)
    for nombre, datos in reglas.items():
        if "error" in datos:
            errores.append(f"regla '{nombre}': {datos['error']}")

    if not repo.get("coherente", False):
        errores.append("contexto de repositorio incoherente")

    coherente = (not errores) and repo.get("coherente", False)

    salida = {
        "O_context": o_ctx,
        "coherente": coherente,
        "escala": "macro" if not peticion else "micro+macro",
        "reglas_internas": {
            "total": len(reglas),
            "choques": choques_reglas,
            "detalle": reglas,
        },
        "repositorio": repo,
        "errores": errores,
        "notas": [],
    }

    if not reglas:
        salida["notas"].append(
            "sin archivos de regla internos (vacío legítimo; "
            "el init solo vela coherencia cuando existan)"
        )

    if not coherente:
        DiagnosticoGlobal.recibir_reporte(
            modulo="contexto",
            errores=[{"tipo": "error_contexto", "detalle": e} for e in errores],
        )

    return salida


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return bool(salida.get("coherente", False))


def inventario(peticion: Any = None) -> Dict[str, Any]:
    reglas = _cargar_reglas()
    return {
        "contenedor": "contexto",
        "version": "1.0",
        "rol": "CX",
        "reglas_internas": list(reglas.keys()),
        "total_reglas": len(reglas),
        "funcion": (
            "Define y vela las reglas del juego contextual. "
            "No calcula Tru. Entrega el marco para CA, AX, FO, UI y el resto."
        ),
    }


def axiomas() -> List[Dict[str, Any]]:
    """Declaraciones mínimas del propio módulo CX."""
    return [
        {
            "id": "CX-1",
            "tipo": "axioma",
            "sujeto": "contexto",
            "relacion": "precede",
            "objeto": "reglas_del_juego",
            "polaridad": True,
            "enunciado": (
                "Contexto no calcula Tru_Ri ni Tru_total; "
                "define las reglas bajo las cuales todo cálculo y juicio son posibles."
            ),
            "depende_de": [],
            "gobierna": ["contexto"],
        },
        {
            "id": "CX-2",
            "tipo": "axioma",
            "sujeto": "O_context",
            "relacion": "es_requerido_por",
            "objeto": "K",
            "polaridad": True,
            "enunciado": (
                "K es indefinido sin O_context explícito (Corolario Def-5.3.1). "
                "Contexto es la fuente de ese marco."
            ),
            "depende_de": ["Def-5.3.1"],
            "gobierna": ["K", "evaluacion"],
        },
        {
            "id": "CX-3",
            "tipo": "axioma",
            "sujeto": "reglas_internas_de_contexto",
            "relacion": "no_deben",
            "objeto": "contradecirse",
            "polaridad": True,
            "enunciado": (
                "Los archivos de regla dentro de contexto/ no pueden "
                "contradecirse entre sí; el init vela esa coherencia."
            ),
            "depende_de": [],
            "gobierna": ["contexto"],
        },
    ]


# ===============================================================
# CONTENEDOR (al final — funciones ya definidas)
# ===============================================================
CONTENEDOR = {
    "nombre": "contexto",
    "rol": "CX",
    "version": "1.0",
    "requiere": ["MC", "CT", "AX"],
    "descripcion": (
        "Contenedor de contexto. Rol CX. "
        "No calcula. Define y vela las reglas del juego contextual "
        "(micro: O_context de una petición; macro: coherencia del repositorio). "
        "Depende de MC para el momento causal de ejecución."
    ),
    "capacidades": {
        "verificar": resolver,
        "evaluar": resolver,
        "inventario": inventario,
        "axiomas": axiomas,
    },
}

__all__ = [
    "CONTENEDOR",
    "UNDEFINED",
    "es_undefined",
    "ContextoError",
    "resolver",
    "verificar_salida",
    "inventario",
    "axiomas",
]
