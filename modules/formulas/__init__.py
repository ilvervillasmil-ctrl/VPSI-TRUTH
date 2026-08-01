from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
from fractions import Fraction
from typing import Any, Callable, Dict, List
from core.diagnostico import DiagnosticoGlobal  # Integración con Diagnostics

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================
CONTENEDOR = {
    "nombre": "formulas",
    "rol": "FO",
    "version": "1.0",
    "requiere": ["CT"],  # Depende de constantes (ALPHA, BETA)
    "descripcion": "Contenedor de fórmulas. Rol FO. Expone tru_ri y tru_total al Engine.",
}

_DIR = Path(__file__).parent

# ===============================================================
# SEGMENTO 2 --- ERRORES
# ===============================================================
class FormulaError(Exception):
    """Error en el cálculo de fórmulas."""
    pass

class FormulaNoEncontradaError(Exception):
    """Fórmula requerida no encontrada en el directorio."""
    pass

# ===============================================================
# SEGMENTO 3 --- CONSTANTES Y CONTRATOS
# ===============================================================
PISO_FORMULAS = 1  # Mínimo de fórmulas para evitar coherencia por vacuidad

# ===============================================================
# SEGMENTO 4 --- ESTADO (Colecciones auto-llenables)
# ===============================================================
_DECLARACIONES: List[Dict[str, Any]] = []  # Axiomas/teoremas del módulo
_REGLAS: List[Callable[[], List[str]]] = []  # Reglas de validación
_FORMULAS: Dict[str, Dict[str, Any]] = {}  # Fórmulas descubiertas

# ===============================================================
# SEGMENTO 5 --- GANCHOS DE ANEXO (Decoradores)
# ===============================================================
def regla(fn: Callable[[], List[str]]) -> Callable[[], List[str]]:
    """Registra una regla de validación."""
    _REGLAS.append(fn)
    return fn

def declarar(d: Dict[str, Any]) -> Dict[str, Any]:
    """Registra una declaración axiomática."""
    _DECLARACIONES.append(d)
    return d

def registrar_formula(nombre: str, meta: Dict[str, Any]):
    """Registra una fórmula en el inventario."""
    def decorator(fn: Callable) -> Callable:
        _FORMULAS[nombre] = {
            **meta,
            "funcion": fn,
        }
        return fn
    return decorator

# ===============================================================
# SEGMENTO 6 --- LECTURA (Funciones privadas)
# ===============================================================
def _descubrir_formulas() -> Dict[str, Dict[str, Any]]:
    """
    Descubre todas las fórmulas en el directorio que declaran FORMULA.
    Cada archivo .py (excepto __init__.py) debe definir un diccionario FORMULA.
    """
    registro = {}
    for f in sorted(_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue  # Ignorar __init__.py
        clave = f"formulas_{f.stem}"
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)
        meta = getattr(mod, "FORMULA", None)
        if isinstance(meta, dict) and "nombre" in meta:
            registro[meta["nombre"]] = {
                "archivo": f.name,
                "expresion": meta.get("expresion", "No definida"),
                "fuente": meta.get("fuente", "Desconocida"),
            }
    return registro

# ===============================================================
# SEGMENTO 7 --- ENGINE (Orquestador)
# ===============================================================
def barrer() -> Dict[str, Any]:
    """
    Ejecuta todas las reglas y devuelve un informe.
    Orquesta la lógica del módulo:
    1. Descubre fórmulas en el directorio.
    2. Valida las reglas internas.
    """
    faltas: List[str] = []
    for regla_fn in _REGLAS:
        try:
            faltas.extend(regla_fn() or [])
        except Exception as e:
            faltas.append(f"{regla_fn.__name__}: {type(e).__name__}: {e}")

    # Enviar reporte a DiagnosticoGlobal si hay faltas (Reporte Omega)
    if faltas:
        DiagnosticoGlobal.recibir_reporte(
            modulo="formulas",
            errores=[{"tipo": "falta", "detalle": falta} for falta in faltas]
        )

    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": "APROBADO" if not faltas else "RECHAZADO",
        "coherente": not faltas,
        "faltas": faltas,
        "reglas": [r.__name__ for r in _REGLAS],
    }

# ===============================================================
# SEGMENTO 8 --- CENTINELA (Eyenet)
# ===============================================================
def verificar_salida(salida: Dict[str, Any]) -> bool:
    """
    Valida la salida del Engine (barrer).
    - Si la salida es coherente, devuelve True.
    - Si no lo es, ya se envió un reporte a DiagnosticoGlobal en barrer().
    """
    return salida.get("coherente", False)

