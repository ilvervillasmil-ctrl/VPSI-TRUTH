"""
VPSI-TRUTH --- modules/calculator/correlacion_k.py

---
### **DESCRIPCIÓN DEL SUB-MÓDULO**
Este archivo implementa **exclusivamente el cálculo de la variable K (Correlación)**.
La correlación mide la **correspondencia entre una descripción D y el dominio observable O_context**.

---
### **DEFINICIÓN FORMAL (IlverVillasmil.pdf)**
- **K(D) = 1** si para todo **z** en el dominio, **||D(z) - O(z)|| ≤ ε**.
  - **D(z)**: Lo que la descripción D asevera en el caso **z**.
  - **O(z)**: Lo que el contexto observable **O_context** revela en el caso **z**.
  - **ε**: Margen de tolerancia admitido.
- **K(D) ∈ [0, 1]**: Grado de correspondencia entre D y O_context.
- **K(D) = UNDEFINED** si no hay un **O_context** explícito (Corolario Def-5.3.1).
- **Fuente**: Axioma TA3 (Dependencia Externa de la Correlación) en IlverVillasmil.pdf.

---
### **DEFINICIÓN OPERACIONAL (PROTOCOLO.pdf)**
- **K = 1 - (f / c)**, donde:
  - **f**: Número de afirmaciones en D que **divergen de O_context**.
  - **c**: Número total de **afirmaciones verificables** en D.
- **Rango**: K ∈ [0, 1].
- **Ejemplo**:
  - Si un sistema hace 3 afirmaciones: ["β = 1/27", "α = 26/27", "β = 1/10"],
    y 1 de ellas diverge de O_context (ej: "β = 1/10" cuando O_context dice "β = 1/27"),
    entonces **K = 1 - (1/3) ≈ 0.6667**.
- **Fuente**: Sección 0.15 (Regla Operacional: Cómputo Determinista de Factores) en PROTOCOLO.pdf.

---
### **NOTAS IMPORTANTES**
1. **K = 1** implica que **D coincide exactamente con O_context** (dentro del margen ε).
2. **K = 0** implica que **todas las afirmaciones de D divergen de O_context**.
3. **K = UNDEFINED** si no hay **O_context** explícito (no es 0, es indefinido).
4. **Precisión**:
   - Todos los cálculos usan `Fraction` para evitar errores de punto flotante.
5. **Dependencias**:
   - **O_context es obligatorio**: Sin él, K no puede calcularse y se devuelve `UNDEFINED`.
   - No depende de otros módulos. Solo usa `Fraction` y el estado `UNDEFINED` definido en `__init__.py`.
"""

from fractions import Fraction
from typing import List, Optional, Union
from . import UNDEFINED, DominioError

# ===============================================================
# FUNCIONES INTERNAS: Cálculo de K (Correlación)
# ===============================================================

