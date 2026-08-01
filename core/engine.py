#!/usr/bin/env python3
"""
Engine Global para VPSI-TRUTH.
Orquestador principal del sistema. Descubre módulos, ejecuta sus capacidades,
y recopila sus reportes internos para validar el sistema.
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional

class Engine:
    """
    Orquestador principal del sistema VPSI-TRUTH.
    - Descubre automáticamente todos los módulos en `modules/`.
    - Ejecuta la capacidad "verificar" de cada módulo.
    - Recopila los reportes internos de cada módulo.
    """

    def __init__(self, invocador_id: str = "core"):
        """
        Constructor para permitir instanciación.
        - `invocador_id`: Identificador del invocador (por defecto: "core").
        """
        self._MODULES_DIR = Path(__file__).parent.parent / "modules"
        self.invocador_id = invocador_id

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
        # Si la capacidad es un string (error en calculator), intentar resolverlo
        if isinstance(func, str):
            # Intentar obtener la función del módulo
            modulo = importlib.import_module(f"modules.{modulo_name}")
            func = getattr(modulo, func, None)
            if func is None:
                raise ValueError(f"Capacidad '{capacidad}' en módulo '{modulo_name}' apunta a un string no válido: '{func}'")
        return func(*args, **kwargs)

    def ejecutar_sistema(self) -> Dict[str, Any]:
        """
        Ejecuta todos los módulos y recopila sus reportes internos.
        """
        modulos = self.descubrir_modulos()
        resultados = {}

        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                try:
                    verificar_func = contenedor["capacidades"]["verificar"]
                    # Manejar el caso donde "verificar" es un string (error en calculator)
                    if isinstance(verificar_func, str):
                        modulo = importlib.import_module(f"modules.{modulo_name}")
                        verificar_func = getattr(modulo, verificar_func, None)
                        if verificar_func is None:
                            resultados[modulo_name] = {"error": f"Capacidad 'verificar' apunta a un string no válido: '{verificar_func}'"}
                            continue
                    resultados[modulo_name] = verificar_func()
                except Exception as e:
                    resultados[modulo_name] = {"error": str(e)}
        return resultados

    def obtener_inventario(self) -> Dict[str, Any]:
        """
        Obtiene el inventario de todos los módulos.
        """
        modulos = self.descubrir_modulos()
        inventario = {}

        for modulo_name, contenedor in modulos.items():
            if "inventario" in contenedor.get("capacidades", {}):
                try:
                    inventario_func = contenedor["capacidades"]["inventario"]
                    inventario[modulo_name] = inventario_func()
                except Exception as e:
                    inventario[modulo_name] = {"error": str(e)}
        return inventario

    def obtener_axiomas(self) -> List[Dict]:
        """
        Obtiene todos los axiomas de los módulos que los exponen.
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

    def obtener_contenedores(self) -> Dict[str, Any]:
        """
        Obtiene todos los contenedores de los módulos.
        """
        return self.descubrir_modulos()

# Exportar las clases para que puedan ser importadas
__all__ = ["Engine"]
