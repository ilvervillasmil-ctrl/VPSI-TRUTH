"""
VPSI-TRUTH --- modules/correlacion_mecanica/__init__.py

Contenedor de mecánica. Rol MC.

Este módulo es el filtro de coherencia mecánica.
- Lee los archivos en su directorio.
- Calcula la mecánica resultante de lo que declaran.
- Comprueba que no se contradigan entre sí.

No exige. No dispone. No ordena. No completa lo que falte.
Si dos archivos colisionan sobre un mismo nodo, el paso se bloquea y el filtro
reporta exactamente los identificadores en desacuerdo.
"""

from pathlib import Path
import importlib.util
import sys
from typing import Dict, List, Any, Tuple, Optional

# ===============================================================
# CONTENEDOR
# ===============================================================
CONTENEDOR = {
    "nombre": "correlacion_mecanica",
    "rol": "MC",
    "version": "1.0",
    "requiere": [],
}

# ===============================================================
# CONSTANTES DEL MÓDULO
# ===============================================================
_DIR = Path(__file__).parent  # Directorio donde están los archivos de mecánica

# Estados posibles del informe
APROBADO = "APROBADO"
RECHAZADO = "RECHAZADO"

# ===============================================================
# DECLARACIONES DEL FILTRO (Axiomas internos de la mecánica)
# ===============================================================
DECLARACIONES = [
    {
        "id": "CORR_SEQ_01",
        "tipo": "axioma",
        "sujeto": "mecanica_declarada",
        "relacion": "se_lee_en",
        "objeto": "orden_nativo",
        "polaridad": True,
        "enunciado": (
            "Principio de Secuencia Transversal: Los objetos de la carpeta "
            "se leen en su orden nativo para verificar que la transición "
            "entre estados cumpla la continuidad causal."
        ),
    },
    {
        "id": "CORR_SEQ_02",
        "tipo": "axioma",
        "sujeto": "colision_sobre_un_nodo",
        "relacion": "permite_el_paso",
        "objeto": "mecanica",
        "polaridad": False,
        "enunciado": (
            "Criterio de No Contradicción Cruzada: Si dos declaraciones de "
            "archivos distintos colisionan sobre el mismo nodo, el paso se "
            "bloquea y se reportan los identificadores en desacuerdo."
        ),
    },
]

# ===============================================================
# FUNCIONES PRINCIPALES
# ===============================================================
def axiomas() -> List[Dict[str, Any]]:
    """
    Devuelve las declaraciones axiomáticas del módulo para el barrido general.
    Estas declaraciones son internas y definen las reglas de la mecánica.
    """
    return DECLARACIONES

# ===============================================================
# LECTURA DE ARCHIVOS EN ORDEN NATIVO
# ===============================================================
def _leer() -> Dict[str, Any]:
    """
    Recoge lo que cada archivo declara en MECANICA.
    No exige forma: se lee lo que hay.
    """
    hallado = {}
    for archivo in sorted(_DIR.glob("*.py")):
        # Ignorar archivos que empiezan con '_' (ej: __init__.py)
        if archivo.name.startswith("_"):
            continue

        # Cargar el módulo dinámicamente
        clave = f"mecanica_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(clave, archivo)
        if spec is None or spec.loader is None:
            continue

        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)

        # Extraer la declaración MECANICA del archivo
        meta = getattr(mod, "MECANICA", None)
        if isinstance(meta, dict):
            hallado[archivo.name] = meta

    return hallado

def _nodos(meta: Dict[str, Any]) -> List[str]:
    """
    Extrae el orden nativo de un archivo (la secuencia de módulos declarada).
    Ejemplo: Si MECANICA = {"orden": ["A", "B", "C"]}, devuelve ["A", "B", "C"].
    """
    orden = meta.get("orden", [])
    if isinstance(orden, (list, tuple)):
        return [str(x) for x in orden]
    return []

def _precedencias(nodos: List[str]) -> List[Tuple[str, str]]:
    """
    Genera todos los pares de precedencia a partir de un orden nativo.
    Ejemplo: Para ["A", "B", "C"], devuelve [("A", "B"), ("A", "C"), ("B", "C")].
    """
    return [(a, b) for i, a in enumerate(nodos) for b in nodos[i + 1:]]

