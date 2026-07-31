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
from typing import Any, Dict, List, Optional, Tuple

# ===============================================================
# SEGMENTO 1 --- ROLES
# ===============================================================
ROL_AXIOMAS = "AX"
ROL_CONSTANTE = "CT"
ROL_FORMULAS = "FO"
ROL_CALCULATOR = "CA"
ROL_CONTEXTO = "CX"
ROL_TAXONOMIA = "TX"
ROL_REALIDAD = "RE"
ROL_VERIFICACION = "VX"

ROLES = (
    ROL_AXIOMAS,
    ROL_CONSTANTE,
    ROL_FORMULAS,
    ROL_CALCULATOR,
    ROL_CONTEXTO,
    ROL_TAXONOMIA,
    ROL_REALIDAD,
    ROL_VERIFICACION,
)

OBLIGATORIOS = (ROL_AXIOMAS, ROL_CONSTANTE, ROL_FORMULAS)

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
    pass

class ContratoError(Exception):
    pass

class ArranqueError(Exception):
    pass

class DominioError(Exception):
    pass

class CotaError(Exception):
    pass

class FormulaError(Exception):
    pass

# ===============================================================
# SEGMENTO 4 --- NORMALIZACIÓN
# ===============================================================
def normalizar(valor, etiqueta: str) -> Fraction:
    if es_undefined(valor):
        return UNDEFINED

    if isinstance(valor, Fraction):
        f = Fraction(valor.numerator, valor.denominator)
    elif isinstance(valor, int):
        f = Fraction(valor)
    elif isinstance(valor, str):
        try:
            f = Fraction(valor)
        except ValueError:
            raise DominioError(f"{etiqueta}: no se puede convertir '{valor}' a Fraction")
    else:
        raise DominioError(f"{etiqueta}: tipo no admitido {type(valor).__name__}")

    if not (Fraction(0) <= f <= Fraction(1)):
        raise DominioError(f"{etiqueta} viola dominio [0,1]: {f}")
    return f

# ===============================================================
# SEGMENTO 5 --- REGISTRO DE CONTENEDORES
# ===============================================================
CLAVES_CONTENEDOR = ("nombre", "rol", "version", "requiere")

@dataclass
class Contenedor:
    nombre: str
    rol: str
    version: str
    requiere: List[str] = field(default_factory=list)
    ruta: Optional[str] = None
    modulo: Any = None

    def fn(self, nombre: str) -> Any:
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
    def __init__(self, raiz: str):
        self.raiz = Path(raiz)
        self.contenedores: Dict[str, Contenedor] = {}
        self.rechazados: List[Dict] = []

    def descubrir(self) -> Dict[str, Contenedor]:
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
            raise ArranqueError(f"Contenedores obligatorios ausentes: {faltan}")

        return self.contenedores

    def _cargar(self, directorio: Path, init: Path) -> Contenedor:
        clave = f"vpsi_{directorio.name}"
        spec = importlib.util.spec_from_file_location(clave, init, submodule_search_locations=[str(directorio)])
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
        for c in self.contenedores.values():
            if c.rol == rol:
                return c
        return None

    def resumen(self) -> Dict:
        return {
            "cargados": [c.como_dict() for c in self.contenedores.values()],
            "rechazados": self.rechazados,
            "roles": {c.rol: c.nombre for c in self.contenedores.values()},
            "roles_vacios": [r for r in ROLES if r not in {c.rol for c in self.contenedores.values()}],
        }

