"""
VPSI-TRUTH --- core/engine.py

El Engine es el ejecutor universal de contratos del framework VPSI-TRUTH.

Principio fundamental:
- Posee conocimiento completo de la arquitectura (módulos, contratos, dependencias,
  estados, capacidades, variables, archivos internos y estructura de cada módulo).
- Su capacidad de actuación está estrictamente limitada por lo que cada contrato
  declara explícitamente en CONTENEDOR["capacidades"].
- Nunca inventa operaciones.
- Nunca modifica resultados.
- Nunca sustituye la lógica de un módulo.
- Nunca interpreta la información producida por un módulo.
- Todo comportamiento de acción proviene exclusivamente de los contratos.
"""

from __future__ import annotations
import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    """Un módulo no cumple con su interfaz / contrato."""
    pass

class ArranqueError(Exception):
    """Falta un módulo obligatorio o hay contradicción axiomática/mecánica."""
    pass

# ===============================================================
# REGISTRO DE MÓDULOS (DESCUBRIMIENTO Y CARGA)
# ===============================================================
# Claves mínimas obligatorias del contrato CONTENEDOR
CLAVES_CONTENEDOR = (
    "nombre",
    "rol",
    "version",
    "requiere",
    "descripcion",
    "capacidades",
)

@dataclass
class Contenedor:
    """
    Representa un módulo en el sistema.
    El Engine tiene conocimiento total de él, pero nunca interviene en su lógica interna.
    Toda acción se obtiene exclusivamente del contrato.
    """
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None
    descripcion: Optional[str] = None
    capacidades: Dict[str, str] = field(default_factory=dict)  # capacidad -> nombre_función

    def obtener_funcion(self, capacidad: str) -> Any:
        """
        Devuelve la función asociada a una capacidad declarada en el contrato.
        Nunca asume nombres. Solo consulta el contrato.
        """
        if self.modulo is None:
            return None
        nombre_fn = self.capacidades.get(capacidad)
        if not nombre_fn:
            return None
        return getattr(self.modulo, nombre_fn, None)

    def tiene_capacidad(self, capacidad: str) -> bool:
        """Indica si el contrato declara la capacidad y la función existe y es callable."""
        fn = self.obtener_funcion(capacidad)
        return callable(fn)

    def como_dict(self) -> Dict:
        """Metadata del módulo (solo lectura)."""
        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "version": self.version,
            "requiere": list(self.requiere),
            "ruta": self.ruta,
            "descripcion": self.descripcion,
            "capacidades": dict(self.capacidades),
        }

    def conocimiento_completo(self) -> Dict:
        """
        Devuelve todo lo que el Engine conoce de este módulo
        (introspección total, sin actuar).
        """
        info = self.como_dict()
        if self.modulo is None:
            info["atributos"] = {}
            info["callables"] = []
            return info

        atributos = {}
        callables = []
        for nombre in dir(self.modulo):
            if nombre.startswith("_"):
                continue
            try:
                valor = getattr(self.modulo, nombre)
                if callable(valor):
                    callables.append(nombre)
                else:
                    # Solo valores simples para no saturar
                    if isinstance(valor, (str, int, float, bool, type(None))):
                        atributos[nombre] = valor
                    else:
                        atributos[nombre] = repr(valor)[:120]
            except Exception:
                atributos[nombre] = "<error al leer>"

        info["atributos"] = atributos
        info["callables"] = callables
        return info

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
                raise ArranqueError(
                    f"Rol '{c.rol}' duplicado: '{ocupados[c.rol]}' y '{c.nombre}'."
                )

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

        capacidades = meta.get("capacidades")
        if not isinstance(capacidades, dict):
            raise ContratoError("CONTENEDOR['capacidades'] debe ser un diccionario.")

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
            "roles_vacios": [
                r for r in ROLES
                if r not in {c.rol for c in self.contenedores.values()}
            ],
        }

    def conocimiento_total(self) -> Dict:
        """
        Devuelve el conocimiento completo que el Engine tiene del sistema.
        Esto es introspección pura: no ejecuta ninguna capacidad.
        """
        return {
            "raiz": str(self.raiz),
            "modulos": {
                nombre: c.conocimiento_completo()
                for nombre, c in self.contenedores.items()
            },
            "rechazados": self.rechazados,
            "roles_ocupados": {
                c.rol: c.nombre for c in self.contenedores.values()
            },
            "roles_vacios": [
                r for r in ROLES
                if r not in {c.rol for c in self.contenedores.values()}
            ],
        }

