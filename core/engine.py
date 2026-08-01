#!/usr/bin/env python3
"""
Engine Global para VPSI-TRUTH.
Orquestador principal del sistema. Descubre módulos, ejecuta sus capacidades,
y recopila sus reportes internos para validar el sistema.
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional

class ArranqueError(Exception):
    """Excepción de arranque para la validación del sistema."""
    pass

class Engine:
    """
    Orquestador principal del sistema VPSI-TRUTH.
    - Puede usarse como clase estática o instanciado.
    - Descubre automáticamente todos los módulos en `modules/`.
    - Ejecuta la capacidad "verificar" de cada módulo.
    - Recopila los reportes internos de cada módulo.
    """

    def __init__(self):
        """Constructor para permitir instanciación."""
        self._MODULES_DIR = Path(__file__).parent.parent / "modules"

    @classmethod
    def descubrir_modulos(cls) -> Dict[str, Any]:
        """
        Descubre todos los módulos en `modules/` y carga sus CONTENEDOR.
        """
        modulos = {}
        modules_dir = Path(__file__).parent.parent / "modules"
        for modulo_dir in modules_dir.iterdir():
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

    def ejecutar_modulo(self, modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
        """
        Ejecuta una capacidad específica de un módulo.
        """
        modulos = self.descubrir_modulos()
        if modulo_name not in modulos:
            raise ValueError(f"Módulo '{modulo_name}' no encontrado.")

        contenedor = modulos[modulo_name]
        if capacidad not in contenedor.get("capacidades", {}):
            raise ValueError(f"Capacidad '{capacidad}' no encontrada en el módulo '{modulo_name}'.")

        func = contenedor["capacidades"][capacidad]
        return func(*args, **kwargs)

    @classmethod
    def ejecutar_modulo_clase(cls, modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
        """
        Ejecuta una capacidad específica de un módulo (versión de clase).
        """
        modulos = cls.descubrir_modulos()
        if modulo_name not in modulos:
            raise ValueError(f"Módulo '{modulo_name}' no encontrado.")

        contenedor = modulos[modulo_name]
        if capacidad not in contenedor.get("capacidades", {}):
            raise ValueError(f"Capacidad '{capacidad}' no encontrada en el módulo '{modulo_name}'.")

        func = contenedor["capacidades"][capacidad]
        return func(*args, **kwargs)

    def ejecutar_sistema(self) -> Dict[str, Any]:
        """
        Ejecuta todos los módulos y recopila sus reportes internos.
        """
        modulos = self.descubrir_modulos()
        resultados = {}

        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                verificar_func = contenedor["capacidades"]["verificar"]
                resultados[modulo_name] = verificar_func()

        return resultados

    @classmethod
    def ejecutar_sistema_clase(cls) -> Dict[str, Any]:
        """
        Ejecuta todos los módulos y recopila sus reportes internos (versión de clase).
        """
        modulos = cls.descubrir_modulos()
        resultados = {}

        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                verificar_func = contenedor["capacidades"]["verificar"]
                resultados[modulo_name] = verificar_func()

        return resultados

    def obtener_inventario(self) -> Dict[str, Any]:
        """
        Obtiene el inventario de todos los módulos.
        """
        modulos = self.descubrir_modulos()
        inventario = {}

        for modulo_name, contenedor in modulos.items():
            if "inventario" in contenedor.get("capacidades", {}):
                inventario_func = contenedor["capacidades"]["inventario"]
                inventario[modulo_name] = inventario_func()

        return inventario

    @classmethod
    def obtener_inventario_clase(cls) -> Dict[str, Any]:
        """
        Obtiene el inventario de todos los módulos (versión de clase).
        """
        modulos = cls.descubrir_modulos()
        inventario = {}

        for modulo_name, contenedor in modulos.items():
            if "inventario" in contenedor.get("capacidades", {}):
                inventario_func = contenedor["capacidades"]["inventario"]
                inventario[modulo_name] = inventario_func()

        return inventario

    def obtener_axiomas(self) -> List[Dict]:
        """
        Obtiene todos los axiomas de los módulos que los exponen.
        """
        modulos = self.descubrir_modulos()
        axiomas = []

        for modulo_name, contenedor in modulos.items():
            if "axiomas" in contenedor.get("capacidades", {}):
                axiomas_func = contenedor["capacidades"]["axiomas"]
                axiomas.extend(axiomas_func())

        return axiomas

    @classmethod
    def obtener_axiomas_clase(cls) -> List[Dict]:
        """
        Obtiene todos los axiomas de los módulos que los exponen (versión de clase).
        """
        modulos = cls.descubrir_modulos()
        axiomas = []

        for modulo_name, contenedor in modulos.items():
            if "axiomas" in contenedor.get("capacidades", {}):
                axiomas_func = contenedor["capacidades"]["axiomas"]
                axiomas.extend(axiomas_func())

        return axiomas

    def obtener_contenedores(self) -> Dict[str, Any]:
        """
        Obtiene todos los contenedores de los módulos.
        """
        return self.descubrir_modulos()

    @classmethod
    def obtener_contenedores_clase(cls) -> Dict[str, Any]:
        """
        Obtiene todos los contenedores de los módulos (versión de clase).
        """
        return cls.descubrir_modulos()

# Exportar las clases y excepciones para que puedan ser importadas
__all__ = ["Engine", "ArranqueError"]
