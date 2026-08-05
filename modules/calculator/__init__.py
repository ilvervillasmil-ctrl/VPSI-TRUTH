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
  - si metodo=operacional y faltan conteos, los produce via conteos.py
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

# Claves que la ruta operacional exige
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
# Conteo (productor operacional)
# ===============================================================
def _cargar_conteos():
    """Carga conteos.py si existe. No tumba el módulo si falta."""
    try:
        mod = importlib.import_module("modules.calculator.conteos")
        extraer = getattr(mod, "extraer_conteos", None)
        inyectar = getattr(mod, "inyectar_en_peticion", None)
        verificar = getattr(mod, "verificar_conteos", None)
        if callable(extraer) and callable(inyectar):
            return {
                "extraer_conteos": extraer,
                "inyectar_en_peticion": inyectar,
                "verificar_conteos": verificar if callable(verificar) else None,
            }
    except Exception:
        pass
    return None


_CONTEOS = _cargar_conteos()


# ===============================================================
# Ids de escala (lectura — no cambia la lógica de C/L/K)
# ===============================================================
# Mapa en escalas_ids.py (y TT si existe). CA lee los ids para saber
# qué recorte pide el ciclo (sujeto, frase, conversación, átomo, repo).
# El cálculo de factores sigue siendo el mismo: conteos + C/L/K.
# Tru_Ri / Tru_total siguen en FO.

def _cargar_escalas_ids():
    try:
        mod = importlib.import_module("modules.calculator.escalas_ids")
        ids_fn = getattr(mod, "ids", None)
        por_id = getattr(mod, "por_id", None)
        version = getattr(mod, "VERSION", None)
        if callable(ids_fn):
            return {
                "ids": ids_fn,
                "por_id": por_id if callable(por_id) else None,
                "version": version,
            }
    except Exception:
        pass
    return None


_ESCALAS = _cargar_escalas_ids()


def _leer_ids_tt():
    try:
        mod = importlib.import_module("modules.tru_totales")
        for nombre in ("ids", "categorias"):
            fn = getattr(mod, nombre, None)
            if not callable(fn):
                continue
            out = fn()
            if not isinstance(out, list):
                continue
            ids = []
            for item in out:
                if isinstance(item, str) and item.strip():
                    ids.append(item.strip().lower())
                elif isinstance(item, dict) and item.get("id"):
                    ids.append(str(item["id"]).strip().lower())
            return [i for i in ids if i]
    except Exception:
        pass
    return []


def leer_ids_escala():
    """Todos los ids de escala que CA puede reconocer para el pedido."""
    ids_local = []
    origenes = []
    if _ESCALAS is not None:
        try:
            ids_local = list(_ESCALAS["ids"]())
            origenes.append("escalas_ids")
        except Exception:
            pass
    ids_tt = _leer_ids_tt()
    if ids_tt:
        origenes.append("tru_totales")
    unidos = []
    vistos = set()
    for i in list(ids_local) + list(ids_tt):
        k = str(i).strip().lower()
        if k and k not in vistos:
            vistos.add(k)
            unidos.append(k)
    return {
        "ids": unidos,
        "n": len(unidos),
        "origenes": origenes,
        "disponible": bool(unidos),
    }


def _id_escala_pedido(peticion):
    for clave in ("escala_id", "categoria_tru", "id_escala", "escala"):
        v = peticion.get(clave)
        if v is not None and str(v).strip():
            return str(v).strip().lower()
    return None




def _faltan_conteos(peticion: Dict[str, Any]) -> bool:
    """True si falta alguna clave que la ruta operacional necesita."""
    for k in _CLAVES_CONTEO:
        if k not in peticion or peticion[k] is None:
            return True
    return False