# ===============================================================
# SEGMENTO 9 --- API DEL CONTENEDOR (Contrato con el Engine)
# ===============================================================
def inventario() -> Dict[str, Any]:
    """Devuelve metadatos del contenedor."""
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "formulas": _descubrir_formulas(),
        "reglas": len(_REGLAS),
        "declaraciones": len(_DECLARACIONES),
    }

def axiomas() -> List[Dict[str, Any]]:
    """Devuelve las declaraciones axiomáticas del módulo."""
    return _DECLARACIONES

# ===============================================================
# SEGMENTO 10 --- REGLAS (Validaciones internas)
# ===============================================================
@regla
def _validar_piso_formulas() -> List[str]:
    """Verifica que haya al menos PISO_FORMULAS fórmulas."""
    if len(_descubrir_formulas()) < PISO_FORMULAS:
        return [f"Menos de {PISO_FORMULAS} fórmulas: coherencia por vacuidad"]
    return []

@regla
def _validar_formulas_canónicas() -> List[str]:
    """Verifica que tru_ri y tru_total estén definidas."""
    faltas = []
    if "tru_ri" not in _FORMULAS:
        faltas.append("Fórmula tru_ri no encontrada.")
    if "tru_total" not in _FORMULAS:
        faltas.append("Fórmula tru_total no encontrada.")
    return faltas

# ===============================================================
# SEGMENTO 11 --- DECLARACIONES (Axiomas/Teoremas del módulo)
# ===============================================================
declarar({
    "id": "FO-1",
    "tipo": "axioma",
    "sujeto": "Tru_Ri",
    "relacion": "=",
    "objeto": "C * L * K",
    "polaridad": True,
    "enunciado": "Tru_Ri(D) = C(D) * L(D) * K(D) (Axioma TA5: Multiplicatividad).",
    "cota": None,
    "depende_de": ["TA5"],
    "gobierna": ["tru_ri"],
})

declarar({
    "id": "FO-2",
    "tipo": "axioma",
    "sujeto": "Tru_total",
    "relacion": "=",
    "objeto": "(Tru_Ri * ALPHA) + BETA",
    "polaridad": True,
    "enunciado": "Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA (Definición 2.14).",
    "cota": None,
    "depende_de": ["Def-2.14"],
    "gobierna": ["tru_total"],
})

declarar({
    "id": "FO-3",
    "tipo": "teorema",
    "sujeto": "Tru_Ri",
    "relacion": "≤",
    "objeto": "ALPHA",
    "polaridad": True,
    "enunciado": "Tru_Ri(D) ≤ ALPHA = 26/27 (Teorema 16: Techo Estructural).",
    "cota": "26/27",
    "depende_de": ["T16"],
    "gobierna": ["tru_ri"],
})

declarar({
    "id": "FO-4",
    "tipo": "teorema",
    "sujeto": "Tru_total",
    "relacion": "≥",
    "objeto": "BETA",
    "polaridad": True,
    "enunciado": "Tru_total(D) ≥ BETA = 1/27 (Teorema 17: Piso Estructural).",
    "cota": "1/27",
    "depende_de": ["T17"],
    "gobierna": ["tru_total"],
})

# ===============================================================
# ZONA DE ANEXO
# ===============================================================
# Importar fórmulas canónicas (truth.py)
from .truth import tru_ri, tru_total, FORMULA as TRUTH_FORMULA

# Registrar fórmulas canónicas con el decorador
@registrar_formula("tru_ri", TRUTH_FORMULA)
def _tru_ri_wrapper(C, L, K):
    """Wrapper para tru_ri (compatibilidad con el decorador)."""
    return tru_ri(C, L, K)

@registrar_formula("tru_total", TRUTH_FORMULA)
def _tru_total_wrapper(C, L, K):
    """Wrapper para tru_total (compatibilidad con el decorador)."""
    return tru_total(C, L, K)

# ===============================================================
# CONTENEDOR (Contrato final)
# ===============================================================
CONTENEDOR = {
    "nombre": "formulas",
    "rol": "FO",
    "version": "1.0",
    "requiere": ["CT"],  # Depende de constantes (ALPHA, BETA)
    "descripcion": "Contenedor de fórmulas. Rol FO. Expone tru_ri y tru_total al Engine.",
    "capacidades": {
        "verificar": barrer,      # Capacidad para validar el módulo
        "evaluar": barrer,        # Igual que "verificar"
        "axiomas": axiomas,       # Devuelve declaraciones axiomáticas
        "inventario": inventario, # Devuelve metadatos
    }
}

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "barrer",
    "axiomas",
    "inventario",
    "verificar_salida",  # Nueva función para el Centinela
    "FormulaError",
    "FormulaNoEncontradaError",
]
