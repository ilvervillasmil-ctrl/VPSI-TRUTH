#!/usr/bin/env python3
"""
Engine Global para VPSI-TRUTH.
Orquestador principal del sistema. Descubre módulos, ejecuta sus capacidades,
y recopila sus reportes internos para validar el sistema.

Este Engine está diseñado para trabajar con la arquitectura real de los módulos,
donde cada módulo expone un CONTENEDOR con capacidades definidas como funciones.
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict


# Excepción para errores de arranque
class ArranqueError(Exception):
    """Excepción lanzada cuando hay un error de arranque en el sistema."""
    pass


# Estructura esperada para el CONTENEDOR de un módulo
class Contenedor(TypedDict, total=False):
    nombre: str
    rol: str
    version: str
    requiere: List[str]
    descripcion: str
    capacidades: Dict[str, Any]  # Las capacidades deben ser funciones


class Engine:
    """
    Orquestador principal del sistema VPSI-TRUTH.
    - Descubre automáticamente todos los módulos en `modules/`.
    - Valida que los módulos tengan un CONTENEDOR bien definido.
    - Ejecuta las capacidades de los módulos (ej: "verificar", "inventario").
    - Recopila los reportes internos de cada módulo.
    """

    def __init__(self, invocador_id: str = "core"):
        """
        Constructor del Engine.
        
        Args:
            invocador_id (str): Identificador del invocador. Por defecto: "core".
        """
        self._MODULES_DIR = Path(__file__).parent.parent / "modules"
        self.invocador_id = invocador_id

    @classmethod
    def descubrir_modulos(cls) -> Dict[str, Contenedor]:
        """
        Descubre todos los módulos en `modules/` y carga sus CONTENEDOR.
        
        Returns:
            Dict[str, Contenedor]: Diccionario de módulos, donde la clave es el nombre del módulo
                                y el valor es su CONTENEDOR.
        
        Raises:
            ArranqueError: Si un módulo no tiene un CONTENEDOR válido.
        """
        modulos = {}
        modules_dir = Path(__file__).parent.parent / "modules"
        
        for modulo_dir in modules_dir.iterdir():
            if not modulo_dir.is_dir():
                continue
            
            modulo_name = modulo_dir.name
            try:
                modulo = importlib.import_module(f"modules.{modulo_name}")
                if not hasattr(modulo, "CONTENEDOR"):
                    raise ArranqueError(f"El módulo '{modulo_name}' no tiene CONTENEDOR definido.")
                
                contenedor = modulo.CONTENEDOR
                cls._validar_contenedor(contenedor, modulo_name)
                modulos[modulo_name] = contenedor
                
            except ImportError as e:
                raise ArranqueError(f"No se pudo importar el módulo '{modulo_name}': {str(e)}")
            except Exception as e:
                raise ArranqueError(f"Error al cargar el módulo '{modulo_name}': {str(e)}")
        
        return modulos

    @staticmethod
    def _validar_contenedor(contenedor: Dict, modulo_name: str) -> None:
        """
        Valida que el CONTENEDOR de un módulo tenga la estructura esperada.
        
        Args:
            contenedor (Dict): El CONTENEDOR del módulo.
            modulo_name (str): Nombre del módulo.
        
        Raises:
            ArranqueError: Si el CONTENEDOR no es válido.
        """
        if not isinstance(contenedor, dict):
            raise ArranqueError(f"El CONTENEDOR de '{modulo_name}' no es un diccionario.")
        
        if "capacidades" not in contenedor:
            raise ArranqueError(f"El CONTENEDOR de '{modulo_name}' no tiene la clave 'capacidades'.")
        
        if not isinstance(contenedor["capacidades"], dict):
            raise ArranqueError(f"La clave 'capacidades' en '{modulo_name}' no es un diccionario.")
        
        for capacidad, func in contenedor["capacidades"].items():
            if not callable(func):
                raise ArranqueError(
                    f"La capacidad '{capacidad}' en '{modulo_name}' no es una función. "
                    f"Tipo: {type(func).__name__}"
                )

    def ejecutar_modulo(self, modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
        """
        Ejecuta una capacidad específica de un módulo.
        
        Args:
            modulo_name (str): Nombre del módulo.
            capacidad (str): Nombre de la capacidad a ejecutar.
            *args: Argumentos posicionales para la capacidad.
            **kwargs: Argumentos nominales para la capacidad.
        
        Returns:
            Any: Resultado de ejecutar la capacidad.
        
        Raises:
            ValueError: Si el módulo o la capacidad no existen.
        """
        modulos = self.descubrir_modulos()
        if modulo_name not in modulos:
            raise ValueError(f"Módulo '{modulo_name}' no encontrado.")
        
        contenedor = modulos[modulo_name]
        if capacidad not in contenedor.get("capacidades", {}):
            raise ValueError(f"Capacidad '{capacidad}' no encontrada en el módulo '{modulo_name}'.")
        
        func = contenedor["capacidades"][capacidad]
        return func(*args, **kwargs)

    def ejecutar_sistema(self) -> Dict[str, Any]:
        """
        Ejecuta la capacidad "verificar" de todos los módulos y recopila sus reportes.
        
        Returns:
            Dict[str, Any]: Diccionario donde las claves son los nombres de los módulos
                           y los valores son los resultados de su capacidad "verificar".
        """
        modulos = self.descubrir_modulos()
        resultados = {}
        
        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                try:
                    verificar_func = contenedor["capacidades"]["verificar"]
                    resultados[modulo_name] = verificar_func()
                except Exception as e:
                    resultados[modulo_name] = {
                        "error": str(e),
                        "modulo": modulo_name,
                        "capacidad": "verificar"
                    }
        
        return resultados

    def obtener_inventario(self) -> Dict[str, Any]:
        """
        Obtiene el inventario de todos los módulos que exponen la capacidad "inventario".
        
        Returns:
            Dict[str, Any]: Diccionario donde las claves son los nombres de los módulos
                           y los valores son los resultados de su capacidad "inventario".
        """
        modulos = self.descubrir_modulos()
        inventario = {}
        
        for modulo_name, contenedor in modulos.items():
            if "inventario" in contenedor.get("capacidades", {}):
                try:
                    inventario_func = contenedor["capacidades"]["inventario"]
                    inventario[modulo_name] = inventario_func()
                except Exception as e:
                    inventario[modulo_name] = {
                        "error": str(e),
                        "modulo": modulo_name,
                        "capacidad": "inventario"
                    }
        
        return inventario

    def obtener_axiomas(self) -> List[Dict]:
        """
        Obtiene todos los axiomas de los módulos que exponen la capacidad "axiomas".
        
        Returns:
            List[Dict]: Lista de axiomas de todos los módulos.
        """
        modulos = self.descubrir_modulos()
        axiomas = []
        
        for modulo_name, contenedor in modulos.items():
            if "axiomas" in contenedor.get("capacidades", {}):
                try:
                    axiomas_func = contenedor["capacidades"]["axiomas"]
                    axiomas.extend(axiomas_func())
                except Exception:
                    continue
        
        return axiomas

    def obtener_contenedores(self) -> Dict[str, Contenedor]:
        """
        Obtiene los CONTENEDOR de todos los módulos.
        
        Returns:
            Dict[str, Contenedor]: Diccionario de CONTENEDOR de todos los módulos.
        """
        return self.descubrir_modulos()


# Exportar las clases para que puedan ser importadas
__all__ = ["Engine", "ArranqueError", "Contenedor"]
