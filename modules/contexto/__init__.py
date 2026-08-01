from __future__ import annotations
import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from core.diagnostico import DiagnosticoGlobal  # Integración con Diagnostics

# ===============================================================
# CONTENEDOR: Metadatos del módulo
# ===============================================================
CONTENEDOR = {
    "nombre": "contexto",
    "rol": "CX",
    "version": "1.0",
    "requiere": ["AX", "CT", "MC"],
    "descripcion": (
        "Filtro inicial del sistema VPSI-TRUTH. "
        "Valida el contexto base del repositorio (axiomas, orden causal, constantes) "
        "y expone la función resolver(peticion) para el Engine."
    ),
    "capacidades": {
        "verificar": resolver,
        "inventario": inventario,
    },
}

# ===============================================================
# ESTADO UNDEFINIDO (UNDEFINED)
# ===============================================================
class _Undefined:
    """Estado para valores sin evidencia."""
    __slots__ = ()

    def __repr__(self):
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, otro):
        return isinstance(otro, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")

UNDEFINED = _Undefined()

def es_undefined(v) -> bool:
    """Verifica si un valor es UNDEFINED."""
    return v is UNDEFINED or isinstance(v, _Undefined)

# ===============================================================
# EXCEPCIONES
# ===============================================================
class ContextoError(Exception):
    """Error al resolver el contexto (ej: axiomas contradichos, constantes inválidas)."""
    pass

# ===============================================================
# CARGA DINÁMICA DE ARCHIVOS DE CONTEXTO
# ===============================================================
_DIR = Path(__file__).parent  # Directorio del módulo contexto

def _cargar_archivos_contexto() -> Dict[str, Any]:
    """
    Carga todos los archivos de contexto dentro de la carpeta `contexto/`.
    Cada archivo debe definir una función `validar()` que devuelva:
    - Un diccionario con el contexto validado.
    - O lanzar una excepción si el contexto es inválido.
    """
    contextos = {}
    for archivo in _DIR.glob("*.py"):
        if archivo.name == "__init__.py":
            continue  # Saltar este archivo

        # Cargar el módulo dinámicamente
        modulo_nombre = f"contexto_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(modulo_nombre, archivo)
        if spec is None or spec.loader is None:
            continue

        modulo = importlib.util.module_from_spec(spec)
        sys.modules[modulo_nombre] = modulo
        spec.loader.exec_module(modulo)

        # Verificar que el módulo tenga una función `validar()`
        if hasattr(modulo, "validar") and callable(modulo.validar):
            try:
                contexto = modulo.validar()
                contextos[archivo.stem] = contexto
            except Exception as e:
                contextos[archivo.stem] = {"error": str(e)}
        else:
            contextos[archivo.stem] = {"error": "No tiene función validar()"}

    return contextos

# ===============================================================
# ENGINE (Orquestador)
# ===============================================================
def resolver(peticion: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Función principal para resolver el contexto base del repositorio.
    Orquesta la lógica del módulo:
    1. Carga archivos de contexto.
    2. Valida axiomas (AX).
    3. Valida orden causal (MC).
    4. Valida constantes (CT).
    5. Retorna el contexto resuelto.
    """
    # Cargar todos los archivos de contexto en la carpeta
    archivos_contexto = _cargar_archivos_contexto()

    # Validar axiomas (AX)
    from modules.axiomas import barrer as barrer_axiomas
    informe_axiomas = barrer_axiomas()
    axiomas_coherentes = informe_axiomas.get("coherente", False)
    choques_axiomas = informe_axiomas.get("choques", [])

    # Validar orden causal (MC)
    from modules.correlacion_mecanica import barrer as barrer_mecanica
    informe_mecanica = barrer_mecanica()
    orden_causal_valido = informe_mecanica.get("coherente", False)
    choques_mecanica = informe_mecanica.get("choques", [])

    # Validar constantes (CT)
    from modules.constante import ALPHA, BETA
    constantes_validas = (ALPHA + BETA == Fraction(1))

    # Determinar coherencia global del repositorio
    coherencia = axiomas_coherentes and orden_causal_valido and constantes_validas

    # Construir el contexto resuelto
    contexto_resuelto = {
        "O_context": "VPSI-TRUTH v9.4 (repositorio)",
        "coherente": coherencia,
        "axiomas": {
            "coherente": axiomas_coherentes,
            "choques": choques_axiomas,
            "declaraciones": informe_axiomas.get("declaraciones", 0),
        },
        "mecanica": {
            "coherente": orden_causal_valido,
            "choques": choques_mecanica,
        },
        "constantes": {
            "ALPHA": str(ALPHA),
            "BETA": str(BETA),
            "suma": str(ALPHA + BETA),
            "valido": constantes_validas,
        },
        "archivos_contexto": archivos_contexto,
        "errores": [],
    }

    # Agregar errores si los hay
    if not axiomas_coherentes:
        contexto_resuelto["errores"].append(
            f"Choques axiomáticos: {choques_axiomas}"
        )
    if not orden_causal_valido:
        contexto_resuelto["errores"].append(
            f"Choques mecánicos: {choques_mecanica}"
        )
    if not constantes_validas:
        contexto_resuelto["errores"].append(
            f"Constantes inválidas: ALPHA + BETA = {ALPHA + BETA} (se exige 1)"
        )

    # Validar que todos los archivos de contexto sean coherentes
    for nombre_archivo, contexto in archivos_contexto.items():
        if "error" in contexto:
            contexto_resuelto["errores"].append(
                f"Archivo de contexto {nombre_archivo} inválido: {contexto['error']}"
            )
            contexto_resuelto["coherente"] = False

    # Enviar reporte a DiagnosticoGlobal si hay errores (Reporte Omega)
    if not contexto_resuelto["coherente"]:
        DiagnosticoGlobal.recibir_reporte(
            modulo="contexto",
            errores=[{"tipo": "error_contexto", "detalle": error} for error in contexto_resuelto["errores"]]
        )

    return contexto_resuelto

# ===============================================================
# CENTINELA (Eyenet)
# ===============================================================
def verificar_salida(salida: Dict[str, Any]) -> bool:
    """
    Valida la salida del Engine (resolver).
    - Si la salida es coherente, devuelve True.
    - Si no lo es, ya se envió un reporte a DiagnosticoGlobal en resolver().
    """
    return salida.get("coherente", False)

# ===============================================================
# INVENTARIO (Opcional)
# ===============================================================
def inventario() -> Dict[str, Any]:
    """
    Devuelve un resumen del módulo contexto.
    """
    archivos_contexto = _cargar_archivos_contexto()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "archivos_contexto": list(archivos_contexto.keys()),
        "coherente": resolver().get("coherente", False),
    }

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "UNDEFINED",
    "es_undefined",
    "ContextoError",
    "resolver",
    "verificar_salida",  # Nueva función para el Centinela
    "inventario",  # Nueva función para introspección
]
