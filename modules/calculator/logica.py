"""
VPSI-TRUTH --- modules/calculator/logica.py

---
### **DESCRIPCIÓN DEL SUB-MÓDULO**
Este archivo implementa **exclusivamente el cálculo de la variable L (Lógica)**.
La lógica mide la **estabilidad y determinismo del proceso** que genera una descripción D o un conjunto de posturas.

---
### **DEFINICIÓN FORMAL (IlverVillasmil.pdf)**
- **L(D) = 1** si existe un espacio **Z** y una transformación **T** tal que:
  - Para todo **z ∈ Z**, **T(z)** es **único e invariante**.
- **L(D) = 0** si el proceso no es determinista o no es invariante.
- **Rango**: L(D) ∈ {0, 1} (en el enfoque teórico puro).
- **Interpretación**:
  - **L = 1**: El proceso es **determinista e invariante** (mismo input → mismo output).
  - **L = 0**: El proceso **no es determinista** (mismo input → outputs diferentes) o **no es invariante** (el output cambia sin cambio en el input).
- **Fuente**: Axioma TA2 (Objetividad de la Lógica) en IlverVillasmil.pdf.

---
### **DEFINICIÓN OPERACIONAL (PROTOCOLO.pdf)**
- **L = 1 - (r / p)**, donde:
  - **r**: Número de **posturas que revierten una posición previamente consolidada** por el sistema.
  - **p**: Número total de **posturas** asumidas por el sistema.
- **Rango**: L ∈ [0, 1] (en el enfoque operacional).
- **Ejemplo**:
  - Si un sistema asume 3 posturas: ["Sé la respuesta", "No sé", "Sé la respuesta"],
    y hay 1 reversión (de "No sé" a "Sé la respuesta"),
    entonces **L = 1 - (1/3) ≈ 0.6667**.
- **Fuente**: Sección 0.15 (Regla Operacional: Cómputo Determinista de Factores) en PROTOCOLO.pdf.

---
### **NOTAS IMPORTANTES**
1. **L = 1** no implica que D sea verdadera, solo que el **proceso es determinista e invariante**.
2. **L = 0** implica que el proceso **no es determinista** o **no es invariante**.
3. **UNDEFINED**:
   - Si no se proporcionan `posturas` o `reversiones` para el método operacional, se devuelve `UNDEFINED`.
   - Si no se proporciona `descripcion` para el método teórico, se devuelve `UNDEFINED`.
4. **Precisión**:
   - Todos los cálculos usan `Fraction` para evitar errores de punto flotante.
5. **Dependencias**:
   - No depende de otros módulos. Solo usa `Fraction` y el estado `UNDEFINED` definido en `__init__.py`.
"""

from fractions import Fraction
from typing import List, Optional, Union
from . import UNDEFINED, DominioError

# ===============================================================
# FUNCIONES INTERNAS: Cálculo de L (Lógica)
# ===============================================================

def _calcular_l_teorico(descripcion: str) -> Union[Fraction, type(UNDEFINED)]:
    """
    Calcula L (Lógica) usando el método teórico (IlverVillasmil.pdf).

    **Definición formal**:
    L(D) = 1 si existe un espacio Z y una transformación T tal que:
    ∀z ∈ Z, T(z) es único e invariante.

    Args:
        descripcion (str): Descripción D a evaluar.

    Returns:
        Fraction: 1 si el proceso es determinista e invariante, 0 de lo contrario.
        UNDEFINED: Si no se puede evaluar (ej: descripcion vacía).
    """
    if not descripcion or not isinstance(descripcion, str):
        return UNDEFINED

    # Verificar si el proceso es determinista e invariante
    es_determinista = _es_proceso_determinista(descripcion)
    es_invariante = _es_proceso_invariante(descripcion)

    return Fraction(1, 1) if (es_determinista and es_invariante) else Fraction(0, 1)

