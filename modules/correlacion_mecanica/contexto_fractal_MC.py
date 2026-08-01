"""
VPSI-TRUTH --- modules/correlacion_mecanica/contexto_fractal_MC.py

CONTEXTO FRACTAL / ENTRADA NATURAL / MULTI-O (MC): sub-ruta de continuación.

No sustituye contexto_MC.py (Declaracion_O → ... → Correlacion_K).
Extiende el dominio con lo admitido en anexo CX v0.4:
  entrada natural, elevación, registro operativo, secuencia multi-O,
  O global de mapa, fijación antes de reclamar K (CX-T16).

Fundamento:
  - CX-A19…A27, CX-L8…L11, CX-T14…T17, CX-C14…C18
  - CX-T16: generación/fijación de O antes de correlación
  - CX-A23: cambio solo por frontera o declaración (no silencio)
  - CX-A25 / CX-L10: O global no colapsa micro

Relación con contexto_MC.py:
  Esta sub-ruta detalla cómo se construye Declaracion_O / Escala /
  Clasificacion_Evento cuando la casilla es natural o hay tramos.
  No invierte nodos de contexto_MC ni de causalidad_universal.
  K numérico sigue condicionado a la sub-ruta de contexto_MC.permite_k.

Cualquier archivo futuro del dominio CX se agrega igual: MECANICA.orden
sin pares invertidos respecto del corpus MC ya cargado.
"""