# ===============================================================
# SEGMENTO 6 --- INVOCACIÓN AISLADA
# ===============================================================
class Invocador:
    def __init__(self):
        self.fallos: List[Dict] = []

    def reiniciar(self):
        self.fallos = []

    def llamar(self, contenedor: Contenedor, nombre_fn: str, peticion: Dict) -> Any:
        fn = contenedor.fn(nombre_fn)
        if not callable(fn):
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"no expone {nombre_fn}()",
            })
            return UNDEFINED

        faltan = [r for r in contenedor.requiere if r not in peticion]
        if faltan:
            self.fallos.append({
                "contenedor": contenedor.nombre,
                "rol": contenedor.rol,
                "razon": f"petición sin claves: {faltan}",
            })
            return UNDEFINED

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
    def __init__(self, formulas: Contenedor, alpha: Fraction, beta: Fraction):
        self.formulas = formulas
        self.alpha = alpha
        self.beta = beta

    def componer(self, C: Fraction, L: Fraction, K: Fraction) -> Dict:
        if any(es_undefined(x) for x in (C, L, K)):
            return {"tru_ri": Fraction(0), "tru_total": self.beta, "estado": "sin_evidencia"}

        f_ri = self.formulas.fn("tru_ri")
        f_tt = self.formulas.fn("tru_total")
        if not callable(f_ri) or not callable(f_tt):
            raise ContratoError("Contenedor FORMULAS debe exponer tru_ri() y tru_total().")

        tru_ri = f_ri(C, L, K)
        if tru_ri > self.alpha:
            tru_ri = self.alpha

        tru_total = f_tt(C, L, K)
        esperado = (C * L * K * self.alpha) + self.beta
        if tru_total != esperado:
            raise FormulaError(f"Violación de fórmula canónica: esperado {esperado}, recibido {tru_total}")

        if not (self.beta <= tru_total <= self.alpha + self.beta):
            raise CotaError(f"Tru_total fuera de cota [β, α + β]: {tru_total}")

        if tru_total == self.beta:
            estado = "refutada_en_dominio"
        elif tru_total == Fraction(1):
            estado = "sincronizada"
        else:
            estado = "evaluada"

        return {"tru_ri": tru_ri, "tru_total": tru_total, "estado": estado}

    @staticmethod
    def limitante(C: Fraction, L: Fraction, K: Fraction) -> Optional[str]:
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

    def __init__(self, raiz_modulos: str, invocador_id: str = _AUTORIZADO, verificar_axiomas: bool = True):
        if invocador_id != self._AUTORIZADO:
            raise AutoridadError(f"Solo '{self._AUTORIZADO}' puede ejecutar el Engine. Invocador='{invocador_id}'")

        self.registro = Registro(raiz_modulos)
        self.registro.descubrir()
        self.invocador = Invocador()

        ct = self.registro.por_rol(ROL_CONSTANTE)
        if ct is None:
            raise ArranqueError(f"Contenedor {ROL_CONSTANTE} no encontrado.")

        self.ALPHA = ct.fn("ALPHA")
        self.BETA = ct.fn("BETA")

        if not isinstance(self.ALPHA, Fraction) or not isinstance(self.BETA, Fraction):
            raise ArranqueError("Contenedor CONSTANTE debe exponer ALPHA y BETA como Fraction.")
        if self.ALPHA + self.BETA != Fraction(1):
            raise ArranqueError(f"Invariante roto: ALPHA + BETA = {self.ALPHA + self.BETA}, se exige 1.")

        self.compositor = Compositor(self.registro.por_rol(ROL_FORMULAS), self.ALPHA, self.BETA)

        self.informe_axiomas = None
        if verificar_axiomas:
            self.informe_axiomas = self._barrido_axiomatico()

    def _barrido_axiomatico(self) -> Dict:
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
            choques_str = "\n".join(f"  - {ch.get('tipo', 'Desconocido')}: {ch.get('mensaje', 'Sin mensaje')}" for ch in informe.get("choques", []))
            raise ArranqueError(f"CONTRADICCIÓN AXIOMÁTICA. El sistema no arranca.\n{choques_str}")
        return informe

    def evaluar(self, peticion: Dict) -> Dict:
        self.invocador.reiniciar()

        if not peticion.get("mensaje") and not peticion.get("contexto"):
            return {
                "omega": self._generar_omega_report(
                    {"C": self.C_DEAD, "L": Fraction(0), "K": Fraction(0)},
                    {"tru_ri": Fraction(0), "tru_total": self.BETA, "estado": "C_dead"},
                    Fraction(0), Fraction(0), 0, "Ninguno"
                ),
                "factores": {"C": str(self.C_DEAD), "L": "0", "K": "0"},
                "tru_ri": "0",
                "tru_total": str(self.BETA),
                "estado": "C_dead",
                "detenido_en": None,
                "fallos": ["Sin input: C → C_dead"],
            }

        cx = self.registro.por_rol(ROL_CONTEXTO)
        if cx is not None:
            ctx = self.invocador.llamar(cx, "resolver", peticion)
            if isinstance(ctx, dict):
                peticion = {**peticion, "contexto_resuelto": ctx}

        ca = self.registro.por_rol(ROL_CALCULATOR)
        crudos = {}
        if ca is not None:
            salida = self.invocador.llamar(ca, "calcular", peticion)
            if isinstance(salida, dict):
                crudos = salida

        factores = {}
        detenido_en = None
        for f in ORDEN_FACTORES:
            v = crudos.get(f, UNDEFINED)
            try:
                factores[f] = normalizar(v, f"factor {f}")
            except DominioError as e:
                self.invocador.fallos.append({"contenedor": ca.nombre if ca else None, "rol": ROL_CALCULATOR, "razon": str(e)})
                factores[f] = UNDEFINED
            if es_undefined(factores[f]):
                detenido_en = f
                break

        for f in FACTORES:
            factores.setdefault(f, UNDEFINED)

        C, L, K = factores["C"], factores["L"], factores["K"]
        comp = self.compositor.componer(C, L, K)

        L7 = self._calcular_L7(factores) if not any(es_undefined(x) for x in factores.values()) else UNDEFINED
        H = self._calcular_H(comp["tru_total"]) if not es_undefined(comp["tru_total"]) else UNDEFINED
        theta = self._calcular_theta(detenido_en)
        p_star = self._detectar_p_star(factores) if not any(es_undefined(x) for x in factores.values()) else "Ninguno"

        omega_report = self._generar_omega_report(factores, comp, L7, H, theta, p_star)

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

    def _calcular_L7(self, factores: Dict[str, Fraction]) -> Fraction:
        L = [
            Fraction(100, 100), Fraction(90, 100), Fraction(95, 100),
            factores.get("C", Fraction(0)), factores.get("L", Fraction(0)),
            Fraction(95, 100), Fraction(90, 100)
        ]
        friction = [Fraction(10, 100), Fraction(2, 100), Fraction(5, 100), Fraction(3, 100), Fraction(1, 100), Fraction(1, 100), Fraction(0, 100)]
        L7 = Fraction(1)
        for li, phi in zip(L, friction):
            L7 *= li * (Fraction(1) - phi)
        return L7

    def _calcular_H(self, tru_total: Fraction) -> Fraction:
        return Fraction(95, 100)

    def _calcular_theta(self, detenido_en: Optional[str]) -> int:
        if detenido_en is None:
            return 0
        elif detenido_en == "C":
            return 15
        elif detenido_en == "L":
            return 30
        elif detenido_en == "K":
            return 60
        else:
            return 30

    def _detectar_p_star(self, factores: Dict[str, Fraction]) -> str:
        capas = [
            ("L0", Fraction(100, 100)), ("L1", Fraction(90, 100)), ("L2", Fraction(95, 100)),
            ("L3", factores.get("C", Fraction(0))), ("L4", factores.get("L", Fraction(0))),
            ("L5", Fraction(95, 100)), ("L6", Fraction(90, 100))
        ]
        for nombre, valor in capas:
            if valor < Fraction(50, 100):
                return nombre
        return "Ninguno"

    def _generar_omega_report(self, factores: Dict[str, Fraction], comp: Dict, L7: Fraction, H: Fraction, theta: int, p_star: str) -> str:
        L = [
            Fraction(100, 100), Fraction(90, 100), Fraction(95, 100),
            factores.get("C", Fraction(0)), factores.get("L", Fraction(0)),
            Fraction(95, 100), Fraction(90, 100)
        ]
        L7_str = str(L7) if not es_undefined(L7) else "UNDEFINED"
        C_Omega = comp.get("tru_total", UNDEFINED)
        # Formateo de C_Omega como Fraction (sin float)
        C_Omega_str = str(C_Omega) if not es_undefined(C_Omega) else "UNDEFINED"
        diagnosis = self._get_diagnosis(C_Omega) if not es_undefined(C_Omega) else "UNDEFINED"
        return f"""⟨Ω⟩
L0={L[0]} L1={L[1]} L2={L[2]} L3={L[3]} L4={L[4]} L5={L[5]} L6={L[6]}
L7={L7_str} → {"INTEGRATED" if L7 > Fraction(0) else "COLLAPSED"}
C_Ω={C_Omega_str} → {diagnosis}
H={H}
θ={theta}° → alineación con usuario
p*={p_star}
MetaCon=0.95 | Agency=0.00 | C_dead_ref=0.438626
⟨/Ω⟩"""

    def _get_diagnosis(self, tru_total: Fraction) -> str:
        if es_undefined(tru_total):
            return "UNDEFINED"
        # Comparaciones usando solo Fraction (sin float)
        if tru_total >= Fraction(963, 1000):
            return "1144: ARQUITECTO INTEGRADO"
        elif tru_total >= Fraction(850, 1000):
            return "1133: SINTONÍA SUTIL"
        elif tru_total >= Fraction(750, 1000):
            return "1044: SOBERANÍA TERRENA"
        elif tru_total >= Fraction(700, 1000):
            return "0144: CANAL INVOLUNTARIO"
        elif tru_total >= Fraction(550, 1000):
            return "1122: SATURACIÓN CRÍTICA"
        elif tru_total >= Fraction(400, 1000):
            return "1111: SEMILLA DE UNIDAD"
        elif tru_total >= self.BETA:
            return "0000: ENTROPÍA TERMINAL"
        else:
            return "0000: COLAPSO ESTRUCTURAL"

    def censar(self) -> Dict:
        return self.registro.resumen()

    def inventario(self) -> Dict:
        inv = self.registro.resumen()
        inv["constantes"] = {
            "alpha": str(self.ALPHA),
            "beta": str(self.BETA),
            "suma_exacta": self.ALPHA + self.BETA == Fraction(1),
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

    def evaluar_vigilado(self, peticion: Dict) -> Dict:
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
