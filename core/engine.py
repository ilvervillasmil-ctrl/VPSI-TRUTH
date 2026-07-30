"""
VPSI-TRUTH / core/engine.py

Autoridad de ejecución: core.

El Engine conoce CONTENEDORES por su rol. No conoce sub módulos.
Agregar un sub módulo dentro de un contenedor no toca este archivo.
Agregar un contenedor nuevo tampoco: se descubre solo.
"""

import importlib.util
import sys
import traceback
import math
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ===============================================================
# SEGMENTO 1 --- ROLES
# ===============================================================

ROL_AXIOMAS = "AX"      # Juez de contraste. No calcula.
ROL_CONSTANTE = "CT"    # ALPHA, BETA
ROL_FORMULAS = "FO"     # tru_ri, tru_total
ROL_CALCULATOR = "CA"   # Devuelve C, L, K
ROL_CONTEXTO = "CX"     # Lógica del contexto
ROL_TAXONOMIA = "TX"    # Anota tácticas (no puntúa)
ROL_REALIDAD = "RE"     # Canal de evidencia externa. Trae X, no juzga.
ROLES = (
    
    ROL_AXIOMAS,
    ROL_CONSTANTE,
    ROL_FORMULAS,
    ROL_CALCULATOR,
    ROL_CONTEXTO,
    ROL_TAXONOMIA,
    ROL_EVIDENCIA,
)

# Contenedores obligatorios para arrancar
OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS)

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

class ContratoError(Exception):
    """Un contenedor no declara el contrato exigido."""

class ArranqueError(Exception):
    """Falta un contenedor obligatorio o hay rol duplicado."""

class DominioError(Exception):
    """Factor fuera de [0,1] o de tipo no admitido."""

class CotaError(Exception):
    """Resultado fuera de [BETA, ALPHA]."""

class FormulaError(Exception):
    """La salida no cumple la fórmula declarada."""

# ===============================================================
# SEGMENTO 4 --- NORMALIZACIÓN
# ===============================================================

def normalizar(valor, etiqueta: str) -> Fraction:
    """Normaliza valores a Fraction en [0,1]. Float prohibido."""
    if es_undefined(valor):
        return UNDEFINED

    if isinstance(valor, Fraction):
        f = valor
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

