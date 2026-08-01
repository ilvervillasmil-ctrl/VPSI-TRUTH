"""
VPSI-TRUTH --- core/engine.py

El Engine es un ejecutor puro de contratos.
- Lee el CONTENEDOR de cada módulo.
- Ejecuta la función declarada en "capacidades" según lo que el contrato indique.
- No asume nada más allá de lo declarado en el contrato.
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
ROL_AXIOMAS = "AX"
ROL_CONSTANTE = "CT"
ROL_FORMULAS = "FO"
ROL_CALCULATOR = "CA"
ROL_CONTEXTO = "CX"
ROL_TAXONOMIA = "TX"
ROL_REALIDAD = "RE"
ROL_VERIFICACION = "VX"
ROL_CORRELACION_MECANICA = "MC"

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

OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS, ROL_CORRELACION_MECANICA)

# ===============================================================
# REGISTRO DE MÓDULOS
# ===============================================================
@dataclass
class Contenedor:
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None
    descripcion: Optional[str] = None
    capacidades: Dict[str, str] = field(default_factory=dict)

    def obtener_funcion(self, capacidad: str) -> Any:
        if self.modulo is None:
            return None
        nombre_fn = self.capacidades.get(capacidad)
        if not nombre_fn:
            return None
        return getattr(self.modulo, nombre_fn, None)

    def tiene_capacidad(self, capacidad: str) -> bool:
        fn = self.obtener_funcion(capacidad)
        return callable(fn)

class Registro:
    def __init__(self, raiz: str):
        self.raiz = Path(raiz)
        self.contenedores: Dict[str, Contenedor] = {}
        self.rechazados: List[Dict] = []

    def descubrir(self) -> Dict[str, Contenedor]:
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
        for c in self.contenedores.values():
            if c.rol == rol:
                return c
        return None

# ===============================================================
# INVOCADOR
# ===============================================================
class Invocador:
    def __init__(self):
        self.fallos: List[Dict] = []

    def reiniciar(self):
        self.fallos = []

    def ejecutar_capacidad(self, contenedor: Contenedor, capacidad: str, *args, **kwargs) -> Any:
        fn = contenedor.obtener_funcion(capacidad)
        if not callable(fn):
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "capacidad": capacidad,
                "razon": f"capacidad '{capacidad}' no declarada o función no callable",
            })
            return None

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
# ENGINE
# ===============================================================
class Engine:
    _AUTORIZADO = "core"

    def __init__(self, raiz_modulos: str, invocador_id: str = _AUTORIZADO):
        if invocador_id != self._AUTORIZADO:
            raise Exception(f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. Invocador='{invocador_id}'")

        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        for rol in OBLIGATORIOS:
            if self.registro.por_rol(rol) is None:
                raise Exception(f"Contenedor {rol} no encontrado.")

        self._verificar_contratos_obligatorios()

    def _verificar_contratos_obligatorios(self):
        ax = self.registro.por_rol(ROL_AXIOMAS)
        if ax is None or not ax.tiene_capacidad("verificar"):
            raise Exception(f"Contenedor {ROL_AXIOMAS} debe declarar capacidad 'verificar'.")

        ct = self.registro.por_rol(ROL_CONSTANTE)
        if ct is None or not ct.tiene_capacidad("alpha") or not ct.tiene_capacidad("beta"):
            raise Exception(f"Contenedor {ROL_CONSTANTE} debe declarar capacidades 'alpha' y 'beta'.")

        fo = self.registro.por_rol(ROL_FORMULAS)
        if fo is None or not fo.capacidades:
            raise Exception(f"Contenedor {ROL_FORMULAS} debe declarar al menos una capacidad.")

        mc = self.registro.por_rol(ROL_CORRELACION_MECANICA)
        if mc is None or not mc.tiene_capacidad("verificar"):
            raise Exception(f"Contenedor {ROL_CORRELACION_MECANICA} debe declarar capacidad 'verificar'.")

        declaraciones = {}
        for c in self.registro.contenedores.values():
            if c.tiene_capacidad("axiomas"):
                result = self.invocador.ejecutar_capacidad(c, "axiomas")
                if result is not None:
                    declaraciones[c.nombre] = result

        informe_mc = self.invocador.ejecutar_capacidad(mc, "verificar")
        if informe_mc is None or not isinstance(informe_mc, dict) or not informe_mc.get("coherente", False):
            choques = informe_mc.get("choques", []) if isinstance(informe_mc, dict) else []
            raise Exception(f"CONTRADICCIÓN MECÁNICA.\n{choques}")

        informe_ax = self.invocador.ejecutar_capacidad(ax, "verificar", declaraciones)
        if informe_ax is None or not isinstance(informe_ax, dict) or not informe_ax.get("coherente", False):
            choques = informe_ax.get("choques", []) if isinstance(informe_ax, dict) else []
            raise Exception(f"CONTRADICCIÓN AXIOMÁTICA.\n{choques}")

    def ejecutar_capacidad(self, rol: str, capacidad: str, *args, **kwargs) -> Any:
        contenedor = self.registro.por_rol(rol)
        if contenedor is None:
            return None
        return self.invocador.ejecutar_capacidad(contenedor, capacidad, *args, **kwargs)

    def ejecutar_contratos(self, peticion: Dict) -> Dict:
        self.invocador.reiniciar()
        reportes = {}

        for contenedor in self.registro.contenedores.values():
            if not contenedor.tiene_capacidad("evaluar"):
                continue
            reporte = self.invocador.ejecutar_capacidad(contenedor, "evaluar", peticion)
            if isinstance(reporte, dict):
                reportes[contenedor.rol] = reporte

        return {"reportes": reportes, "fallos": self.invocador.fallos}

    def evaluar(self, peticion: Dict) -> Dict:
        return self.ejecutar_contratos(peticion)
