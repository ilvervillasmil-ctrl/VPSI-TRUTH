"""
Engine Global para VPSI-TRUTH.
Orquestador principal del sistema. Descubre módulos, ejecuta sus capacidades,
y recopila sus reportes internos para validar el sistema.
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional


class ArranqueError(Exception):
    """
    Excepción crítica de arranque que centraliza, verifica y reporta 
    los errores provenientes de todos los módulos del repositorio.
    """
    def __init__(self, mensaje: str, errores_modulos: Optional[Dict[str, Any]] = None):
        super().__init__(mensaje)
        self.errores_modulos = errores_modulos or {}

    @classmethod
    def verificar_y_construir(cls, errores_modulos: Dict[str, Any]) -> Optional["ArranqueError"]:
        """
        Inspecciona los reportes de los módulos y construye la excepción 
        si se detectan fallos o estados de error estructural.
        """
        fallos_detectados = {}
        for mod, resultado in errores_modulos.items():
            # Evalúa si el módulo reportó un error explícito en su estructura
            if isinstance(resultado, dict) and resultado.get("estado") == "error":
                fallos_detectados[mod] = resultado
            elif resultado is False:
                fallos_detectados[mod] = {"estado": "error", "detalle": "El módulo devolvió False en la verificación."}

        if fallos_detectados:
            return cls(
                f"Fallo crítico en el arranque del sistema. Se detectaron errores en módulos.", 
                fallos_detectados
            )
        return None


class Engine:
    """
    Orquestador principal del sistema VPSI-TRUTH.
    - Descubre automáticamente todos los módulos en `modules/`.
    - Ejecuta la capacidad "verificar" de cada módulo.
    - Recopila los reportes internos de cada módulo.
    """

    _MODULES_DIR = Path(__file__).parent.parent / "modules"

    @classmethod
    def descubrir_modulos(cls) -> Dict[str, Any]:
        """
        Descubre todos los módulos en `modules/` y carga sus CONTENEDOR.
        """
        modulos = {}
        for modulo_dir in cls._MODULES_DIR.iterdir():
            if not modulo_dir.is_dir():
                continue
            modulo_name = modulo_dir.name
            try:
                modulo = importlib.import_module(f"modules.{modulo_name}")
                if hasattr(modulo, "CONTENEDOR"):
                    modulos[modulo_name] = modulo.CONTENEDOR
            except ImportError:
                continue
        return modulos

    @classmethod
    def ejecutar_modulo(cls, modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
        """
        Ejecuta una capacidad específica de un módulo.
        """
        modulos = cls.descubrir_modulos()
        if modulo_name not in modulos:
            raise ValueError(f"Módulo '{modulo_name}' no encontrado.")

        contenedor = modulos[modulo_name]
        if capacidad not in contenedor.get("capacidades", {}):
            raise ValueError(f"Capacidad '{capacidad}' no encontrada en el módulo '{modulo_name}'.")

        func = contenedor["capacidades"][capacidad]
        return func(*args, **kwargs)

    @classmethod
    def ejecutar_sistema(cls) -> Dict[str, Any]:
        """
        Ejecuta la verificación de todos los módulos, recopila sus reportes 
        y lanza ArranqueError si algún módulo presenta fallos.
        """
        modulos = cls.descubrir_modulos()
        resultados = {}

        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                verificar_func = contenedor["capacidades"]["verificar"]
                try:
                    resultados[modulo_name] = verificar_func()
                except Exception as e:
                    resultados[modulo_name] = {"estado": "error", "detalle": str(e)}

        # Conecta la verificación global con ArranqueError
        error_arranque = ArranqueError.verificar_y_construir(resultados)
        if error_arranque:
            raise error_arranque

        return resultados

    @classmethod
    def obtener_inventario(cls) -> Dict[str, Any]:
        """
        Obtiene el inventario de todos los módulos.
        """
        modulos = cls.descubrir_modulos()
        inventario = {}

        for modulo_name, contenedor in modulos.items():
            if "inventario" in contenedor.get("capacidades", {}):
                inventario_func = contenedor["capacidades"]["inventario"]
                inventario[modulo_name] = inventario_func()

        return inventario

    @classmethod
    def obtener_axiomas(cls) -> List[Dict]:
        """
        Obtiene todos los axiomas de los módulos que los exponen.
        """
        modulos = cls.descubrir_modulos()
        axiomas = []

        for modulo_name, contenedor in modulos.items():
            if "axiomas" in contenedor.get("capacidades", {}):
                axiomas_func = contenedor["capacidades"]["axiomas"]
                axiomas.extend(axiomas_func())

        return axiomas
