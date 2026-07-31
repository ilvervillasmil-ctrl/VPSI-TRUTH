"""
VPSI-TRUTH --- core/engine.py

El Engine es el observador omnisciente y conducto estructural transparente del sistema:
- Descubre y carga módulos sin intervenir en su lógica interna.
- Delega tareas a los módulos según su rol (CX, CA, FO, AX, MC, etc.).
- Garantiza que los impulsos fluyan sin distorsión, cumpliendo contratos y axiomas.
- Emite el Omega Report (⟨Ω⟩) como radiografía exacta del estado del sistema.
"""

from __future__ import annotations
import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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

# Tupla de roles válidos
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

# Módulos obligatorios para el arranque
OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS, ROL_CORRELACION_MECANICA)

# Factores que el Engine espera de los módulos
FACTORES = ("C", "L", "K")
ORDEN_FACTORES = ("C", "L", "K")

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

class DominioError(Exception):
    """Un valor está fuera del dominio permitido [0, 1]."""
    pass

class CotaError(Exception):
    """Un resultado viola las cotas del marco (β ≤ Trutotal ≤ 1)."""
    pass

class FormulaError(Exception):
    """La fórmula canónica (Trutotal = C*L*K*α + β) fue violada."""
    pass

# ===============================================================
# NORMALIZACIÓN (ARITMÉTICA EXACTA)
# ===============================================================
def normalizar(valor: Union[Fraction, int, str, _Undefined], etiqueta: str) -> Union[Fraction, _Undefined]:
    """
    Normaliza un valor a Fraction en el dominio [0, 1].
    Si el valor es UNDEFINED, lo devuelve sin cambios.
    """
    if es_undefined(valor):
        return UNDEFINED

    try:
        if isinstance(valor, Fraction):
            f = Fraction(valor.numerator, valor.denominator)
        elif isinstance(valor, int):
            f = Fraction(valor)
        elif isinstance(valor, str):
            f = Fraction(valor)
        else:
            raise DominioError(f"{etiqueta}: tipo no admitido {type(valor).__name__}")
    except (ValueError, TypeError) as e:
        raise DominioError(f"{etiqueta}: no se puede convertir '{valor}' a Fraction") from e

    if not (Fraction(0) <= f <= Fraction(1)):
        raise DominioError(f"{etiqueta} viola dominio [0,1]: {f}")
    return f

# ===============================================================
# REGISTRO DE MÓDULOS (DESCUBRIMIENTO Y CARGA)
# ===============================================================
CLAVES_CONTENEDOR = ("nombre", "rol", "version", "requiere")

@dataclass
class Contenedor:
    """Representa un módulo en el sistema. No interviene en su lógica interna."""
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None

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

        # Verificar que C, L, K sean Fraction o UNDEFINED
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
# COMPOSITOR (ARITMÉTICA EXACTA Y FÓRMULA CANÓNICA)
# ===============================================================
class Compositor:
    """
    Aplica la fórmula canónica: Trutotal = (C * L * K * α) + β.
    No delega en FORMULAS para cálculos críticos (evita distorsiones).
    """
    def __init__(self, alpha: Fraction, beta: Fraction):
        self.alpha = alpha
        self.beta = beta

    def componer(self, C: Union[Fraction, _Undefined], L: Union[Fraction, _Undefined], K: Union[Fraction, _Undefined]) -> Dict:
        """
        Calcula Tru_ri y Trutotal usando la fórmula canónica.
        Si algún factor es UNDEFINED, devuelve UNDEFINED (Organic Fail-Fast).
        """
        if any(es_undefined(x) for x in (C, L, K)):
            return {"tru_ri": UNDEFINED, "tru_total": UNDEFINED, "estado": "sin_evidencia"}

        # Validar dominio [0,1] para C, L, K
        for nombre, valor in [("C", C), ("L", L), ("K", K)]:
            if not (Fraction(0) <= valor <= Fraction(1)):
                raise DominioError(f"{nombre}={valor} viola dominio [0,1]")

        # Cálculo exacto: Tru_ri = C * L * K (Axioma 5)
        tru_ri = C * L * K
        if tru_ri > Fraction(1):
            raise DominioError(f"tru_ri={tru_ri} viola dominio [0,1]")

        # Cálculo exacto: Trutotal = tru_ri * α + β (Teorema 1)
        tru_total = (tru_ri * self.alpha) + self.beta

        # Verificar cotas (Corolario 2: β ≤ Trutotal ≤ 1)
        if not (self.beta <= tru_total <= Fraction(1)):
            raise CotaError(f"Trutotal={tru_total} fuera de cota [β, 1]")

        # Verificar Corolario 1: Si C, L o K = 0 → Trutotal = β
        if any(v == Fraction(0) for v in (C, L, K)) and tru_total != self.beta:
            raise CotaError(f"Si C, L o K = 0, Trutotal debe ser β={self.beta}. Recibido: {tru_total}")

        # Determinar estado (basado en axiomas)
        if tru_total == self.beta:
            estado = "refutada_en_dominio"
        elif tru_total == Fraction(1):
            estado = "sincronizada"
        else:
            estado = "evaluada"

        return {"tru_ri": tru_ri, "tru_total": tru_total, "estado": estado}

    @staticmethod
    def limitante(C: Union[Fraction, _Undefined], L: Union[Fraction, _Undefined], K: Union[Fraction, _Undefined]) -> Optional[str]:
        """Detecta el factor limitante (el más bajo)."""
        for n, v in (("C", C), ("L", L), ("K", K)):
            if es_undefined(v):
                return n
        f = {"C": C, "L": L, "K": K}
        m = min(v for v in f.values() if not es_undefined(v))
        return min(n for n, v in f.items() if v == m and not es_undefined(v))

