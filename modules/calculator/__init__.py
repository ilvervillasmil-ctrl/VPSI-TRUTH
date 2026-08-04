"""
VPSI-TRUTH --- modules/calculator/__init__.py

Rol CA: calcula factores C, L, K.
No calcula Tru_Ri ni Tru_total (eso es FO).

Contrato público de K:
  - Sin O_context / contexto → K is None  (tests + Engine histórico)
  - Con O y base nula        → UNDEFINED
  - Con O y datos            → Fraction

Versión: 2.0
Cambio principal respecto a 1.2:
  - Integra conteos.py v2.0 (anclas de inclusión + retícula + base nula).
  - Integra coherencia / logica / correlacion_k v2.0
    (C/L = UNDEFINED cuando base nula; k/r/f como Fraction).
  - Sin O → K = None (contrato público; no UNDEFINED).
  - El init sigue siendo centinela: descubre, exige APIs, reporta choques.
  - calcular() orquesta solo C, L, K; no forma Tru.
  - requiere: []  (CA no depende de CT ni FO para arrancar).
  - Preparado para leer futuras mejoras de fórmula en los submódulos
    sin reescribir el orquestador (las APIs públicas son el contrato).

El init es centinela de calculator/:
  - descubre archivos de cálculo
  - exige APIs públicas por factor
  - reporta choques / fallos de carga
  - orquesta calcular(peticion) solo sobre lo coherente
  - si metodo=operacional y faltan conteos, los produce via conteos.py
  - verifica que las anclas de base nula se respeten (barrer)
"""

from __future__ import annotations

import importlib
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ===============================================================
# Errores y UNDEFINED
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
    if v is UNDEFINED or isinstance(v, _Undefined):
        return True
    if isinstance(v, str) and v.upper() == "UNDEFINED":
        return True
    return False


VERSION = "2.0"
_DIR = Path(__file__).parent

_FACTORES_CANONICOS = ("C", "L", "K")
_ARCHIVO_FACTOR = {
    "coherencia": "C",
    "logica": "L",
    "correlacion_k": "K",
}

_CLAVES_CONTEO = (
    "compromisos",
    "contradicciones",
    "posturas",
    "reversiones",
    "afirmaciones",
    "afirmaciones_falsas",
)


# ===============================================================
# Carga de submódulos (APIs públicas)
# ===============================================================
def _importar_apis() -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """
    Importa calcular_c / calcular_l / calcular_k si existen.
    Contrato v2: cada API acepta peticion: dict y devuelve dict
    con la clave del factor (C/L/K) y meta.
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
            mod = importlib.import_module(
                "modules.calculator.{0}".format(mod_name)
            )
            fn = getattr(mod, fn_name, None)
            if not callable(fn):
                errores.append({
                    "archivo": "{0}.py".format(mod_name),
                    "error": "falta API pública callable '{0}'".format(fn_name),
                })
                continue
            apis[factor] = fn
            ver = getattr(mod, "VERSION", None)
            if ver is not None:
                apis["_{0}_version".format(factor)] = ver
        except Exception as e:
            errores.append({
                "archivo": "{0}.py".format(mod_name),
                "error": "{0}: {1}".format(type(e).__name__, e),
            })
    return apis, errores


_APIS, _ERRORES_CARGA = _importar_apis()


# ===============================================================
# Conteo (productor operacional)
# ===============================================================
def _cargar_conteos():
    """Carga conteos.py si existe. No tumba el módulo si falta."""
    try:
        mod = importlib.import_module("modules.calculator.conteos")
        extraer = getattr(mod, "extraer_conteos", None)
        inyectar = getattr(mod, "inyectar_en_peticion", None)
        verificar = getattr(mod, "verificar_conteos", None)
        version = getattr(mod, "VERSION", None)
        if callable(extraer) and callable(inyectar):
            return {
                "extraer_conteos": extraer,
                "inyectar_en_peticion": inyectar,
                "verificar_conteos": verificar if callable(verificar) else None,
                "version": version,
            }
    except Exception:
        pass
    return None


_CONTEOS = _cargar_conteos()


def _faltan_conteos(peticion: Dict[str, Any]) -> bool:
    for k in _CLAVES_CONTEO:
        if k not in peticion or peticion[k] is None:
            return True
    return False


def _asegurar_conteos(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Si metodo=operacional y faltan conteos, los produce con conteos.py.
    Si conteos.py no está cargado, deja la petición igual.
    """
    if _CONTEOS is None:
        return peticion
    meta = peticion.get("_conteos_meta")
    if isinstance(meta, dict) and meta.get("version"):
        return peticion
    if not _faltan_conteos(peticion):
        return peticion
    return _CONTEOS["inyectar_en_peticion"](peticion)


