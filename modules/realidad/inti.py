"""
VPSI-TRUTH  ---  modules/realidad/inti.py
INTI DE REALIDAD  ---  filtro de frontera

======================================================================

REALIDAD es el unico modulo que no es autor de su contenido. La RAE,
la gramatica y la red vienen de afuera. Por eso este INTI no verifica
que ese contenido sea verdadero: verifica el CONTRATO DE FRONTERA.

No sabe que es un diccionario. No sabe que es un verbo. No abre una
regla gramatical. Trata igual a toda fuente declarada, y por eso
agregar una fuente manana no obliga a tocar este archivo.

Lo que vigila, y nada mas:

  1. FUNCION DECLARADA   cada fuente dice que hace y que alcance cubre
  2. PISO DE CARGA       una fuente vacia es trivialmente consistente
  3. FORMA DE RESPUESTA  tres estados, no dos
  4. PROCEDENCIA         toda salida dice de que fuente vino
  5. SIN VEREDICTO       dato y origen; nunca juicio
  6. INSTANTANEA         se sella antes; durante la pasada no hay red
  7. DETERMINISMO        misma consulta, misma respuesta bajo el sello

Lo que NO vigila: la coherencia entre fuentes. Que la sintaxis y la
RAE se contradigan es contraste entre modulos, y eso lo ve el Engine
contra los axiomas. El filtro local se queda en lo local.
======================================================================
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

# ===============================================================
# SEGMENTO 1 --- ESTADOS DE RESPUESTA
# ===============================================================
#
# Tres, no dos. Si "no existe" y "fuera de alcance" se colapsan, un
# termino que la fuente no cubre se lee como inexistente, y eso es
# K = 0 donde corresponde UNDEFINED (Lema 1.16: la ausencia de
# referente deja el factor indefinido, no nulo).

ENCONTRADO = "ENCONTRADO"
NO_EXISTE = "NO_EXISTE"
FUERA_DE_ALCANCE = "FUERA_DE_ALCANCE"

ESTADOS = (ENCONTRADO, NO_EXISTE, FUERA_DE_ALCANCE)

# ===============================================================
# SEGMENTO 2 --- ERRORES DE FRONTERA
# ===============================================================

class FronteraRota(Exception):
    """Una fuente existe y no cumple lo que declara."""
    def __init__(self, fuente: str, exigido: str, recibido: str):
        self.fuente = fuente
        super().__init__(f"[{fuente}] se exige {exigido}; se recibio {recibido}")


class SelloAusente(Exception):
    """Se intento consultar sin instantanea sellada."""
    def __init__(self, detalle: str = ""):
        super().__init__(
            "consulta sin instantanea sellada: refrescar y evaluar son "
            "operaciones distintas y no ocurren en la misma pasada. " + detalle
        )


class FuenteIndisponible(Exception):
    """Una fuente declarada no respondio. No se sustituye en silencio."""
    def __init__(self, fuente: str, razon: str):
        self.fuente = fuente
        super().__init__(f"[{fuente}] declarada pero indisponible: {razon}")

# ===============================================================
# SEGMENTO 3 --- CONTRATO DE FUENTE
# ===============================================================
#
# Lo que toda fuente debe declarar antes de que el INTI la admita.
# Da igual si es la RAE, la sintaxis, la morfologia o la red.

CLAVES_FUENTE = ("nombre", "funcion", "alcance", "version")

# Campos que una respuesta NUNCA puede traer. REALIDAD es Ri, no R
# (TA8: la falla reside en el sistema interpretativo, nunca en R).
# Si aparece un veredicto, la fuente dejo de ser canal y se volvio juez.
CAMPOS_PROHIBIDOS = (
    "verdadero", "falso", "correcto", "incorrecto",
    "veredicto", "juicio", "valor_de_verdad",
    "puntaje", "score", "C", "L", "K", "tru_ri", "tru_total",
)

PISO_ENTRADAS = 1   # una fuente vacia es coherente con todo por vacuidad


def declarar_fuente(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Admite una fuente si declara su funcion y su alcance.
    Sin declaracion no pasa: no se infiere lo que la fuente hace.
    """
    if not isinstance(meta, dict):
        raise FronteraRota("?", "diccionario de declaracion", type(meta).__name__)

    for clave in CLAVES_FUENTE:
        if not meta.get(clave):
            raise FronteraRota(
                str(meta.get("nombre", "?")),
                f"clave '{clave}' declarada",
                "ausente o vacia",
            )

    if not isinstance(meta["alcance"], (list, tuple)) or not meta["alcance"]:
        raise FronteraRota(
            meta["nombre"], "alcance como lista no vacia", repr(meta["alcance"])
        )

    n = int(meta.get("entradas", 0))
    if n < PISO_ENTRADAS:
        raise FronteraRota(
            meta["nombre"],
            f"al menos {PISO_ENTRADAS} entrada cargada",
            f"{n}: coherente por vacuidad, no por coherencia",
        )

    return {
        "nombre": str(meta["nombre"]),
        "funcion": str(meta["funcion"]),
        "alcance": [str(a) for a in meta["alcance"]],
        "version": str(meta["version"]),
        "entradas": n,
    }