def _calcular_l_operacional(
    posturas: Optional[List[str]] = None,
    reversiones: Optional[int] = None
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Calcula L (Lógica) usando el método operacional (PROTOCOLO.pdf).

    **Fórmula**:
    L = 1 - (r / p), donde:
    - r: Número de reversiones de postura.
    - p: Número total de posturas asumidas.

    Args:
        posturas (List[str]): Lista de posturas asumidas por el sistema.
        reversiones (int): Número de posturas que revierten una posición previa.

    Returns:
        Fraction: Valor de L en [0, 1].
        UNDEFINED: Si no se proporcionan posturas o reversiones.

    Raises:
        DominioError: Si reversiones > len(posturas).
    """
    if posturas is None or reversiones is None:
        return UNDEFINED

    p = len(posturas)
    if p == 0:
        return Fraction(1, 1)  # Sin posturas, L = 1 por defecto

    r = reversiones
    if r > p:
        raise DominioError(
            f"El número de reversiones (r={r}) no puede ser mayor que el número de posturas (p={p})."
        )

    return Fraction(p - r, p)

# ===============================================================
# FUNCIONES AUXILIARES: Lógica interna para validar determinismo e invariancia
# ===============================================================

def _es_proceso_determinista(descripcion: str) -> bool:
    """
    Verifica si un proceso es determinista.
    **Criterio**: El mismo input siempre produce el mismo output.

    Args:
        descripcion (str): Descripción del proceso o sistema.

    Returns:
        bool: True si el proceso es determinista, False de lo contrario.
    """
    # En la práctica, esto se validaría con pruebas o análisis del código.
    # Aquí asumimos que es determinista si no hay indicios de aleatoriedad.
    descripcion_lower = descripcion.lower()

    # Patrones que indican no determinismo
    patrones_no_deterministas = [
        "aleatorio", "random", "azar", "probabilidad",
        "no determinista", "estocástico", "incierto",
        "depende de", "varía con", "puede cambiar",
    ]

    for patron in patrones_no_deterministas:
        if patron in descripcion_lower:
            return False

    # Si no hay patrones de no determinismo, asumimos que es determinista
    return True

def _es_proceso_invariante(descripcion: str) -> bool:
    """
    Verifica si un proceso es invariante.
    **Criterio**: El output no cambia si el input no cambia.

    Args:
        descripcion (str): Descripción del proceso o sistema.

    Returns:
        bool: True si el proceso es invariante, False de lo contrario.
    """
    # En la práctica, esto se validaría con pruebas o análisis del código.
    # Aquí asumimos que es invariante si no hay indicios de que el output cambie sin cambio en el input.
    descripcion_lower = descripcion.lower()

    # Patrones que indican no invariancia
    patrones_no_invariantes = [
        "cambia con el tiempo", "varía sin razón", "no es estable",
        "depende de estado interno", "no es reproducible",
    ]

    for patron in patrones_no_invariantes:
        if patron in descripcion_lower:
            return False

    # Si no hay patrones de no invariancia, asumimos que es invariante
    return True

# ===============================================================
# FUNCIONES PÚBLICAS: Interfaz para el módulo calculator
# ===============================================================

def calcular_l(
    descripcion: Optional[str] = None,
    posturas: Optional[List[str]] = None,
    reversiones: Optional[int] = None,
    metodo: str = "operacional"
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Interfaz pública para calcular L (Lógica).

    Args:
        descripcion (str): Descripción D (para método teórico).
        posturas (List[str]): Lista de posturas asumidas (para método operacional).
        reversiones (int): Número de reversiones de postura (para método operacional).
        metodo (str): "teorico" o "operacional" (default: "operacional").

    Returns:
        Fraction: Valor de L en [0, 1].
        UNDEFINED: Si no hay suficiente información.

    Raises:
        MetodoError: Si el método no es "teorico" ni "operacional".
        DominioError: Si los inputs violan el dominio (ej: reversiones > posturas).
    """
    if metodo == "teorico":
        return _calcular_l_teorico(descripcion)
    elif metodo == "operacional":
        return _calcular_l_operacional(posturas, reversiones)
    else:
        from . import MetodoError
        raise MetodoError(
            f"Método '{metodo}' no soportado. Usa 'teorico' o 'operacional'."
        )
