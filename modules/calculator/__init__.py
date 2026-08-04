"""
VPSI-TRUTH --- modules/calculator/__init__.py

Rol CA: calcula factores C, L, K.
No calcula Tru_Ri ni Tru_total (eso es FO).
Sin O_context / contexto, K queda UNDEFINED (Def-5.3.1).

Versión: 2.0
Cambio principal respecto a 1.2:
  - Integra conteos.py v2.0 (anclas de inclusión + retícula + base nula).
  - Integra coherencia / logica / correlacion_k v2.0
    (C/L/K = UNDEFINED cuando base nula; k/r/f como Fraction).
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
            # Leer versión del submódulo si existe (para auditoría)
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
    # Si ya hay meta de conteos v2, no regenerar
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
    - Smoke de anclas: base nula debe producir UNDEFINED en C/L/K
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

    # ----- Smoke de anclas (base nula → UNDEFINED) -----
    if all(f in _APIS for f in _FACTORES_CANONICOS) and conteos_ok:
        try:
            vacio = calcular({"mensaje": "", "contexto": None, "metodo": "operacional"})
            for factor in _FACTORES_CANONICOS:
                val = vacio.get(factor)
                # K sin O también debe ser UNDEFINED/None
                if factor == "K":
                    if val is not None and not es_undefined(val):
                        errores.append({
                            "archivo": "correlacion_k.py",
                            "error": (
                                "ancla Def-5.3.1 violada: sin O_context "
                                "K debió ser UNDEFINED/None y fue {0}".format(val)
                            ),
                        })
                else:
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

    # Versiones de submódulos
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
            "base nula → UNDEFINED; sin O → K UNDEFINED; "
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
            "UNDEFINED = base nula o sin O (Def-5.3.1 / AM-D6). "
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

    # Asegurar que metodo viaje dentro de la petición
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

    # ----- K (exige contexto / O; sin él → UNDEFINED) -----
    fn_k = _APIS.get("K")
    o_ctx = (
        peticion.get("contexto")
        or peticion.get("O_context")
        or peticion.get("o_context")
    )
    if callable(fn_k):
        try:
            # Aun sin O dejamos que correlacion_k decida (devuelve UNDEFINED)
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
            if o_ctx is None and not es_undefined(K) and K is not None:
                # Defensa extra del orquestador (Def-5.3.1)
                K = UNDEFINED
                notas.append(
                    "K forzado a UNDEFINED por orquestador: O_context ausente "
                    "(Def-5.3.1)"
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
    None / UNDEFINED en un factor es legítimo (sobre todo K sin O,
    o base nula en C/L).
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
        "UNDEFINED = base nula (AM-D6) o sin O_context (Def-5.3.1). "
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

# Exponer oficio de conteos solo si el archivo cargó
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
