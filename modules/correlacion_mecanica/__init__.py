from pathlib import Path
import importlib.util
import sys
from typing import Dict, List, Any, Tuple, Optional
from core.diagnostico import DiagnosticoGlobal  # Importar DiagnosticoGlobal para Reportes Omega

# ===============================================================
# CONTENEDOR (Contrato del módulo)
# ===============================================================
CONTENEDOR = {
    "nombre": "correlacion_mecanica",
    "rol": "MC",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Contenedor de mecánica. Rol MC. Filtro de coherencia mecánica. "
        "Lee los archivos en su directorio, calcula la mecánica resultante "
        "y comprueba que no se contradigan entre sí."
    ),
    "capacidades": {
        "verificar": "barrer",      # Capacidad para validar el módulo
        "axiomas": "axiomas",       # Devuelve las declaraciones axiomáticas
        "evaluar": "barrer",        # Igual que "verificar"
        "inventario": "inventario"  # Resumen del módulo
    }
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
# FUNCIONES PRINCIPALES (Lógica Interna del Módulo)
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
        if archivo.name.startswith("_"):
            continue

        clave = f"mecanica_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(clave, archivo)
        if spec is None or spec.loader is None:
            continue

        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)

        meta = getattr(mod, "MECANICA", None)
        if isinstance(meta, dict):
            hallado[archivo.name] = meta

    return hallado

def _nodos(meta: Dict[str, Any]) -> List[str]:
    """
    Extrae el orden nativo de un archivo (la secuencia de módulos declarada).
    """
    orden = meta.get("orden", [])
    if isinstance(orden, (list, tuple)):
        return [str(x) for x in orden]
    return []

def _precedencias(nodos: List[str]) -> List[Tuple[str, str]]:
    """
    Genera todos los pares de precedencia a partir de un orden nativo.
    """
    return [(a, b) for i, a in enumerate(nodos) for b in nodos[i + 1:]]

# ===============================================================
# ENGINE (Orquestador)
# ===============================================================
def barrer() -> Dict[str, Any]:
    """
    Calcula la mecánica y comprueba que los archivos no colisionen.
    - Si hay contradicciones, devuelve estado = RECHAZADO y lista de choques.
    - Si no hay contradicciones, devuelve estado = APROBADO y el orden válido.
    """
    hallado = _leer()
    choques = []
    errores = []

    if not hallado:
        errores.append("ninguna mecánica declarada")
        # Enviar reporte a DiagnosticoGlobal (Reporte Omega)
        DiagnosticoGlobal.recibir_reporte(
            modulo="correlacion_mecanica",
            errores=errores
        )
        return _informe([], choques, errores, hallado)

    precede: Dict[Tuple[str, str], List[str]] = {}

    for archivo, meta in sorted(hallado.items()):
        nodos = _nodos(meta)
        if len(nodos) < 2:
            errores.append(f"{archivo}: sin orden nativo legible")
            continue

        for a, b in _precedencias(nodos):
            precede.setdefault((a, b), []).append(archivo)

    # Detectar colisiones
    for (a, b), quienes in sorted(precede.items()):
        contrarios = precede.get((b, a))
        if contrarios and (a, b) < (b, a):
            choques.append(
                f"nodo '{a}'/'{b}': {quienes} lo ponen en un orden y "
                f"{contrarios} en el contrario"
            )

    # Detectar ciclos
    universo = {x for par in precede for x in par}
    pendientes = set(universo)
    mecanica = []

    while pendientes:
        libres = sorted(
            n for n in pendientes
            if not any((o, n) in precede for o in pendientes if o != n)
        )

        if not libres:
            choques.append(
                f"nodos {sorted(pendientes)}: la secuencia se muerde la cola, "
                "no hay orden posible"
            )
            break

        mecanica.extend(libres)
        pendientes -= set(libres)

    # Enviar reporte a DiagnosticoGlobal si hay choques o errores
    if choques or errores:
        DiagnosticoGlobal.recibir_reporte(
            modulo="correlacion_mecanica",
            errores=choques + errores
        )

    return _informe(mecanica, choques, errores, hallado)

# ===============================================================
# CENTINELA (Eyenet)
# ===============================================================
def verificar_salida(salida: Dict[str, Any]) -> bool:
    """
    Valida la salida del Engine (barrer) y envía reportes si hay errores.
    - Si la salida es coherente, devuelve True.
    - Si no lo es, ya se envió un reporte a DiagnosticoGlobal en barrer().
    """
    return salida.get("coherente", False)

# ===============================================================
# FUNCIÓN DE REPORTE (Informe)
# ===============================================================
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
        "mecanica": mecanica if limpio else [],
        "archivos": sorted(hallado),
    }

# ===============================================================
# INTROSPECCIÓN
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
    "verificar_salida",
    "APROBADO",
    "RECHAZADO",
]
