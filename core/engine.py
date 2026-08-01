import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from core.diagnostico import DiagnosticoGlobal

class GlobalEngine:
    """
    Orquestador principal del sistema VPSI-TRUTH.
    - Descubre automáticamente todos los módulos en `modules/`.
    - Consulta `correlacion_mecanica/` para obtener el orden de ejecución.
    - Ejecuta los módulos en ese orden.
    - No modifica la lógica interna de los módulos.
    """

    # Ruta base donde están los módulos
    _MODULES_DIR = Path(__file__).parent.parent / "modules"

    @classmethod
    def descubrir_modulos(cls) -> Dict[str, Any]:
        """
        Descubre automáticamente todos los módulos en `modules/`.
        Retorna un diccionario con el nombre del módulo y su CONTENEDOR.
        """
        modulos = {}
        for modulo_dir in cls._MODULES_DIR.iterdir():
            if not modulo_dir.is_dir():
                continue

            # Intentar importar el módulo
            modulo_name = modulo_dir.name
            try:
                modulo = importlib.import_module(f"modules.{modulo_name}")
                if hasattr(modulo, "CONTENEDOR"):
                    modulos[modulo_name] = modulo.CONTENEDOR
            except ImportError:
                # Si no se puede importar, ignorar (o reportar error)
                DiagnosticoGlobal.recibir_reporte(
                    modulo=f"core/engine",
                    errores=[f"No se pudo importar el módulo {modulo_name}"]
                )
                continue

        return modulos

    @classmethod
    def obtener_orden_ejecucion(cls) -> Optional[List[str]]:
        """
        Consulta `correlacion_mecanica/` para obtener el orden válido de ejecución.
        Retorna None si no hay un orden válido (choques en correlacion_mecanica).
        """
        try:
            from modules.correlacion_mecanica import CONTENEDOR as correlacion_contenedor
            resultado = correlacion_contenedor["capacidades"]["verificar"]()
            if resultado["coherente"]:
                return resultado["mecanica"]  # Orden válido: ["axiomas", "realidad", ...]
            else:
                return None
        except ImportError:
            # Si no existe correlacion_mecanica, asumir orden alfabético (o reportar error)
            DiagnosticoGlobal.recibir_reporte(
                modulo="core/engine",
                errores=["No se encontró el módulo correlacion_mecanica"]
            )
            return None

    @classmethod
    def ejecutar_modulo(cls, modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
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
                        modulo=f"core/engine",
                        errores=[f"Capacidad '{capacidad}' no encontrada en {modulo_name}"]
                    )
            else:
                DiagnosticoGlobal.recibir_reporte(
                    modulo=f"core/engine",
                    errores=[f"Módulo {modulo_name} no tiene CONTENEDOR"]
                )
        except Exception as e:
            DiagnosticoGlobal.recibir_reporte(
                modulo=f"core/engine",
                errores=[f"Error al ejecutar {modulo_name}/{capacidad}: {str(e)}"]
            )
        return None

    @classmethod
    def ejecutar_sistema(cls) -> Dict[str, Any]:
        """
        Ejecuta todos los módulos en el orden definido por `correlacion_mecanica/`.
        Retorna un diccionario con los resultados de cada módulo.
        """
        # Descubrir todos los módulos
        modulos = cls.descubrir_modulos()
        if not modulos:
            DiagnosticoGlobal.recibir_reporte(
                modulo="core/engine",
                errores=["No se encontraron módulos en modules/"]
            )
            return {"status": "error", "mensaje": "No hay módulos para ejecutar"}

        # Obtener el orden de ejecución
        orden = cls.obtener_orden_ejecucion()
        if not orden:
            return {"status": "error", "mensaje": "No hay orden válido (choques en correlacion_mecanica)"}

        # Ejecutar módulos en el orden definido
        resultados = {}
        for modulo_name in orden:
            if modulo_name not in modulos:
                DiagnosticoGlobal.recibir_reporte(
                    modulo="core/engine",
                    errores=[f"Módulo {modulo_name} no encontrado en el orden definido"]
                )
                continue

            # Ejecutar la capacidad "verificar" del módulo
            resultado = cls.ejecutar_modulo(modulo_name, "verificar")
            resultados[modulo_name] = resultado

        return {"status": "ok", "resultados": resultados}

    @classmethod
    def obtener_autorizaciones(cls) -> Dict[str, bool]:
        """
        Verifica qué módulos están autorizados para funcionar (sin contradicciones).
        Retorna un diccionario con el estado de autorización de cada módulo.
        """
        modulos = cls.descubrir_modulos()
        autorizaciones = {}

        for modulo_name, contenedor in modulos.items():
            resultado = cls.ejecutar_modulo(modulo_name, "verificar")
            autorizaciones[modulo_name] = resultado.get("coherente", False) if resultado else False

        return autorizaciones