# ===============================================================
# SEGMENTO 4 --- CONTRATO DE RESPUESTA
# ===============================================================

def verificar_respuesta(fuente: str, resp: Any) -> Dict[str, Any]:
    """
    Toda respuesta lleva estado, dato y procedencia. Nada mas y nada menos.
    """
    if not isinstance(resp, dict):
        raise FronteraRota(fuente, "respuesta como diccionario", type(resp).__name__)

    estado = resp.get("estado")
    if estado not in ESTADOS:
        raise FronteraRota(fuente, f"estado en {ESTADOS}", repr(estado))

    if "procedencia" not in resp or not resp["procedencia"]:
        raise FronteraRota(fuente, "procedencia declarada", "ausente")

    if resp["procedencia"] != fuente:
        raise FronteraRota(
            fuente, f"procedencia '{fuente}'", repr(resp["procedencia"])
        )

    intrusos = [k for k in resp if k in CAMPOS_PROHIBIDOS]
    if intrusos:
        raise FronteraRota(
            fuente,
            "dato y origen, sin juicio (REALIDAD es Ri, no R)",
            f"campos de veredicto: {intrusos}",
        )

    if estado == ENCONTRADO and resp.get("dato") in (None, "", [], {}):
        raise FronteraRota(fuente, "dato no vacio si estado=ENCONTRADO", "dato vacio")

    if estado != ENCONTRADO and resp.get("dato") not in (None, "", [], {}):
        raise FronteraRota(
            fuente, f"dato vacio si estado={estado}", repr(resp.get("dato"))
        )

    return dict(resp)

# ===============================================================
# SEGMENTO 5 --- HUELLA DETERMINISTA
# ===============================================================
#
# Sin componentes estocasticos: sha256 sobre json canonico.
# La misma instantanea da siempre la misma huella.

def _huella(obj: Any) -> str:
    crudo = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:16]

# ===============================================================
# SEGMENTO 6 --- INTI
# ===============================================================