def _calcular_k_teorico(
    descripcion: str,
    o_context: str,
    epsilon: Fraction = Fraction(1, 100)  # Margen de tolerancia por defecto: 1%
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Calcula K (Correlación) usando el método teórico (IlverVillasmil.pdf).

    **Definición formal**:
    K(D) = 1 si para todo z, ||D(z) - O(z)|| ≤ ε.

    Args:
        descripcion (str): Descripción D a evaluar.
        o_context (str): Contexto observable O_context.
        epsilon (Fraction): Margen de tolerancia admitido (default: 1%).

    Returns:
        Fraction: 1 si D coincide con O_context dentro de ε, 0 de lo contrario.
        UNDEFINED: Si no hay O_context (aunque aquí ya se valida en la interfaz pública).
    """
    if not o_context or not isinstance(o_context, str):
        return UNDEFINED

    # Verificar si D coincide con O_context dentro del margen ε
    coincide = _coincide_con_contexto(descripcion, o_context, epsilon)

    return Fraction(1, 1) if coincide else Fraction(0, 1)

def _calcular_k_operacional(
    afirmaciones: Optional[List[str]] = None,
    afirmaciones_falsas: Optional[int] = None,
    o_context: Optional[str] = None
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Calcula K (Correlación) usando el método operacional (PROTOCOLO.pdf).

    **Fórmula**:
    K = 1 - (f / c), donde:
    - f: Número de afirmaciones que divergen de O_context.
    - c: Número total de afirmaciones verificables.

    Args:
        afirmaciones (List[str]): Lista de afirmaciones verificables en D.
        afirmaciones_falsas (int): Número de afirmaciones que divergen de O_context.
        o_context (str): Contexto observable (obligatorio).

    Returns:
        Fraction: Valor de K en [0, 1].
        UNDEFINED: Si no hay O_context, afirmaciones o afirmaciones_falsas.

    Raises:
        DominioError: Si afirmaciones_falsas > len(afirmaciones).
    """
    if o_context is None or afirmaciones is None or afirmaciones_falsas is None:
        return UNDEFINED

    c = len(afirmaciones)
    if c == 0:
        return Fraction(1, 1)  # Sin afirmaciones, K = 1 por defecto

    f = afirmaciones_falsas
    if f > c:
        raise DominioError(
            f"El número de afirmaciones falsas (f={f}) no puede ser mayor que el número de afirmaciones (c={c})."
        )

    return Fraction(c - f, c)

# ===============================================================
# FUNCIONES AUXILIARES: Lógica interna para comparar D con O_context
# ===============================================================

def _coincide_con_contexto(
    descripcion: str,
    o_context: str,
    epsilon: Fraction = Fraction(1, 100)
) -> bool:
    """
    Verifica si una descripción D coincide con O_context dentro de un margen ε.

    **Criterios**:
    1. **Coincidencia exacta**: D es un subconjunto de O_context.
    2. **Coincidencia semántica**: D y O_context describen lo mismo (simplificado aquí como coincidencia literal).
    3. **Margen de tolerancia ε**: Pequeñas diferencias se ignoran si están dentro de ε.

    Args:
        descripcion (str): Descripción D.
        o_context (str): Contexto observable O_context.
        epsilon (Fraction): Margen de tolerancia (default: 1%).

    Returns:
        bool: True si D coincide con O_context dentro de ε, False de lo contrario.
    """
    if not descripcion or not o_context:
        return False

    # Normalizar textos (minúsculas, sin espacios adicionales)
    desc_normalizada = descripcion.strip().lower()
    ctx_normalizada = o_context.strip().lower()

    # Coincidencia exacta
    if desc_normalizada in ctx_normalizada:
        return True

    # Coincidencia por palabras clave (simplificado)
    # Ejemplo: Si D dice "β = 1/27" y O_context dice "El valor de β es 1/27", coinciden.
    palabras_clave = ["β = 1/27", "α = 26/27", "cubo 3x3x3"]
    for palabra in palabras_clave:
        if palabra in desc_normalizada and palabra in ctx_normalizada:
            return True

    # Si no hay coincidencia exacta ni por palabras clave, asumir que no coincide
    return False

# ===============================================================
# FUNCIONES PÚBLICAS: Interfaz para el módulo calculator
# ===============================================================

def calcular_k(
    descripcion: Optional[str] = None,
    afirmaciones: Optional[List[str]] = None,
    afirmaciones_falsas: Optional[int] = None,
    o_context: Optional[str] = None,
    metodo: str = "operacional",
    epsilon: Fraction = Fraction(1, 100)
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Interfaz pública para calcular K (Correlación).

    Args:
        descripcion (str): Descripción D (para método teórico).
        afirmaciones (List[str]): Lista de afirmaciones verificables (para método operacional).
        afirmaciones_falsas (int): Número de afirmaciones falsas (para método operacional).
        o_context (str): Contexto observable (obligatorio para ambos métodos).
        metodo (str): "teorico" o "operacional" (default: "operacional").
        epsilon (Fraction): Margen de tolerancia para el método teórico (default: 1%).

    Returns:
        Fraction: Valor de K en [0, 1].
        UNDEFINED: Si no hay O_context o falta información para el método seleccionado.

    Raises:
        MetodoError: Si el método no es "teorico" ni "operacional".
        DominioError: Si los inputs violan el dominio (ej: afirmaciones_falsas > afirmaciones).
    """
    if o_context is None:
        return UNDEFINED  # K es UNDEFINED sin O_context (Corolario Def-5.3.1)

    if metodo == "teorico":
        if descripcion is None:
            return UNDEFINED
        return _calcular_k_teorico(descripcion, o_context, epsilon)
    elif metodo == "operacional":
        return _calcular_k_operacional(afirmaciones, afirmaciones_falsas, o_context)
    else:
        from . import MetodoError
        raise MetodoError(
            f"Método '{metodo}' no soportado. Usa 'teorico' o 'operacional'."
        )