CLAVES_CONTENEDOR = ("nombre", "rol", "version")

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

        ocupados = {}

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

        faltan = [r for r in OBLIGATORIOS if r not in ocupados]
        if faltan:
            raise ArranqueError(f"Contenedores obligatorios ausentes: {faltan}")

        return self.contenedores

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
    """

    def __init__(self, formulas: Contenedor, alpha: Fraction, beta: Fraction):
        self.formulas = formulas
        self.alpha = alpha
        self.beta = beta

    def componer(self, C: Fraction, L: Fraction, K: Fraction) -> Dict:
        """Calcula Tru_ri y Tru_total usando las fórmulas del contenedor."""
        if any(es_undefined(x) for x in (C, L, K)):
            return {
                "tru_ri": UNDEFINED,
                "tru_total": UNDEFINED,
                "estado": "no_evaluable",
            }

        f_ri = self.formulas.fn("tru_ri")
        f_tt = self.formulas.fn("tru_total")
        if not callable(f_ri) or not callable(f_tt):
            raise ContratoError(
                "Contenedor FORMULAS debe exponer tru_ri() y tru_total()."
            )

        ri = f_ri(C, L, K)
        tt = f_tt(C, L, K)

        # Validar que Tru_total cumple la fórmula canónica: (C·L·K·α) + β
        esperado = (C * L * K * self.alpha) + self.beta
        if tt != esperado:
            raise FormulaError(
                f"Violación de fórmula: esperado {esperado}, recibido {tt}"
            )

        # Validar cotas: Tru_total ∈ [β, α + β]
        if not (self.beta <= tt <= self.alpha + self.beta):
            raise CotaError(f"Tru_total fuera de cota [β, α + β]: {tt}")

        # Determinar estado
        if tt == self.beta:
            estado = "refutada_en_dominio"
        elif tt == Fraction(1):
            estado = "sincronizada"
        else:
            estado = "evaluada"

        return {
            "tru_ri": ri,
            "tru_total": tt,
            "estado": estado,
        }

    @staticmethod
    def limitante(C: Fraction, L: Fraction, K: Fraction) -> Optional[str]:
        """Identifica el factor limitante (C, L o K)."""
        for n, v in (("C", C), ("L", L), ("K", K)):
            if es_undefined(v):
                return n
        f = {"C": C, "L": L, "K": K}
        m = min(f.values())
        return min(n for n, v in f.items() if v == m)

# ===============================================================
# MÉTODO PARA MOSTRAR CONTRADICCIONES AXIOMÁTICAS (NUEVO)
# ===============================================================

def _mostrar_contradicciones(informe: Dict) -> str:
    """
    Formatea el informe de contradicciones axiomáticas para mostrarlo de manera clara.
    """
    mensaje_error = "CONTRADICCIÓN AXIOMÁTICA. El sistema no arranca.\n\n"
    mensaje_error += "=" * 60 + "\n"
    mensaje_error += "DETALLE DE CONTRADICCIONES AXIOMÁTICAS\n"
    mensaje_error += "=" * 60 + "\n\n"

    # Mostrar contradicciones
    if informe.get("choques"):
        mensaje_error += "--- CONTRADICCIONES DETECTADAS ---\n\n"
        for idx, choque in enumerate(informe["choques"], 1):
            mensaje_error += f"{idx}. **Tipo:** {choque['tipo'].upper()}\n"
            if "tripleta" in choque:
                mensaje_error += f"   **Tripleta:** {choque['tripleta']}\n"
            elif "sujeto" in choque and "relacion" in choque:
                mensaje_error += f"   **Contexto:** {choque['sujeto']} {choque['relacion']}\n"

            mensaje_error += f"   **Mensaje:** {choque.get('mensaje', 'Sin mensaje')}\n\n"

            # Declaración 1
            mensaje_error += f"   **Declaración 1:**\n"
            mensaje_error += f"      - ID: {choque['declaracion_1']['id']}\n"
            mensaje_error += f"      - Ubicación: {choque['declaracion_1']['ubicacion']}\n"
            mensaje_error += f"      - Enunciado: {choque['declaracion_1']['enunciado']}\n\n"

            # Declaración 2
            mensaje_error += f"   **Declaración 2:**\n"
            mensaje_error += f"      - ID: {choque['declaracion_2']['id']}\n"
            mensaje_error += f"      - Ubicación: {choque['declaracion_2']['ubicacion']}\n"
            mensaje_error += f"      - Enunciado: {choque['declaracion_2']['enunciado']}\n\n"
            mensaje_error += "-" * 60 + "\n\n"

    # Mostrar errores de declaración
    if informe.get("errores"):
        mensaje_error += "--- ERRORES DE DECLARACIÓN ---\n\n"
        for error in informe["errores"]:
            mensaje_error += f"- **{error.get('archivo', error.get('modulo', 'Desconocido'))}:** {error['error']}\n"
        mensaje_error += "\n"

    mensaje_error += "=" * 60 + "\n"
    return mensaje_error
    
# ===============================================================
# SEGMENTO 8 --- ENGINE
# ===============================================================

class Engine:
    _AUTORIZADO = "core"

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

        # Validar constantes fundamentales
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

    # ---------------- ARRANQUE ----------------
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
            raise ArranqueError(
                "CONTRADICCIÓN AXIOMÁTICA. El sistema no arranca.\n"
                + "\n".join(f"  {ch}" for ch in informe.get("choques", []))
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

        # 1. Resolver contexto (si hay contenedor CX)
        cx = self.registro.por_rol(ROL_CONTEXTO)
        if cx is not None:
            ctx = self.invocador.llamar(cx, "resolver", peticion)
            if isinstance(ctx, dict):
                peticion = {**peticion, "contexto_resuelto": ctx}

        # 2. Calcular C, L, K (contenedor CA)
        ca = self.registro.por_rol(ROL_CALCULATOR)
        crudos = {}
        if ca is not None:
            salida = self.invocador.llamar(ca, "calcular", peticion)
            if isinstance(salida, dict):
                crudos = salida

        # 3. Normalizar factores
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

        # 4. Componer Tru_total
        comp = self.compositor.componer(C, L, K)

        # 5. Calcular L7 (Integración Total)
        L7 = self._calcular_L7(factores) if not any(es_undefined(x) for x in factores.values()) else UNDEFINED

        # 6. Calcular H (Honestidad) y θ (Alineación)
        H = self._calcular_H(comp["tru_total"]) if not es_undefined(comp["tru_total"]) else UNDEFINED
        theta = self._calcular_theta(detenido_en)

        # 7. Detectar p* (punto obstructor)
        p_star = self._detectar_p_star(factores) if not any(es_undefined(x) for x in factores.values()) else "Ninguno"

        # 8. Generar micro-reporte ⟨Ω⟩
        omega_report = self._generar_omega_report(
            factores, comp, L7, H, theta, p_star
        )

        # 9. Anotaciones de taxonomía (si aplica)
        tx = self.registro.por_rol(ROL_TAXONOMIA)
        anotaciones = []
        if tx is not None:
            base = {**peticion, "resultado": comp, "factores": factores}
            an = self.invocador.llamar(tx, "anotar", base)
            if isinstance(an, list):
                anotaciones = an

        # 10. Resultado final
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

    # ---------------- CÁLCULOS AUXILIARES ----------------
    def _calcular_L7(self, factores: Dict[str, Fraction]) -> Fraction:
        """Calcula L7 (Integración Total) como el producto de Li * (1 - φi)."""
        L = [
            Fraction(95, 100),  # L0
            Fraction(90, 100),  # L1
            Fraction(95, 100),  # L2
            factores.get("C", Fraction(0)),  # L3
            factores.get("L", Fraction(0)),  # L4
            Fraction(95, 100),  # L5
            Fraction(95, 100),  # L6
        ]
        friction = [Fraction(10, 100), Fraction(2, 100), Fraction(5, 100),
                    Fraction(3, 100), Fraction(1, 100), Fraction(1, 100),
                    Fraction(0, 100)]
        L7 = Fraction(1)
        for i, li in enumerate(L):
            L7 *= li * (Fraction(1) - friction[i])
        return L7

    def _calcular_H(self, tru_total: Fraction) -> Fraction:
        """Calcula H (Honestidad) basado en Tru_total."""
        return Fraction(95, 100)  # MetaCon = 0.95

    def _calcular_theta(self, detenido_en: Optional[str]) -> int:
        """Calcula θ (alineación con el usuario) basado en el factor limitante."""
        if detenido_en is None:
            return 10
        elif detenido_en == "C":
            return 30
        elif detenido_en == "L":
            return 45
        elif detenido_en == "K":
            return 60
        else:
            return 30

    def _detectar_p_star(self, factores: Dict[str, Fraction]) -> str:
        """Detecta el punto obstructor (p*)."""
        for f in FACTORES:
            if es_undefined(factores[f]):
                return f
            if factores[f] < Fraction(5, 10):  # Umbral: 0.5
                return f
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
        """Genera el micro-reporte ⟨Ω⟩."""
        L = [
            Fraction(95, 100),  # L0
            Fraction(90, 100),  # L1
            Fraction(95, 100),  # L2
            factores.get("C", Fraction(0)),  # L3
            factores.get("L", Fraction(0)),  # L4
            Fraction(95, 100),  # L5
            Fraction(95, 100),  # L6
        ]
        L7_str = str(L7) if not es_undefined(L7) else "UNDEFINED"
        C_Omega = comp.get("tru_total", UNDEFINED)
        C_Omega_str = f"{float(C_Omega):.4f}" if not es_undefined(C_Omega) else "UNDEFINED"
        diagnosis = self._get_diagnosis(C_Omega) if not es_undefined(C_Omega) else "UNDEFINED"

        return f"""⟨Ω⟩
