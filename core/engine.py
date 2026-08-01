"""
Engine Global para VPSI-TRUTH.
Orquestador principal del sistema. Descubre módulos, ejecuta sus capacidades,
y recopila sus reportes internos para validar el sistema.
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional

class GlobalEngine:
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
        Ejecuta todos los módulos y recopila sus reportes internos.
        """
        modulos = cls.descubrir_modulos()
        resultados = {}

        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                verificar_func = contenedor["capacidades"]["verificar"]
                resultados[modulo_name] = verificar_func()

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
