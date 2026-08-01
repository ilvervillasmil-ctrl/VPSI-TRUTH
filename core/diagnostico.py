from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from collections import defaultdict
import threading

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================
CONTENEDOR = {
    "nombre": "diagnostico",
    "rol": "DG",
    "version": "1.0",
    "descripcion": "Receptor centralizado de reportes Omega. Acumula faltas, errores y choques de todos los módulos.",
}

# ===============================================================
# SEGMENTO 2 --- ERRORES
# ===============================================================
class DiagnosticoError(Exception):
    """Error interno del sistema de diagnóstico."""
    pass

# ===============================================================
# SEGMENTO 3 --- ESTADO GLOBAL (Thread-safe)
# ===============================================================
class _EstadoDiagnostico:
    """Estado interno compartido del diagnóstico global."""

    def __init__(self):
        self._lock = threading.RLock()
        self._reportes: List[Dict[str, Any]] = []
        self._por_modulo: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._contador = 0

    def recibir(self, modulo: str, errores: List[Dict[str, Any]]) -> None:
        with self._lock:
            timestamp = datetime.now(timezone.utc).isoformat()
            for error in errores:
                self._contador += 1
                entrada = {
                    "id": self._contador,
                    "timestamp": timestamp,
                    "modulo": modulo,
                    "tipo": error.get("tipo", "desconocido"),
                    "detalle": error.get("detalle", error),
                }
                self._reportes.append(entrada)
                self._por_modulo[modulo].append(entrada)

    def obtener_todos(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._reportes)

    def obtener_por_modulo(self, modulo: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._por_modulo.get(modulo, []))

    def limpiar(self, modulo: Optional[str] = None) -> int:
        """Limpia reportes. Si se pasa módulo, solo de ese módulo. Devuelve cantidad eliminada."""
        with self._lock:
            if modulo is None:
                eliminados = len(self._reportes)
                self._reportes.clear()
                self._por_modulo.clear()
                return eliminados
            else:
                eliminados = len(self._por_modulo.get(modulo, []))
                self._reportes = [r for r in self._reportes if r["modulo"] != modulo]
                if modulo in self._por_modulo:
                    del self._por_modulo[modulo]
                return eliminados

    def resumen(self) -> Dict[str, Any]:
        with self._lock:
            por_tipo = defaultdict(int)
            for r in self._reportes:
                por_tipo[r["tipo"]] += 1
            return {
                "total_reportes": len(self._reportes),
                "modulos_afectados": list(self._por_modulo.keys()),
                "por_modulo": {m: len(v) for m, v in self._por_modulo.items()},
                "por_tipo": dict(por_tipo),
                "coherente_global": len(self._reportes) == 0,
            }

    def es_coherente(self) -> bool:
        with self._lock:
            return len(self._reportes) == 0


# Instancia única (singleton de estado)
_estado = _EstadoDiagnostico()

# ===============================================================
# SEGMENTO 4 --- API PÚBLICA (DiagnosticoGlobal)
# ===============================================================
class DiagnosticoGlobal:
    """
    Receptor centralizado de reportes Omega.
    Todos los módulos (FO, CA, AX, etc.) reportan aquí.
    """

    @staticmethod
    def recibir_reporte(modulo: str, errores: List[Dict[str, Any]]) -> None:
        """
        Recibe un reporte de un módulo.
        - modulo: nombre del contenedor que reporta ("formulas", "calculator", "axiomas", ...)
        - errores: lista de dicts con al menos {"tipo": ..., "detalle": ...}
        """
        if not isinstance(errores, list):
            raise DiagnosticoError(f"errores debe ser lista, recibido: {type(errores)}")
        if not modulo or not isinstance(modulo, str):
            raise DiagnosticoError("modulo debe ser str no vacío")
        _estado.recibir(modulo, errores)

    @staticmethod
    def obtener_reportes(modulo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Devuelve todos los reportes o solo los de un módulo."""
        if modulo is None:
            return _estado.obtener_todos()
        return _estado.obtener_por_modulo(modulo)

    @staticmethod
    def limpiar(modulo: Optional[str] = None) -> int:
        """Limpia reportes. Devuelve cuántos se eliminaron."""
        return _estado.limpiar(modulo)

    @staticmethod
    def resumen() -> Dict[str, Any]:
        """Resumen global del estado de diagnóstico."""
        return _estado.resumen()

    @staticmethod
    def es_coherente() -> bool:
        """True si no hay ningún reporte pendiente."""
        return _estado.es_coherente()

    @staticmethod
    def barrer() -> Dict[str, Any]:
        """
        Capacidad de verificación del propio módulo de diagnóstico.
        Devuelve el estado actual del sistema de reportes.
        """
        res = _estado.resumen()
        return {
            "contenedor": CONTENEDOR["nombre"],
            "estado": "APROBADO" if res["coherente_global"] else "RECHAZADO",
            "coherente": res["coherente_global"],
            "resumen": res,
        }


# ===============================================================
# SEGMENTO 5 --- CENTINELA
# ===============================================================
def verificar_salida(salida: Dict[str, Any]) -> bool:
    """Valida la salida de barrer() del diagnóstico."""
    return salida.get("coherente", False)


# ===============================================================
# SEGMENTO 6 --- CONTENEDOR (Contrato)
# ===============================================================
CONTENEDOR = {
    "nombre": "diagnostico",
    "rol": "DG",
    "version": "1.0",
    "requiere": [],
    "descripcion": "Receptor centralizado de reportes Omega. Acumula faltas, errores y choques de todos los módulos.",
    "capacidades": {
        "verificar": DiagnosticoGlobal.barrer,
        "evaluar": DiagnosticoGlobal.barrer,
        "recibir": DiagnosticoGlobal.recibir_reporte,
        "resumen": DiagnosticoGlobal.resumen,
        "limpiar": DiagnosticoGlobal.limpiar,
    },
}

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "DiagnosticoGlobal",
    "CONTENEDOR",
    "verificar_salida",
    "DiagnosticoError",
]