# ===============================================================
# Helpers de normalización de salida de factor
# ===============================================================
def _extraer_factor(raw: Any, clave: str) -> Any:
    """
    Normaliza la salida del submódulo v2 (dict) o v1 (Fraction | UNDEFINED).
    Devuelve Fraction | UNDEFINED | None.
    """
    if raw is None:
        return None
    if es_undefined(raw):
        return UNDEFINED
    if isinstance(raw, dict):
        val = raw.get(clave)
        if es_undefined(val):
            return UNDEFINED
        if val is None:
            return None
        if isinstance(val, Fraction):
            return val
        try:
            return Fraction(str(val))
        except Exception:
            return None
    if isinstance(raw, Fraction):
        return raw
    try:
        return Fraction(str(raw))
    except Exception:
        return None


def _notas_factor(raw: Any) -> List[str]:
    if isinstance(raw, dict):
        return list(raw.get("notas") or [])
    return []


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
    - Choque: dos stems mapeados al mismo factor
    - Presencia de conteos.py
    - Smoke de anclas:
        * C/L base nula → UNDEFINED
        * K sin O        → None  (contrato público)
    No calcula Tru. No exige valores numéricos sin petición.
    """
    errores: List[Dict[str, str]] = list(_ERRORES_CARGA)
    choques: List[str] = []
    avisos: List[str] = []
    archivos = [p.name for p in _listar_py()]

    factores_ok = [f for f in _FACTORES_CANONICOS if f in _APIS]
    for factor in _FACTORES_CANONICOS:
        if factor not in _APIS:
            errores.append({
                "archivo": "?",
                "error": "factor canónico '{0}' sin API pública cargada".format(
                    factor
                ),
            })

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

    stems_conocidos = set(_ARCHIVO_FACTOR.keys()) | {"conteos"}
    extra = [p.stem for p in _listar_py() if p.stem not in stems_conocidos]

    conteos_ok = _CONTEOS is not None
    conteos_ver = (_CONTEOS or {}).get("version")

    # ----- Smoke de anclas -----
    if all(f in _APIS for f in _FACTORES_CANONICOS) and conteos_ok:
        try:
            vacio = calcular({
                "mensaje": "",
                "contexto": None,
                "metodo": "operacional",
            })
            for factor in _FACTORES_CANONICOS:
                val = vacio.get(factor)
                if factor == "K":
                    # Contrato público: sin O → None
                    if val is not None:
                        errores.append({
                            "archivo": "correlacion_k.py / orquestador",
                            "error": (
                                "contrato público violado: sin O_context "
                                "K debió ser None y fue {0}".format(val)
                            ),
                        })
                else:
                    # Ancla AM: base nula → UNDEFINED
                    if val is not None and not es_undefined(val):
                        errores.append({
                            "archivo": "?",
                            "error": (
                                "ancla AM-D6/AM-A3 violada: base nula, "
                                "{0} debió ser UNDEFINED y fue {1}".format(
                                    factor, val
                                )
                            ),
                        })
        except Exception as e:
            avisos.append(
                "smoke de anclas no pudo ejecutarse: {0}".format(e)
            )

    versiones = {
        "C": _APIS.get("_C_version"),
        "L": _APIS.get("_L_version"),
        "K": _APIS.get("_K_version"),
        "conteos": conteos_ver,
        "orquestador": VERSION,
    }

    limpio = not errores and not choques
    return {
        "contenedor": "calculator",
        "rol": "CA",
        "version": VERSION,
        "coherente": limpio,
        "errores": errores,
        "choques": choques,
        "avisos": avisos,
        "archivos": archivos,
        "factores_api": factores_ok,
        "archivos_extra": extra,
        "conteos_disponible": conteos_ok,
        "versiones": versiones,
        "nota": (
            "conteos.py produce k/m, r/p, f/c bajo anclas AM; "
            "base nula C/L → UNDEFINED; sin O → K is None; "
            "CA no calcula Tru (FO)."
        ),
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    b = barrer()
    return {
        "contenedor": "calculator",
        "version": VERSION,
        "rol": "CA",
        "archivos": b.get("archivos"),
        "factores_api": b.get("factores_api"),
        "conteos_disponible": b.get("conteos_disponible"),
        "versiones": b.get("versiones"),
        "coherente": b.get("coherente"),
        "funcion": (
            "Calcula C, L, K bajo anclas de medición (AM). "
            "C/L UNDEFINED = base nula (AM-D6). "
            "K is None = sin O_context (contrato público / Def-5.3.1). "
            "No calcula Tru_total (FO). "
            "Si metodo=operacional y faltan conteos, los produce conteos.py. "
            "barrer = centinela de carpeta + smoke de anclas."
        ),
    }


# ===============================================================
# Cálculo (oficio principal) — solo C, L, K
# ===============================================================
def calcular(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Orquesta C, L, K vía APIs públicas de los submódulos.

    Contrato v2:
      - Si metodo=operacional y faltan conteos → conteos.inyectar_en_peticion
      - Cada factor recibe la petición completa (dict) y devuelve dict
      - Se extrae C / L / K (Fraction | UNDEFINED | None)
      - Sin O_context → K is None  (contrato público histórico)
      - No se forma Tru_Ri ni Tru_total (eso es FO)

    None / UNDEFINED = dato no disponible (legítimo), no es fallo del contenedor.
    """
    peticion = dict(peticion or {})
    metodo = str(peticion.get("metodo") or "operacional")
    errores: List[str] = []
    notas: List[str] = []
    meta_conteos = None
    detalle: Dict[str, Any] = {}

    # ----- producir conteos si hace falta (solo operacional) -----
    if metodo == "operacional":
        peticion = _asegurar_conteos(peticion)
        meta_conteos = peticion.get("_conteos_meta")
        if isinstance(meta_conteos, dict):
            notas.extend(meta_conteos.get("notas") or [])

    peticion["metodo"] = metodo

    C = L = K = None

    # ----- C -----
    fn_c = _APIS.get("C")
    if callable(fn_c):
        try:
            raw = fn_c(peticion)
            C = _extraer_factor(raw, "C")
            notas.extend(_notas_factor(raw))
            if isinstance(raw, dict):
                detalle["C"] = {
                    "m": raw.get("m"),
                    "k": raw.get("k"),
                    "ruta": raw.get("ruta"),
                    "version": raw.get("version"),
                }
        except Exception as e:
            errores.append("Error en C: {0}".format(e))
            C = None
    else:
        errores.append("API C no disponible")

    # ----- L -----
    fn_l = _APIS.get("L")
    if callable(fn_l):
        try:
            raw = fn_l(peticion)
            L = _extraer_factor(raw, "L")
            notas.extend(_notas_factor(raw))
            if isinstance(raw, dict):
                detalle["L"] = {
                    "p": raw.get("p"),
                    "r": raw.get("r"),
                    "ruta": raw.get("ruta"),
                    "version": raw.get("version"),
                }
        except Exception as e:
            errores.append("Error en L: {0}".format(e))
            L = None
    else:
        errores.append("API L no disponible")

    # ----- K -----
    # Contrato público: sin O_context → K is None.
    # Con O: se delega a correlacion_k (Fraction | UNDEFINED).
    fn_k = _APIS.get("K")
    o_ctx = (
        peticion.get("contexto")
        or peticion.get("O_context")
        or peticion.get("o_context")
    )
    if callable(fn_k):
        try:
            if o_ctx is None or (isinstance(o_ctx, str) and not str(o_ctx).strip()):
                # Contrato público histórico + tests:
                # sin O_context → K is None (no UNDEFINED).
                # Def-5.3.1 se respeta: no se inventa correspondencia.
                K = None
                notas.append(
                    "K = None (sin O_context; contrato público CA / Def-5.3.1)"
                )
                detalle["K"] = {
                    "c": None,
                    "f": None,
                    "o_presente": False,
                    "ruta": "orquestador",
                    "version": _APIS.get("_K_version"),
                }
            else:
                raw = fn_k(peticion)
                K = _extraer_factor(raw, "K")
                notas.extend(_notas_factor(raw))
                if isinstance(raw, dict):
                    detalle["K"] = {
                        "c": raw.get("c"),
                        "f": raw.get("f"),
                        "o_presente": raw.get("o_presente"),
                        "ruta": raw.get("ruta"),
                        "version": raw.get("version"),
                    }
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

    salida: Dict[str, Any] = {
        "C": C,
        "L": L,
        "K": K,
        "errores": errores,
        "notas": notas,
        "metodo": metodo,
        "version": VERSION,
        "detalle": detalle,
    }
    if meta_conteos is not None:
        salida["conteos"] = meta_conteos
    return salida


