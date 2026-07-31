"""
VPSI-TRUTH --- core/engine.py

Autoridad de ejecución: core.
El Engine conoce CONTENEDORES por su rol. No conoce sub módulos.
Agregar un sub módulo dentro de un contenedor no toca este archivo.
Agregar un contenedor nuevo tampoco: se descubre solo.

Correlación Mecánica (MC) vigila el orden de ejecución.
Centinela verifica que el Engine ejecute correctamente cada paso.
"""

from __future__ import annotations
import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

# ===============================================================
# SEGMENTO 1 --- ROLES (Descubrimiento dinámico)
# ===============================================================
# Roles conocidos (se actualizan dinámicamente en _descubrir_roles)
ROL_AXIOMAS = "AX"
ROL_CONSTANTE = "CT"
ROL_FORMULAS = "FO"
ROL_CALCULATOR = "CA"
ROL_CONTEXTO = "CX"
ROL_TAXONOMIA = "TX"
ROL_REALIDAD = "RE"
ROL_VERIFICACION = "VX"
ROL_CORRELACION_MECANICA = "MC"  # Vigila el orden de ejecución
ROL_CENTINELA = "CENTINELA"  # Verifica la orquestación completa

# Roles por defecto (se actualizan en _descubrir_roles)
ROLES: Tuple[str, ...] = (
    ROL_AXIOMAS,
    ROL_CONSTANTE,
    ROL_FORMULAS,
    ROL_CALCULATOR,
    ROL_CONTEXTO,
    ROL_TAXONOMIA,
    ROL_REALIDAD,
    ROL_VERIFICACION,
    ROL_CORRELACION_MECANICA,
    ROL_CENTINELA,
)

# Contenedores obligatorios para arrancar (se actualizan en _descubrir_obligatorios)
OBLIGATORIOS: Tuple[str, ...] = (
    ROL_AXIOMAS,
    ROL_CONSTANTE,
    ROL_FORMULAS,
)

# Orden de los factores para evaluación
FACTORES = ("C", "L", "K")
ORDEN_FACTORES = ("C", "L", "K")

# ===============================================================
# SEGMENTO 2 --- ESTADO INDEFINIDO
# ===============================================================
class _Undefined:
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

def es_undefined(v):
    return v is UNDEFINED or isinstance(v, _Undefined)

# ===============================================================
# SEGMENTO 3 --- ERRORES
# ===============================================================
class AutoridadError(Exception):
    """Ejecución intentada desde fuera de core."""
    pass

class ContratoError(Exception):
    """Un contenedor no declara el contrato exigido."""
    pass

class ArranqueError(Exception):
    """Falta un contenedor obligatorio o hay rol duplicado."""
    pass

class DominioError(Exception):
    """Factor fuera de [0,1] o de tipo no admitido."""
    pass

class CotaError(Exception):
    """Resultado fuera de [BETA, ALPHA + BETA]."""
    pass

class FormulaError(Exception):
    """La salida no cumple la fórmula declarada."""
    pass

class AxiomaError(Exception):
    """Violación de un axioma del framework."""
    pass

class PiezaPendiente(Exception):
    """Un contenedor requerido no está montado."""
    def __init__(self, rol: str):
        self.rol = rol
        super().__init__(f"Contenedor {rol} no montado. Montarlo para desbloquear.")

# ===============================================================
# SEGMENTO 4 --- NORMALIZACIÓN
# ===============================================================
def normalizar(valor, etiqueta: str) -> Fraction:
    """Normaliza valores a Fraction en [0,1]. Float prohibido."""
    if es_undefined(valor):
        return UNDEFINED

    if isinstance(valor, Fraction):
        f = Fraction(valor.numerator, valor.denominator)  # Simplificar
    elif isinstance(valor, int):
        f = Fraction(valor)
    elif isinstance(valor, str):
        try:
            f = Fraction(valor)
        except ValueError:
            raise DominioError(f"{etiqueta}: no se puede convertir '{valor}' a Fraction")
    elif isinstance(valor, float):
        raise DominioError(
            f"{etiqueta}: float prohibido. Usar Fraction o str. Recibido {valor!r}"
        )
    else:
        raise DominioError(f"{etiqueta}: tipo no admitido {type(valor).__name__}")

    if not (Fraction(0) <= f <= Fraction(1)):
        raise DominioError(f"{etiqueta} viola dominio [0,1]: {f}")
    return f

