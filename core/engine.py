"""
VPSI-TRUTH --- core/engine.py

El Engine es UNICAMENTE un ejecutor de contratos.
- Carga módulos.
- Ejecuta capacidades declaradas en los contratos.
- No tiene lógica de negocio.
- No interpreta resultados.
- No modifica datos.
- No conoce fórmulas, axiomas, ni reportes.
"""

from __future__ import annotations
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ===============================================================
# CONSTANTES GLOBALES: ROLES DE MÓDULOS
# ===============================================================
# Solo define los roles. NADA MÁS.
ROL_AXIOMAS = "AX"
ROL_CONSTANTE = "CT"
ROL_FORMULAS = "FO"
ROL_CALCULATOR = "CA"
ROL_CONTEXTO = "CX"
ROL_TAXONOMIA = "TX"
ROL_REALIDAD = "RE"
ROL_VERIFICACION = "VX"
ROL_CORRELACION_MECANICA = "MC"

# Tupla de roles válidos (solo para validación de duplicados)
ROLES = (
    ROL_AXIOMAS,
    ROL_CONSTANTE,
    ROL_FORMULAS,
    ROL_CALCULATOR,
    ROL_CONTEXTO,
    ROL_TAXONOMIA,
    ROL_REALIDAD,
    ROL_VERIFICACION,
    ROL_CORRELACION_MECANICA,
)

# Módulos obligatorios para el arranque (solo para validación)
OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS, ROL_CORRELACION_MECANICA)

# ===============================================================
# REGISTRO DE MÓDULOS
# ===============================================================
@dataclass
class Contenedor:
    """Representa un módulo. El Engine NO interviene en su lógica."""
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None
    descripcion: Optional[str] = None
    capacidades: Dict[str, str] = field(default_factory=dict)  # capacidad -> nombre_función

    def obtener_funcion(self, capacidad: str) -> Any:
        """Devuelve la función asociada a una capacidad declarada en el contrato."""
        if self.modulo is None:
            return None
        nombre_fn = self.capacidades.get(capacidad)
        if not nombre_fn:
            return None
        return getattr(self.modulo, nombre_fn, None)

    def tiene_capacidad(self, capacidad: str) -> bool:
        """Verifica si el módulo declara y tiene la capacidad."""
        fn = self.obtener_funcion(capacidad)
        return callable(fn)

class Registro:
    """Registro de módulos. Solo carga, NO interviene."""
    def __init__(self, raiz: str):
        self.raiz = Path(raiz)
        self.contenedores: Dict[str, Contenedor] = {}
        self.rechazados: List[Dict] = []

    def descubrir(self) -> Dict[str, Contenedor]:
        """Descubre módulos en el directorio. NO inventa ni modifica nada."""
        self.contenedores = {}
        self.rechazados = []

        if not self.raiz.exists():
            raise Exception(f"Directorio {self.raiz} no existe.")

        ocupados = {}

        for d in sorted(p for p in self.raiz.iterdir() if p.is_dir()):
            if d.name.startswith(("_", ".")):
                continue

            init = d / "__init__.py"
            if not init.exists():
                self.rechazados.append({"ruta": d.name, "razon": "sin __init__.py"})
                continue

            try:
                c = self._cargar(d, init)
            except Exception as e:
                self.rechazados.append({"ruta": d.name, "razon": str(e)})
                continue

            if c.rol in ocupados:
                raise Exception(f"Rol '{c.rol}' duplicado: '{ocupados[c.rol]}' y '{c.nombre}'.")

            ocupados[c.rol] = c.nombre
            self.contenedores[c.nombre] = c

        faltan = [r for r in OBLIGATORIOS if r not in ocupados]
        if faltan:
            raise Exception(f"Módulos obligatorios ausentes: {faltan}")

        return self.contenedores

    def _cargar(self, directorio: Path, init: Path) -> Contenedor:
        """Carga un módulo desde su directorio. NO modifica su comportamiento."""
        clave = f"vpsi_{directorio.name}"
        spec = importlib.util.spec_from_file_location(
            clave, init, submodule_search_locations=[str(directorio)]
        )
        if spec is None or spec.loader is None:
            raise Exception("No se pudo crear spec para el módulo.")

        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)

        meta = getattr(mod, "CONTENEDOR", None)
        if not isinstance(meta, dict):
            raise Exception("Falta el diccionario CONTENEDOR.")

        for k in ("nombre", "rol", "version", "requiere", "descripcion", "capacidades"):
            if k not in meta:
                raise Exception(f"CONTENEDOR sin clave '{k}'.")

        capacidades = meta.get("capacidades")
        if not isinstance(capacidades, dict):
            raise Exception("CONTENEDOR['capacidades'] debe ser un diccionario.")

        return Contenedor(
            nombre=str(meta["nombre"]),
            rol=str(meta["rol"]),
            version=str(meta["version"]),
            requiere=list(meta.get("requiere", [])),
            ruta=directorio.name,
            modulo=mod,
            descripcion=str(meta.get("descripcion", "")),
            capacidades={str(k): str(v) for k, v in capacidades.items()},
        )

    def por_rol(self, rol: str) -> Optional[Contenedor]:
        """Busca un módulo por su rol."""
        for c in self.contenedores.values():
            if c.rol == rol:
                return c
        return None