class Inti:
    """
    Filtro de frontera de REALIDAD.

    Ciclo:
        declarar(...)     una vez por fuente
        sellar(instante)  congela la instantanea; a partir de aqui no hay red
        consultar(...)    lee del sello, nunca del cable
        barrer()          informe para el Engine
    """

    def __init__(self):
        self._fuentes: Dict[str, Dict[str, Any]] = {}
        self._indisponibles: Dict[str, str] = {}
        self._sello: Optional[Dict[str, Any]] = None
        self._respuestas: Dict[Tuple[str, str], str] = {}

    # ----- declaracion -----------------------------------------

    def declarar(self, meta: Dict[str, Any]) -> None:
        limpia = declarar_fuente(meta)
        self._fuentes[limpia["nombre"]] = limpia

    def marcar_indisponible(self, nombre: str, razon: str) -> None:
        """Se reporta; no se sustituye en silencio por otra fuente."""
        self._indisponibles[nombre] = razon

    # ----- sellado ---------------------------------------------

    def sellar(self, instante: str) -> Dict[str, Any]:
        """
        Congela la instantanea. Refrescar ocurre antes de esto;
        evaluar ocurre despues. Nunca en la misma pasada.

        Instante unico para todas las fuentes: si cada una llevara su
        fecha, el ancla no seria un objeto sino varios.
        """
        if not self._fuentes:
            raise FronteraRota("realidad", "al menos una fuente declarada", "ninguna")

        cuerpo = {
            "instante": str(instante),
            "fuentes": {
                n: {
                    "funcion": f["funcion"],
                    "alcance": f["alcance"],
                    "version": f["version"],
                    "entradas": f["entradas"],
                }
                for n, f in sorted(self._fuentes.items())
            },
        }
        self._sello = {**cuerpo, "huella": _huella(cuerpo)}
        return dict(self._sello)

    @property
    def sellado(self) -> bool:
        return self._sello is not None

    # ----- consulta --------------------------------------------

    def consultar(self, fuente: str, clave: str, respuesta: Any) -> Dict[str, Any]:
        """
        Verifica una respuesta contra el contrato y la devuelve sellada.
        No consulta nada: recibe lo que la fuente entrego y lo filtra.
        """
        if not self.sellado:
            raise SelloAusente(f"consulta '{clave}' a '{fuente}'")

        if fuente in self._indisponibles:
            raise FuenteIndisponible(fuente, self._indisponibles[fuente])

        if fuente not in self._fuentes:
            raise FronteraRota(fuente, "fuente declarada antes de consultar", "no declarada")

        limpia = verificar_respuesta(fuente, respuesta)

        # determinismo: misma consulta, misma respuesta bajo el mismo sello
        firma = _huella(limpia)
        llave = (fuente, str(clave))
        previa = self._respuestas.get(llave)
        if previa is not None and previa != firma:
            raise FronteraRota(
                fuente,
                f"misma consulta '{clave}', misma respuesta bajo el sello",
                "dos respuestas distintas: invariancia rota",
            )
        self._respuestas[llave] = firma

        limpia["sello"] = self._sello["huella"]
        limpia["instante"] = self._sello["instante"]
        return limpia

    # ----- barrido ---------------------------------------------

    def barrer(self) -> Dict[str, Any]:
        """
        Informe de frontera para el Engine. No lanza: informa.
        Si pasa == False, REALIDAD no cruza hacia el Engine.
        """
        faltas: List[str] = []

        if not self._fuentes:
            faltas.append("ninguna fuente declarada")

        for nombre, razon in sorted(self._indisponibles.items()):
            faltas.append(f"fuente '{nombre}' indisponible: {razon}")

        if not self.sellado:
            faltas.append("instantanea sin sellar")

        return {
            "modulo": "realidad",
            "pasa": not faltas,
            "faltas": faltas,
            "fuentes": sorted(self._fuentes),
            "indisponibles": sorted(self._indisponibles),
            "sello": self._sello["huella"] if self._sello else None,
            "instante": self._sello["instante"] if self._sello else None,
            "consultas_registradas": len(self._respuestas),
        }

    # ----- inventario ------------------------------------------

    def inventario(self) -> Dict[str, Any]:
        return {
            "modulo": "realidad",
            "filtro": "inti",
            "estados": list(ESTADOS),
            "claves_fuente": list(CLAVES_FUENTE),
            "campos_prohibidos": list(CAMPOS_PROHIBIDOS),
            "piso_entradas": PISO_ENTRADAS,
            "fuentes": {n: dict(f) for n, f in sorted(self._fuentes.items())},
            "sello": dict(self._sello) if self._sello else None,
        }

# ===============================================================
# SEGMENTO 7 --- AXIOMAS DECLARADOS POR EL FILTRO
# ===============================================================

def axiomas() -> List[Dict[str, Any]]:
    return [
        {
            "id": "RE-1",
            "tipo": "axioma",
            "sujeto": "realidad",
            "relacion": "emite_veredicto_sobre",
            "objeto": "R",
            "polaridad": False,
            "cota": None,
            "depende_de": [],
            "gobierna": ["realidad"],
            "enunciado": (
                "REALIDAD entrega dato y procedencia, nunca juicio: es Ri "
                "y no R (TA8)."
            ),
        },
        {
            "id": "RE-2",
            "tipo": "axioma",
            "sujeto": "ausencia_de_referente",
            "relacion": "colapsa_a",
            "objeto": "cero",
            "polaridad": False,
            "cota": None,
            "depende_de": [],
            "gobierna": ["realidad"],
            "enunciado": (
                "Fuera de alcance no es inexistente: la ausencia de referente "
                "deja el factor indefinido y no nulo (Lema 1.16)."
            ),
        },
        {
            "id": "RE-3",
            "tipo": "axioma",
            "sujeto": "consulta_externa",
            "relacion": "ocurre_durante",
            "objeto": "pasada",
            "polaridad": False,
            "cota": None,
            "depende_de": [],
            "gobierna": ["realidad"],
            "enunciado": (
                "La pasada lee de la instantanea sellada y no de la red; "
                "de otro modo la misma entrada admite dos salidas y L decae."
            ),
        },
    ]

# ===============================================================
# SEGMENTO 8 --- EXPORTACION
# ===============================================================

__all__ = [
    "Inti",
    "ENCONTRADO", "NO_EXISTE", "FUERA_DE_ALCANCE", "ESTADOS",
    "FronteraRota", "SelloAusente", "FuenteIndisponible",
    "declarar_fuente", "verificar_respuesta",
    "axiomas",
]