# ===============================================================
# INVOCADOR (DELEGACIÓN ESTRICTA POR CAPACIDAD)
# ===============================================================
class Invocador:
    """
    Invoca capacidades declaradas en los contratos.
    Nunca conoce nombres de funciones. Solo usa el contrato.
    """
    def __init__(self):
        self.fallos: List[Dict] = []

    def reiniciar(self):
        """Reinicia el registro de fallos (para cada evaluación independiente)."""
        self.fallos = []

    def ejecutar_capacidad(
        self,
        contenedor: Contenedor,
        capacidad: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Ejecuta una capacidad declarada en el contrato del módulo.
        Si la capacidad no existe o falla, registra el error y devuelve UNDEFINED.
        """
        fn = contenedor.obtener_funcion(capacidad)
        if not callable(fn):
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "capacidad": capacidad,
                "razon": f"capacidad '{capacidad}' no declarada o función no callable",
            })
            return UNDEFINED

        # Verificar claves requeridas solo cuando se pasa una petición (dict)
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
                return UNDEFINED

        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "capacidad": capacidad,
                "razon": f"{type(e).__name__}: {e}",
                "traza": traceback.format_exc(limit=3),
            })
            return UNDEFINED

# ===============================================================
# ENGINE (EJECUTOR UNIVERSAL DE CONTRATOS)
# ===============================================================
class Engine:
    _AUTORIZADO = "core"  # Solo el core puede ejecutar el Engine

    def __init__(
        self,
        raiz_modulos: str,
        invocador_id: str = _AUTORIZADO,
        verificar_contratos: bool = True,
    ):
        """
        Inicializa el Engine:

        1. Descubre y carga todos los módulos (conocimiento total).
        2. Valida que los contratos de los módulos obligatorios declaren
           las capacidades mínimas requeridas.
        3. Ejecuta las verificaciones de coherencia (AX y MC) exclusivamente
           a través de las capacidades declaradas en los contratos.
        4. Queda listo para actuar solo según lo que cada contrato autorice.
        """
        if invocador_id != self._AUTORIZADO:
            raise AutoridadError(
                f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. "
                f"Invocador='{invocador_id}'"
            )

        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        # Verificar presencia de módulos obligatorios
        for rol in OBLIGATORIOS:
            if self.registro.por_rol(rol) is None:
                raise ArranqueError(f"Contenedor {rol} no encontrado.")

        if verificar_contratos:
            self._verificar_contratos_obligatorios()

    # ---------------- VERIFICACIÓN DE CONTRATOS OBLIGATORIOS ----------------
    def _verificar_contratos_obligatorios(self) -> None:
        """
        Verifica que los módulos obligatorios declaren las capacidades mínimas
        necesarias para el arranque. Todo se obtiene del contrato.
        El Engine conoce los módulos, pero solo actúa por lo declarado.
        """
        # AX debe declarar capacidad de verificación
        ax = self.registro.por_rol(ROL_AXIOMAS)
        if ax is None:
            raise ArranqueError(f"Contenedor {ROL_AXIOMAS} no encontrado.")
        if not ax.tiene_capacidad("verificar"):
            raise ContratoError(
                f"Contenedor {ROL_AXIOMAS} debe declarar capacidad 'verificar'."
            )

        # CT debe declarar capacidades de constantes
        ct = self.registro.por_rol(ROL_CONSTANTE)
        if ct is None:
            raise ArranqueError(f"Contenedor {ROL_CONSTANTE} no encontrado.")
        if not ct.tiene_capacidad("alpha") or not ct.tiene_capacidad("beta"):
            raise ContratoError(
                f"Contenedor {ROL_CONSTANTE} debe declarar capacidades 'alpha' y 'beta'."
            )

        # FO debe declarar al menos una capacidad
        fo = self.registro.por_rol(ROL_FORMULAS)
        if fo is None:
            raise ArranqueError(f"Contenedor {ROL_FORMULAS} no encontrado.")
        if not fo.capacidades:
            raise ContratoError(
                f"Contenedor {ROL_FORMULAS} debe declarar al menos una capacidad."
            )

        # MC debe declarar capacidad de verificación
        mc = self.registro.por_rol(ROL_CORRELACION_MECANICA)
        if mc is None:
            raise ArranqueError(f"Contenedor {ROL_CORRELACION_MECANICA} no encontrado.")
        if not mc.tiene_capacidad("verificar"):
            raise ContratoError(
                f"Contenedor {ROL_CORRELACION_MECANICA} debe declarar capacidad 'verificar'."
            )

        # --- Verificación mecánica (solo a través de la capacidad declarada) ---
        informe_mc = self.invocador.ejecutar_capacidad(mc, "verificar")
        if es_undefined(informe_mc):
            raise ArranqueError("Fallo al ejecutar capacidad 'verificar' de MC.")
        if not isinstance(informe_mc, dict) or not informe_mc.get("coherente", False):
            choques = informe_mc.get("choques", []) if isinstance(informe_mc, dict) else []
            choques_str = "\n".join(str(c) for c in choques)
            raise ArranqueError(
                f"CONTRADICCIÓN MECÁNICA. Los módulos no pueden ejecutarse en orden.\n{choques_str}"
            )

        # --- Verificación axiomática (solo a través de la capacidad declarada) ---
        declaraciones = {}
        for c in self.registro.contenedores.values():
            if c.tiene_capacidad("axiomas"):
                result = self.invocador.ejecutar_capacidad(c, "axiomas")
                if not es_undefined(result):
                    declaraciones[c.nombre] = result

        informe_ax = self.invocador.ejecutar_capacidad(ax, "verificar", declaraciones)
        if es_undefined(informe_ax):
            raise ArranqueError("Fallo al ejecutar capacidad 'verificar' de AX.")
        if not isinstance(informe_ax, dict) or "coherente" not in informe_ax:
            raise ContratoError(
                "Capacidad 'verificar' de AX debe devolver dict con clave 'coherente'."
            )
        if not informe_ax["coherente"]:
            choques = informe_ax.get("choques", [])
            choques_str = "\n".join(
                f"  - {ch.get('tipo', 'Desconocido')}: {ch.get('mensaje', 'Sin mensaje')}"
                if isinstance(ch, dict) else f"  - {ch}"
                for ch in choques
            )
            raise ArranqueError(f"CONTRADICCIÓN AXIOMÁTICA.\n{choques_str}")

    # ---------------- EJECUCIÓN DE CAPACIDADES (ÚNICA VÍA DE ACCIÓN) ----------------
    def ejecutar_capacidad(
        self,
        rol: str,
        capacidad: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Ejecuta una capacidad de un módulo identificado por rol.
        El Engine solo consulta el contrato. Nunca conoce el nombre real de la función.
        """
        contenedor = self.registro.por_rol(rol)
        if contenedor is None:
            return UNDEFINED
        return self.invocador.ejecutar_capacidad(contenedor, capacidad, *args, **kwargs)

    def ejecutar_contratos(self, peticion: Dict) -> Dict:
        """
        Ejecuta la capacidad canónica "evaluar" de cada módulo
        según lo declarado en su contrato.
        El Engine no conoce nombres de funciones; solo capacidades.
        """
        self.invocador.reiniciar()
        reportes = {}

        for contenedor in self.registro.contenedores.values():
            if not contenedor.tiene_capacidad("evaluar"):
                continue

            reporte = self.invocador.ejecutar_capacidad(
                contenedor, "evaluar", peticion
            )
            if isinstance(reporte, dict):
                reportes[contenedor.rol] = reporte

        return {
            "reportes": reportes,
            "fallos": list(self.invocador.fallos),
        }

    # ---------------- EVALUACIÓN ----------------
    def evaluar(self, peticion: Dict) -> Dict:
        """
        Evalúa una petición ejecutando las capacidades declaradas.
        El Engine no interpreta resultados; solo recopila reportes.
        """
        return self.ejecutar_contratos(peticion)

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
            rol_pendiente = str(e).split(" ")[1] if " " in str(e) else "desconocido"
            return {
                "estado": "PENDIENTE",
                "detenido_en": "centinela",
                "rol_pendiente": rol_pendiente,
                "razon": str(e),
                "accion": f"Montar el contenedor {rol_pendiente} para desbloquear.",
                "reportes": {},
                "fallos": [],
            }
        return self.evaluar(peticion)

    # ---------------- CONOCIMIENTO TOTAL (SIN ACTUAR) ----------------
    def censar(self) -> Dict:
        """Devuelve el estado de los módulos cargados (transparencia total)."""
        return self.registro.resumen()

    def conocimiento(self) -> Dict:
        """
        Devuelve el conocimiento completo que el Engine tiene del sistema.
        Esta operación es puramente introspectiva: no ejecuta ninguna capacidad.
        """
        return self.registro.conocimiento_total()

    def inventario(self) -> Dict:
        """
        Devuelve un resumen del estado del Engine y de los módulos
        que declaran la capacidad 'inventario'.
        Solo actúa sobre módulos que explícitamente autorizan esta capacidad.
        """
        inv = self.registro.resumen()
        inv["contenido"] = {}

        for c in self.registro.contenedores.values():
            if c.tiene_capacidad("inventario"):
                result = self.invocador.ejecutar_capacidad(c, "inventario")
                if not es_undefined(result):
                    inv["contenido"][c.nombre] = result
                else:
                    inv["contenido"][c.nombre] = {"error": "capacidad 'inventario' falló"}
        return inv
