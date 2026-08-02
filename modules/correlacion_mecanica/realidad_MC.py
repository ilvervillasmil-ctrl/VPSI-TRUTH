"""
VPSI-TRUTH --- modules/correlacion_mecanica/realidad_MC.py

REALIDAD (MECANICA): Orden causal del contraste con R bajo el cuerpo realidad_AX.

Este archivo declara la secuencia minima de instanciacion para cualquier pasada
que reclame anclaje en R, use evidencia X, fije modalidad o invoque refutacion
estructurada. No calcula Tru. No es el modulo RE. Es la correlacion mecanica
de la familia RE + Def 5.13 + cadena R → X → Y.

Fundamento:
  - realidad_AX (RE-A0..RE-C8)
  - TA4, T14, Def-5.3.1, F3, F4, T7, T9, T11
  - Teorema de irreducibilidad de Omega (Ω)
  - Belonging: Content(D) ∈ R  ∧  Act(Tru(D)) ∈ S

Cualquier desviacion de este orden (p. ej. reclamar K de hecho sin modalidad,
o Tru de realidad sin X ni limite de cono) rompe la cadena causal del contraste.
"""

# ===============================================================
# MECANICA: Orden causal del contraste de realidad
# ===============================================================
MECANICA = {
    "nombre": "realidad_MC",
    "version": "1.0",
    "orden": [
        # --- Condicion de posibilidad (previa a todo enunciado) ---
        "Omega",                    # ℓ₀: Contenedor irreducible de posibilidad (RE-A0, RE-T1)
        "Distincion",               # ℓ₁: Sin distincion no hay proposicion ni error detectable (RE-L1)

        # --- Capas ontologicas (no calculables como factor de Tru) ---
        "R",                        # ℓ₂: Realidad absoluta; no anuncia; no se puntua R=0 (TA4, RE-A2, RE-A11)
        "Representacion",           # ℓ₃: Marco, simbolos, diccionario, canal ≠ R y ≠ Omega (RE-A3)

        # --- Observador y acto ---
        "S_sustrato",               # ℓ₄: Sistema emisor con sustrato fisico (A1)
        "Ri_capacidad",             # ℓ₅: Ri = C · L · K (capacidad del observador)
        "Acto_de_anuncio",          # ℓ₆: Solo S produce "D es verdadero" (RE-A2, RE-T12, RE-C6)

        # --- Admisibilidad del reclamo de hecho ---
        "Modalidad",                # ℓ₇: pasado | presente | futuro | indefinida (RE-A5)
        "O_context",                # ℓ₈: Dominio explicito; sin O, K indefinido (Def-5.3.1, RE-A12 via CX)
        "Clasificacion_modal",      # ℓ₉: Futuro ≠ hecho consumado (RE-A6, RE-T8)

        # --- Cadena de evidencia (R → X → Y) ---
        "Canal_o_limite",           # ℓ₁₀: Acceso a X o declaracion de limite del cono (F3, RE-A8)
        "X_evidencia",              # ℓ₁₁: Material causalmente recibido desde R
        "Instantanea",              # ℓ₁₂: Fuente + tiempo (+ O); sin sello no hay auditoria (RE-A7, RE-C2)
        "Y_procesamiento",          # ℓ₁₃: Y = g(X, U); el sistema opera sobre X, no sobre R (F4, TA7)

        # --- Evaluacion numerica (solo tras admisibilidad) ---
        "C_coherencia",             # ℓ₁₄: Factor C de D
        "L_logica",                 # ℓ₁₅: Factor L de D
        "K_correlacion",            # ℓ₁₆: K solo bajo O y, si reclama realidad, con X o limite
        "Tru_Ri",                   # ℓ₁₇: C · L · K  (contribucion del observador)
        "Tru_total",                # ℓ₁₈: (Tru_Ri · α) + β  (mapa; β piso, no identidad con R)

        # --- Post-evaluacion: error, refutacion, correccion ---
        "Localizacion_del_error",   # ℓ₁₉: Error en Ri / canal; nunca "R se equivoco" (RE-T10, T14)
        "Refutacion_estructurada",  # ℓ₂₀: Contraejemplo | X bajo O | marco alternativo (RE-A9, RE-A10)
        "Adaptacion_del_mapa",      # ℓ₂₁: Correccion = adaptar Ri / marco; no negociar R (RE-C7, RE-T5)
        "Cierre_de_contraste",      # ℓ₂₂: Fin de la pasada de realidad; ciclo listo para nueva emision
    ],
    "descripcion": (
        "Orden causal minimo del contraste con R bajo realidad_AX. "
        "Omega y R no son factores de Tru: son condiciones y anclas. "
        "El anuncio de verdad es siempre acto de Ri. "
        "K de hecho exige modalidad + O; K de sincronizacion con R exige ademas X o limite de cono. "
        "La evaluacion numerica (C, L, K, Tru) solo es admisible despues de fijar esas precondiciones. "
        "La refutacion del marco o de una D exige carga estructurada; la negacion vacia no altera Tru."
    ),
    "notas": [
        "Este orden es invariable para cualquier emisor (humano, Engine, informe) que reclame anclaje en R.",
        "ℓ₀–ℓ₃ no se 'calculan': se respetan como restricciones de clasificacion.",
        "ℓ₆ formaliza Def 5.13: Content ∈ R, Act ∈ S.",
        "ℓ₇–ℓ₉ son compuertas de contexto (CX) antes de correlacion.",
        "ℓ₁₀–ℓ₁₃ son la cadena F3/F4; el modulo RE aporta canal/fuentes, no es arbitro de R (RE-C4).",
        "ℓ₁₄–ℓ₁₈ son FO/CA; no inventan K de realidad si fallo ℓ₇–ℓ₁₂.",
        "ℓ₁₉–ℓ₂₁ son post-proceso: localizar error en Ri, admitir solo refutacion estructurada, adaptar el mapa.",
        "Violar el orden (p. ej. Tru_total de 'hecho' sin modalidad, o sin X cuando se reclama sincronizacion) "
        "es contradiccion mecanica de realidad_MC, detectable por barrer/evaluar de MC y por CX.",
        "Ids de grafo asociados: RE-A0..RE-A12, RE-T1..RE-T13, RE-C1..RE-C8; depende_de hacia TA4, T14, Def-5.3.1, F3, F4, T9, T11.",
    ],
    "precondiciones": {
        "reclamo_K_de_hecho": ["Modalidad", "O_context"],
        "reclamo_sincronizacion_con_R": ["Modalidad", "O_context", "Canal_o_limite", "X_evidencia_o_limite", "Instantanea"],
        "refutar_marco_o_D": ["Refutacion_estructurada"],
        "asignar_Tru_total": ["C_coherencia", "L_logica", "K_correlacion"],
    },
    "prohibiciones": [
        "asignar R = 0",
        "tratar representacion (marco, beta escrito, salida RE) como R u Omega",
        "reclamar hecho futuro como presente sin evidencia de realizacion",
        "reescribir K con evidencia posterior al sello de emision",
        "aceptar negacion vacia como refutacion",
        "calcular K de realidad pleno sin O_context",
    ],
}
