# VPSI-TRUTH / modules/verificacion/auditor.py

import ast
from typing import Any, Dict, List

class ContradiccionCodigoError(Exception):
    """Lanzado cuando el código fuente viola un axioma estructural del sistema."""
    def __init__(self, axioma_id: str, detalle: str, nodo_info: str):
        self.axioma_id = axioma_id
        self.detalle = detalle
        super().__init__(
            f"\n[PARO AXIOMÁTICO]\n"
            f"  -> Axioma Violado: {axioma_id}\n"
            f"  -> Contradicción: {detalle}\n"
            f"  -> Contexto de Código: {nodo_info}"
        )

class AuditorAxiomatico:
    """
    Analiza AST (Árbitros de Sintaxis Abstracta) del código fuente y contrasta
    sus implicaciones lógicas contra el diccionario de axiomas del VPSI.
    """

    def ejecutar_barrido_transversal(self, archivos_codigo: Dict[str, str], axiomas_sistema: Dict[str, Any]) -> Dict[str, Any]:
        choques = []
        
        for ruta, codigo in archivos_codigo.items():
            try:
                arbol = ast.parse(codigo, filename=ruta)
                self._analizar_nodo(arbol, ruta, axiomas_sistema, choques)
            except SyntaxError as e:
                choques.append({
                    "archivo": ruta,
                    "error": f"Error de sintaxis: {e}"
                })

        if choques:
            return {
                "coherente": False,
                "choques": choques
            }

        return {
            "coherente": True,
            "choques": []
        }

    def _analizar_nodo(self, nodo: ast.AST, ruta: str, axiomas: Dict[str, Any], choques: List[Dict]):
        # Ejemplo de regla estructural: Prohibición de uso de tipos float en cálculos de verdad
        for subnodo in ast.walk(nodo):
            if isinstance(subnodo, ast.Call):
                if isinstance(subnodo.func, ast.Name) and subnodo.func.id == "float":
                    choques.append({
                        "archivo": ruta,
                        "linea": subnodo.lineno,
                        "razon": "Uso de float detectado en código fuente. Violación de precisión exacta por Fraction."
                    })