# ===============================================================
# MECANICA: Orden nativo de la sub-ruta fractal / natural / multi-O
# ===============================================================
MECANICA = {
    "nombre": "contexto_fractal_mecanico",
    "version": "1.0",
    "orden": [
        # --- Apertura de material (casilla / tramos) ---
        "CXF_Ciclo_Sesion",           # f₀: identidad de sesión o ciclo local
        "CXF_Entrada_Natural",        # f₁: prosa, lista, etiqueta, vacío (CX-A20, CX-D18)
        "CXF_Deteccion_Forma",        # f₂: vacio|prosa|lista|meta|cambio|multi_bloque
        "CXF_Elevacion_Enunciado",    # f₃: texto → enunciado_O o indefinido (CX-L8, CX-A21)

        # --- Registro y grano ---
        "CXF_Registro_Operativo",     # f₄: O_id + enunciado + estado (CX-A14, CX-T14)
        "CXF_Grano_Contextual",       # f₅: palabra|frase|turno|conversacion|meta (CX-D16, CX-A19)
        "CXF_Criterios_Bajo_O",       # f₆: lista 1..n → un O, no N O (CX-A22, CX-L9)
        "CXF_Modalidad_Emision",      # f₇: lengua/canal; no implica cambio de O (CX-A26)

        # --- Secuencia y multi-marco ---
        "CXF_Secuencia_Tramos",       # f₈: familia de micro-registros (CX-T15)
        "CXF_Frontera_Cambio_O",      # f₉: cambio solo declarado o por O_id distinto (CX-A23)
        "CXF_O_Global_Mapa",          # f₁₀: mapa opcional; no promedia K micro (CX-A25, CX-C18)

        # --- Generación y permiso local ---
        "CXF_Generacion_O",           # f₁₁: si la petición ordena crear marco (CX-A24, CX-D19)
        "CXF_Fijacion_O",             # f₁₂: O por escrito antes de reclamar K (CX-T16)
        "CXF_Permiso_K_Local",        # f₁₃: estable/cambio con registro; indefinido ⇒ ∅
    ],
    "descripcion": (
        "Sub-ruta mecánica del anexo CX v0.4 (fractalidad, entrada natural, multi-O). "
        "Continúa y detalla la construcción del armazón O cuando la entrada es de "
        "interfaz humana o conversación multi-tramo. "
        "No reemplaza contexto_MC: la correlación numérica K del ciclo sigue "
        "la sub-ruta Declaracion_O → Escala_O → Regla_Significado → Correlacion_K. "
        "Esta ruta garantiza fijación explícita (CX-T16) y prohíbe multi-O silencioso."
    ),
    "notas": [
        "Nodos con prefijo CXF_ para no colisionar nombres con contexto_MC ni Λ_E/Λ_V.",
        "Orden invariable dentro de esta sub-ruta (R1 local).",
        "CXF_Entrada_Natural vacía ⇒ elevación a indefinido; no se fuerza O inventado.",
        "CXF_Criterios_Bajo_O: una casilla con 1.2.3. es un O, no tres (CX-A22).",
        "CXF_Frontera_Cambio_O: sin declaración ni O_id distinto no hay evento=cambio.",
        "CXF_O_Global_Mapa mide el mapa; no agrega Tru de los micro (CX-C18).",
        "CXF_Fijacion_O es el ancla de CX-T16: sin ella CXF_Permiso_K_Local no aplica.",
        "Compatible con contexto_MC: completar esta sub-ruta alimenta Declaracion_O "
        "y Clasificacion_Evento; no autoriza saltar a Correlacion_K por sí sola.",
        "Archivos futuros del dominio CX: mismo contrato MECANICA.orden sin invertir pares.",
    ],
    "transiciones_prohibidas": [
        {
            "desde": "CXF_Ciclo_Sesion",
            "hacia": "CXF_Permiso_K_Local",
            "motivo": "CX-T16 / Def-5.3.1: K local sin entrada, elevación, registro y fijación.",
        },
        {
            "desde": "CXF_Entrada_Natural",
            "hacia": "CXF_Fijacion_O",
            "motivo": "Faltan forma, elevación y registro operativo (CX-A14, CX-L8).",
        },
        {
            "desde": "CXF_Deteccion_Forma=vacio",
            "hacia": "CXF_Permiso_K_Local",
            "motivo": "CX-A21: vacío ⇒ indefinido; K no reclamable.",
        },
        {
            "desde": "CXF_Secuencia_Tramos",
            "hacia": "CXF_O_Global_Mapa_como_unico_K",
            "motivo": "CX-A25 / CX-T15: el global no sustituye ni promedia los micro.",
        },
        {
            "desde": "cambio_silencioso",
            "hacia": "CXF_Frontera_Cambio_O",
            "motivo": "CX-A23: cambio solo por declaración o frontera explícita.",
        },
        {
            "desde": "CXF_Generacion_O",
            "hacia": "CXF_Permiso_K_Local",
            "motivo": "CX-A24 / CX-T16: generar sin fijar por escrito no habilita K.",
        },
    ],
    "clasificacion_forma": {
        "vacio": "Sin texto usable → indefinido (CX-A21).",
        "prosa": "Un enunciado_O por elevación (CX-A20, CX-L8).",
        "lista_criterios": "Un O con criterios (CX-A22, CX-L9).",
        "meta_indefinido": "Declaración meta; no rellena K del agujero (CX-C15).",
        "cambio_declarado": "Cierre de O previo + apertura (CX-A23).",
        "multi_bloque": "Por defecto criterios de un O; no multi-O inventado.",
    },
    "granos_admitidos": [
        "grafema_forma",
        "palabra",
        "frase",
        "turno",
        "conversacion",
        "sesion",
        "meta",
    ],
    "anclas_cx": [
        "CX-A19", "CX-A20", "CX-A21", "CX-A22", "CX-A23", "CX-A24",
        "CX-A25", "CX-A26", "CX-A27",
        "CX-L8", "CX-L9", "CX-L10", "CX-L11",
        "CX-T14", "CX-T15", "CX-T16", "CX-T17",
        "CX-C14", "CX-C15", "CX-C16", "CX-C17", "CX-C18",
        "CX-A14", "Def-5.3.1",
    ],
}


def orden() -> list:
    return list(MECANICA["orden"])


def indice(paso: str) -> int:
    return MECANICA["orden"].index(paso)


def precondiciones(paso: str) -> list:
    i = indice(paso)
    return list(MECANICA["orden"][:i])


def permite_k_local(instanciados: set) -> bool:
    """
    Permiso local de esta sub-ruta (no sustituye contexto_MC.permite_k).
    Exige fijación + registro en la cadena fractal.
    """
    requeridos = {
        "CXF_Ciclo_Sesion",
        "CXF_Entrada_Natural",
        "CXF_Elevacion_Enunciado",
        "CXF_Registro_Operativo",
        "CXF_Fijacion_O",
    }
    return requeridos.issubset(set(instanciados))


def ruta_minima_fijacion() -> list:
    """Hasta fijar O (CX-T16), sin opcionales de secuencia/global."""
    return [
        "CXF_Ciclo_Sesion",
        "CXF_Entrada_Natural",
        "CXF_Deteccion_Forma",
        "CXF_Elevacion_Enunciado",
        "CXF_Registro_Operativo",
        "CXF_Fijacion_O",
    ]


__all__ = [
    "MECANICA",
    "orden",
    "indice",
    "precondiciones",
    "permite_k_local",
    "ruta_minima_fijacion",
]
