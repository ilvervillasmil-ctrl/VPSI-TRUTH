#!/usr/bin/env python3
"""
Engine Global para VPSI-TRUTH.
Orquestador principal del sistema con resolución de dependencias topológicas,
gestión unificada de rutas, recarga en caliente de módulos (importlib.reload),
aislamiento de errores de carga y soporte flexible para argumentos de ejecución.
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List, TypedDict, Optional

class ArranqueError(Exception):
    """Excepción lanzada cuando hay un error crítico de arranque en el sistema."""
    pass

class Contenedor(TypedDict, total=true):
    nombre: str
    rol: str
    version: str
    requiere: List[str]
    descripcion: str
    capacidades: Dict[str, Any]

class Engine:
    """
    Orquestador principal del sistema VPSI-TRUTH.
    - Descubre y valida automáticamente los módulos desde un directorio configurable.
    - Resuelve dependencias topológicas según el campo 'requiere' del CONTENEDOR.
    - Maneja la recarga de módulos y aísla fallos de carga individuales.
    - Se integra con DiagnosticoGlobal para la centralización de errores.
    """

    def __init__(self, invocador_id: Optional[str] = None, modules_dir: Optional[Path] = None, *args, **kwargs):
        """Constructor del Engine con compatibilidad total para harnesses de prueba y rutas personalizadas."""
        self.modules_dir = modules_dir or (Path(__file__).parent.parent / "modules")
        self._modulos_cache: Optional[Dict[str, Contenedor]] = None
        self.errores_carga: Dict[str, str] = {}

    def descubrir_modulos(self, forzar_recarga: bool = False) -> Dict[str, Contenedor]:
        """
        Descubre todos los módulos en `modules/`, valida sus CONTENEDOR,
        actualiza la caché mediante recarga segura y los ordena por dependencias.
        """
        if self._modulos_cache is not None and not forzar_recarga:
            return self._modulos_cache

        modulos = {}
        self.errores_carga.clear()

        if not self.modules_dir.exists():
            self._modulos_cache = {}
            return self._modulos_cache

        for modulo_dir in self.modules_dir.iterdir():
            if not modulo_dir.is_dir() or modulo_dir.name.startswith("_"):
                continue

            modulo_name = modulo_dir.name
            module_full_name = f"modules.{modulo_name}"
            
            try:
                # Recarga limpia si ya está en sys.modules para evitar estados obsoletos
                if module_full_name in sys.modules:
                    modulo = importlib.reload(sys.modules[module_full_name])
                else:
                    modulo = importlib.import_module(module_full_name)

                if not hasattr(modulo, "CONTENEDOR"):
                    raise ArranqueError(f"El módulo '{modulo_name}' no tiene CONTENEDOR definido.")

                contenedor = modulo.CONTENEDOR
                self._validar_contenedor(contenedor, modulo_name)
                modulos[modulo_name] = contenedor

            except Exception as e:
                error_msg = str(e)
                self.errores_carga[modulo_name] = error_msg
                # Aislamiento de fallo: reportar al DiagnosticoGlobal sin tumbar todo el motor
                try:
                    from core.diagnostico import DiagnosticoGlobal
                    DiagnosticoGlobal.recibir_reporte(
                        modulo=modulo_name,
                        errores=[{"tipo": "error_carga", "detalle": error_msg}]
                    )
                except Exception:
                    pass

        self._modulos_cache = self._resolver_dependencias(modulos)
        return self._modulos_cache

    @staticmethod
    def _validar_contenedor(contenedor: Dict, modulo_name: str) -> None:
        """Valida que el CONTENEDOR de un módulo posea la estructura y tipos requeridos."""
        if not isinstance(contenedor, dict):
            raise ArranqueError(f"El CONTENEDOR de '{modulo_name}' no es un diccionario.")

        campos_requeridos = ["nombre", "rol", "version", "capacidades"]
        for campo in campos_requeridos:
            if campo not in contenedor:
                raise ArranqueError(f"El CONTENEDOR de '{modulo_name}' no tiene el campo obligatorio '{campo}'.")

        if not isinstance(contenedor["capacidades"], dict):
            raise ArranqueError(f"La clave 'capacidades' en '{modulo_name}' no es un diccionario.")

        for capacidad, func in contenedor["capacidades"].items():
            if not callable(func):
                raise ArranqueError(
                    f"La capacidad '{capacidad}' en '{modulo_name}' no es una función. Tipo: {type(func).__name__}"
                )

        if "requiere" in contenedor and not isinstance(contenedor["requiere"], list):
            raise ArranqueError(f"El campo 'requiere' en '{modulo_name}' debe ser una lista.")

    @staticmethod
    def _resolver_dependencias(modulos: Dict[str, Contenedor]) -> Dict[str, Contenedor]:
        """Ordena los módulos topológicamente según sus dependencias declaradas en 'requiere'."""
        ordenados = {}
        visitados = {}  # 0: no visitado, 1: visitando, 2: visitado

        def visitar(name: str):
            if name not in modulos:
                raise ArranqueError(f"El módulo '{name}' es requerido pero no existe o falló al cargarse.")
            if visitados.get(name, 0) == 1:
                raise ArranqueError(f"Dependencia circular detectada que involucra al módulo '{name}'.")
            if visitados.get(name, 0) == 2:
                return

            visitados[name] = 1
            dependencias = modulos[name].get("requiere", [])
            for dep in dependencias:
                visitar(dep)
            visitados[name] = 2
            ordenados[name] = modulos[name]

        for mod_name in modulos:
            if visitados.get(mod_name, 0) == 0:
                visitar(mod_name)

        return ordenados

    @staticmethod
    def _validar_salida_verificar(salida: Any, modulo_name: str) -> None:
        """Valida que la salida del método 'verificar' cumpla con el contrato esperado."""
        if not isinstance(salida, dict):
            raise ValueError(f"La salida de 'verificar' en '{modulo_name}' no es un diccionario.")
        if "coherente" not in salida:
            raise ValueError(f"La salida de 'verificar' en '{modulo_name}' no contiene la clave obligatoria 'coherente'.")

    def ejecutar_modulo(self, modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
        """Ejecuta de forma segura una capacidad específica de un módulo."""
        modulos = self.descubrir_modulos()
        if modulo_name not in modulos:
            raise ValueError(f"Módulo '{modulo_name}' no encontrado o no disponible.")

        contenedor = modulos[modulo_name]
        if capacidad not in contenedor.get("capacidades", {}):
            raise ValueError(f"Capacidad '{capacidad}' no encontrada en el módulo '{modulo_name}'.")

        func = contenedor["capacidades"][capacidad]
        return func(*args, **kwargs)

    def ejecutar_sistema(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la capacidad 'verificar' de todos los módulos disponibles,
        pasando argumentos opcionales si las capacidades los requieren, validando salidas
        e integrando los reportes con DiagnosticoGlobal.
        """
        modulos = self.descubrir_modulos()
        resultados = {}

        diagnostico_global = None
        try:
            from core.diagnostico import DiagnosticoGlobal
            diagnostico_global = DiagnosticoGlobal
        except ImportError:
            pass

        for modulo_name, contenedor in modulos.items():
            if "verificar" in contenedor.get("capacidades", {}):
                try:
                    verificar_func = contenedor["capacidades"]["verificar"]
                    resultado = verificar_func(*args, **kwargs)
                    self._validar_salida_verificar(resultado, modulo_name)
                    resultados[modulo_name] = resultado

                    if not resultado.get("coherente", True) and diagnostico_global:
                        errores = resultado.get("errores", []) + resultado.get("choques", [])
                        diagnostico_global.recibir_reporte(
                            modulo=modulo_name,
                            errores=errores
                        )
                except Exception as e:
                    error_detalle = {
                        "error": str(e),
                        "modulo": modulo_name,
                        "capacidad": "verificar"
                    }
                    resultados[modulo_name] = error_detalle
                    if diagnostico_global:
                        try:
                            diagnostico_global.recibir_reporte(
                                modulo=modulo_name,
                                errores=[{"tipo": "error_ejecucion", "detalle": str(e)}]
                            )
                        except Exception:
                            pass

        return resultados

    def obtener_inventario(self) -> Dict[str, Any]:
        """Obtiene el inventario de todos los módulos que exponen la capacidad 'inventario'."""
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
        """Obtiene todos los axiomas de los módulos que exponen la capacidad 'axiomas'."""
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
        """Obtiene los CONTENEDOR de todos los módulos ordenados por dependencias."""
        return self.descubrir_modulos()

__all__ = ["Engine", "ArranqueError", "Contenedor"]
