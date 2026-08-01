"""
Centinela Global para VPSI-TRUTH.
Valida que el sistema completo sea coherente usando los reportes
generados por el Engine Global.
"""

from typing import Dict, Any, List
from core.engine import GlobalEngine


class CentinelaGlobal:
    """
    Valida que el sistema completo sea coherente.
    - Usa los reportes internos de cada módulo (recopilados por el Engine Global).
    - Determina si el sistema está en un estado válido o no.
    """

    @staticmethod
    def validar_sistema() -> Dict[str, Any]:
        """
        Valida que todos los módulos estén coherentes.
        """
        resultados = GlobalEngine.ejecutar_sistema()
        errores = []

        for modulo_name, resultado in resultados.items():
            if not resultado.get("coherente", True):
                errores.append({
                    "modulo": modulo_name,
                    "errores": resultado.get("errores", []),
                    "choques": resultado.get("choques", [])
                })

        if errores:
            return {
                "status": "error",
                "errores": errores
            }
        else:
            return {"status": "ok"}

    @staticmethod
    def validar_modulo(modulo_name: str) -> Dict[str, Any]:
        """
        Valida un módulo específico.
        """
        try:
            resultado = GlobalEngine.ejecutar_modulo(modulo_name, "verificar")
            if resultado.get("coherente", True):
                return {"status": "ok", "modulo": modulo_name}
            else:
                return {
                    "status": "error",
                    "modulo": modulo_name,
                    "errores": resultado.get("errores", []),
                    "choques": resultado.get("choques", [])
                }
        except Exception as e:
            return {
                "status": "error",
                "modulo": modulo_name,
                "error": str(e)
            }

    @staticmethod
    def obtener_estado_global() -> Dict[str, Any]:
        """
        Obtiene el estado global del sistema, incluyendo:
        - Estado de cada módulo.
        - Inventario de declaraciones.
        - Axiomas cargados.
        """
        resultados = GlobalEngine.ejecutar_sistema()
        inventario = GlobalEngine.obtener_inventario()
        axiomas = GlobalEngine.obtener_axiomas()

        estado_modulos = {}
        for modulo_name, resultado in resultados.items():
            estado_modulos[modulo_name] = {
                "coherente": resultado.get("coherente", False),
                "declaraciones": resultado.get("declaraciones", 0),
                "errores": len(resultado.get("errores", [])),
                "choques": len(resultado.get("choques", []))
            }

        return {
            "estado_modulos": estado_modulos,
            "inventario": inventario,
            "axiomas": axiomas
        }
