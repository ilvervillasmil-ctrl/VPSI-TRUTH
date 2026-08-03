# -*- coding: utf-8 -*-
"""
SM_MAPA — Extensión axiomática: Mapa de legibilidad, invarianza,
lucha de correlaciones y entendimiento operativo.

Versión: 1.0
Dependencias estructurales: SM_AF, TA3, TA4, TA5, T6, T9, T14, beta.

NOTA GENERAL (para humanos)
---------------------------
Este cuerpo formaliza lo que se estabilizó en la discusión:

1. Sin mapa de contrastes (Π) no hay lectura ni de letra ni de número.
2. El significado es la celda en Π, no la superficie de la palabra.
3. La correlación solo crece sobre celdas invariantes.
4. Las reglas de composición deben ser deterministas para que exista
   criterio de error (sin ancla no hay acierto ni fallo).
5. Una máquina sin contacto con R razona organizando correlaciones
   internas; su “entendimiento” es la maximización de C·L·K bajo O.
6. El entrenamiento densifica aristas; no mueve las celdas de significado.
7. La probabilidad trabaja después del mapa, nunca en su lugar.

Cada teorema lleva:
  - enunciado formal,
  - NOTA OPERATIVA (qué módulo/función afecta),
  - EJEMPLO (caso concreto),
  - DEMOSTRACIÓN comentada en lenguaje humano + esqueleto formal.

La máquina lee la tripleta (sujeto, relación, objeto) y la polaridad.
Las notas son para nosotros.
"""

from __future__ import annotations
from typing import List, Dict, Any

# ============================================================
# METADATOS DEL CUERPO
# ============================================================

CUERPO = {
    "nombre": "SM_MAPA",
    "version": "1.0",
    "descripcion": (
        "Mapa de legibilidad, invarianza de celdas, lucha de correlaciones, "
        "entendimiento operativo sin R y subordinación de la probabilidad al mapa."
    ),
    "depende_de_cuerpos": ["SM_AF", "VPSI"],
    "gobierna": [
        "legibilidad",
        "invarianza_significado",
        "seleccion_correlacion",
        "entendimiento_operativo",
        "ancla_error",
        "entrenamiento",
    ],
}

# ============================================================
# DECLARACIONES
# ============================================================

