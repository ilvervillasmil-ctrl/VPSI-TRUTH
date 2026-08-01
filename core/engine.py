from __future__ import annotations
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from core.diagnostico import DiagnosticoGlobal

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================
CONTENEDOR = {
    "nombre": "engine",
    "rol": "EN",
    "version": "1.0",
    "requiere": [],
    "descripcion": "Orquestador principal del sistema VPSI-TRUTH. Descubre módulos, obtiene orden de ejecución y los ejecuta.",
}

# ===============================================================
# SEGMENTO 2 --- CONSTANTES
# ===============================================================
_MODULES_DIR = Path(__file__).parent.parent / "modules"

# ===============================================================
# SEGMENTO 3 --- ENGINE (Lógica original preservada)
# ===============================================================
def descubrir_modulos() -> Dict[str, Any]:
    """
    Descubre automáticamente todos los módulos en `modules/`.
    Retorna un diccionario con el nombre del módulo y su CONTENEDOR.
    """
    modulos = {}
    for modulo_dir in _MODULES_DIR.iterdir():
        if not modulo_dir.is_dir():
            continue

        modulo_name = modulo_dir.name
        try:
            modulo = importlib.import_module(f"modules.{modulo_name}")
            if hasattr(modulo, "CONTENEDOR"):
                modulos[modulo_name] = modulo.CONTENEDOR
        except ImportError:
            DiagnosticoGlobal.recibir_reporte(
                modulo="engine",
                errores=[{"tipo": "import_error", "detalle": f"No se pudo importar el módulo {modulo_name}"}]
            )
            continue

    return modulos


def obtener_orden_ejecucion() -> Optional[List[str]]:
    """
    Consulta `correlacion_mecanica/` para obtener el orden válido de ejecución.
    Retorna None si no hay un orden válido (choques en correlacion_mecanica).
    """
    try:
        from modules.correlacion_mecanica import CONTENEDOR as correlacion_contenedor
        resultado = correlacion_contenedor["capacidades"]["verificar"]()
        if resultado["coherente"]:
            return resultado["mecanica"]
        else:
            return None
    except ImportError:
        DiagnosticoGlobal.recibir_reporte(
            modulo="engine",
            errores=[{"tipo": "import_error", "detalle": "No se encontró el módulo correlacion_mecanica"}]
        )
        return None


def ejecutar_modulo(modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
    """
    Ejecuta una capacidad específica de un módulo.
    """
    try:
        modulo = importlib.import_module(f"modules.{modulo_name}")
        if hasattr(modulo, "CONTENEDOR"):
            funcion = modulo.CONTENEDOR["capacidades"].get(capacidad)
            if funcion:
                return funcion(*args, **kwargs)
            else:
                DiagnosticoGlobal.recibir_reporte(
                    modulo="engine",
                    errores=[{"tipo": "capacidad_no_encontrada", "detalle": f"Capacidad '{capacidad}' no encontrada en {modulo_name}"}]
                )
        else:
            DiagnosticoGlobal.recibir_reporte(
                modulo="engine",
                errores=[{"tipo": "sin_contenedor", "detalle": f"Módulo {modulo_name} no tiene CONTENEDOR"}]
            )
    except Exception as e:
        DiagnosticoGlobal.recibir_reporte(
            modulo="engine",
            errores=[{"tipo": "error_ejecucion", "detalle": f"Error al ejecutar {modulo_name}/{capacidad}: {str(e)}"}]
        )
    return None


def ejecutar_sistema() -> Dict[str, Any]:
    """
    Ejecuta todos los módulos en el orden definido por `correlacion_mecanica/`.
    Retorna un diccionario con los resultados de cada módulo.
    """
    modulos = descubrir_modulos()
    if not modulos:
        DiagnosticoGlobal.recibir_reporte(
            modulo="engine",
            errores=[{"tipo": "sin_modulos", "detalle": "No se encontraron módulos en modules/"}]
        )
        return {"status": "error", "mensaje": "No hay módulos para ejecutar"}

    orden = obtener_orden_ejecucion()
    if not orden:
        return {"status": "error", "mensaje": "No hay orden válido (choques en correlacion_mecanica)"}

    resultados = {}
    for modulo_name in orden:
        if modulo_name not in modulos:
            DiagnosticoGlobal.recibir_reporte(
                modulo="engine",
                errores=[{"tipo": "modulo_ausente", "detalle": f"Módulo {modulo_name} no encontrado en el orden definido"}]
            )
            continue

        resultado = ejecutar_modulo(modulo_name, "verificar")
        resultados[modulo_name] = resultado

    return {"status": "ok", "resultados": resultados}


def obtener_autorizaciones() -> Dict[str, bool]:
    """
    Verifica qué módulos están autorizados para funcionar (sin contradicciones).
    Retorna un diccionario con el estado de autorización de cada módulo.
    """
    modulos = descubrir_modulos()
    autorizaciones = {}

    for modulo_name, contenedor in modulos.items():
        resultado = ejecutar_modulo(modulo_name, "verificar")
        autorizaciones[modulo_name] = resultado.get("coherente", False) if resultado else False

    return autorizaciones


def barrer() -> Dict[str, Any]:
    """
    Capacidad de verificación del Engine.
    Ejecuta el sistema y reporta el estado global.
    """
    resultado = ejecutar_sistema()
    coherente = resultado.get("status") == "ok"
    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": "APROBADO" if coherente else "RECHAZADO",
        "coherente": coherente,
        "resultado": resultado,
    }

# ===============================================================
# SEGMENTO 4 --- CENTINELA
# ===============================================================
def verificar_salida(salida: Dict[str, Any]) -> bool:
    """Valida la salida del Engine (barrer)."""
    return salida.get("coherente", False)

# ===============================================================
# SEGMENTO 5 --- CONTENEDOR (Contrato final)
# ===============================================================
CONTENEDOR = {
    "nombre": "engine",
    "rol": "EN",
    "version": "1.0",
    "requiere": [],
    "descripcion": "Orquestador principal del sistema VPSI-TRUTH. Descubre módulos, obtiene orden de ejecución y los ejecuta.",
    "capacidades": {
        "verificar": barrer,
        "evaluar": barrer,
        "descubrir": descubrir_modulos,
        "ejecutar": ejecutar_sistema,
        "autorizaciones": obtener_autorizaciones,
        "orden": obtener_orden_ejecucion,
    },
}

# ===============================================================
# EXPORTACIÓN
# ===============================================================
# Alias de compatibilidad (por si alguien aún importa Engine)
Engine = CONTENEDOR
GlobalEngine = CONTENEDOR

__all__ = [
    "CONTENEDOR",
    "Engine",
    "GlobalEngine",
    "barrer",
    "descubrir_modulos",
    "obtener_orden_ejecucion",
    "ejecutar_modulo",
    "ejecutar_sistema",
    "obtener_autorizaciones",
    "verificar_salida",
]