# ===============================================================
# ENGINE (OBSERVADOR OMNISCIENTE)
# ===============================================================
class Engine:
    _AUTORIZADO = "core"  # Solo el core puede ejecutar el Engine

    def __init__(self, raiz_modulos: str, invocador_id: str = _AUTORIZADO, verificar_axiomas: bool = True):
        """
        Inicializa el Engine:
        - Descubre y carga módulos.
        - Verifica que los obligatorios (AX, CT, FO, MC) estén presentes.
        - Carga constantes (ALPHA, BETA) y valida α + β = 1.
        - Verifica coherencia axiomática (AX) y mecánica (MC) si se solicita.
        """
        if invocador_id != self._AUTORIZADO:
            raise AutoridadError(f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. Invocador='{invocador_id}'")

        # Descubrir módulos (sin intervencionismo)
        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        # Cargar constantes (ALPHA, BETA) desde CT
        ct = self.registro.por_rol(ROL_CONSTANTE)
        if ct is None:
            raise ArranqueError(f"Contenedor {ROL_CONSTANTE} no encontrado.")

        # Validar que ALPHA y BETA sean Fraction y cumplan α + β = 1
        self.ALPHA = Fraction(ct.fn("ALPHA"))
        self.BETA = Fraction(ct.fn("BETA"))

        if self.ALPHA != Fraction(26, 27) or self.BETA != Fraction(1, 27):
            raise ArranqueError(f"ALPHA debe ser 26/27 y BETA debe ser 1/27. Recibido: ALPHA={self.ALPHA}, BETA={self.BETA}")
        if self.ALPHA + self.BETA != Fraction(1):
            raise ArranqueError(f"Invariante roto: ALPHA + BETA = {self.ALPHA + self.BETA}, se exige 1.")

        # Inicializar compositor (fórmula canónica)
        self.compositor = Compositor(self.ALPHA, self.BETA)

        # Verificar coherencia axiomática (AX)
        self.informe_axiomas = None
        if verificar_axiomas:
            self.informe_axiomas = self._barrido_axiomatico()

        # Verificar correlación mecánica (MC)
        self._verificar_correlacion_mecanica()

    # ---------------- VERIFICACIÓN DE CORRELACIÓN MECÁNICA ----------------
    def _verificar_correlacion_mecanica(self) -> None:
        """Verifica que los módulos no tengan contradicciones en su orden de ejecución (MC)."""
        mc = self.registro.por_rol(ROL_CORRELACION_MECANICA)
        if mc is None:
            raise ArranqueError(f"Contenedor {ROL_CORRELACION_MECANICA} no encontrado.")

        informe_mc = mc.fn("barrer")()
        if not informe_mc.get("coherente", False):
            choques_str = "\n".join(informe_mc.get("choques", []))
            raise ArranqueError(f"CONTRADICCIÓN MECÁNICA. Los módulos no pueden ejecutarse en orden.\n{choques_str}")

    # ---------------- VERIFICACIÓN AXIOMÁTICA ----------------
    def _barrido_axiomatico(self) -> Dict:
        """
        Verifica coherencia axiomática entre módulos usando AX.
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
            choques_str = "\n".join(
                f"  - {ch.get('tipo', 'Desconocido')}: {ch.get('mensaje', 'Sin mensaje')}"
                for ch in informe.get("choques", [])
            )
            raise ArranqueError(f"CONTRADICCIÓN AXIOMÁTICA. El sistema no arranca.\n{choques_str}")
        return informe

    # ---------------- EVALUACIÓN (DELEGACIÓN ESTRICTA) ----------------
    def evaluar(self, peticion: Dict) -> Dict:
        """
        Evalúa una petición:
        1. Si no hay input (mensaje/contexto), reporta sin_evidencia.
        2. Delega en CX para resolver contexto.
        3. Delega en CA para calcular C, L, K.
        4. Normaliza factores y calcula Trutotal (Compositor).
        5. Genera el Omega Report (⟨Ω⟩) delegando en AX.
        """
        self.invocador.reiniciar()

        # --- Caso 1: Sin input (F(t) = 0) ---
        if not peticion.get("mensaje") and not peticion.get("contexto"):
            ax = self.registro.por_rol(ROL_AXIOMAS)
            omega_report = self._generar_omega_report_sin_evidencia(ax)
            return {
                "omega": omega_report,
                "factores": {"C": "UNDEFINED", "L": "UNDEFINED", "K": "UNDEFINED"},
                "tru_ri": "UNDEFINED",
                "tru_total": "UNDEFINED",
                "estado": "sin_evidencia",
                "detenido_en": None,
                "fallos": ["Sin input: C, L, K → UNDEFINED (sin evidencia)"],
                "anotaciones": [],
            }

        # --- Paso 1: Resolver contexto (CX) ---
        cx = self.registro.por_rol(ROL_CONTEXTO)
        if cx is not None:
            ctx = self.invocador.llamar(cx, "resolver", peticion)
            if isinstance(ctx, dict):
                peticion = {**peticion, "contexto_resuelto": ctx}

        # --- Paso 2: Calcular C, L, K (CA) ---
        ca = self.registro.por_rol(ROL_CALCULATOR)
        crudos = {}
        if ca is not None:
            salida = self.invocador.llamar(ca, "calcular", peticion)
            if isinstance(salida, dict):
                crudos = salida

        # --- Paso 3: Normalizar factores ---
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

        # Forzar K = UNDEFINED si no hay contexto (Corolario Def-5.3.1)
        if "contexto" not in peticion and "contexto_resuelto" not in peticion:
            factores["K"] = UNDEFINED
            detenido_en = "K"

        for f in FACTORES:
            factores.setdefault(f, UNDEFINED)

        # --- Paso 4: Componer Tru_ri y Trutotal (Compositor) ---
        C, L, K = factores["C"], factores["L"], factores["K"]
        comp = self.compositor.componer(C, L, K)

        # --- Paso 5: Generar Omega Report (⟨Ω⟩) ---
        ax = self.registro.por_rol(ROL_AXIOMAS)
        if ax is not None:
            omega_fn = ax.fn("generar_omega_report")
            if callable(omega_fn):
                omega_report = omega_fn(factores, comp)
            else:
                omega_report = self._generar_omega_report_basico(factores, comp, detenido_en)
        else:
            omega_report = self._generar_omega_report_basico(factores, comp, detenido_en)

        # --- Paso 6: Anotaciones de taxonomía (TX) ---
        tx = self.registro.por_rol(ROL_TAXONOMIA)
        anotaciones = []
        if tx is not None:
            base = {**peticion, "resultado": comp, "factores": factores}
            an = self.invocador.llamar(tx, "anotar", base)
            if isinstance(an, list):
                anotaciones = an

        return {
            "omega": omega_report,
            "factores": {f: "UNDEFINED" if es_undefined(factores[f]) else str(factores[f]) for f in FACTORES},
            "tru_ri": "UNDEFINED" if es_undefined(comp["tru_ri"]) else str(comp["tru_ri"]),
            "tru_total": "UNDEFINED" if es_undefined(comp["tru_total"]) else str(comp["tru_total"]),
            "estado": comp["estado"],
            "limitante": self.compositor.limitante(C, L, K),
            "detenido_en": detenido_en,
            "cota": {"piso": str(self.BETA), "techo": str(self.ALPHA)},
            "fallos": list(self.invocador.fallos),
            "anotaciones": anotaciones,
        }

    # ---------------- REPORTE SIN EVIDENCIA ----------------
    def _generar_omega_report_sin_evidencia(self, ax: Optional[Contenedor]) -> str:
        """Genera un Omega Report para el caso sin input (F(t) = 0)."""
        if ax is not None:
            omega_fn = ax.fn("generar_omega_report")
            if callable(omega_fn):
                return omega_fn(
                    {"C": UNDEFINED, "L": UNDEFINED, "K": UNDEFINED},
                    {"tru_ri": UNDEFINED, "tru_total": UNDEFINED, "estado": "sin_evidencia"}
                )
        # Fallback: reporte básico
        return """⟨Ω⟩
L0=1 L1=0.9 L2=0.95 L3=UNDEFINED L4=UNDEFINED L5=0.95 L6=0.9
L7=UNDEFINED → COLLAPSED
C_Ω=UNDEFINED → UNDEFINED
H=UNDEFINED
θ=0° → alineación con usuario
p*=Ninguno
MetaCon=0.95 | Agency=0.00
⟨/Ω⟩"""

    # ---------------- REPORTE BÁSICO (FALLBACK) ----------------
    def _generar_omega_report_basico(self, factores: Dict, comp: Dict, detenido_en: Optional[str]) -> str:
        """
        Genera un Omega Report básico si AX no tiene la función generar_omega_report.
        Basado en axiomas y estado del sistema.
        """
        L = [
            Fraction(100, 100),  # L0
            Fraction(90, 100),   # L1
            Fraction(95, 100),   # L2
            factores.get("C", UNDEFINED),  # L3
            factores.get("L", UNDEFINED),  # L4
            Fraction(95, 100),   # L5
            Fraction(90, 100),   # L6
        ]

        # Calcular L7 (basado en axiomas)
        L7_str = "UNDEFINED"
        L7_estado = "COLLAPSED"
        if not any(es_undefined(x) for x in L):
            friction = [Fraction(10, 100), Fraction(2, 100), Fraction(5, 100),
                        Fraction(3, 100), Fraction(1, 100), Fraction(1, 100), Fraction(0, 100)]
            L7 = Fraction(1)
            for li, phi in zip(L, friction):
                L7 *= li * (Fraction(1) - phi)
            L7_str = str(L7)
            L7_estado = "INTEGRATED" if L7 > Fraction(0) else "COLLAPSED"

        # C_Ω (Trutotal)
        C_Omega = comp.get("tru_total", UNDEFINED)
        C_Omega_str = str(C_Omega) if not es_undefined(C_Omega) else "UNDEFINED"

        # Diagnóstico (basado en axiomas)
        if es_undefined(C_Omega):
            diagnosis = "UNDEFINED"
        elif C_Omega >= Fraction(963, 1000):
            diagnosis = "1144: ARQUITECTO INTEGRADO"
        elif C_Omega >= Fraction(850, 1000):
            diagnosis = "1133: SINTONÍA SUTIL"
        elif C_Omega >= Fraction(750, 1000):
            diagnosis = "1044: SOBERANÍA TERRENA"
        elif C_Omega >= Fraction(700, 1000):
            diagnosis = "0144: CANAL INVOLUNTARIO"
        elif C_Omega >= Fraction(550, 1000):
            diagnosis = "1122: SATURACIÓN CRÍTICA"
        elif C_Omega >= Fraction(400, 1000):
            diagnosis = "1111: SEMILLA DE UNIDAD"
        elif C_Omega >= self.BETA:
            diagnosis = "0000: ENTROPÍA TERMINAL"
        else:
            diagnosis = "0000: COLAPSO ESTRUCTURAL"

        # Theta (basado en detenido_en)
        theta_map = {
            None: 0,
            "C": 15,
            "L": 30,
            "K": 60,
        }
        theta = theta_map.get(detenido_en, 30)

        # p* (primer L_i < 0.5)
        p_star = "Ninguno"
        for nombre, valor in [("L0", L[0]), ("L1", L[1]), ("L2", L[2]),
                              ("L3", L[3]), ("L4", L[4]), ("L5", L[5]), ("L6", L[6])]:
            if es_undefined(valor):
                continue
            if valor < Fraction(50, 100):
                p_star = nombre
                break

        return f"""⟨Ω⟩
L0={L[0]} L1={L[1]} L2={L[2]} L3={L[3]} L4={L[4]} L5={L[5]} L6={L[6]}
L7={L7_str} → {L7_estado}
C_Ω={C_Omega_str} → {diagnosis}
H=0.95
θ={theta}° → alineación con usuario
p*={p_star}
MetaCon=0.95 | Agency=0.00
⟨/Ω⟩"""

    # ---------------- CENSO Y VERIFICACIÓN ----------------
    def censar(self) -> Dict:
        """Devuelve el estado de los módulos cargados (transparencia total)."""
        return self.registro.resumen()

    def inventario(self) -> Dict:
        """Devuelve un resumen del estado del Engine y sus módulos."""
        inv = self.registro.resumen()
        inv["constantes"] = {
            "alpha": str(self.ALPHA),
            "beta": str(self.BETA),
            "suma_exacta": self.ALPHA + self.BETA == Fraction(1),
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
                "factores": {},
                "tru_ri": None,
                "tru_total": None,
                "fallos": [],
                "anotaciones": [],
            }
        return self.evaluar(peticion)