def verificar_salida(salida: Any) -> bool:
    """
    Forma mínima de salida de calcular: dict con C, L, K.
    None / UNDEFINED en un factor es legítimo
    (K sin O = None; C/L base nula = UNDEFINED).
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
    "version": VERSION,
    "requiere": [],
    "descripcion": (
        "Calcula C, L, K bajo anclas de medición (AM v1.0). "
        "C/L UNDEFINED = base nula (AM-D6 / AM-A3). "
        "K is None = sin O_context (contrato público / Def-5.3.1). "
        "No calcula Tru_Ri ni Tru_total (FO). "
        "Si metodo=operacional y faltan conteos, los produce conteos.py v2. "
        "barrer = centinela de carpeta + smoke de anclas. "
        "Las mejoras futuras de fórmula viven en los submódulos; "
        "este orquestador solo exige las APIs públicas."
    ),
    "capacidades": {
        "calcular": calcular,
        "verificar": barrer,
        "inventario": inventario,
    },
}

if _CONTEOS is not None:
    CONTENEDOR["capacidades"]["extraer_conteos"] = _CONTEOS["extraer_conteos"]
    CONTENEDOR["capacidades"]["inyectar_conteos"] = _CONTEOS["inyectar_en_peticion"]


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
    "VERSION",
]
