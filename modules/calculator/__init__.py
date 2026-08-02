"""
VPSI-TRUTH --- modules/calculator/__init__.py

Rol CA: calcula factores C, L, K.
No calcula Tru_Ri ni Tru_total (eso es FO).
Sin O_context / contexto, K queda ausente (None) — Def-5.3.1.

El init es centinela de calculator/:
  - descubre archivos de cálculo
  - exige APIs públicas por factor
  - reporta choques / fallos de carga
  - orquesta calcular(peticion) solo sobre lo coherente
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ===============================================================
# Errores y UNDEFINED (antes de importar submódulos)
# ===============================================================
class DominioError(ValueError):
    """Entrada fuera de dominio (p. ej. k > m)."""


class MetodoError(ValueError):
    """Método de cálculo no admitido."""


class _Undefined:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, other):
        return isinstance(other, _Undefined)

    def __hash__(self):
        return hash("VPSI_CA_UNDEFINED")


UNDEFINED = _Undefined()


def es_undefined(v: Any) -> bool:
    return v is UNDEFINED or isinstance(v, _Undefined)


_DIR = Path(__file__).parent

# Factores canónicos y archivo esperado (convención; barrer admite más)
_FACTORES_CANONICOS = ("C", "L", "K")
_ARCHIVO_FACTOR = {
    "coherencia": "C",
    "logica": "L",
    "correlacion_k": "K",
}


# ===============================================================
# Carga de submódulos (APIs públicas)
# ===============================================================
def _importar_apis() -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """
    Importa calcular_c / calcular_l / calcular_k si existen.
    No lanza: acumula errores para barrer().
    """
    apis: Dict[str, Any] = {}
    errores: List[Dict[str, str]] = []

    pares = (
        ("coherencia", "calcular_c", "C"),
        ("logica", "calcular_l", "L"),
        ("correlacion_k", "calcular_k", "K"),
    )
    for mod_name, fn_name, factor in pares:
        try:
            mod = importlib.import_module("modules.calculator.{0}".format(mod_name))
            fn = getattr(mod, fn_name, None)
            if not callable(fn):
                errores.append({
                    "archivo": "{0}.py".format(mod_name),
                    "error": "falta API pública callable '{0}'".format(fn_name),
                })
                continue
            apis[factor] = fn
        except Exception as e:
            errores.append({
                "archivo": "{0}.py".format(mod_name),
                "error": "{0}: {1}".format(type(e).__name__, e),
            })
    return apis, errores


_APIS, _ERRORES_CARGA = _importar_apis()


# ===============================================================
# Centinela de carpeta
# ===============================================================
def _listar_py() -> List[Path]:
    out = []
    for f in sorted(_DIR.glob("*.py")):
        if f.name == "__init__.py" or f.name.startswith("_"):
            continue
        out.append(f)
    return out


def barrer() -> Dict[str, Any]:
    """
    Centinela del módulo CA.
    - Archivos presentes
    - APIs de factores canónicos resolubles
    - Choque: dos stems mapeados al mismo factor sin regla
    No calcula Tru. No exige que C/L/K salgan numéricos sin petición.
    """
    errores: List[Dict[str, str]] = list(_ERRORES_CARGA)
    choques: List[str] = []
    archivos = [p.name for p in _listar_py()]

    # Factores cubiertos por API
    factores_ok = sorted(_APIS.keys())
    for factor in _FACTORES_CANONICOS:
        if factor not in _APIS:
            errores.append({
                "archivo": "?",
                "error": "factor canónico '{0}' sin API pública cargada".format(
                    factor
                ),
            })

    # Convención stem → factor: detectar colisión de stems distintos al mismo factor
    por_factor: Dict[str, List[str]] = {}
    for stem, factor in _ARCHIVO_FACTOR.items():
        path = _DIR / "{0}.py".format(stem)
        if path.exists():
            por_factor.setdefault(factor, []).append(stem)
    for factor, stems in por_factor.items():
        if len(stems) > 1:
            choques.append(
                "factor '{0}' reclamado por varios archivos: {1}".format(
                    factor, stems
                )
            )

    # Archivos huérfanos de convención (aviso, no tumba si no rompen API)
    stems_conocidos = set(_ARCHIVO_FACTOR.keys())
    extra = [
        p.stem for p in _listar_py()
        if p.stem not in stems_conocidos
    ]

    limpio = not errores and not choques
    return {
        "contenedor": "calculator",
        "rol": "CA",
        "coherente": limpio,
        "errores": errores,
        "choques": choques,
        "archivos": archivos,
        "factores_api": factores_ok,
        "archivos_extra": extra,
        "nota": (
            "archivos_extra son candidatos a nuevos factores; "
            "añadir convención o API antes de usarlos en calcular()"
        ),
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    b = barrer()
    return {
        "contenedor": "calculator",
        "version": "1.1",
        "rol": "CA",
        "archivos": b.get("archivos"),
        "factores_api": b.get("factores_api"),
        "coherente": b.get("coherente"),
        "funcion": (
            "Calcula C, L, K. No calcula Tru. "
            "K ausente sin contexto/O (Def-5.3.1)."
        ),
    }


# ===============================================================
# Cálculo (oficio principal)
# ===============================================================
def calcular(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Orquesta C, L, K vía APIs públicas de los submódulos.
    Devuelve Fraction | None por factor.
    None = dato no disponible (legítimo), no es fallo del contenedor.
    """
    peticion = dict(peticion or {})
    metodo = str(peticion.get("metodo") or "operacional")
    errores: List[str] = []

    C = L = K = None

    # ----- C -----
    fn_c = _APIS.get("C")
    if callable(fn_c):
        try:
            if metodo == "teorico":
                raw = fn_c(
                    descripcion=peticion.get("mensaje") or peticion.get("descripcion"),
                    metodo="teorico",
                )
            else:
                raw = fn_c(
                    compromisos=peticion.get("compromisos"),
                    contradicciones=peticion.get("contradicciones"),
                    metodo="operacional",
                )
            if not es_undefined(raw):
                C = raw if isinstance(raw, Fraction) else (
                    Fraction(str(raw)) if raw is not None else None
                )
        except Exception as e:
            errores.append("Error en C: {0}".format(e))
            C = None
    else:
        errores.append("API C no disponible")

    # ----- L -----
    fn_l = _APIS.get("L")
    if callable(fn_l):
        try:
            if metodo == "teorico":
                raw = fn_l(
                    descripcion=peticion.get("mensaje") or peticion.get("descripcion"),
                    metodo="teorico",
                )
            else:
                raw = fn_l(
                    posturas=peticion.get("posturas"),
                    reversiones=peticion.get("reversiones"),
                    metodo="operacional",
                )
            if not es_undefined(raw):
                L = raw if isinstance(raw, Fraction) else (
                    Fraction(str(raw)) if raw is not None else None
                )
        except Exception as e:
            errores.append("Error en L: {0}".format(e))
            L = None
    else:
        errores.append("API L no disponible")

    # ----- K (exige contexto / O) -----
    fn_k = _APIS.get("K")
    o_ctx = (
        peticion.get("contexto")
        or peticion.get("O_context")
        or peticion.get("o_context")
    )
    if callable(fn_k):
        try:
            if o_ctx is None:
                K = None
            elif metodo == "teorico":
                raw = fn_k(
                    descripcion=peticion.get("mensaje") or peticion.get("descripcion"),
                    o_context=o_ctx,
                    metodo="teorico",
                )
                if not es_undefined(raw):
                    K = raw if isinstance(raw, Fraction) else (
                        Fraction(str(raw)) if raw is not None else None
                    )
            else:
                raw = fn_k(
                    afirmaciones=peticion.get("afirmaciones"),
                    afirmaciones_falsas=peticion.get("afirmaciones_falsas"),
                    o_context=o_ctx,
                    metodo="operacional",
                )
                if not es_undefined(raw):
                    K = raw if isinstance(raw, Fraction) else (
                        Fraction(str(raw)) if raw is not None else None
                    )
        except Exception as e:
            errores.append("Error en K: {0}".format(e))
            K = None
    else:
        errores.append("API K no disponible")

    if errores:
        try:
            from core.diagnostico import DiagnosticoGlobal

            recibir = getattr(DiagnosticoGlobal, "recibir_reporte", None)
            if callable(recibir):
                recibir(
                    "calculator",
                    [
                        {"tipo": "error_calculo", "detalle": e}
                        for e in errores
                    ],
                )
        except Exception:
            pass

    return {"C": C, "L": L, "K": K, "errores": errores}


def verificar_salida(salida: Any) -> bool:
    """
    Forma mínima de salida de calcular: dict con C, L, K.
    None en un factor es legítimo (sobre todo K sin O).
    """
    if not isinstance(salida, dict):
        return False
    return all(k in salida for k in ("C", "L", "K"))


# ===============================================================
# CONTENEDOR (contrato — al final)
# ===============================================================
CONTENEDOR = {
    "nombre": "calculator",
    "rol": "CA",
    "version": "1.1",
    "requiere": [],
    "descripcion": (
        "Calcula C, L, K. None = dato no disponible. "
        "Sin contexto/O, K queda None (Def-5.3.1). "
        "No calcula Tru_total (FO). "
        "verificar = centinela de carpeta; calcular = oficio de factores."
    ),
    "capacidades": {
        "calcular": calcular,
        "verificar": barrer,
        "inventario": inventario,
    },
}


__all__ = [
    "CONTENEDOR",
    "UNDEFINED",
    "es_undefined",
    "DominioError",
    "MetodoError",
    "calcular",
    "barrer",
    "inventario",
    "verificar_salida",
]
