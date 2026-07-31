"""
VPSI-TRUTH --- modules/calculator/__init__.py

---
### **DESCRIPCIÓN DEL MÓDULO**
Este módulo es el **encargado exclusivo de calcular las variables fundamentales de verdad**:
- **C (Coherencia)**: Ausencia de contradicciones internas en una descripción D.
- **L (Lógica)**: Determinismo e invariancia del proceso de generación de D.
- **K (Correlación)**: Correspondencia entre D y el dominio observable O_context.

---
### **CONTRATO**
1. **No calcula Tru_Ri ni Tru_total**: Esas fórmulas son responsabilidad del módulo `formulas` (rol FO).
2. **Solo calcula C, L, K**: Usando métodos teóricos (IlverVillasmil.pdf) u operacionales (PROTOCOLO.pdf).
3. **Dependencias**:
   - **CT**: Para acceder a las constantes ALPHA y BETA (aunque no las use directamente).
   - **MC**: Para validar que el orden causal de los cálculos sea coherente (vía `correlacion_mecanica.barrer()`).
4. **Inputs requeridos**:
   - Para **C**: `compromisos` (lista de compromisos estructurales) y `contradicciones` (número de contradicciones).
   - Para **L**: `posturas` (lista de posturas asumidas) y `reversiones` (número de reversiones).
   - Para **K**: `afirmaciones` (lista de afirmaciones verificables), `afirmaciones_falsas` (número de afirmaciones falsas), y **`O_context` (obligatorio)**.
5. **Outputs**:
   - `C`, `L`, `K` como `Fraction` en el rango [0, 1] o `UNDEFINED` (si falta información).
6. **Manejo de errores**:
   - `DominioError`: Si un valor está fuera del dominio [0, 1].
   - `ContextoError`: Si falta O_context para calcular K.
   - `UNDEFINED`: Si no hay suficiente información para calcular una variable.

---
### **ACOPLAMIENTO CON OTROS MÓDULOS**
- **engine**: Orquesta el cálculo de C, L, K y valida el orden causal antes de delegar en este módulo.
- **formulas**: Recibe C, L, K de este módulo para calcular Tru_Ri y Tru_total.
- **correlacion_mecanica**: Valida que el orden causal de los cálculos sea coherente antes de que este módulo actúe.
- **centinela**: Puede usar los resultados de C, L, K para detectar fallos o desviaciones.
- **diagnostico**: Usa C, L, K y Tru_total para generar el Omega Report (⟨Ω⟩).

---
### **NOTAS IMPORTANTES**
- Este módulo **no valida el orden causal**: Eso es responsabilidad de `correlacion_mecanica`.
- Este módulo **no calcula fórmulas canónicas**: Eso es responsabilidad de `formulas`.
- Este módulo **no audita fallos**: Eso es responsabilidad de `centinela`.
- Este módulo **no genera informes**: Eso es responsabilidad de `diagnostico`.
- **Todo cálculo se hace con `Fraction`**: Para garantizar precisión matemática.
- **UNDEFINED no es 0**: Si falta información (ej: O_context para K), se devuelve UNDEFINED, no 0.
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, List, Optional, Union, Any

# ===============================================================
# CONTENEDOR: Metadatos del módulo
# ===============================================================
CONTENEDOR = {
    "nombre": "calculator",
    "rol": "CA",  # Rol: Cálculo de variables de verdad (C, L, K)
    "version": "1.0",
    "requiere": ["CT", "MC"],  # Depende de constantes (CT) y correlación mecánica (MC)
    "descripcion": (
        "Calcula las variables fundamentales de verdad (C, L, K) usando métodos "
        "teóricos (IlverVillasmil.pdf) u operacionales (PROTOCOLO.pdf). "
        "No calcula Tru_Ri ni Tru_total (eso es responsabilidad de 'formulas')."
    ),
}

# ===============================================================
# ESTADO UNDEFINED: Para valores sin evidencia
# ===============================================================
class _Undefined:
    """
    Estado para valores sin evidencia.
    - No es 0, es UNDEFINED (ej: K sin O_context).
    - Propaga limpiamente sin intervencionismo.
    """
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
# EXCEPCIONES: Errores específicos del módulo
# ===============================================================
class DominioError(Exception):
    """Error cuando un valor está fuera del dominio permitido [0, 1]."""
    pass

class ContextoError(Exception):
    """Error cuando falta O_context para calcular K."""
    pass

class MetodoError(Exception):
    """Error cuando se usa un método no soportado (solo 'teorico' o 'operacional')."""
    pass

# ===============================================================
# INTERFACES PÚBLICAS: Funciones que delegarán en los sub-módulos
# ===============================================================
def calcular_c(*args, **kwargs) -> Union[Fraction, type(UNDEFINED)]:
    """
    Interfaz pública para calcular C (Coherencia).
    Delegará en el sub-módulo coherencia.py.
    """
    from .coherencia import _calcular_c
    return _calcular_c(*args, **kwargs)

def calcular_l(*args, **kwargs) -> Union[Fraction, type(UNDEFINED)]:
    """
    Interfaz pública para calcular L (Lógica).
    Delegará en el sub-módulo logica.py.
    """
    from .logica import _calcular_l
    return _calcular_l(*args, **kwargs)

def calcular_k(*args, **kwargs) -> Union[Fraction, type(UNDEFINED)]:
    """
    Interfaz pública para calcular K (Correlación).
    Delegará en el sub-módulo correlacion.py.
    Requiere O_context (de lo contrario, devuelve UNDEFINED).
    """
    from .correlacion import _calcular_k
    return _calcular_k(*args, **kwargs)

# ===============================================================
# EXPORTACIÓN: Lo que el módulo expone al exterior
# ===============================================================
__all__ = [
    # Metadatos
    "CONTENEDOR",
    # Estado y utilidades
    "UNDEFINED",
    "es_undefined",
    # Excepciones
    "DominioError",
    "ContextoError",
    "MetodoError",
    # Interfaces públicas
    "calcular_c",
    "calcular_l",
    "calcular_k",
]
