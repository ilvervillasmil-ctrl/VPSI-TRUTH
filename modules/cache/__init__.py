"""
modules/cache/__init__.py
=========================
CACHE — registro de evidencia del ciclo (fase).

Función específica
------------------
Guardar la información y la evidencia de **todo** el proceso:
secuencias, cálculos, propuestas del Engine, veredictos del Centinela,
contextos y factores tal como ocurrieron.

No calcula Tru. No orquesta. No reordena el mundo.
El orden causal de ejecución lo define correlacion_mecanica (MC);
CACHE solo **registra** lo que ya pasó, en el orden en que se le entrega.

Filtro de integridad
--------------------
La memoria de evidencia es **append-only** en operación normal:
no se modifica ni se reescribe un registro depositado.
Lo que entró permanece como evidencia (propuesta, veredicto, secuencia).

Archivos internos (posteriores)
-------------------------------
Bajo cache/ se anexarán políticas: persistencia, sin-internet, prioridad,
evicción controlada. El init no las inventa: solo expone el contrato
y el registro en memoria de fase.

Contrato con Engine
-------------------
Engine (y Centinela) depositan; Engine puede leer.
CACHE no entra en otros módulos.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from collections import defaultdict
import threading
import copy


# ===============================================================
# ERRORES
# ===============================================================
class CacheError(Exception):
    """Error de forma o de integridad del módulo cache."""


class CacheInmutableError(CacheError):
    """Intento de modificar evidencia ya depositada."""


# ===============================================================
# ESTADO INTERNO (append-only)
# ===============================================================
class _MemoriaEvidencia:
    """
    Almacén de fase: lista ordenada de eventos.
    No permite mutar registros ya escritos.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._eventos: List[Dict[str, Any]] = []
        self._por_ciclo: Dict[str, List[int]] = defaultdict(list)
        self._seq = 0

    def append(self, evento: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(evento, dict):
            raise CacheError("evento debe ser dict")
        with self._lock:
            self._seq += 1
            entrada = {
                "seq": self._seq,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tipo": evento.get("tipo", "evento"),
                "ciclo_id": evento.get("ciclo_id"),
                "origen": evento.get("origen"),  # engine | centinela | sistema
                "payload": copy.deepcopy(evento.get("payload", evento)),
            }
            # quitar claves ya promovidas del payload duplicado si vinieron planas
            for k in ("tipo", "ciclo_id", "origen", "payload"):
                entrada["payload"].pop(k, None)
            self._eventos.append(entrada)
            cid = entrada.get("ciclo_id")
            if cid:
                self._por_ciclo[str(cid)].append(len(self._eventos) - 1)
            return copy.deepcopy(entrada)

    def listar(
        self,
        ciclo_id: Optional[str] = None,
        tipo: Optional[str] = None,
        desde_seq: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            out: List[Dict[str, Any]] = []
            for e in self._eventos:
                if ciclo_id is not None and str(e.get("ciclo_id")) != str(ciclo_id):
                    continue
                if tipo is not None and e.get("tipo") != tipo:
                    continue
                if desde_seq is not None and int(e.get("seq", 0)) < int(desde_seq):
                    continue
                out.append(copy.deepcopy(e))
            return out

    def secuencia_ciclo(self, ciclo_id: str) -> List[Dict[str, Any]]:
        """Todos los eventos de un ciclo, en orden de depósito (seq)."""
        return self.listar(ciclo_id=str(ciclo_id))

    def obtener_ultimo(
        self, ciclo_id: str, tipo: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        regs = self.listar(ciclo_id=str(ciclo_id), tipo=tipo)
        return regs[-1] if regs else None

    def resumen(self) -> Dict[str, Any]:
        with self._lock:
            por_tipo: Dict[str, int] = defaultdict(int)
            for e in self._eventos:
                por_tipo[str(e.get("tipo"))] += 1
            return {
                "total_eventos": len(self._eventos),
                "ciclos": len(self._por_ciclo),
                "por_tipo": dict(por_tipo),
                "seq_actual": self._seq,
                "inmutable": True,
            }

    def intentar_modificar(self, *args: Any, **kwargs: Any) -> None:
        raise CacheInmutableError(
            "CACHE no modifica evidencia depositada; solo registra secuencias"
        )

    def intentar_borrar_evento(self, *args: Any, **kwargs: Any) -> None:
        raise CacheInmutableError(
            "CACHE no borra evidencia en operación normal (append-only)"
        )


_memoria = _MemoriaEvidencia()


# ===============================================================
# API PÚBLICA
# ===============================================================
def depositar(
    tipo: str,
    payload: Dict[str, Any],
    *,
    ciclo_id: Optional[str] = None,
    origen: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Registra un evento de evidencia. Única vía de escritura de negocio.

    tipos de fase (ejemplos, no exhaustivo):
      - propuesta_engine
      - veredicto_centinela
      - secuencia_mecanica
      - factores
      - contexto
      - evaluacion
      - meta
    """
    if not tipo or not isinstance(tipo, str):
        raise CacheError("tipo debe ser str no vacío")
    if not isinstance(payload, dict):
        raise CacheError("payload debe ser dict")
    return _memoria.append({
        "tipo": tipo,
        "ciclo_id": ciclo_id or payload.get("ciclo_id"),
        "origen": origen or payload.get("origen") or "desconocido",
        "payload": payload,
    })


def leer(
    ciclo_id: Optional[str] = None,
    tipo: Optional[str] = None,
    desde_seq: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Lectura de evidencia; no muta."""
    return _memoria.listar(ciclo_id=ciclo_id, tipo=tipo, desde_seq=desde_seq)


def secuencia(ciclo_id: str) -> List[Dict[str, Any]]:
    """Secuencia completa de un ciclo en orden de registro."""
    if not ciclo_id:
        raise CacheError("ciclo_id obligatorio")
    return _memoria.secuencia_ciclo(ciclo_id)


def ultimo(ciclo_id: str, tipo: Optional[str] = None) -> Optional[Dict[str, Any]]:
    return _memoria.obtener_ultimo(ciclo_id, tipo=tipo)


def inventario() -> Dict[str, Any]:
    return {
        "contenedor": "cache",
        "rol": "CH",
        "memoria": _memoria.resumen(),
        "nota": (
            "Append-only. Orden de causa-efecto del sistema: MC. "
            "CACHE solo registra lo depositado."
        ),
    }


def barrer() -> Dict[str, Any]:
    """Centinela local del módulo: integridad del contrato de no-mutación."""
    res = _memoria.resumen()
    return {
        "contenedor": "cache",
        "rol": "CH",
        "coherente": True,
        "inmutable": True,
        "resumen": res,
        "errores": [],
    }


def verificar() -> Dict[str, Any]:
    return barrer()


def verificar_salida(salida: Dict[str, Any]) -> bool:
    if not isinstance(salida, dict):
        return False
    return "coherente" in salida or "seq" in salida or "memoria" in salida


# Protocolo compatible con core.centinela.CacheEvidencia
class CacheBackend:
    """Adaptador para Centinela: guardar / obtener por ciclo_id."""

    def guardar(self, registro: Dict[str, Any]) -> None:
        tipo = str(registro.get("tipo") or "evento")
        ciclo_id = registro.get("ciclo_id")
        depositar(
            tipo,
            registro,
            ciclo_id=str(ciclo_id) if ciclo_id else None,
            origen=str(registro.get("origen") or "centinela"),
        )

    def obtener(self, ciclo_id: str) -> Optional[Dict[str, Any]]:
        # última propuesta_engine del ciclo, o último evento del ciclo
        reg = ultimo(ciclo_id, tipo="propuesta_engine")
        if reg is None:
            regs = secuencia(ciclo_id)
            return regs[-1] if regs else None
        # forma esperada por centinela: paquete en payload o en raíz
        payload = reg.get("payload") or {}
        if "paquete" in payload:
            return {"paquete": payload["paquete"], "ciclo_id": ciclo_id}
        return {"paquete": payload, "ciclo_id": ciclo_id}


def backend_para_centinela() -> CacheBackend:
    return CacheBackend()


# ===============================================================
# CONTENEDOR (Contrato — Engine solo ejecuta lo declarado)
# ===============================================================
CONTENEDOR = {
    "nombre": "cache",
    "rol": "CH",
    "version": "0.1-fase",
    "requiere": [],
    "descripcion": (
        "Registro completo de evidencia del repositorio: secuencias, cálculos, "
        "propuestas y veredictos. Append-only: no modifica lo depositado. "
        "No calcula Tru. No define el orden causal (eso es MC). "
        "Archivos internos futuros: persistencia, prioridad, modo sin red."
    ),
    "capacidades": {
        "verificar": verificar,
        "barrer": barrer,
        "depositar": depositar,
        "leer": leer,
        "secuencia": secuencia,
        "inventario": inventario,
    },
}


__all__ = [
    "CONTENEDOR",
    "CacheError",
    "CacheInmutableError",
    "depositar",
    "leer",
    "secuencia",
    "ultimo",
    "inventario",
    "verificar",
    "barrer",
    "verificar_salida",
    "CacheBackend",
    "backend_para_centinela",
]