def _asegurar_conteos(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Si metodo=operacional y faltan conteos, los produce con conteos.py.
    Si conteos.py no está cargado, deja la petición igual (CA devolverá None).
    """
    if _CONTEOS is None:
        return peticion
    if not _faltan_conteos(peticion):
        return peticion
    inyectar = _CONTEOS["inyectar_en_peticion"]
    return inyectar(peticion)


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
    - Presencia de conteos.py (productor operacional)
    No calcula Tru. No exige que C/L/K salgan numéricos sin petición.
    """
    errores: List[Dict[str, str]] = list(_ERRORES_CARGA)
    choques: List[str] = []
    archivos = [p.name for p in _listar_py()]

    factores_ok = sorted(_APIS.keys())
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

    stems_conocidos = set(_ARCHIVO_FACTOR.keys()) | {"conteos", "escalas_ids"}
    extra = [
        p.stem for p in _listar_py()
        if p.stem not in stems_conocidos
    ]

    conteos_ok = _CONTEOS is not None
    ids_info = leer_ids_escala()

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
        "conteos_disponible": conteos_ok,
        "escalas_ids_disponible": _ESCALAS is not None,
        "ids_escala": ids_info,
        "nota": (
            "conteos.py produce k/m, r/p, f/c para la ruta operacional; "
            "ids_escala = sujeto/frase/conversacion/atomo/repo leidos del mapa; "
            "CA calcula C/L/K; Tru en FO; archivos_extra = candidatos"
        ),
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    b = barrer()
    return {
        "contenedor": "calculator",
        "version": "1.2",
        "rol": "CA",
        "archivos": b.get("archivos"),
        "factores_api": b.get("factores_api"),
        "conteos_disponible": b.get("conteos_disponible"),
        "escalas_ids_disponible": b.get("escalas_ids_disponible"),
        "ids_escala": b.get("ids_escala"),
        "coherente": b.get("coherente"),
        "funcion": (
            "Calcula C, L, K. No calcula Tru (FO). "
            "K ausente sin contexto/O (Def-5.3.1). "
            "Si metodo=operacional y faltan conteos, los produce conteos.py. "
            "Lee todos los ids de escala (sujeto, frase, conversacion, atomo, repo) "
            "para el pedido; el recorte del material lo trae quien orquesta."
        ),
    }


# ===============================================================
# Cálculo (oficio principal)
# ===============================================================
def calcular(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Orquesta C, L, K vía APIs públicas de los submódulos.

    Si metodo=operacional (default) y faltan las claves de conteo,
    intenta producirlas con conteos.py antes de llamar a los factores.

    Devuelve Fraction | None por factor.
    None = dato no disponible (legítimo), no es fallo del contenedor.
    """
    peticion = dict(peticion or {})
    metodo = str(peticion.get("metodo") or "operacional")
    errores: List[str] = []
    meta_conteos = None

    # ----- id de escala del pedido (lectura; no cambia C/L/K) -----
    escala_id = _id_escala_pedido(peticion)
    escala_meta = None
    if escala_id:
        inv = leer_ids_escala()
        conocido = escala_id in (inv.get("ids") or [])
        desc = None
        if _ESCALAS and callable(_ESCALAS.get("por_id")):
            try:
                desc = _ESCALAS["por_id"](escala_id)
            except Exception:
                desc = None
        escala_meta = {
            "escala_id": escala_id,
            "conocido": conocido,
            "ids_disponibles": list(inv.get("ids") or []),
        }
        if isinstance(desc, dict):
            escala_meta["material"] = desc.get("material")
            escala_meta["repetir_por"] = desc.get("repetir_por")
            escala_meta["nombre"] = desc.get("nombre")

    # ----- producir conteos si hace falta (solo operacional) -----
    if metodo == "operacional":
        peticion = _asegurar_conteos(peticion)
        meta_conteos = peticion.get("_conteos_meta")

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

    salida: Dict[str, Any] = {
        "C": C,
        "L": L,
        "K": K,
        "errores": errores,
        "metodo": metodo,
    }
    if meta_conteos is not None:
        salida["conteos"] = meta_conteos
    if escala_meta is not None:
        salida["escala"] = escala_meta
    return salida


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
    "version": "1.2",
    "requiere": [],
    "descripcion": (
        "Calcula C, L, K. None = dato no disponible. "
        "Sin contexto/O, K queda None (Def-5.3.1). "
        "No calcula Tru_total (FO). "
        "Si metodo=operacional y faltan conteos, los produce conteos.py. "
        "Lee ids de escala (sujeto, frase, conversacion, atomo, repo) del mapa. "
        "verificar = centinela de carpeta; calcular = oficio de factores C/L/K."
    ),
    "capacidades": {
        "calcular": calcular,
        "verificar": barrer,
        "inventario": inventario,
        "leer_ids_escala": leer_ids_escala,
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
    "leer_ids_escala",
    "verificar_salida",
]