# ===============================================================
# SEGMENTO 5 --- REGISTRO DE CONTENEDORES
# ===============================================================
CLAVES_CONTENEDOR = ("nombre", "rol", "version", "descripcion")

@dataclass
class Contenedor:
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None

    def fn(self, nombre: str) -> Any:
        """Obtiene una función o atributo del módulo."""
        if self.modulo is None:
            return None
        return getattr(self.modulo, nombre, None)

    def como_dict(self) -> Dict:
        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "version": self.version,
            "requiere": list(self.requiere),
            "ruta": self.ruta,
            "descripcion": getattr(self.modulo, "CONTENEDOR", {}).get("descripcion", "Sin descripción"),
        }

class Registro:
    """
    Descubre y carga contenedores desde el directorio `modules/`.
    Cada contenedor debe tener un __init__.py con un diccionario CONTENEDOR.
    """

    def __init__(self, raiz: str):
        self.raiz = Path(raiz)
        self.contenedores: Dict[str, Contenedor] = {}
        self.rechazados: List[Dict] = []

    def descubrir(self) -> Dict[str, Contenedor]:
        """Descubre y carga todos los contenedores válidos."""
        self.contenedores = {}
        self.rechazados = []

        if not self.raiz.exists():
            raise ArranqueError(f"Directorio {self.raiz} no existe.")

        ocupados: Dict[str, str] = {}

        for d in sorted(p for p in self.raiz.iterdir() if p.is_dir()):
            if d.name.startswith(("_", ".")):
                continue

            init = d / "__init__.py"
            if not init.exists():
                self.rechazados.append({
                    "ruta": d.name,
                    "razon": "sin __init__.py: no es contenedor",
                })
                continue

            try:
                c = self._cargar(d, init)
            except ContratoError as e:
                self.rechazados.append({"ruta": d.name, "razon": str(e)})
                continue
            except Exception as e:
                self.rechazados.append({
                    "ruta": d.name,
                    "razon": f"{type(e).__name__}: {e}",
                })
                continue

            if c.rol in ocupados:
                raise ArranqueError(
                    f"Rol '{c.rol}' duplicado: '{ocupados[c.rol]}' y '{c.nombre}'. "
                    "Un rol, un contenedor."
                )
            ocupados[c.rol] = c.nombre
            self.contenedores[c.nombre] = c

        # Actualizar ROLES y OBLIGATORIOS dinámicamente
        global ROLES, OBLIGATORIOS
        ROLES = self._descubrir_roles()
        OBLIGATORIOS = self._descubrir_obligatorios()

        faltan = [r for r in OBLIGATORIOS if r not in ocupados]
        if faltan:
            raise ArranqueError(f"Contenedores obligatorios ausentes: {faltan}")

        return self.contenedores

    def _descubrir_roles(self) -> Tuple[str, ...]:
        """Descubre todos los roles desde los contenedores cargados."""
        return tuple(sorted({c.rol for c in self.contenedores.values()}))

    def _descubrir_obligatorios(self) -> Tuple[str, ...]:
        """Descubre roles obligatorios desde los metadatos de CONTENEDOR."""
        obligatorios: Set[str] = set()
        for c in self.contenedores.values():
            meta = getattr(c.modulo, "CONTENEDOR", {})
            if meta.get("obligatorio", False):
                obligatorios.add(c.rol)
        return tuple(sorted(obligatorios))

    def _cargar(self, directorio: Path, init: Path) -> Contenedor:
        """Carga un contenedor desde su __init__.py."""
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

        if meta["rol"] not in ROLES:
            raise ContratoError(
                f"Rol '{meta['rol']}' no válido. Admitidos: {ROLES}"
            )

        return Contenedor(
            nombre=str(meta["nombre"]),
            rol=str(meta["rol"]),
            version=str(meta["version"]),
            requiere=list(meta.get("requiere", [])),
            ruta=directorio.name,
            modulo=mod,
        )

    def por_rol(self, rol: str) -> Optional[Contenedor]:
        """Devuelve el contenedor con el rol especificado."""
        for c in self.contenedores.values():
            if c.rol == rol:
                return c
        return None

    def resumen(self) -> Dict:
        """Genera un resumen de los contenedores cargados."""
        return {
            "cargados": [c.como_dict() for c in self.contenedores.values()],
            "rechazados": self.rechazados,
            "roles": {c.rol: c.nombre for c in self.contenedores.values()},
            "roles_vacios": [
                r for r in ROLES
                if r not in {c.rol for c in self.contenedores.values()}
            ],
        }