# ===============================================================
# INVOCADOR (Solo ejecuta, NO interpreta)
# ===============================================================
class Invocador:
    """Invoca capacidades declaradas en los contratos. NO conoce la lógica."""
    def __init__(self):
        self.fallos: List[Dict] = []

    def reiniciar(self):
        """Reinicia el registro de fallos."""
        self.fallos = []

    def ejecutar_capacidad(self, contenedor: Contenedor, capacidad: str, *args, **kwargs) -> Any:
        """
        Ejecuta una capacidad declarada en el contrato.
        Si falla, registra el error y devuelve None.
        """
        fn = contenedor.obtener_funcion(capacidad)
        if not callable(fn):
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "capacidad": capacidad,
                "razon": f"capacidad '{capacidad}' no declarada o función no callable",
            })
            return None

        # Verificar claves requeridas (si la petición es un dict)
        if args and isinstance(args[0], dict):
            peticion = args[0]
            faltan = [r for r in contenedor.requiere if r not in peticion]
            if faltan:
                self.fallos.append({
                    "contenedor": contenedor.nombre,
                    "rol": contenedor.rol,
                    "capacidad": capacidad,
                    "razon": f"petición sin claves: {faltan}",
                })
                return None

        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "capacidad": capacidad,
                "razon": f"{type(e).__name__}: {e}",
            })
            return None

# ===============================================================
# ENGINE (Solo ejecutor de contratos)
# ===============================================================
class Engine:
    _AUTORIZADO = "core"  # Solo el core puede ejecutar el Engine

    def __init__(self, raiz_modulos: str, invocador_id: str = _AUTORIZADO):
        """
        Inicializa el Engine:
        - Descubre y carga módulos.
        - Verifica que los obligatorios estén presentes.
        """
        if invocador_id != self._AUTORIZADO:
            raise Exception(f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. Invocador='{invocador_id}'")

        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        # Verificar módulos obligatorios (solo presencia, NO lógica)
        for rol in OBLIGATORIOS:
            if self.registro.por_rol(rol) is None:
                raise Exception(f"Contenedor {rol} no encontrado.")

    def ejecutar_capacidad(self, rol: str, capacidad: str, *args, **kwargs) -> Any:
        """Ejecuta una capacidad de un módulo por su rol."""
        contenedor = self.registro.por_rol(rol)
        if contenedor is None:
            return None
        return self.invocador.ejecutar_capacidad(contenedor, capacidad, *args, **kwargs)

    def ejecutar_contratos(self, peticion: Dict) -> Dict:
        """
        Ejecuta la capacidad 'evaluar' de todos los módulos que la tengan.
        NO asume nada sobre los módulos.
        """
        self.invocador.reiniciar()
        reportes = {}

        for contenedor in self.registro.contenedores.values():
            if contenedor.tiene_capacidad("evaluar"):
                reporte = self.invocador.ejecutar_capacidad(contenedor, "evaluar", peticion)
                if reporte is not None:
                    reportes[contenedor.rol] = reporte

        return {"reportes": reportes, "fallos": self.invocador.fallos}

    def evaluar(self, peticion: Dict) -> Dict:
        """Puerta única de evaluación: ejecuta contratos y devuelve reportes."""
        return self.ejecutar_contratos(peticion)