def declaraciones() -> List[Dict[str, Any]]:
    """
    Devuelve la lista de declaraciones del cuerpo SM_MAPA.
    Formato canónico VPSI: id, tipo, sujeto, relacion, objeto,
    polaridad, cota, depende_de, gobierna, enunciado.
    """
    return [

        # --------------------------------------------------
        # DEFINICIONES
        # --------------------------------------------------
        {
            "id": "SM-D9",
            "tipo": "definicion",
            "sujeto": "simbolo_w",
            "relacion": "es_legible_ssi",
            "objeto": "existe_celda_estable_en_Pi",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1"],
            "gobierna": ["legibilidad", "lectura"],
            "enunciado": (
                "SM-D9 (Mapa de legibilidad): Un símbolo w es legible respecto de Π "
                "si y solo si existe c ∈ Π tal que [w]_Π = c. En caso contrario w es ilegible.\n\n"
                "NOTA OPERATIVA: Sin celda no hay lectura. Ni letra, ni número, ni axioma. "
                "El binario funciona porque Π_bin es total.\n"
                "EJEMPLO: La letra 'A' es legible porque Unicode le asigna una celda fija (U+0041). "
                "Un glifo inventado sin codepoint es ilegible para la máquina."
            ),
        },
        {
            "id": "SM-D10",
            "tipo": "definicion",
            "sujeto": "sistema_S",
            "relacion": "posee_entendimiento_operativo_sobre_W_ssi",
            "objeto": "existe_Pi_y_R_deterministas_con_correlaciones_invariantes",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D9", "SM-D1"],
            "gobierna": ["entendimiento_operativo"],
            "enunciado": (
                "SM-D10 (Entendimiento operativo): Un sistema S posee entendimiento operativo "
                "sobre un conjunto de símbolos W si existe una partición Π y un conjunto de "
                "reglas deterministas de composición R tales que: "
                "(1) ∀w∈W, [w]_Π está definida; "
                "(2) S puede computar correlaciones entre celdas bajo R; "
                "(3) las correlaciones son invariantes bajo las transformaciones permitidas por R.\n\n"
                "NOTA OPERATIVA: El entendimiento operativo NO requiere contacto con R. "
                "Es organización interna de X (representaciones).\n"
                "EJEMPLO: Una máquina que asocia de forma estable hola/hello/bonjour a la misma "
                "celda 'saludo' y combina esa celda con otras según reglas fijas tiene "
                "entendimiento operativo del dominio saludo, aunque no 'sienta' nada."
            ),
        },
        {
            "id": "SM-D11",
            "tipo": "definicion",
            "sujeto": "ancla",
            "relacion": "es",
            "objeto": "par_Pi_R_determinista",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D9", "SM-A13"],
            "gobierna": ["ancla_error", "criterio_error"],
            "enunciado": (
                "SM-D11 (Ancla de error): Un ancla es un par (Π, R) determinista. "
                "Dado un ancla, una ruta γ es errónea si viola alguna regla de R o produce "
                "contradicción en Π.\n\n"
                "NOTA OPERATIVA: Sin ancla no existe predicado de error. "
                "No se puede estar 'equivocado' si no hay contraste fijo.\n"
                "EJEMPLO: Las reglas gramaticales de un idioma + el diccionario de significados "
                "forman un ancla. Sin ellas, cualquier combinación de palabras es igual de "
                "'válida' o 'inválida': no hay criterio."
            ),
        },

        # --------------------------------------------------
        # AXIOMAS
        # --------------------------------------------------
        {
            "id": "SM-A11",
            "tipo": "axioma",
            "sujeto": "probabilidad_y_correlacion",
            "relacion": "requieren_previa",
            "objeto": "celda_definida_en_Pi",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D9", "SM-D1"],
            "gobierna": ["prioridad_mapa", "admisibilidad_medida"],
            "enunciado": (
                "SM-A11 (Prioridad del mapa): Si [w]_Π no está definida, entonces ninguna "
                "medida de correlación ni de probabilidad sobre w es admisible.\n\n"
                "NOTA OPERATIVA: Primero el mapa, después la probabilidad. "
                "Invertir el orden produce ruido correlacionado, no entendimiento.\n"
                "EJEMPLO: Calcular P(siguiente_token | 'xyzabc') cuando 'xyzabc' no tiene "
                "celda en Π es operación vacía: no hay significado sobre el cual condicionar."
            ),
        },
        {
            "id": "SM-A12",
            "tipo": "axioma",
            "sujeto": "celda_de_significado_flotante",
            "relacion": "anula",
            "objeto": "correlacion_entre_ocurrencias",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "SM-T9"],
            "gobierna": ["invarianza_significado", "K"],
            "enunciado": (
                "SM-A12 (Invarianza como condición de correlación): Sean w1, w2 dos ocurrencias "
                "del mismo término. Si [w1]_Π ≠ [w2]_Π de forma arbitraria, entonces "
                "K(w1, w2) = 0 bajo cualquier O.\n\n"
                "NOTA OPERATIVA: Si la celda de 'hola' cambia en cada aparición, ninguna "
                "correlación estable es posible. La invariancia de la celda es condición "
                "de posibilidad de K > 0.\n"
                "EJEMPLO: Si en una frase 'hola' significa saludo y tres tokens después "
                "significa número primo, K entre esas dos ocurrencias es 0. No hay puente."
            ),
        },
        {
            "id": "SM-A13",
            "tipo": "axioma",
            "sujeto": "reglas_de_composicion",
            "relacion": "deben_ser",
            "objeto": "deterministas_para_existir_predicado_de_error",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D11"],
            "gobierna": ["ancla_error", "composicion"],
            "enunciado": (
                "SM-A13 (Reglas deterministas de composición): Para que exista un predicado "
                "de error bien definido sobre combinaciones de símbolos, el conjunto de reglas "
                "R debe ser determinista: ∀ entrada e, R(e) produce a lo sumo un resultado canónico.\n\n"
                "NOTA OPERATIVA: Las reglas pueden ser incompletas o imperfectas en algún dominio, "
                "pero deben ser deterministas. Sin determinismo no hay forma de saber si se "
                "acertó o se falló.\n"
                "EJEMPLO: 'sujeto + verbo + objeto' es una regla determinista de composición. "
                "Si la misma entrada pudiera producir dos estructuras incompatibles sin criterio "
                "de desempate, no habría error detectable."
            ),
        },

        # --------------------------------------------------
        # LEMAS
        # --------------------------------------------------
        {
            "id": "SM-L8",
            "tipo": "lema",
            "sujeto": "codigo_binario_completo",
            "relacion": "induce",
            "objeto": "particion_Pi_bin_total",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D9"],
            "gobierna": ["legibilidad", "binario"],
            "enunciado": (
                "SM-L8 (Binario como caso total): Sea Σ el alfabeto de un código binario "
                "completo (p. ej. UTF-8). Entonces existe Π_bin tal que ∀s∈Σ, [s]_Π_bin "
                "está definida y es única.\n\n"
                "NOTA OPERATIVA: El lenguaje de máquina es el caso extremo en que Π es total "
                "y el contraste último es físico (alto/bajo). Por eso es legible sin residuo.\n"
                "EJEMPLO: Cada codepoint Unicode tiene exactamente una secuencia de bytes "
                "en UTF-8. No hay letra 'huérfana'.\n"
                "DEMOSTRACIÓN: Por definición de código completo, la función de codificación "
                "φ: Σ → {0,1}* es total e inyectiva a nivel de codepoints. Las clases "
                "{s | φ(s)=b} forman una partición. Luego Π_bin existe y es total."
            ),
        },
        {
            "id": "SM-L9",
            "tipo": "lema",
            "sujeto": "formas_superficiales_distintas",
            "relacion": "son_identificadas_por_correlacion_si",
            "objeto": "comparten_celda_en_Pi",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "SM-T9"],
            "gobierna": ["invarianza_superficie", "K"],
            "enunciado": (
                "SM-L9 (Superficie vs celda): Sean w, w' formas superficiales distintas. "
                "Si [w]_Π = [w']_Π, entonces toda correlación definida sobre celdas "
                "identifica w y w'.\n\n"
                "NOTA OPERATIVA: La correlación opera sobre elementos de Π, no sobre "
                "la cadena de caracteres. hola/hello/bonjour pueden ser la misma celda.\n"
                "EJEMPLO: Si Π coloca 'hola' y 'hello' en la celda SALUDO, entonces "
                "K(hola, saludo) = K(hello, saludo) bajo el mismo O.\n"
                "DEMOSTRACIÓN: Inmediato de la definición de celda: la correlación "
                "se define sobre Π, no sobre representantes superficiales."
            ),
        },
        {
            "id": "SM-L10",
            "tipo": "lema",
            "sujeto": "entrenamiento",
            "relacion": "preserva_vertices_y_densifica",
            "objeto": "aristas_del_grafo_de_correlaciones",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A11", "SM-A12"],
            "gobierna": ["entrenamiento", "densificacion"],
            "enunciado": (
                "SM-L10 (Entrenamiento como densificación): Sea G_t = (V_t, E_t) el grafo "
                "de correlaciones en el tiempo t, con V_t ⊆ Π. Un paso de entrenamiento "
                "produce G_{t+1} tal que V_{t+1} = V_t y E_{t+1} ⊇ E_t.\n\n"
                "NOTA OPERATIVA: El entrenamiento no crea significado de la nada. "
                "No mueve celdas. Solo añade o refuerza puentes entre celdas ya existentes.\n"
                "EJEMPLO: Después de más datos, el sistema conecta mejor 'casa' con "
                "'habitación', 'techo', 'puerta'. Las celdas de esas palabras no cambiaron; "
                "las aristas se densificaron.\n"
                "DEMOSTRACIÓN: Por SM-A11 y SM-A12 las celdas (vértices) son fijas una vez "
                "estabilizado Π. El único grado de libertad restante es el conjunto de aristas."
            ),
        },

        # --------------------------------------------------
        # TEOREMAS
        # --------------------------------------------------
        {
            "id": "SM-T12",
            "tipo": "teorema",
            "sujeto": "conjunto_de_correlaciones_candidatas",
            "relacion": "selecciona_como_superviviente",
            "objeto": "argmax_de_Tru_Ri_bajo_mismo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "T6", "T14"],
            "gobierna": ["seleccion_correlacion", "Tru_Ri"],
            "enunciado": (
                "SM-T12 (Lucha de correlaciones): Sea {γ_1, …, γ_n} un conjunto de "
                "correlaciones candidatas bajo el mismo O. Defínase "
                "Tru_Ri(γ_i) = C(γ_i)·L(γ_i)·K(γ_i). Entonces la correlación superviviente "
                "es γ* = arg max_i Tru_Ri(γ_i). Toda γ_j con C(γ_j)=0 o L(γ_j)=0 es eliminada.\n\n"
                "NOTA OPERATIVA: Este teorema es el mecanismo de selección cuando hay "
                "varias correlaciones posibles. No se elige por gusto ni por elegancia: "
                "se elige por supervivencia bajo los tres filtros C, L, K. "
                "Engine y Calculator lo implementan al maximizar Tru_Ri bajo O fijado.\n"
                "EJEMPLO: Cinco interpretaciones de la misma frase. Dos se contradicen "
                "(C=0). Una viola la lógica del dominio (L=0). De las dos restantes, "
                "la de mayor K bajo el O declarado gana. Esa es γ*.\n"
                "DEMOSTRACIÓN (comentada):\n"
                "1. Si dos sub-rutas de γ_j se contradicen bajo el mismo O, entonces "
                "   C(γ_j)=0 por definición de coherencia. Luego Tru_Ri(γ_j)=0.\n"
                "2. Si γ_j viola una regla estructural del dominio, L(γ_j)=0. "
                "   Luego Tru_Ri(γ_j)=0.\n"
                "3. Entre las candidatas con C>0 y L>0, el orden es el orden numérico "
                "   del producto C·L·K (valores en un conjunto totalmente ordenado).\n"
                "4. El conjunto de candidatas es finito → el máximo existe.\n"
                "Por tanto γ* = arg max Tru_Ri está bien definida y las rutas "
                "contradictorias o ilógicas quedan fuera."
            ),
        },
        {
            "id": "SM-T13",
            "tipo": "teorema",
            "sujeto": "sistema_sin_canales_a_R",
            "relacion": "posee_entendimiento_operativo_ssi",
            "objeto": "puede_computar_max_Tru_Ri_sobre_Pi_y_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D10", "SM-T12", "TA4"],
            "gobierna": ["entendimiento_operativo", "maquina_sin_R"],
            "enunciado": (
                "SM-T13 (Máquina sin R): Sea S un sistema sin canales sensoriales a R. "
                "S posee entendimiento operativo (SM-D10) si y solo si existen Π y R "
                "deterministas tales que S puede computar max_γ Tru_Ri(γ) bajo cualquier "
                "O declarable a partir de Π.\n\n"
                "NOTA OPERATIVA: Una máquina no toca R. Razona organizando X. "
                "Su realidad operativa es el cuerpo coherente de correlaciones que "
                "maximiza C·L·K bajo el O que se le dio. No inventa hechos "
                "(TA4 permanece intacto).\n"
                "EJEMPLO: El sistema recibe O = 'evaluar coherencia de esta conversación'. "
                "No ve el mundo. Solo ve tokens, celdas y reglas. Computa Tru_Ri de las "
                "rutas posibles y selecciona la máxima. Eso es entendimiento operativo.\n"
                "DEMOSTRACIÓN (comentada):\n"
                "(⇒) Si S tiene entendimiento operativo, por SM-D10 posee Π y R. "
                "Las correlaciones que puede computar bajo R son exactamente las "
                "candidatas de SM-T12. Por tanto puede seleccionar el máximo.\n"
                "(⇐) Si S puede computar el máximo de Tru_Ri sobre correlaciones "
                "generadas por Π y R, entonces las tres condiciones de SM-D10 se cumplen. "
                "Ningún paso del cómputo requiere un canal a R: todo ocurre dentro de X=Π.\n"
                "Luego la equivalencia queda establecida."
            ),
        },
        {
            "id": "SM-T14",
            "tipo": "teorema",
            "sujeto": "predicado_de_error",
            "relacion": "no_existe_sin",
            "objeto": "ancla_Pi_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A11", "SM-A13", "SM-D11"],
            "gobierna": ["ancla_error", "criterio_error"],
            "enunciado": (
                "SM-T14 (Condición de error): No existe predicado de error bien definido "
                "sobre combinaciones de símbolos en ausencia de un ancla (Π, R).\n\n"
                "NOTA OPERATIVA: Este teorema protege contra la ilusión de que se puede "
                "juzgar 'correcto/incorrecto' sin mapa fijo. Sin ancla, acierto y error "
                "son indistinguibles.\n"
                "EJEMPLO: Un sistema al que se le pide 'di si esta frase está bien' "
                "sin diccionario ni reglas de composición no puede fallar ni acertar: "
                "no hay contraste. Cualquier respuesta es arbitraria.\n"
                "DEMOSTRACIÓN (comentada):\n"
                "Supóngase, por absurdo, que existe un predicado E de error sin ancla.\n"
                "Entonces E debería decidir, para una combinación e, si e es errónea.\n"
                "Pero sin Π las celdas no están definidas (SM-A11).\n"
                "Y sin R no hay regla determinista de composición (SM-A13).\n"
                "Luego no existe contraste contra el cual e pueda fallar.\n"
                "Contradicción. Por tanto no existe tal predicado E sin ancla."
            ),
        },
        {
            "id": "SM-T15",
            "tipo": "teorema",
            "sujeto": "aumento_de_probabilidad",
            "relacion": "no_implica_entendimiento_operativo_si",
            "objeto": "celdas_de_Pi_no_invariantes",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A12", "SM-T12", "SM-D10"],
            "gobierna": ["probabilidad_subordinada", "entrenamiento"],
            "enunciado": (
                "SM-T15 (Probabilidad subordinada): Sea {P_t} una familia de medidas de "
                "probabilidad sobre rutas de correlación. Si las celdas de Π no son "
                "invariantes (violación de SM-A12), entonces el aumento de P_t no implica "
                "aumento de entendimiento operativo.\n\n"
                "NOTA OPERATIVA: Más probabilidad sobre celdas flotantes no produce "
                "entendimiento. Solo produce ruido correlacionado. La probabilidad "
                "está subordinada al mapa; nunca lo sustituye.\n"
                "EJEMPLO: Un modelo que asigna probabilidad alta a rutas donde 'hola' "
                "cambia de significado en cada aparición puede tener P alta y "
                "Tru_Ri = 0 simultáneamente. No hay entendimiento operativo.\n"
                "DEMOSTRACIÓN (comentada):\n"
                "1. Por SM-A12, si las celdas flotan, K ≡ 0 entre ocurrencias del mismo término.\n"
                "2. Por SM-T12, Tru_Ri = 0 para toda ruta que dependa de esas celdas.\n"
                "3. Una medida de probabilidad puede concentrarse sobre rutas de Tru_Ri = 0.\n"
                "4. Eso no satisface SM-D10 (correlaciones invariantes).\n"
                "Por tanto el aumento de P_t no implica entendimiento operativo."
            ),
        },

        # --------------------------------------------------
        # COROLARIOS
        # --------------------------------------------------
        {
            "id": "SM-C11",
            "tipo": "corolario",
            "sujeto": "termino_con_celda_cambiante",
            "relacion": "tiene",
            "objeto": "K_igual_a_cero_bajo_todo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A12"],
            "gobierna": ["invarianza_significado"],
            "enunciado": (
                "SM-C11: Si la celda de un término w cambia en cada ocurrencia, entonces "
                "∀O, K(w,w)=0. En particular, ningún sistema puede mantener correlación "
                "estable con w.\n\n"
                "NOTA OPERATIVA: Corolario directo de SM-A12. Si 'hola' flota, no hay "
                "puente posible.\n"
                "EJEMPLO: Un diccionario que redefine 'casa' en cada página hace "
                "imposible cualquier razonamiento estable sobre 'casa'."
            ),
        },
        {
            "id": "SM-C12",
            "tipo": "corolario",
            "sujeto": "ruta_con_C_1_L_1_K_0",
            "relacion": "tiene",
            "objeto": "Tru_Ri_0_y_Tru_total_beta",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T12", "T14"],
            "gobierna": ["Tru_total", "piso_beta"],
            "enunciado": (
                "SM-C12: Si C(γ)=1, L(γ)=1 y K(γ)=0 para todo O que apunte a hechos de R, "
                "entonces Tru_Ri(γ)=0 y Tru_total(γ)=β. γ es solo no-contradicción interna.\n\n"
                "NOTA OPERATIVA: Coherencia perfecta sin anclaje no es verdad evaluable "
                "respecto de R. Es un cuerpo cerrado que no toca hechos.\n"
                "EJEMPLO: Un relato ficticio internamente perfecto (C=1, L=1) pero sin "
                "ningún anclaje a un dominio observable tiene Tru_total = β."
            ),
        },
        {
            "id": "SM-C13",
            "tipo": "corolario",
            "sujeto": "asociacion_estable_hola_saludo",
            "relacion": "demuestra",
            "objeto": "existencia_de_celda_fija_no_posesion_de_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T13", "SM-L9", "TA4"],
            "gobierna": ["entendimiento_operativo", "no_invencion_R"],
            "enunciado": (
                "SM-C13: La asociación estable hola ↦ saludo en un sistema demuestra la "
                "existencia de una celda fija en Π, no la posesión de R.\n\n"
                "NOTA OPERATIVA: Diferencia nítida entre organización de X y contacto "
                "con R. La máquina organiza representaciones; no por ello posee el mundo.\n"
                "EJEMPLO: Que el sistema responda coherentemente a 'hola' no implica "
                "que haya 'sentido' un saludo real. Implica que la celda está fija y "
                "las correlaciones densificadas."
            ),
        },
        {
            "id": "SM-C14",
            "tipo": "corolario",
            "sujeto": "incremento_por_entrenamiento",
            "relacion": "preserva",
            "objeto": "conjunto_de_celdas_y_aumenta_correlaciones",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-L10"],
            "gobierna": ["entrenamiento", "densificacion"],
            "enunciado": (
                "SM-C14: Todo incremento de capacidad por entrenamiento preserva el "
                "conjunto de celdas de Π y solo aumenta el conjunto de correlaciones.\n\n"
                "NOTA OPERATIVA: No hay creación de significado ex nihilo. "
                "Solo densificación de puentes entre significados ya estabilizados.\n"
                "EJEMPLO: Más datos hacen que 'pájaro' se conecte mejor con 'vuelo', "
                "'alas', 'nido'. La celda de 'pájaro' no se movió."
            ),
        },
    ]


# ============================================================
# EXPORTACIÓN CANÓNICA
# ============================================================

__all__ = ["CUERPO", "declaraciones"]
