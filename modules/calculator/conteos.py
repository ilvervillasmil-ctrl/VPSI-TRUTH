"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales (§0.15 / PROTOCOLO).

Oficio único:
    texto + O_context  →  {compromisos, contradicciones,
                           posturas, reversiones,
                           afirmaciones, afirmaciones_falsas}

No calcula C, L, K.
No calcula Tru.
No inventa factores.
Solo materializa los conteos que la ruta operacional de CA ya exige.

Nodos de ciclo_calculo_MC que materializa:
    CC_Premisas_Registro
    CC_Afirmaciones_D
    CC_Conteo_C / CC_Conteo_L / CC_Conteo_K

Fuente de reglas:
    - C = 1 - k/m   (k = pares contradictorios, m = compromisos)
    - L = 1 - r/p   (r = reversiones, p =
