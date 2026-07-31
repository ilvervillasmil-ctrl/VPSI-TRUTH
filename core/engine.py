"""
VPSI-TRUTH --- core/engine.py

El Engine es el ejecutor de contratos del framework VPSI-TRUTH.
- Conoce absolutamente todo sobre el sistema: módulos, contratos, dependencias, estados y capacidades.
- Su capacidad de actuar está estrictamente limitada por los contratos de los módulos.
- Descubre y carga módulos sin intervenir en su lógica interna.
- Ejecuta las operaciones definidas en los contratos de los módulos.
- Recopila los reportes generados por los módulos y los unifica para el Omega Report.
- No conoce funciones concretas, lógica de negocio, ni interpreta resultados.
"""

from __future__ import annotations
import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

# ===============================================================
# CONSTANTES GLOBALES: ROLES DE MÓDULOS
# ===============================================================
# Nota: Los roles son parte de la arquitectura, no de la lógica de negocio.
ROL_AXIOMAS = "AX"
ROL_CONSTANTE = "CT"
ROL_FORMULAS = "FO"
ROL_CALCULATOR = "CA"
ROL_CONTEXTO = "CX"
ROL_TAXONOMIA = "TX"
ROL_REALIDAD = "RE"
ROL_VERIFICACION = "VX"
ROL_CORRELACION_MECANICA = "MC"

# Tupla de roles válidos (parte de la arquitectura)
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

# Módulos obligatorios para el arranque (parte de la arquitectura)
OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS, ROL_CORRELACION_MECANICA)

# ===============================================================
# ESTADO INDEFINIDO (UNDEFINED)
# ===============================================================
class _Undefined:
    """Estado para valores sin evidencia. Propaga limpiamente sin intervencionismo."""
    __slots__ = ()

    def __repr__(self):
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, otro):
        return isinstance(otro, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")

UNDEFINED = _Undefined()

def es_undefined(v) -> bool:
    """Verifica si un valor es UNDEFINED."""
    return v is UNDEFINED or isinstance(v, _Undefined)

# ===============================================================
# EXCEPCIONES (CONTRATOS Y ERRORES)
# ===============================================================
class AutoridadError(Exception):
    """Solo el core puede ejecutar el Engine."""
    pass

class ContratoError(Exception):
    """Un módulo no cumple con su interfaz."""
    pass

class ArranqueError(Exception):
    """Falta un módulo obligatorio o hay contradicción axiomática/mecánica."""
    pass

# ===============================================================
# REGISTRO DE MÓDULOS (DESCUBRIMIENTO Y CARGA)
# ===============================================================
CLAVES_CONTENEDOR = ("nombre", "rol", "version", "requiere", "descripcion", "operacion_principal")

@dataclass
class Contenedor:
    """Representa un módulo en el sistema. No interviene en su lógica interna."""
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None
    descripcion: Optional[str] = None
    operacion_principal: Optional[str] = None  # Nombre de la función principal del contrato

    def fn(self, nombre: str) -> Any:
        """Devuelve una función del módulo (sin modificar su comportamiento)."""
        if self.modulo is None:
            return None
        return getattr(self.modulo, nombre, None)

    def como_dict(self) -> Dict:
        """Metadata del módulo (solo lectura)."""
        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "version": self.version,
            "requiere": list(self.requiere),
            "ruta": self.ruta,
            "descripcion": self.descripcion,
            "operacion_principal": self.operacion_principal,
        }

class Registro:
    """Registro de módulos. Descubre y carga sin alterar su esencia."""
    def __init__(self, raiz: str):
        self.raiz = Path(raiz)
        self.contenedores: Dict[str, Contenedor] = {}
        self.rechazados: List[Dict] = []

    def descubrir(self) -> Dict[str, Contenedor]:
        """Descubre módulos en el directorio. No inventa rutas ni maquilla vacíos."""
        self.contenedores = {}
        self.rechazados = []

        if not self.raiz.exists():
            raise ArranqueError(f"Directorio {self.raiz} no existe.")

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
            except ContratoError as e:
                self.rechazados.append({"ruta": d.name, "razon": str(e)})
                continue
            except Exception as e:
                self.rechazados.append({"ruta": d.name, "razon": f"{type(e).__name__}: {e}"})
                continue

            if c.rol in ocupados:
                raise ArranqueError(f"Rol '{c.rol}' duplicado: '{ocupados[c.rol]}' y '{c.nombre}'.")

            ocupados[c.rol] = c.nombre
            self.contenedores[c.nombre] = c

        faltan = [r for r in OBLIGATORIOS if r not in ocupados]
        if faltan:
            raise ArranqueError(f"Módulos obligatorios ausentes: {faltan}")

        return self.contenedores

    def _cargar(self, directorio: Path, init: Path) -> Contenedor:
        """Carga un módulo desde su directorio. No modifica su comportamiento."""
        clave = f"vpsi_{directorio.name}"
        spec = importlib.util.spec_from_file_location(
            clave, init, submodule_search_locations=[str(directorio)]
        )
        if spec is None or spec.loader is None:
            raise ContratoError("No se pudo crear spec para el módulo.")

        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)

        meta = getattr(mod, "CONTENEDOR", None)
        if not isinstance(meta, dict):
            raise ContratoError("Falta el diccionario CONTENEDOR.")

        for k in CLAVES_CONTENEDOR:
            if k not in meta:
                raise ContratoError(f"CONTENEDOR sin clave '{k}'.")

        return Contenedor(
            nombre=str(meta["nombre"]),
            rol=str(meta["rol"]),
            version=str(meta["version"]),
            requiere=list(meta.get("requiere", [])),
            ruta=directorio.name,
            modulo=mod,
            descripcion=str(meta.get("descripcion", "")),
            operacion_principal=str(meta.get("operacion_principal", None)),
        )

    def por_rol(self, rol: str) -> Optional[Contenedor]:
        """Busca un módulo por su rol (sin asumir su existencia)."""
        for c in self.contenedores.values():
            if c.rol == rol:
                return c
        return None

    def resumen(self) -> Dict:
        """Resumen de módulos cargados y rechazados (transparencia total)."""
        return {
            "cargados": [c.como_dict() for c in self.contenedores.values()],
            "rechazados": self.rechazados,
            "roles": {c.rol: c.nombre for c in self.contenedores.values()},
            "roles_vacios": [r for r in ROLES if r not in {c.rol for c in self.contenedores.values()}],
        }

