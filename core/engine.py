# ==============================================================
# INICIO: core/engine.py — versión completa y limpia
# ==============================================================

# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- core/engine.py

Nucleo del repositorio.
Integra cada modulo solo a partir de su CONTENEDOR.
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional


# ===============================================================
# EXCEPCIONES Y REGISTRO
# ===============================================================
class ArranqueError(Exception):
    pass


class Contenedor:
    def __init__(self, nombre: str, rol: str, version: str, modulo: Any, ruta: Path, meta: Dict[str, Any]) -> None:
        self.nombre = nombre
        self.rol = rol
        self.version = version
        self.modulo = modulo
        self.ruta = ruta
        self.meta = meta
        self.capacidades = meta.get("capacidades", {})
        self.requiere = meta.get("requiere", [])
        
        # Recuperación explícita o fallback universal del resolvedor fn()
        resolver = meta.get("fn")
        if callable(resolver):
            self._fn_custom = resolver
        else:
            self._fn_custom = None

    def tiene(self, capacidad: str) -> bool:
        if capacidad not in self.capacidades:
            return False
        ref = self.capacidades[capacidad]
        if callable(ref):
            return True
        return self.modulo is not None and callable(getattr(self.modulo, str(ref), None))

    def fn(self, clave: str) -> Any:
        """Método de resolución unificado para que el Engine y el auditor forense consulten capacidades."""
        if self._fn_custom is not None:
            try:
                res = self._fn_custom(clave)
                if res is not None:
                    return res
            except Exception:
                pass
                
        ref = self.capacidades.get(clave)
        if callable(ref):
            return ref
        if isinstance(ref, str) and self.modulo is not None:
            return getattr(self.modulo, ref, None)
        return None


class RegistroModulos:
    def __init__(self) -> None:
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {}

    def registrar(self, cont: Contenedor) -> None:
        self.contenedores[cont.nombre] = cont
        self.por_rol.setdefault(cont.rol, []).append(cont)

    def primero(self, clave_rol_o_nombre: str) -> Optional[Contenedor]:
        if clave_rol_o_nombre in self.contenedores:
            return self.contenedores[clave_rol_o_nombre]
        lista = self.por_rol.get(clave_rol_o_nombre)
        return lista[0] if lista else None

    def total(self) -> int:
        return len(self.contenedores)


