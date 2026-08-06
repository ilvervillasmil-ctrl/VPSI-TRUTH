"""
VPSI-TRUTH  ---  diagnostics/evidencia.py

Depositario unico de evidencia de evaluacion.

======================================================================
Omega no evalua: solo lee diagnostics/evaluaciones.json. Quien evalua
deposita aqui.

Por que existe este archivo:

  El paso "Auditoria estructural de contratos" del CI escribia
  evaluaciones.json con write_text(), y corre DESPUES de "Run tests".
  Cualquier evidencia depositada por un test quedaba pisada antes de
  que Omega la leyera.

  Este depositario FUSIONA por origen en vez de sobrescribir. Cada
  productor de evidencia (tests, auditoria de contratos, Engine)
  conserva la suya, y Omega las ve todas.

Un solo escritor, no dos.

Contrato de conservacion (inviolable):
  - No reconstruye registros.
  - No elimina claves del body ni de resultado.
  - No interpreta sujetos / tru / factores.
  - Solo etiqueta origen y rehace secuencia global.
  - deepcopy de cada registro recibido → disco.

Version:
  1.0  write_text plano (pisaba evidencia)
  1.1  fusion por origen + normalizacion de origen + paquete diagnostics
  1.2  deepcopy + conservacion estructural del resultado (sujetos, etc.)
======================================================================
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================

DIAGNOSTICS_DIR = Path(__file__).resolve().parent
RUTA = DIAGNOSTICS_DIR / "evaluaciones.json"

TIPO = "evidencia_evaluacion"
VERSION = "1.2"

_ORIGEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-.]{0,63}$")


def _normalizar_origen(origen: Any) -> str:
    """
    Exige un identificador estable.
    Rechaza vacio, comas (romperian la lista de origenes) y basura.
    """
    if origen is None:
        raise ValueError("depositar() exige un origen declarado")
    s = str(origen).strip()
    if not s:
        raise ValueError("origen no puede ser vacio")
    if "," in s:
        raise ValueError(
            "origen no puede contener comas (se usa como separador de lista)"
        )
    if not _ORIGEN_RE.match(s):
        raise ValueError(
            "origen debe ser identificador simple "
            "(letras/digitos/_/-/., max 64 chars): {0!r}".format(s)
        )
    return s


# ===============================================================
# SEGMENTO 2 --- LECTURA
# ===============================================================

def leer() -> Dict[str, Any]:
    """Devuelve el documento actual, o uno vacio si no existe o no es legible."""
    vacio: Dict[str, Any] = {
        "tipo": TIPO,
        "version": VERSION,
        "origen": None,
        "origenes": [],
        "n": 0,
        "resultados": [],
    }
    if not RUTA.exists():
        return vacio
    try:
        doc = json.loads(RUTA.read_text(encoding="utf-8"))
    except Exception:
        return vacio
    if not isinstance(doc, dict) or not isinstance(doc.get("resultados"), list):
        return vacio
    return doc


def _con_origen(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Etiqueta las entradas que no traen origen con el del documento.
    Copia profunda de cada fila para no compartir refs con el doc en memoria.
    """
    heredado = doc.get("origen") or "desconocido"
    if isinstance(heredado, str) and "," in heredado:
        heredado = "desconocido"
    filas: List[Dict[str, Any]] = []
    for r in doc.get("resultados", []):
        if not isinstance(r, dict):
            continue
        fila = deepcopy(r)
        if not fila.get("origen"):
            fila["origen"] = heredado
        filas.append(fila)
    return filas


def resultados_de(origen: str) -> List[Dict[str, Any]]:
    """Lo depositado por un origen concreto."""
    origen = _normalizar_origen(origen)
    return [r for r in _con_origen(leer()) if r.get("origen") == origen]


# ===============================================================
# SEGMENTO 3 --- DEPOSITO
# ===============================================================

def _conservar_registro(
    r: Dict[str, Any],
    origen: str,
    invocador_id: Optional[str],
) -> Dict[str, Any]:
    """
    Copia profunda del registro tal cual.
    Solo anade/asegura 'origen' e invocador_id si falta.
    No reconstruye resultado. No borra sujetos/n_sujetos/tru/factores.
    """
    fila = deepcopy(r)
    fila["origen"] = origen
    if invocador_id is not None:
        fila.setdefault("invocador_id", invocador_id)
    return fila


