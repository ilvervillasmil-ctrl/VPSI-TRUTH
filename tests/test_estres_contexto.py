"""
Archivo de pruebas de estrés para el contenedor de Contexto (CX).
Puedes modificar 'peticion_estres' con cualquier texto o discrepancia
para ver cómo reacciona el INIT y sus reglas internas.
"""

import json
from pprint import pprint
# Importamos el INIT directamente para que el Centinela evalúe la petición
from modules.contexto import resolver


def test_discrepancias_contexto():
    # =================================================================
    # TU ZONA DE JUEGO: Modifica esta petición como quieras
    # =================================================================
    peticion_estres = {
        # 1. Choque de dominios: Señal de auto-auditoría VS criterios naturales
        "casilla_contexto": "1. Auditar el repositorio VPSI-TRUTH y sus contratos.\n2. Evaluar si Carlos robó el dinero.",
        
        # 2. Choque de estados: O_id vacío (indefinido) VS estado declarado estable
        "O_id": "", 
        "estado": "estable",
        
        # 3. Peticiones de anuncio: Una válida, una inventada
        "pedir_anuncio": True,
        "tipos_peticion": ["dame_cadena_completa", "calcular_K_oculto"],
        
        # 4. Choque de secuencias y modos: Modo conversacion pero con tramos mixtos
        "modo_entrada": "conversacion",
        "tramos": [
            "Carlos: Yo no fui.",
            {"texto": "Cambiando de tema", "cambio_declarado": True}
        ],
        "armar_o_global": True
    }

    # =================================================================
    # PASAMOS LA PETICIÓN AL INIT (El Centinela y las Reglas actúan aquí)
    # =================================================================
    resultado = resolver(peticion_estres)
    
    # Extraemos cómo quedó el registro final después de que el INIT fusionó todo
    registro_final = resultado.get("registro", {})
    
    # Aseguramos que el INIT procesó la petición (debe devolver un registro)
    assert registro_final is not None, "El INIT no devolvió un registro."

    # Comprobamos cómo se resolvieron las discrepancias
    # La regla peticion_anuncio.py debería haber filtrado "calcular_K_oculto"
    tipos_finales = registro_final.get("tipos_peticion", [])
    assert "calcular_K_oculto" not in tipos_finales, "¡Fallo! El tipo inválido se coló."

    return resultado


# Si ejecutas el archivo directamente con python (python tests/test_estres_contexto.py), 
# imprimirá el diagnóstico completo.
if __name__ == "__main__":
    print("\n--- INYECTANDO TORMENTA DE CONTEXTO AL INIT ---")
    salida = test_discrepancias_contexto()
    
    print("\n[ESTADO GLOBAL]")
    print(f"Coherente: {salida.get('coherente')}")
    print(f"Permite K: {salida.get('permite_k')}")
    print(f"Errores detectados: {salida.get('errores')}")
    
    print("\n[REGISTRO FINAL (Fusión del INIT)]")
    print(json.dumps(salida.get("registro"), indent=2, ensure_ascii=False))
    
    print("\n[MENSAJES DE LAS REGLAS]")
    # Mostramos qué regla aportó qué mensaje para rastrear la batalla interna
    detalle_reglas = salida.get("reglas_internas", {}).get("detalle", {})
    for nombre_regla, datos in detalle_reglas.items():
        clasificacion = datos.get("clasificacion", {})
        mensajes = clasificacion.get("mensajes", [])
        if mensajes:
            print(f"\n- Regla: {nombre_regla}.py")
            for msg in mensajes:
                print(f"  > {msg}")
