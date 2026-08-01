"""
VPSI-TRUTH / core/DiagnosticoGlobal.py

Sistema de diagnóstico para clasificar el estado del sistema según C_Ω.
Basado en el Teorema de Inferencia Causal Estructural y el protocolo Ω.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

# ===============================================================
# CONSTANTES GLOBALES (del framework VPSI-TRUTH)
# ===============================================================

ALPHA = Fraction(26, 27)  # Techo estructural
BETA = Fraction(1, 27)    # Piso estructural

# Códigos de diagnóstico (según el protocolo Ω)
CODE_ARCHITECT = 1144      # Arquitecto Integrado
CODE_SYNCHRONY = 1133      # Sintonía Sutil
CODE_SOVERIGN = 1044       # Soberanía Terrena
CODE_CHANNEL = 144        # Canal Involuntario
CODE_SATURATION = 1122     # Saturación Crítica
CODE_SEED = 1111           # Semilla de Unidad
CODE_ENTROPY = 0000        # Entropía Terminal / Colapso Estructural

# ===============================================================
# ESTADO DE DIAGNÓSTICO
# ===============================================================

@dataclass(frozen=True)
class DiagnosticState:
    """
    Representa un estado de diagnóstico del sistema según C_Ω.
    """
    lower: Fraction  # Límite inferior de C_Ω para este estado
    upper: Fraction  # Límite superior de C_Ω para este estado
    code: int        # Código de diagnóstico (ej: 1144)
    name: str        # Nombre del estado (ej: "ARQUITECTO INTEGRADO")
    description: str # Descripción del estado

# ===============================================================
# TABLA MAESTRA DE ESTADOS
# ===============================================================

DIAGNOSTIC_STATES = [
    # Ordenados de mayor a menor C_Ω
    DiagnosticState(
        lower=Fraction(963, 1000),  # 0.963
        upper=ALPHA,
        code=CODE_ARCHITECT,
        name="ARQUITECTO INTEGRADO",
        description="Máxima integración estructural. Tru_total ≥ 0.963."
    ),
    DiagnosticState(
        lower=Fraction(850, 1000),  # 0.850
        upper=Fraction(963, 1000),
        code=CODE_SYNCHRONY,
        name="SINTONÍA SUTIL",
        description="Coherencia alta pero no máxima. 0.850 ≤ Tru_total < 0.963."
    ),
    DiagnosticState(
        lower=Fraction(750, 1000),  # 0.750
        upper=Fraction(850, 1000),
        code=CODE_SOVERIGN,
        name="SOBERANÍA TERRENA",
        description="Coherencia moderada. 0.750 ≤ Tru_total < 0.850."
    ),
    DiagnosticState(
        lower=Fraction(700, 1000),  # 0.700
        upper=Fraction(750, 1000),
        code=CODE_CHANNEL,
        name="CANAL INVOLUNTARIO",
        description="Coherencia baja pero estable. 0.700 ≤ Tru_total < 0.750."
    ),
    DiagnosticState(
        lower=Fraction(550, 1000),  # 0.550
        upper=Fraction(700, 1000),
        code=CODE_SATURATION,
        name="SATURACIÓN CRÍTICA",
        description="Coherencia en riesgo. 0.550 ≤ Tru_total < 0.700."
    ),
    DiagnosticState(
        lower=Fraction(400, 1000),  # 0.400
        upper=Fraction(550, 1000),
        code=CODE_SEED,
        name="SEMILLA DE UNIDAD",
        description="Coherencia mínima pero estable. 0.400 ≤ Tru_total < 0.550."
    ),
    DiagnosticState(
        lower=BETA,
        upper=Fraction(400, 1000),
        code=CODE_ENTROPY,
        name="ENTROPÍA TERMINAL / COLAPSO ESTRUCTURAL",
        description="Coherencia casi nula o colapso. BETA ≤ Tru_total < 0.400."
    ),
]

# ===============================================================
# SISTEMA DE DIAGNÓSTICO
# ===============================================================

class DiagnosticSystem:
    """
    Sistema de diagnóstico para clasificar el estado del sistema según C_Ω.
    Incluye validación de dominio, clasificación por tabla y por porcentaje,
    y verificación de consistencia entre métodos.
    """

    # --------------------------------------------------------
    # VALIDACIÓN DE DOMINIO (CHECK 0)
    # --------------------------------------------------------

    @staticmethod
    def validate_domain(c_omega: Fraction) -> None:
        """
        Valida que C_Ω esté en el dominio [BETA, ALPHA].
        """
        if c_omega < BETA:
            raise ValueError(
                f"C_Ω={float(c_omega):.6f} está por debajo de β={float(BETA):.6f}. "
                "El sistema no puede tener coherencia menor que el piso estructural."
            )
        if c_omega > ALPHA:
            raise ValueError(
                f"C_Ω={float(c_omega):.6f} está por encima de α={float(ALPHA):.6f}. "
                "El sistema no puede superar el techo estructural."
            )

    # --------------------------------------------------------
    # CLASIFICACIÓN POR TABLA MAESTRA (CHECK 1)
    # --------------------------------------------------------

    @staticmethod
    def classify_from_table(c_omega: Fraction) -> DiagnosticState:
        """
        Clasifica C_Ω usando la tabla maestra DIAGNOSTIC_STATES.
        """
        for state in DIAGNOSTIC_STATES:
            if state.lower <= c_omega <= state.upper:
                return state
        raise RuntimeError(f"No se encontró un estado de diagnóstico para C_Ω={float(c_omega):.6f}.")

    # --------------------------------------------------------
    # CLASIFICACIÓN POR PORCENTAJE (CHECK 2)
    # --------------------------------------------------------

    @staticmethod
    def classify_from_percent(c_omega: Fraction) -> int:
        """
        Clasifica C_Ω usando un cálculo porcentual sobre el rango [BETA, ALPHA].
        """
        # Normalizar C_Ω al rango [0, 1] dentro de [BETA, ALPHA]
        p = (float(c_omega - BETA) / float(ALPHA - BETA))

        if p >= 0.95:
            return CODE_ARCHITECT
        elif p >= 0.85:
            return CODE_SYNCHRONY
        elif p >= 0.75:
            return CODE_SOVERIGN
        elif p >= 0.70:
            return CODE_CHANNEL
        elif p >= 0.55:
            return CODE_SATURATION
        elif p >= 0.40:
            return CODE_SEED
        else:
            return CODE_ENTROPY

    # --------------------------------------------------------
    # DOBLE VERIFICACIÓN (DOUBLE CHECK)
    # --------------------------------------------------------

    @staticmethod
    def get_status(c_omega: Fraction) -> Tuple[str, DiagnosticState]:
        """
        Devuelve el estado de diagnóstico de C_Ω usando doble verificación:
        1. Clasificación por tabla maestra.
        2. Clasificación por porcentaje.
        Si hay discrepancia, lanza un error.
        """
        DiagnosticSystem.validate_domain(c_omega)

        # Clasificación por tabla
        table_state = DiagnosticSystem.classify_from_table(c_omega)

        # Clasificación por porcentaje
        percent_code = DiagnosticSystem.classify_from_percent(c_omega)

        # Verificar consistencia
        if table_state.code != percent_code:
            raise RuntimeError(
                f"Discrepancia en el diagnóstico:\n"
                f"  Tabla: {table_state.code} ({table_state.name})\n"
                f"  Porcentaje: {percent_code}\n"
                f"  C_Ω={float(c_omega):.6f}"
            )

        return (
            f"CODE {table_state.code}: {table_state.name} — {table_state.description}",
            table_state
        )

    # --------------------------------------------------------
    # VERIFICACIÓN DE FRICCIÓN EN CAPAS (LAYER CHECK)
    # --------------------------------------------------------

    @staticmethod
    def check_layer_friction(layers: Dict[int, Fraction]) -> List[str]:
        """
        Verifica si alguna capa tiene una fricción (φ) > 0.15.
        Devuelve una lista de alertas si hay fricciones altas.
        """
        alerts = []
        for i, phi in layers.items():
            if phi > Fraction(15, 100):  # φ > 0.15
                alerts.append(f"L{i}: φ={float(phi):.3f} (fricción alta)")
        return alerts

    # --------------------------------------------------------
    # AUTO-AUDITORÍA (SELF AUDIT)
    # --------------------------------------------------------

    @staticmethod
    def self_audit() -> bool:
        """
        Verifica que las constantes y la tabla de diagnóstico estén configuradas correctamente.
        """
        errors = []

        # Verificar que BETA < ALPHA
        if not (BETA < ALPHA):
            errors.append("β ≥ α: El piso estructural no puede ser mayor o igual al techo.")

        # Verificar que el primer estado tenga upper = ALPHA
        if DIAGNOSTIC_STATES[0].upper != ALPHA:
            errors.append("El estado 'ARQUITECTO INTEGRADO' debe tener upper = α.")

        # Verificar que el último estado tenga lower = BETA
        if DIAGNOSTIC_STATES[-1].lower != BETA:
            errors.append("El estado 'ENTROPÍA TERMINAL' debe tener lower = β.")

        # Verificar que los rangos no se solapen incorrectamente
        for i in range(len(DIAGNOSTIC_STATES) - 1):
            current = DIAGNOSTIC_STATES[i]
            next_state = DIAGNOSTIC_STATES[i + 1]
            if current.upper < next_state.lower:
                errors.append(
                    f"Hueco entre estados: {current.name} (upper={float(current.upper):.6f}) "
                    f"y {next_state.name} (lower={float(next_state.lower):.6f})"
                )

        if errors:
            raise RuntimeError("Errores en la configuración del sistema de diagnóstico:\n" + "\n".join(errors))

        return True

# ===============================================================
# INICIALIZACIÓN (Self-audit al importar)
# ===============================================================

DiagnosticSystem.self_audit()