def depositar(
    resultados: List[Dict[str, Any]],
    origen: str,
    invocador_id: Optional[str] = None,
    estado_engine: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Funde `resultados` en evaluaciones.json bajo la etiqueta `origen`.

    Lo de otros origenes se conserva. Lo del mismo origen se reemplaza.

    Conservacion estructural:
      registro recibido (con resultado.sujetos, n_sujetos, tru_*, ...)
      se escribe igual; solo se etiqueta origen y se reenumera secuencia.

    La numeracion `secuencia` se rehace sobre el documento completo
    (Omega imprime "seq k/n" global).
    """
    origen = _normalizar_origen(origen)

    doc = leer()
    previos = [r for r in _con_origen(doc) if r.get("origen") != origen]

    nuevos: List[Dict[str, Any]] = []
    for r in resultados or []:
        if not isinstance(r, dict):
            continue
        nuevos.append(_conservar_registro(r, origen, invocador_id))

    fusionados = previos + nuevos
    for i, r in enumerate(fusionados, 1):
        r["secuencia"] = i

    origenes = sorted({
        str(r.get("origen"))
        for r in fusionados
        if isinstance(r, dict) and r.get("origen")
    })

    salida = {
        "tipo": TIPO,
        "version": VERSION,
        "origen": ", ".join(origenes) if origenes else None,
        "origenes": origenes,
        "invocador_id": (
            invocador_id if invocador_id is not None else doc.get("invocador_id")
        ),
        "estado_engine": (
            estado_engine if estado_engine is not None else doc.get("estado_engine")
        ),
        "n": len(fusionados),
        "resultados": fusionados,
    }

    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    RUTA.write_text(
        json.dumps(salida, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return salida


def depositar_desde_engine(
    eng: Any,
    origen: str,
    desde: int = 0,
) -> Dict[str, Any]:
    """
    Toma lo que el Engine acumulo en resultados_evaluacion y lo deposita.

    `desde` permite depositar solo lo producido a partir de un indice,
    para no arrastrar evaluaciones de otra fase de la misma corrida.
    """
    if hasattr(eng, "get_resultados_evaluacion"):
        evals = list(eng.get_resultados_evaluacion() or [])
    else:
        evals = list(getattr(eng, "resultados_evaluacion", []) or [])

    if desde < 0:
        desde = 0

    return depositar(
        evals[desde:],
        origen=origen,
        invocador_id=getattr(eng, "invocador_id", None),
        estado_engine=getattr(eng, "estado", None),
    )


# ===============================================================
# SEGMENTO 4 --- LIMPIEZA
# ===============================================================

def limpiar(origen: Optional[str] = None) -> Dict[str, Any]:
    """
    Sin argumento vacia el documento. Con origen, retira solo lo de ese
    origen y conserva el resto.
    """
    doc = leer()
    if origen is None:
        quedan: List[Dict[str, Any]] = []
    else:
        origen = _normalizar_origen(origen)
        quedan = [r for r in _con_origen(doc) if r.get("origen") != origen]
    return _escribir(quedan, doc)


def _escribir(
    resultados: List[Dict[str, Any]],
    doc: Dict[str, Any],
) -> Dict[str, Any]:
    # copia profunda para no mutar entradas vivas del caller
    filas = [deepcopy(r) for r in resultados if isinstance(r, dict)]
    for i, r in enumerate(filas, 1):
        r["secuencia"] = i
    origenes = sorted({
        str(r.get("origen"))
        for r in filas
        if isinstance(r, dict) and r.get("origen")
    })
    salida = {
        "tipo": TIPO,
        "version": VERSION,
        "origen": ", ".join(origenes) if origenes else None,
        "origenes": origenes,
        "invocador_id": doc.get("invocador_id"),
        "estado_engine": doc.get("estado_engine"),
        "n": len(filas),
        "resultados": filas,
    }
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    RUTA.write_text(
        json.dumps(salida, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return salida


# ===============================================================
# ZONA DE ANEXO
# ===============================================================

__all__ = [
    "TIPO",
    "VERSION",
    "RUTA",
    "leer",
    "resultados_de",
    "depositar",
    "depositar_desde_engine",
    "limpiar",
]