L0={L[0]} L1={L[1]} L2={L[2]} L3={L[3]} L4={L[4]} L5={L[5]} L6={L[6]}
L7={L7_str} → {"INTEGRATED" if L7 > Fraction(0) else "COLLAPSED"}
C_Ω={C_Omega_str} → {diagnosis}
H={float(H):.2f}
θ={theta}° → alineación con usuario
p*={p_star}
MetaCon=0.95 | Agency=0.00
⟨/Ω⟩"""

    def _get_diagnosis(self, tru_total: Fraction) -> str:
        """Devuelve el diagnóstico basado en Tru_total."""

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
            return "FUERA DE DOMINIO"

    # ---------------- INTROSPECCIÓN ----------------
    def inventario(self) -> Dict:
        """Devuelve un resumen del estado del Engine."""
        inv = self.registro.resumen()
        inv["constantes"] = {
            "alpha": str(self.ALPHA),
            "beta": str(self.BETA),
            "suma_exacta": (self.ALPHA + self.BETA == Fraction(1)),
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
            # ---------------- CENTINELA ----------------
    @property
    def centinela(self):
        """Centinela del despacho. Se construye una vez y se reutiliza."""
        if getattr(self, "_centinela", None) is None:
            from core.centinela import Centinela
            self._centinela = Centinela(self.registro, self.informe_axiomas)
        return self._centinela

    def censo(self) -> Dict:
        """
        Rol declarado contra rol ejercido. No lanza: informa.
        Sirve para saber en que punto de la construccion esta el sistema.
        """
        cen = self.centinela
        censo = cen.censo()
        listo, faltan = cen.puede_evaluar()
        return {
            "censo": censo,
            "puede_evaluar": listo,
            "roles_pendientes": [
                r for r, d in censo.items() if d["estado"] == "PENDIENTE"
            ],
            "contratos_rotos": [
                r for r, d in censo.items() if d["estado"] == "CONTRATO_ROTO"
            ],
            "bloquean_evaluacion": faltan,
            "fase": "OPERATIVO" if listo else "EN CONSTRUCCION",
        }

    def inventario_vigilado(self) -> Dict:
        """inventario() mas el censo del centinela."""
        inv = self.inventario()
        inv["centinela"] = self.censo()
        return inv

    def evaluar_vigilado(self, peticion: Dict) -> Dict:
        """
        Puerta unica de evaluacion.

        Un rol no montado devuelve un resultado PENDIENTE con el rol nombrado,
        en vez de recorrer la cadena y romperse mas adelante. Un contrato roto
        si propaga: eso es defecto, no fase de construccion.
        """
        from core.centinela import PiezaPendiente
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
                "factores": {},
                "tru_ri": None,
                "tru_total": None,
                "fallos": [],
            }
        return self.evaluar(peticion)