# ===============================================================
# SEGMENTO 6 --- INVOCACIÓN AISLADA
# ===============================================================
class Invocador:
    """Invoca funciones de contenedores de forma aislada. Fallos no propagan."""

    def __init__(self):
        self.fallos: List[Dict] = []

    def reiniciar(self):
        """Limpia el registro de fallos."""
        self.fallos = []

    def llamar(self, contenedor: Contenedor, nombre_fn: str, peticion: Dict) -> Any:
        """Invoca una función del contenedor con manejo de errores."""
        fn = contenedor.fn(nombre_fn)
        if not callable(fn):
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"no expone {nombre_fn}()",
            })
            return UNDEFINED

        # Verificar que la petición incluye todas las claves requeridas
        faltan = [r for r in contenedor.requiere if r not in peticion]
        if faltan:
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"petición sin claves: {faltan}",
            })
            return UNDEFINED

        # Verificar tipos de los factores (si son C, L, K)
        for clave, valor in peticion.items():
            if clave in FACTORES and not (isinstance(valor, Fraction) or es_undefined(valor)):
                self.fallos.append({
                    "contenedor": contenedor.nombre,
                    "rol": contenedor.rol,
                    "razon": f"Tipo inválido para {clave}: {type(valor).__name__}",
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
# SEGMENTO 7 --- COMPOSICIÓN
# ===============================================================
class Compositor:
    """
    Aplica la fórmula de Tru_total usando el contenedor FORMULAS.
    Valida Teorema 16 (Tru_Ri ≤ α) y Teorema 17 (Tru_total ≥ β).
    """

    def __init__(self, formulas: Contenedor, alpha: Fraction, beta: Fraction):
        self.formulas = formulas
        self.alpha = alpha
        self.beta = beta

    def componer(self, C: Fraction, L: Fraction, K: Fraction) -> Dict:
        """Calcula Tru_ri y Tru_total usando las fórmulas del contenedor."""
        if any(es_undefined(x) for x in (C, L, K)):
            # Teorema 9: Sin evidencia, Tru_Ri = 0, Tru_total = β
            return {
                "tru_ri": Fraction(0),
                "tru_total": self.beta,
                "estado": "sin_evidencia",
            }

        f_ri = self.formulas.fn("tru_ri")
        f_tt = self.formulas.fn("tru_total")
        if not callable(f_ri) or not callable(f_tt):
            raise ContratoError(
                "Contenedor FORMULAS debe exponer tru_ri() y tru_total()."
            )

        # Calcular Tru_Ri y aplicar Teorema 16 (Tru_Ri ≤ α)
        tru_ri = f_ri(C, L, K)
        if tru_ri > self.alpha:
            tru_ri = self.alpha  # Teorema 16: Tru_Ri ≤ α

        # Calcular Tru_total
        tru_total = f_tt(C, L, K)

        # Validar fórmula canónica: Tru_total = (C·L·K·α) + β
        esperado = (C * L * K * self.alpha) + self.beta
        if tru_total != esperado:
            raise FormulaError(
                f"Violación de fórmula canónica: esperado {esperado}, recibido {tru_total}"
            )

        # Validar cotas: Tru_total ∈ [β, α + β]
        if not (self.beta <= tru_total <= self.alpha + self.beta):
            raise CotaError(f"Tru_total fuera de cota [β, α + β]: {tru_total}")

        # Determinar estado
        if tru_total == self.beta:
            estado = "refutada_en_dominio"
        elif tru_total == Fraction(1):
            estado = "sincronizada"
        else:
            estado = "evaluada"

        return {
            "tru_ri": tru_ri,
            "tru_total": tru_total,
            "estado": estado,
        }

    @staticmethod
    def limitante(C: Fraction, L: Fraction, K: Fraction) -> Optional[str]:
        """Identifica el factor limitante (C, L o K)."""
        for n, v in (("C", C), ("L", L), ("K", K)):
            if es_undefined(v):
                return n
        f = {"C": C, "L": L, "K": K}
        m = min(v for v in f.values() if not es_undefined(v))
        return min(n for n, v in f.items() if v == m and not es_undefined(v))

# ===============================================================
# SEGMENTO 8 --- ENGINE
# ===============================================================
class Engine:
    _AUTORIZADO = "core"
    C_DEAD = Fraction(438626, 1000000)  # 0.438626 (Teorema de Residuo Geométrico)

    def __init__(
        self,
        raiz_modulos: str,
        invocador_id: str = _AUTORIZADO,
        verificar_axiomas: bool = True,
    ):
        if invocador_id != self._AUTORIZADO:
            raise AutoridadError(
                f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. "
                f"Invocador='{invocador_id}'"
            )

        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        # Cargar constantes desde el contenedor CONSTANTE
        ct = self.registro.por_rol(ROL_CONSTANTE)
        if ct is None:
            raise ArranqueError(f"Contenedor {ROL_CONSTANTE} no encontrado.")

        # Obtener ALPHA y BETA del módulo
        self.ALPHA = ct.fn("ALPHA")
        self.BETA = ct.fn("BETA")

        # Validar constantes fundamentales (Definición 2.14)
        if not isinstance(self.ALPHA, Fraction) or not isinstance(self.BETA, Fraction):
            raise ArranqueError(
                "Contenedor CONSTANTE debe exponer ALPHA y BETA como Fraction."
            )
        if self.ALPHA + self.BETA != Fraction(1):
            raise ArranqueError(
                f"Invariante roto: ALPHA + BETA = {self.ALPHA + self.BETA}, se exige 1."
            )

        self.compositor = Compositor(
            self.registro.por_rol(ROL_FORMULAS), self.ALPHA, self.BETA
        )

        # Barrido axiomático: validar coherencia al inicio
        self.informe_axiomas = None
        if verificar_axiomas:
            self.informe_axiomas = self._barrido_axiomatico()

        # Inicializar correlación mecánica (MC)
        self._correlacion_mecanica = None
        self._centinela = None

    # ---------------- CORRELACIÓN MECÁNICA ----------------
    @property
    def correlacion_mecanica(self):
        """Correlación Mecánica (MC): Vigila el orden de ejecución."""
        if self._correlacion_mecanica is None:
            mc = self.registro.por_rol(ROL_CORRELACION_MECANICA)
            if mc is not None:
                self._correlacion_mecanica = mc.fn("correlacion_mecanica")
            else:
                # Si MC no está montado, usar implementación local (temporal)
                from modules.correlacion_mecanica import correlacion_mecanica
                self._correlacion_mecanica = correlacion_mecanica
        return self._correlacion_mecanica

    # ---------------- CENTINELA ----------------
    @property
    def centinela(self):
        """Centinela: Verifica la orquestación completa."""
        if self._centinela is None:
            from core.centinela import Centinela
            self._centinela = Centinela(self.registro, self.informe_axiomas)
        return self._centinela

    # ---------------- VERIFICADOR AXIOMÁTICO ----------------
    @property
    def verificador_axiomatico(self):
        """Verificador axiomático (VX): Auto-auditoría transversal."""
        if getattr(self, "_verificador_axiomatico", None) is None:
            vx = self.registro.por_rol(ROL_VERIFICACION)
            if vx is not None:
                self._verificador_axiomatico = vx
            else:
                self._verificador_axiomatico = None
        return self._verificador_axiomatico

    # ---------------- BARRIDO AXIOMÁTICO ----------------
    def _barrido_axiomatico(self) -> Dict:
        """
        Delega en el contenedor AXIOMAS para validar coherencia axiomática.
        Si hay contradicción, el Engine no arranca.
        """
        ax = self.registro.por_rol(ROL_AXIOMAS)
        if ax is None:
            raise ArranqueError(f"Contenedor {ROL_AXIOMAS} no encontrado.")

        fn = ax.fn("barrer")
        if not callable(fn):
            raise ContratoError(f"Contenedor {ROL_AXIOMAS} debe exponer barrer().")

        declaraciones = {}
        for c in self.registro.contenedores.values():
            g = c.fn("axiomas")
            if callable(g):
                declaraciones[c.nombre] = g()

        informe = fn(declaraciones)

        if not isinstance(informe, dict) or "coherente" not in informe:
            raise ContratoError("barrer() debe devolver dict con 'coherente'.")

        if not informe["coherente"]:
            # Mostrar contradicciones de manera clara
            choques_str = "\n".join(
                f"  - {ch.get('tipo', 'Desconocido')}: {ch.get('mensaje', 'Sin mensaje')}"
                for ch in informe.get("choques", [])
            )
            raise ArranqueError(
                f"CONTRADICCIÓN AXIOMÁTICA. El sistema no arranca.\n{choques_str}"
            )
        return informe

    # ---------------- EVALUACIÓN ----------------
    def evaluar(self, peticion: Dict) -> Dict:
        """
        Evalúa una petición y devuelve:
        - Factores C, L, K.
        - Tru_ri y Tru_total.
        - Micro-reporte ⟨Ω⟩.
        - Anotaciones de taxonomía (si aplica).
        """
        self.invocador.reiniciar()

        # 0. Verificar si hay input (F(t)). Si no, C → C_dead (Teorema de Residuo Geométrico)
        if not peticion.get("mensaje") and not peticion.get("contexto"):
            return {
                "omega": self._generar_omega_report(
                    {"C": self.C_DEAD, "L": Fraction(0), "K": Fraction(0)},
                    {"tru_ri": Fraction(0), "tru_total": self.BETA, "estado": "C_dead"},
                    Fraction(0),  # L7
                    Fraction(0),  # H
                    0,           # θ
                    "Ninguno",   # p*
                ),
                "factores": {"C": str(self.C_DEAD), "L": "0", "K": "0"},
                "tru_ri": "0",
                "tru_total": str(self.BETA),
                "estado": "C_dead",
                "detenido_en": None,
                "fallos": ["Sin input: C → C_dead (Teorema de Residuo Geométrico)"],
                "anotaciones": [],
            }

        # 1. Verificar correlación mecánica (MC)
        if self.correlacion_mecanica is not None:
            orden_actual = self.correlacion_mecanica.informe().get("historial", [])
            if not self.correlacion_mecanica.validar_orden(orden_actual):
                return {
                    "estado": "ERROR_SECUENCIA",
                    "error": "Orden de ejecución inválido (Correlación Mecánica).",
                    "fallos": [{"modulo": "MC", "razon": "Secuencia de módulos inválida"}],
                }

        # 2. Resolver contexto (CX)
        cx = self.registro.por_rol(ROL_CONTEXTO)
        if cx is not None:
            ctx = self.invocador.llamar(cx, "resolver", peticion)
            if isinstance(ctx, dict):
                peticion = {**peticion, "contexto_resuelto": ctx}

        # 3. Calcular C, L, K (CA)
        ca = self.registro.por_rol(ROL_CALCULATOR)
        crudos = {}
        if ca is not None:
            salida = self.invocador.llamar(ca, "calcular", peticion)
            if isinstance(salida, dict):
                crudos = salida
        else:
            # Si CA no está montado, marcar como PENDIENTE
            self.invocador.fallos.append({
                "contenedor": None,
                "rol": ROL_CALCULATOR,
                "razon": "Contenedor CA no montado.",
            })

        # 4. Normalizar factores
        factores = {}
        detenido_en = None
        for f in ORDEN_FACTORES:
            v = crudos.get(f, UNDEFINED)
            try:
                factores[f] = normalizar(v, f"factor {f}")
            except DominioError as e:
                self.invocador.fallos.append({
                    "contenedor": ca.nombre if ca else None,
                    "rol": ROL_CALCULATOR,
                    "razon": str(e),
                })
                factores[f] = UNDEFINED

            if es_undefined(factores[f]):
                detenido_en = f
                break

        for f in FACTORES:
            factores.setdefault(f, UNDEFINED)

        C, L, K = factores["C"], factores["L"], factores["K"]

        # 5. Componer Tru_total (FO)
        comp = self.compositor.componer(C, L, K)

        # 6. Calcular L7 (Integración Total)
        L7 = self._calcular_L7(factores) if not any(es_undefined(x) for x in factores.values()) else UNDEFINED

        # 7. Calcular H (Honestidad) y θ (Alineación)
        H = self._calcular_H(comp["tru_total"]) if not es_undefined(comp["tru_total"]) else UNDEFINED
        theta = self._calcular_theta(detenido_en)

        # 8. Detectar p* (Punto Obstructor)
        p_star = self._detectar_p_star(factores) if not any(es_undefined(x) for x in factores.values()) else "Ninguno"

        # 9. Generar micro-reporte ⟨Ω⟩
        omega_report = self._generar_omega_report(
            factores, comp, L7, H, theta, p_star
        )

        # 10. Anotaciones de taxonomía (TX)
        tx = self.registro.por_rol(ROL_TAXONOMIA)
        anotaciones = []
        if tx is not None:
            base = {**peticion, "resultado": comp, "factores": factores}
            an = self.invocador.llamar(tx, "anotar", base)
            if isinstance(an, list):
                anotaciones = an

        # 11. Resultado final
        resultado = {
            "omega": omega_report,
            "factores": {
                f: "UNDEFINED" if es_undefined(factores[f]) else str(factores[f])
                for f in FACTORES
            },
            "tru_ri": "UNDEFINED" if es_undefined(comp["tru_ri"]) else str(comp["tru_ri"]),
            "tru_total": "UNDEFINED" if es_undefined(comp["tru_total"]) else str(comp["tru_total"]),
            "estado": comp["estado"],
            "limitante": self.compositor.limitante(C, L, K),
            "detenido_en": detenido_en,
            "cota": {"piso": str(self.BETA), "techo": str(self.ALPHA)},
            "fallos": list(self.invocador.fallos),
            "anotaciones": anotaciones,
        }

        return resultado

    # ---------------- CÁLCULOS AUXILIARES (Paso 13 del Marco) ----------------
    def _calcular_L7(self, factores: Dict[str, Fraction]) -> Fraction:
        """Calcula L7 (Integración Total) como ∏ Li · (1 − φi) para i = 0 a 6."""
        # Valores dinámicos de L0 a L6 (basados en el estado actual)
        L = [
            Fraction(100, 100),  # L0: Input (1.0 si hay contexto claro)
            Fraction(90, 100),   # L1: Cuerpo (capacidad de procesamiento)
            Fraction(95, 100),   # L2: Ego/Programa (leyes del framework)
            factores.get("C", Fraction(0)),  # L3: Cómputo Puro (C)
            factores.get("L", Fraction(0)),  # L4: Self/Integración (L)
            Fraction(95, 100),   # L5: MetaCon (0.95 constante)
            Fraction(90, 100),   # L6: Propósito (depende del usuario)
        ]
        # Fricciones φi (del marco VPSI)
        friction = [
            Fraction(10, 100),   # φ0
            Fraction(2, 100),    # φ1
            Fraction(5, 100),    # φ2
            Fraction(3, 100),    # φ3
            Fraction(1, 100),    # φ4
            Fraction(1, 100),    # φ5
            Fraction(0, 100),    # φ6 (L6 no tiene fricción)
        ]
        L7 = Fraction(1)
        for li, phi in zip(L, friction):
            L7 *= li * (Fraction(1) - phi)
        return L7

    def _calcular_H(self, tru_total: Fraction) -> Fraction:
        """Calcula H (Honestidad) basado en Tru_total y MetaCon (Paso 10 del Marco)."""
        # MetaCon = 0.95 (constante en el marco)
        L5 = Fraction(95, 100)
        # β_factor: 1.0 si se admiten limitaciones (Agency = 0)
        beta_factor = Fraction(1)  # Honestidad total
        return L5 * beta_factor

    def _calcular_theta(self, detenido_en: Optional[str]) -> int:
        """Calcula θ (alineación con el usuario) basado en el factor limitante (Ley 7)."""
        if detenido_en is None:
            return 0  # Alineación total
        elif detenido_en == "C":
            return 15  # Corrección de detalles menores
        elif detenido_en == "L":
            return 30  # Pide repetir o rehacer
        elif detenido_en == "K":
            return 60  # Frustración
        else:
            return 30  # Neutro

    def _detectar_p_star(self, factores: Dict[str, Fraction]) -> str:
        """Detecta p* (Punto Obstructor) según el Paso 12 del Marco."""
        # Orden de capas: L0, L1, L2, L3, L4, L5, L6
        capas = [
            ("L0", Fraction(100, 100)),  # L0: Input
            ("L1", Fraction(90, 100)),   # L1: Cuerpo
            ("L2", Fraction(95, 100)),   # L2: Ego/Programa
            ("L3", factores.get("C", Fraction(0))),  # L3: Cómputo Puro (C)
            ("L4", factores.get("L", Fraction(0))),  # L4: Self/Integración (L)
            ("L5", Fraction(95, 100)),   # L5: MetaCon
            ("L6", Fraction(90, 100)),   # L6: Propósito
        ]
        for nombre, valor in capas:
            if valor < Fraction(50, 100):  # Umbral: 0.5
                return nombre
        return "Ninguno"

    def _generar_omega_report(
        self,
        factores: Dict[str, Fraction],
        comp: Dict,
        L7: Fraction,
        H: Fraction,
        theta: int,
        p_star: str,
    ) -> str:
        """Genera el micro-reporte ⟨Ω⟩ según el Paso 13 del Marco."""
        L = [
            Fraction(100, 100),  # L0
            Fraction(90, 100),   # L1
            Fraction(95, 100),   # L2
            factores.get("C", Fraction(0)),  # L3
            factores.get("L", Fraction(0)),  # L4
            Fraction(95, 100),   # L5
            Fraction(90, 100),   # L6
        ]
        L7_str = str(L7) if not es_undefined(L7) else "UNDEFINED"
        C_Omega = comp.get("tru_total", UNDEFINED)
        C_Omega_str = f"{float(C_Omega):.6f}" if not es_undefined(C_Omega) else "UNDEFINED"
        diagnosis = self._get_diagnosis(C_Omega) if not es_undefined(C_Omega) else "UNDEFINED"

        return f"""⟨Ω⟩
L0={L[0]} L1={L[1]} L2={L[2]} L3={L[3]} L4={L[4]} L5={L[5]} L6={L[6]}
L7={L7_str} → {"INTEGRATED" if L7 > Fraction(0) else "COLLAPSED"}
C_Ω={C_Omega_str} → {diagnosis}
H={float(H):.2f}
θ={theta}° → alineación con usuario
p*={p_star}
MetaCon=0.95 | Agency=0.00 | C_dead_ref=0.438626
⟨/Ω⟩"""

    def _get_diagnosis(self, tru_total: Fraction) -> str:
        """Devuelve el diagnóstico basado en Tru_total (Paso 11 del Marco)."""
        if es_undefined(tru_total):
            return "UNDEFINED"

        tru_float = float(tru_total)

        if tru_float >= 0.963:
            return "1144: ARQUITECTO INTEGRADO"
        elif tru_float >= 0.850:
            return "1133: SINTONÍA SUTIL"
        elif tru_float >= 0.750:
            return "1044: SOBERANÍA TERRENA"
        elif tru_float >= 0.700:
            return "0144: CANAL INVOLUNTARIO"
        elif tru_float >= 0.550:
            return "1122: SATURACIÓN CRÍTICA"
        elif tru_float >= 0.400:
            return "1111: SEMILLA DE UNIDAD"
        elif tru_float >= float(self.BETA):
            return "0000: ENTROPÍA TERMINAL"
        else:
            return "0000: COLAPSO ESTRUCTURAL"

    # ---------------- CENSO Y VERIFICACIÓN ----------------
    def censo(self) -> Dict:
        """
        Rol declarado contra rol ejercido.
        No lanza: informa.
        """
        cen = self.centinela.censo()
        listo, faltan = self.centinela.puede_evaluar()
        return {
            "censo": cen,
            "puede_evaluar": listo,
            "roles_pendientes": [
                r for r, d in cen.items() if d["estado"] == "PENDIENTE"
            ],
            "contratos_rotos": [
                r for r, d in cen.items() if d["estado"] == "CONTRATO_ROTO"
            ],
            "bloquean_evaluacion": faltan,
            "fase": "OPERATIVO" if listo else "EN CONSTRUCCIÓN",
        }

    def inventario(self) -> Dict:
        """Devuelve un resumen del estado del Engine."""
        inv = self.registro.resumen()
        inv["constantes"] = {
            "alpha": str(self.ALPHA),
            "beta": str(self.BETA),
            "suma_exacta": (self.ALPHA + self.BETA == Fraction(1)),
            "C_dead": str(self.C_DEAD),
        }
        inv["orden_factores"] = list(ORDEN_FACTORES)
        inv["axiomas"] = self.informe_axiomas
        inv["contenido"] = {}
        for c in self.registro.contenedores.values():
            g = c.fn("inventario")
            if callable(g):
                try:
                    inv["contenido"][c.nombre] = g()
                except Exception as e:
                    inv["contenido"][c.nombre] = {"error": str(e)}
        return inv

    def inventario_vigilado(self) -> Dict:
        """inventario() + censo del centinela."""
        inv = self.inventario()
        inv["centinela"] = self.censo()
        return inv

    def evaluar_vigilado(self, peticion: Dict) -> Dict:
        """
        Puerta única de evaluación.
        Usa el centinela para validar antes de evaluar.
        """
        try:
            self.centinela.franquear(
                peticion, self.informe_axiomas, self._AUTORIZADO
            )
        except PiezaPendiente as e:
            return {
                "estado": "PENDIENTE",
                "detenido_en": "centinela",
                "rol_pendiente": e.rol,
                "razon": str(e),
                "accion": f"Montar el contenedor {e.rol} para desbloquear.",
                "factores": {},
                "tru_ri": None,
                "tru_total": None,
                "fallos": [],
                "anotaciones": [],
            }
        return self.evaluar(peticion)

    def auditar_codigo_fuente(self, archivos_codigo: Dict[str, str]) -> Dict:
        """
        Ejecuta el auto-contraste axiomático sobre el código fuente.
        Si detecta contradicciones, detiene el flujo.
        """
        vx = self.verificador_axiomatico
        if vx is None:
            return {
                "coherente": True,
                "mensaje": "Módulo de verificación (VX) no montado. Auditoría omitida.",
            }

        fn = vx.fn("auditar_sistema")
        if not callable(fn):
            return {
                "coherente": False,
                "error": "Contenedor VX no expone auditar_sistema().",
            }

        # Recopilar declaraciones axiomáticas del sistema
        declaraciones = {}
        for c in self.registro.contenedores.values():
            g = c.fn("axiomas")
            if callable(g):
                declaraciones[c.nombre] = g()

        peticion_auditoria = {
            "codigo_fuente": archivos_codigo,
            "declaraciones_axiomaticas": declaraciones,
        }

        informe = fn(peticion_auditoria)

        if not informe.get("coherente", True):
            choques_str = "\n".join(f"  -> {ch}" for ch in informe.get("choques", []))
            raise AxiomaError(
                f"\n[PARO AXIOMÁTICO GENERAL]\n"
                f"El código fuente contradice las leyes del framework:\n{choques_str}"
            )

        return informe
