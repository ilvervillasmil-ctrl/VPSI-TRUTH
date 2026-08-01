#!/usr/bin/env python3
"""
CENTINELA DEL ENGINE - VPSI-TRUTH

Vigila el despacho, no el resultado. Distingue dos cosas:

    PENDIENTE      el rol no está montado todavía. Fase de construcción,
                   no defecto. El centinela lo nombra y detiene la pasada.

    CONTRATO_ROTO  el módulo existe y no expone lo que su rol exige.
                   Eso sí es defecto.

Adaptado a la nueva arquitectura donde:
- Los módulos exponen sus capacidades a través de CONTENEDOR.
- El Engine Global (core/engine.py) descubre módulos y ejecuta sus capacidades.
- El Centinela Global valida el sistema usando los reportes del Engine.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple


class PiezaPendiente(Exception):
    def __init__(self, rol: str, para_que: str):
        self.rol = rol
        self.para_que = para_que
        super().__init__(f"rol '{rol}' no montado ({para_que})")


class ContratoRoto(Exception):
    def __init__(self, quien: str, exigido: str, recibido: str):
        self.quien = quien
        super().__init__(f"{quien}: se exige {exigido}, se recibió {recibido}")


class Centinela:
    """
    Centinela Global para validar el sistema VPSI-TRUTH.
    - Vigila que los módulos cumplan sus contratos (capacidades exigidas).
    - Valida el orden de arranque (barrido axiomático previo).
    - Exige roles imprescindibles (AX, CT, FO, CA).
    """

    # rol -> (clase, nombres exigidos, para qué sirve)
    CONTRATOS: Dict[str, Tuple[str, Tuple[str, ...], str]] = {
        "AX": ("funcion", ("barrer",), "juez de contraste axiomático"),
        "CT": ("atributo", ("ALPHA", "BETA"), "ALPHA y BETA exactos"),
        "FO": ("funcion", ("tru_ri", "tru_total"), "funcional canónico"),
        "CA": ("funcion", ("calcular",), "devuelve C, L, K"),
        "CX": ("funcion", ("resolver",), "resuelve Octx"),
        "TX": ("funcion", ("anotar",), "anota tácticas T1-T15"),
    }

    IMPRESCINDIBLES = ("AX", "CT", "FO", "CA")

    def __init__(self, registro, informe_axiomas: Optional[Dict] = None):
        self.registro = registro
        self.informe_axiomas = informe_axiomas
        self._ultima_pasada: Optional[Tuple[str, str]] = None

    def _contenedor_de(self, rol: str):
        """Busca el contenedor asociado a un rol en el registro."""
        for c in self.registro.contenedores.values():
            if getattr(c, "rol", None) == rol:
                return c
        return None

    def _obtener_capacidad(self, contenedor, nombre: str, clase: str) -> Any:
        """
        Obtiene una capacidad de un contenedor y valida su tipo.
        """
        if nombre not in contenedor.get("capacidades", {}):
            return None
        valor = contenedor["capacidades"][nombre]
        if clase == "funcion" and not callable(valor):
            return None
        if clase == "atributo" and not isinstance(valor, Fraction):
            return None
        return valor

    # ---------------------------------------------------------------
    # CENSO: rol declarado contra rol ejercido
    # ---------------------------------------------------------------

    def censo(self) -> Dict[str, Dict[str, Any]]:
        """No lanza. Devuelve el estado de cada rol para el inventario."""
        out: Dict[str, Dict[str, Any]] = {}
        for rol, (clase, nombres, para_que) in self.CONTRATOS.items():
            exige = ", ".join(
                n + "()" if clase == "funcion" else n for n in nombres
            )
            cont = self._contenedor_de(rol)

            if cont is None:
                out[rol] = {
                    "estado": "PENDIENTE",
                    "modulo": None,
                    "exige": exige,
                    "para_que": para_que,
                }
                continue

            faltan: List[str] = []
            for n in nombres:
                v = self._obtener_capacidad(cont, n, clase)
                if v is None:
                    if clase == "funcion":
                        faltan.append(f"{n}()")
                    else:
                        faltan.append(f"{n} (Fraction, recibido {type(v).__name__ if v is not None else 'None'})")

            if faltan:
                out[rol] = {
                    "estado": "CONTRATO_ROTO",
                    "modulo": cont.get("nombre", "desconocido"),
                    "exige": exige,
                    "falta": faltan,
                    "para_que": para_que,
                }
            else:
                out[rol] = {
                    "estado": "MONTADO",
                    "modulo": cont.get("nombre", "desconocido"),
                    "exige": exige,
                    "para_que": para_que,
                }
        return out

    def puede_evaluar(self) -> Tuple[bool, List[str]]:
        c = self.censo()
        faltan = [r for r in self.IMPRESCINDIBLES if c[r]["estado"] != "MONTADO"]
        return (not faltan), faltan

    # ---------------------------------------------------------------
    # ORDEN DE ARRANQUE
    # ---------------------------------------------------------------

    def exigir_barrido_previo(self, informe: Optional[Dict]) -> None:
        if informe is None:
            raise ContratoRoto(
                "orden de arranque",
                "barrido axiomático antes del primer evaluar()",
                "informe_axiomas ausente",
            )
        if not informe.get("coherente", False):
            n = len(informe.get("choques", []) or [])
            raise ContratoRoto(
                "orden de arranque", "axiomática coherente",
                f"{n} choques sin resolver",
            )
        if informe.get("declaraciones", 0) == 0:
            raise ContratoRoto(
                "orden de arranque", "al menos una declaración cargada",
                "0 declaraciones: coherente por vacuidad",
            )

    # ---------------------------------------------------------------
    # ROLES
    # ---------------------------------------------------------------

    def exigir_roles(self, roles: Optional[List[str]] = None) -> None:
        censo = self.censo()
        for rol in (roles or self.IMPRESCINDIBLES):
            d = censo[rol]
            if d["estado"] == "PENDIENTE":
                raise PiezaPendiente(rol, d["para_que"])
            if d["estado"] == "CONTRATO_ROTO":
                raise ContratoRoto(
                    f"contenedor '{d['modulo']}' con rol {rol}",
                    d["exige"],
                    f"falta {d.get('falta')}",
                )

    # ---------------------------------------------------------------
    # FRONTERA DE TIPOS
    # ---------------------------------------------------------------

    @staticmethod
    def exigir_exacto(nombre: str, valor: Any) -> Fraction:
        """Rechaza, no convierte. Fraction(str(0.1)) finge la precisión."""
        if isinstance(valor, Fraction):
            return valor
        if isinstance(valor, int):
            return Fraction(valor)
        raise ContratoRoto(
            nombre, "Fraction o int", f"{type(valor).__name__} ({valor!r})"
        )

    def exigir_factores(self, factores: Dict[str, Any]) -> Dict[str, Fraction]:
        limpios: Dict[str, Fraction] = {}
        for nombre in ("C", "L", "K"):
            if nombre not in factores:
                raise ContratoRoto("factores", f"'{nombre}' presente", "ausente")
            v = factores[nombre]
            if str(v).upper() == "UNDEFINED":
                raise PiezaPendiente("CA", f"factor {nombre} quedó UNDEFINED")
            v = self.exigir_exacto(f"factor {nombre}", v)
            if not (Fraction(0) <= v <= Fraction(1)):
                raise ContratoRoto(f"factor {nombre}", "valor en [0, 1]", str(v))
            limpios[nombre] = v
        return limpios

    # ---------------------------------------------------------------
    # AUTORIDAD E INVARIANCIA L
    # ---------------------------------------------------------------

    def exigir_invocador(self, invocador_id: str) -> None:
        if invocador_id != "core":
            raise ContratoRoto(
                "autoridad de despacho", "invocador 'core'", f"'{invocador_id}'"
            )

    def registrar_pasada(self, huella_peticion: str, huella_resultado: str) -> None:
        if self._ultima_pasada is not None:
            prev_p, prev_r = self._ultima_pasada
            if huella_peticion == prev_p and huella_resultado != prev_r:
                raise ContratoRoto(
                    "invariancia L",
                    "misma petición, mismo resultado",
                    f"dos resultados distintos para la huella {huella_peticion}",
                )
        self._ultima_pasada = (huella_peticion, huella_resultado)

    # ---------------------------------------------------------------
    # PUERTA ÚNICA
    # ---------------------------------------------------------------

    def franquear(
        self,
        peticion: Dict[str, Any],
        informe_axiomas: Optional[Dict],
        invocador_id: str,
        roles: Optional[List[str]] = None,
    ) -> None:
        self.exigir_invocador(invocador_id)
        self.exigir_barrido_previo(informe_axiomas)
        self.exigir_roles(roles)
        if not peticion.get("contexto"):
            raise ContratoRoto(
                "petición",
                "Octx declarado (sin él, K queda indefinida y no nula)",
                "sin contexto",
            )

    # ---------------------------------------------------------------
    # INTEGRACIÓN CON EL ENGINE GLOBAL
    # ---------------------------------------------------------------

    def validar_sistema(self) -> Dict[str, Any]:
        """
        Valida el sistema completo usando el Engine Global.
        """
        from core.engine import GlobalEngine
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
            return {"status": "error", "errores": errores}
        else:
            return {"status": "ok"}