# ===============================================================
# FILTRO DE COHERENCIA MECÁNICA
# ===============================================================
def barrer() -> Dict[str, Any]:
    """
    Calcula la mecánica y comprueba que los archivos no colisionen.
    - Si hay contradicciones, devuelve estado = RECHAZADO y lista de choques.
    - Si no hay contradicciones, devuelve estado = APROBADO y el orden válido.

    No lanza excepciones: solo informa.
    """
    hallado = _leer()
    choques = []
    errores = []

    # Si no hay archivos con MECANICA, reportar error
    if not hallado:
        errores.append("ninguna mecánica declarada")
        return _informe([], choques, errores, {})

    # Diccionario para almacenar quién dice que un nodo va antes que otro
    # Ejemplo: {("A", "B"): ["archivo1.py", "archivo2.py"]}
    precede: Dict[Tuple[str, str], List[str]] = {}

    # Procesar cada archivo para extraer sus precedencias
    for archivo, meta in sorted(hallado.items()):
        nodos = _nodos(meta)
        if len(nodos) < 2:
            errores.append(f"{archivo}: sin orden nativo legible")
            continue

        # Registrar todas las precedencias declaradas en este archivo
        for a, b in _precedencias(nodos):
            precede.setdefault((a, b), []).append(archivo)

    # CORR_SEQ_02: Detectar colisiones sobre el mismo nodo
    # Ejemplo: Si un archivo dice A -> B y otro dice B -> A, hay choque
    for (a, b), quienes in sorted(precede.items()):
        contrarios = precede.get((b, a))
        if contrarios and (a, b) < (b, a):  # Evitar duplicados (ej: (A,B) y (B,A))
            choques.append(
                f"nodo '{a}'/'{b}': {quienes} lo ponen en un orden y "
                f"{contrarios} en el contrario"
            )

    # CORR_SEQ_01: Detectar ciclos (la secuencia se "muerde la cola")
    universo = {x for par in precede for x in par}
    pendientes = set(universo)
    mecanica = []

    while pendientes:
        # Nodos sin dependencias pendientes (pueden procesarse ahora)
        libres = sorted(
            n for n in pendientes
            if not any((o, n) in precede for o in pendientes if o != n)
        )

        if not libres:
            # Hay un ciclo: no se puede resolver el orden
            choques.append(
                f"nodos {sorted(pendientes)}: la secuencia se muerde la cola, "
                "no hay orden posible"
            )
            break

        # Añadir los nodos libres al orden válido
        mecanica.extend(libres)
        pendientes -= set(libres)

    return _informe(mecanica, choques, errores, hallado)

def _informe(
    mecanica: List[str],
    choques: List[str],
    errores: List[str],
    hallado: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Genera el informe final del barrido mecánico.
    """
    limpio = not (choques or errores)
    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": APROBADO if limpio else RECHAZADO,
        "coherente": limpio,
        "choques": choques,
        "errores": errores,
        "mecanica": mecanica if limpio else [],  # Orden válido si no hay choques
        "archivos": sorted(hallado),  # Lista de archivos procesados
    }

# ===============================================================
# INTROSPECCIÓN (Para depuración)
# ===============================================================
def inventario() -> Dict[str, Any]:
    """
    Devuelve un resumen de los archivos de mecánica cargados.
    """
    hallado = _leer()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "declaraciones": len(DECLARACIONES),
        "archivos": sorted(hallado),
        "declaran": {
            archivo: meta.get("nombre", "Sin nombre")
            for archivo, meta in sorted(hallado.items())
        },
    }

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "DECLARACIONES",
    "axiomas",
    "barrer",
    "inventario",
    "APROBADO",
    "RECHAZADO",
]

CONTENEDOR = {
    "nombre": "correlacion_mecanica",
    "rol": "MC",
    "version": "1.0",
    "requiere": [],
    "descripcion": "Contenedor de mecánica. Rol MC. Filtro de coherencia mecánica.",
    "capacidades": {
        "verificar": "barrer",
        "axiomas": "axiomas",
        "evaluar": "barrer",
        "inventario": "inventario",
    }
}
