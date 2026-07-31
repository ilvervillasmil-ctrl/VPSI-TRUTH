"""
VPSI-TRUTH --- modules/calculator/coherencia.py

---
### **DESCRIPCIÓN DEL SUB-MÓDULO**
Este archivo implementa **exclusivamente el cálculo de la variable C (Coherencia)**.
La coherencia mide la **ausencia de contradicciones internas** en una descripción D o en un conjunto de compromisos estructurales.

---
### **DEFINICIÓN FORMAL (IlverVillasmil.pdf)**
- **C(D) = 1** si no existe una proposición P tal que:
  - **D ⊢ P** (D implica P) **Y**
  - **D ⊢ ¬P** (D implica la negación de P).
- **C(D) = 0** si existe al menos una proposición P que cumpla lo anterior.
- **Rango**: C(D) ∈ {0, 1} (en el enfoque teórico puro).
- **Fuente**: Axioma TA1 (No-Contradicción de la Coherencia) en IlverVillasmil.pdf.

---
### **DEFINICIÓN OPERACIONAL (PROTOCOLO.pdf)**
- **C = 1 - (k / m)**, donde:
  - **k**: Número de pares de compromisos estructurales **mutuamente contradictorios** en D.
  - **m**: Número total de compromisos estructurales declarados en D.
- **Rango**: C ∈ [0, 1] (en el enfoque operacional).
- **Ejemplo**:
  - Si un sistema declara 3 compromisos: ["No modifico nada", "No tomo decisiones", "Soy determinista"],
    y hay 1 contradicción (ej: "No tomo decisiones" vs. "Elijo no responder"),
    entonces **C = 1 - (1/3) ≈ 0.6667**.
- **Fuente**: Sección 0.15 (Regla Operacional: Cómputo Determinista de Factores) en PROTOCOLO.pdf.

---
### **NOTAS IMPORTANTES**
1. **C = 1** no implica que D sea verdadera, solo que es **internamente consistente**.
2. **C = 0** implica que D contiene al menos una contradicción lógica interna.
3. **UNDEFINED**:
   - Si no se proporcionan `compromisos` o `contradicciones` para el método operacional, se devuelve `UNDEFINED`.
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
# FUNCIONES INTERNAS: Cálculo de C (Coherencia)
# ===============================================================

def _calcular_c_teorico(descripcion: str) -> Union[Fraction, type(UNDEFINED)]:
    """
    Calcula C (Coherencia) usando el método teórico (IlverVillasmil.pdf).

    **Definición formal**:
    C(D) = 1 si no existe P tal que (D ⊢ P) ∧ (D ⊢ ¬P).
    C(D) = 0 si existe al menos una P que cumpla lo anterior.

    Args:
        descripcion (str): Descripción D a evaluar.

    Returns:
        Fraction: 1 si no hay contradicciones lógicas, 0 si las hay.
        UNDEFINED: Si no se puede evaluar (ej: descripcion vacía).
    """
    if not descripcion or not isinstance(descripcion, str):
        return UNDEFINED

    # Verificar si hay contradicciones lógicas en la descripción
    tiene_contradicciones = _tiene_contradicciones_logicas(descripcion)

    return Fraction(0, 1) if tiene_contradicciones else Fraction(1, 1)

def _calcular_c_operacional(
    compromisos: Optional[List[str]] = None,
    contradicciones: Optional[int] = None
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Calcula C (Coherencia) usando el método operacional (PROTOCOLO.pdf).

    **Fórmula**:
    C = 1 - (k / m), donde:
    - k: Número de contradicciones (pares de compromisos contradictorios).
    - m: Número total de compromisos estructurales.

    Args:
        compromisos (List[str]): Lista de compromisos estructurales declarados.
        contradicciones (int): Número de pares de compromisos contradictorios.

    Returns:
        Fraction: Valor de C en [0, 1].
        UNDEFINED: Si no se proporcionan compromisos o contradicciones.

    Raises:
        DominioError: Si contradicciones > len(compromisos).
    """
    if compromisos is None or contradicciones is None:
        return UNDEFINED

    m = len(compromisos)
    if m == 0:
        return Fraction(1, 1)  # Sin compromisos, C = 1 por defecto

    k = contradicciones
    if k > m:
        raise DominioError(
            f"El número de contradicciones (k={k}) no puede ser mayor que el número de compromisos (m={m})."
        )

    return Fraction(m - k, m)

# ===============================================================
# FUNCIONES AUXILIARES: Lógica interna para detectar contradicciones
# ===============================================================

def _tiene_contradicciones_logicas(descripcion: str) -> bool:
    """
    Verifica si una descripción D contiene contradicciones lógicas.

    **Criterios de contradicción**:
    1. Presencia de pares como "P y no P", "P pero no P", etc.
    2. Uso de conectores lógicos que impliquen contradicción (ej: "y", "pero", "sin embargo").

    Args:
        descripcion (str): Descripción a evaluar.

    Returns:
        bool: True si hay contradicciones, False de lo contrario.
    """
    descripcion_lower = descripcion.lower()

    # Patrones de contradicción directa
    patrones_contradiccion = [
        " y no ",      # Ej: "A y no A"
        " pero no ",   # Ej: "A pero no A"
        " sin embargo ", # Ej: "A, sin embargo no A"
        " aunque ",     # Ej: "A, aunque no A"
        " mas no ",     # Ej: "A, mas no A"
        " sin embargo no ",
        " no obstante ",
        " por otro lado no ",
    ]

    # Verificar si algún patrón está presente
    for patron in patrones_contradiccion:
        if patron in descripcion_lower:
            return True

    # Verificar contradicciones explícitas (ej: "P = True y P = False")
    if " = true y " in descripcion_lower or " = false y " in descripcion_lower:
        return True

    # Verificar negaciones directas (ej: "es A y no es A")
    if " es " in descripcion_lower and " no es " in descripcion_lower:
        # Ejemplo: "Es coherente y no es coherente"
        return True

    return False

# ===============================================================
# FUNCIONES PÚBLICAS: Interfaz para el módulo calculator
# ===============================================================

def calcular_c(
    descripcion: Optional[str] = None,
    compromisos: Optional[List[str]] = None,
    contradicciones: Optional[int] = None,
    metodo: str = "operacional"
) -> Union[Fraction, type(UNDEFINED)]:
    """
    Interfaz pública para calcular C (Coherencia).

    Args:
        descripcion (str): Descripción D (para método teórico).
        compromisos (List[str]): Lista de compromisos estructurales (para método operacional).
        contradicciones (int): Número de contradicciones (para método operacional).
        metodo (str): "teorico" o "operacional" (default: "operacional").

    Returns:
        Fraction: Valor de C en [0, 1].
        UNDEFINED: Si no hay suficiente información.

    Raises:
        MetodoError: Si el método no es "teorico" ni "operacional".
        DominioError: Si los inputs violan el dominio (ej: contradicciones > compromisos).
    """
    if metodo == "teorico":
        return _calcular_c_teorico(descripcion)
    elif metodo == "operacional":
        return _calcular_c_operacional(compromisos, contradicciones)
    else:
        raise MetodoError(
            f"Método '{metodo}' no soportado. Usa 'teorico' o 'operacional'."
        )