# ===============================================================
# INVOCADOR (DELEGACIÓN ESTRICTA)
# ===============================================================
class Invocador:
    """Invoca funciones de módulos sin alterar su lógica. Registra fallos sin intervencionismo."""
    def __init__(self):
        self.fallos: List[Dict] = []

    def reiniciar(self):
        """Reinicia el registro de fallos (para cada evaluación independiente)."""
        self.fallos = []

    def llamar(self, contenedor: Contenedor, nombre_fn: str, peticion: Dict) -> Any:
        """
        Invoca una función de módulo.
        Si falla, registra el error y devuelve UNDEFINED (Organic Fail-Fast).
        """
        fn = contenedor.fn(nombre_fn)
        if not callable(fn):
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"no expone {nombre_fn}()",
            })
            return UNDEFINED

        # Verificar que la petición tenga las claves requeridas por el módulo
        faltan = [r for r in contenedor.requiere if r not in peticion]
        if faltan:
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"petición sin claves: {faltan}",
            })
            return UNDEFINED

        try:
            return fn(peticion)
        except Exception as e:
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"{type(e).__name__}: {e}",
                "traza": traceback.format_exc(limit=3),
            })
            return UNDEFINED

# ===============================================================
# ENGINE (EJECUTOR DE CONTRATOS)
# ===============================================================
class Engine:
    _AUTORIZADO = "core"  # Solo el core puede ejecutar el Engine

    def __init__(self, raiz_modulos: str, invocador_id: str = _AUTORIZADO, verificar_axiomas: bool = True):
        """
        Inicializa el Engine:
        - Descubre y carga módulos.
        - Verifica que los obligatorios (AX, CT, FO, MC) estén presentes.
        - Verifica coherencia axiomática (AX) y mecánica (MC) si se solicita.
        - Conoce absolutamente todo sobre el sistema, pero su acción está limitada por los contratos.
        """
        if invocador_id != self._AUTORIZADO:
            raise AutoridadError(f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. Invocador='{invocador_id}'")

        # Descubrir módulos (conocimiento absoluto)
        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        # Verificar módulos obligatorios (parte de la arquitectura)
        for rol in OBLIGATORIOS:
            if self.registro.por_rol(rol) is None:
                raise ArranqueError(f"Contenedor {rol} no encontrado.")

        # Verificar coherencia axiomática (AX) y mecánica (MC) (acción limitada por contrato)
        if verificar_axiomas:
            self._verificar_contratos_obligatorios()

    # ---------------- VERIFICACIÓN DE CONTRATOS OBLIGATORIOS ----------------
    def _verificar_contratos_obligatorios(self) -> None:
        """Verifica que los módulos obligatorios cumplan con sus contratos."""
        # Verificar AX (debe exponer "barrer" y "operacion_principal" debe estar definida)
        ax = self.registro.por_rol(ROL_AXIOMAS)
        if ax is None:
            raise ArranqueError(f"Contenedor {ROL_AXIOMAS} no encontrado.")
        if not callable(ax.fn("barrer")):
            raise ContratoError(f"Contenedor {ROL_AXIOMAS} debe exponer barrer().")
        if ax.operacion_principal is None:
            raise ContratoError(f"Contenedor {ROL_AXIOMAS} debe definir operacion_principal en CONTENEDOR.")

        # Verificar CT (debe exponer "ALPHA" y "BETA")
        ct = self.registro.por_rol(ROL_CONSTANTE)
        if ct is None:
            raise ArranqueError(f"Contenedor {ROL_CONSTANTE} no encontrado.")
        if ct.fn("ALPHA") is None or ct.fn("BETA") is None:
            raise ContratoError(f"Contenedor {ROL_CONSTANTE} debe exponer ALPHA y BETA.")

        # Verificar FO (debe exponer su operación principal)
        fo = self.registro.por_rol(ROL_FORMULAS)
        if fo is None:
            raise ArranqueError(f"Contenedor {ROL_FORMULAS} no encontrado.")
        if fo.operacion_principal is None:
            raise ContratoError(f"Contenedor {ROL_FORMULAS} debe definir operacion_principal en CONTENEDOR.")

        # Verificar MC (debe exponer "barrer")
        mc = self.registro.por_rol(ROL_CORRELACION_MECANICA)
        if mc is None:
            raise ArranqueError(f"Contenedor {ROL_CORRELACION_MECANICA} no encontrado.")
        if not callable(mc.fn("barrer")):
            raise ContratoError(f"Contenedor {ROL_CORRELACION_MECANICA} debe exponer barrer().")

        # Verificar correlación mecánica (MC)
        informe_mc = mc.fn("barrer")()
        if not informe_mc.get("coherente", False):
            choques_str = "\n".join(informe_mc.get("choques", []))
            raise ArranqueError(f"CONTRADICCIÓN MECÁNICA. Los módulos no pueden ejecutarse en orden.\n{choques_str}")

        # Verificar coherencia axiomática (AX)
        declaraciones = {}
        for c in self.registro.contenedores.values():
            g = c.fn("axiomas")
            if callable(g):
                declaraciones[c.nombre] = g()

        informe_ax = ax.fn("barrer")(declaraciones)
        if not isinstance(informe_ax, dict) or "coherente" not in informe_ax:
            raise ContratoError("barrer() debe devolver dict con 'coherente'.")
        if not informe_ax["coherente"]:
            choques_str = "\n".join(
                f"  - {ch.get('tipo', 'Desconocido')}: {ch.get('mensaje', 'Sin mensaje')}"
                for ch in informe_ax.get("choques", [])
            )
            raise ArranqueError(f"CONTRADICCIÓN AXIOMÁTICA. {choques_str}")

    # ---------------- EJECUCIÓN DE CONTRATOS ----------------
    def ejecutar_contratos(self, peticion: Dict) -> Dict:
        """
        Ejecuta la operación principal de cada módulo según su contrato.
        El Engine NO conoce funciones concretas, solo ejecuta lo definido en los contratos.
        """
        self.invocador.reiniciar()
        reportes = {}

        # Recorrer todos los módulos registrados y ejecutar su operación principal
        for contenedor in self.registro.contenedores.values():
            if contenedor.operacion_principal is None:
                continue  # Saltar módulos sin operación principal definida

            # Ejecutar la operación principal del módulo
            reporte = self.invocador.llamar(contenedor, contenedor.operacion_principal, peticion)
            if isinstance(reporte, dict):
                reportes[contenedor.rol] = reporte

        return {
            "reportes": reportes,
            "fallos": list(self.invocador.fallos),
        }

    # ---------------- EVALUACIÓN (EJECUCIÓN DE CONTRATOS) ----------------
    def evaluar(self, peticion: Dict) -> Dict:
        """
        Evalúa una petición ejecutando los contratos de los módulos.
        El Engine NO interpreta resultados, solo recopila reportes.
        """
        return self.ejecutar_contratos(peticion)

    # ---------------- EVALUACIÓN VIGILADA (CONTRATOS) ----------------
    def evaluar_vigilado(self, peticion: Dict) -> Dict:
        """
        Puerta única de evaluación.
        Verifica que los módulos obligatorios estén presentes antes de evaluar.
        """
        try:
            for rol in OBLIGATORIOS:
                if self.registro.por_rol(rol) is None:
                    raise ArranqueError(f"Contenedor {rol} no encontrado.")
        except ArranqueError as e:
            return {
                "estado": "PENDIENTE",
                "detenido_en": "centinela",
                "rol_pendiente": str(e).split(" ")[1],  # Extrae el rol del mensaje
                "razon": str(e),
                "accion": f"Montar el contenedor {str(e).split(' ')[1]} para desbloquear.",
                "reportes": {},
                "fallos": [],
            }
        return self.evaluar(peticion)

    # ---------------- CENSO Y VERIFICACIÓN (CONOCIMIENTO ABSOLUTO) ----------------
    def censar(self) -> Dict:
        """Devuelve el estado de los módulos cargados (transparencia total)."""
        return self.registro.resumen()

    def inventario(self) -> Dict:
        """Devuelve un resumen del estado del Engine y sus módulos (conocimiento absoluto)."""
        inv = self.registro.resumen()
        inv["contenido"] = {}
        for c in self.registro.contenedores.values():
            g = c.fn("inventario")
            if callable(g):
                try:
                    inv["contenido"][c.nombre] = g()
                except Exception as e:
                    inv["contenido"][c.nombre] = {"error": str(e)}
        return inv