# ===============================================================
# ENGINE
# ===============================================================
class Engine:
    VERSION = "12.0"

    def __init__(
        self,
        raiz_modulos: str | Path,
        invocador_id: str = "core",
        strict: bool = True,
    ) -> None:
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id = invocador_id
        self.strict = strict
        self.fallos: List[Dict[str, Any]] = []
        self.errores_arranque: List[str] = []
        self.informe_axiomas: Optional[Dict[str, Any]] = None
        self.estado = "NO_INICIADO"
        
        # Inicialización del registro central
        self.registro = RegistroModulos()

        # ==========================================================
        # INICIO: Atributo resultados_evaluacion en core/engine.py
        # ==========================================================
        self.resultados_evaluacion = []
        # ==========================================================
        # FIN: Atributo resultados_evaluacion en core/engine.py
        # ==========================================================

        # Carga automática de todos los módulos mediante su CONTENEDOR
        self._cargar_modulos_automaticos()

        if self.errores_arranque:
            self.estado = "RECHAZADO"
            if self.strict:
                raise ArranqueError(
                    "Engine no pudo arrancar:\n  - "
                    + "\n  - ".join(self.errores_arranque)
                )
        else:
            self.estado = "OPERATIVO"

    # ===============================================================
    # CARGADOR DE MÓDULOS / CONTENEDORES
    # ===============================================================
    def _cargar_modulos_automaticos(self) -> None:
        """Escanea dinámicamente la carpeta de módulos y registra cualquier CONTENEDOR válido."""
        if not self.raiz.is_dir():
            return

        for path_dir in sorted(self.raiz.iterdir()):
            if not path_dir.is_dir():
                continue
            
            init_path = path_dir / "__init__.py"
            if not init_path.is_file():
                continue

            nombre_mod = f"vpsi_dinamico_{path_dir.name}"
            spec = importlib.util.spec_from_file_location(
                nombre_mod,
                init_path,
                submodule_search_locations=[str(path_dir)],
            )
            if spec is None or spec.loader is None:
                continue

            mod = importlib.util.module_from_spec(spec)
            sys.modules[nombre_mod] = mod
            try:
                spec.loader.exec_module(mod)
            except Exception as e:
                self.errores_arranque.append(
                    f"{path_dir.name}: import fallo: {type(e).__name__}: {e}"
                )
                continue

            meta = getattr(mod, "CONTENEDOR", None)
            if not isinstance(meta, dict):
                continue

            nombre = meta.get("nombre", path_dir.name)
            rol = meta.get("rol", "GEN")
            version = str(meta.get("version", "1.0"))

            contenedor = Contenedor(
                nombre=nombre,
                rol=rol,
                version=version,
                modulo=mod,
                ruta=init_path,
                meta=meta,
            )
            self.registro.registrar(contenedor)

            caps = meta.get("capacidades", {})
            fn_validar = caps.get("verificar") or caps.get("barrer") or caps.get("evaluar")
            if fn_validar:
                fn = fn_validar if callable(fn_validar) else getattr(mod, str(fn_validar), None)
                if callable(fn):
                    try:
                        informe = fn()
                        if isinstance(informe, dict) and not informe.get("coherente", True):
                            self.errores_arranque.append(
                                f"{rol}: módulo incoherente según su contrato"
                            )
                    except Exception as e:
                        self.errores_arranque.append(
                            f"{rol}: error ejecutando validación: {type(e).__name__}: {e}"
                        )

    # ==========================================================
    # INICIO: Método censar() para la clase Engine
    # ==========================================================
    def censar(self) -> dict:
        """Devuelve un censo estructurado de los contenedores y roles cargados dinámicamente."""
        cargados = []
        roles_dict = {}
        for nombre, cont in self.registro.contenedores.items():
            cargados.append({"nombre": cont.nombre, "rol": cont.rol, "version": cont.version})
            roles_dict.setdefault(cont.rol, []).append(cont.nombre)
            
        return {
            "total": self.registro.total() if hasattr(self.registro, "total") else len(self.registro.contenedores),
            "roles": roles_dict,
            "roles_vacios": [],
            "rechazados": [],
            "cargados": cargados,
        }
    # ==========================================================
    # FIN: Método censar() para la clase Engine
    # ==========================================================

    # ===============================================================
    # EJECUCIÓN DINÁMICA DE CONTRATOS Y EXPLORACIÓN DE CARPETAS
    # ===============================================================
    def ejecutar_contratos_y_explorar(self) -> Dict[str, Any]:
        """
        Ejecuta de manera autónoma cada capacidad declarada en los contratos 
        de cada módulo y permite explorar cualquier subcarpeta o recurso interno 
        presente en la ruta del módulo.
        """
        resultados_ejecucion = {}

        for nombre_mod, contenedor in self.registro.contenedores.items():
            rol = contenedor.rol
            capacidades = contenedor.capacidades
            modulo_ref = contenedor.modulo
            ruta_modulo = contenedor.ruta.parent

            # 1. Exploración de subcarpetas y archivos internos del módulo
            recursos_internos = [
                p.relative_to(self.raiz) for p in ruta_modulo.glob("**/*") if p.is_file()
            ]

            resultados_modulo = {
                "rol": rol,
                "version": contenedor.version,
                "ruta_base": str(ruta_modulo),
                "archivos_internos": [str(r) for r in recursos_internos],
                "capacidades_ejecutadas": {}
            }

            # 2. Ejecución dinámica de cada contrato/capacidad declarada en el contenedor
            for clave_cap in capacidades.keys():
                fn = contenedor.fn(clave_cap)

                if callable(fn):
                    try:
                        salida = fn()
                        resultados_modulo["capacidades_ejecutadas"][clave_cap] = {
                            "estado": "EXITO",
                            "resultado": salida
                        }
                    except Exception as e:
                        resultados_modulo["capacidades_ejecutadas"][clave_cap] = {
                            "estado": "ERROR_EJECUCION",
                            "error": f"{type(e).__name__}: {e}"
                        }
                else:
                    resultados_modulo["capacidades_ejecutadas"][clave_cap] = {
                        "estado": "NO_CALLABLE",
                        "error": "La capacidad declarada no apunta a una función ejecutable"
                    }

            resultados_ejecucion[nombre_mod] = resultados_modulo

        return resultados_ejecucion


# ===============================================================
# LISTA MAESTRA UNIVERSAL DE CAPACIDADES PARA TODOS LOS INI
# ===============================================================
UNIVERSAL_CAPACIDADES_MAP = {
    "verificar": "barrer",
    "barrer": "barrer",
    "verificar_salida": "verificar_salida",
    "inventario": "inventario",
    "meta": "meta",
    "axiomas": "axiomas",
    "generatividad": "generatividad",
    "resolver": "resolver",
    "listar": "listar",
    "listar_por_idioma": "listar_por_idioma",
    "cargar": "cargar",
    "cargar_todos": "cargar_todos",
    "cargar_idioma": "cargar_idioma",
    "definir": "definir",
    "significado": "significado",
    "palabras": "palabras",
    "inyectar_en_peticion": "inyectar_en_peticion",
}


def obtener_funcion_universal(capacidad_clave: str) -> str:
    return UNIVERSAL_CAPACIDADES_MAP.get(capacidad_clave, capacidad_clave)


# ==============================================================
# FIN: core/engine.py — versión completa y limpia
# (Pegue aquí cualquier código nuevo que se agregue en el futuro)
# ==============================================================
