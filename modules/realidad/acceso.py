"""
VPSI-TRUTH  ---  modules/realidad/acceso.py
ACCESO A INTERNET

======================================================================
Este archivo hace una sola cosa: dar al programa acceso a Internet.

No sabe a que pagina va. No sabe que fuente se consulta. No juzga
lo que llega. Abre el canal, trae bytes, y cierra.

Que URL se pide, con que proposito y como se interpreta la respuesta
son decisiones de las capas de arriba.
======================================================================
"""

from __future__ import annotations

import socket
import ssl
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

# ===============================================================
# SEGMENTO 1 --- BIBLIOTECAS
# ===============================================================
#
# ESTANDAR (vienen con Python, no se instala nada):
#     socket           TCP y resolucion DNS
#     ssl              TLS y verificacion de certificados
#     urllib.request   cliente HTTP/HTTPS
#     urllib.error     errores de urllib
#     http.client      HTTP/1.1 de bajo nivel (usado por urllib)
#
# OPCIONAL (si esta instalada se usa; si no, se cae a la estandar):
#     requests         sesion con pooling y reintentos
#                      arrastra: urllib3, certifi, idna, charset-normalizer
#
# Con solo la estandar el acceso funciona completo. requests agrega
# reutilizacion de conexion y reintentos, nada mas.

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAY_REQUESTS = True
except ImportError:
    requests = None
    HTTPAdapter = None
    Retry = None
    HAY_REQUESTS = False

# ===============================================================
# SEGMENTO 2 --- PARAMETROS DEL CANAL
# ===============================================================

AGENTE = "VPSI-TRUTH/1.0"

TIMEOUT_CONEXION = 5     # segundos para abrir el socket
TIMEOUT_LECTURA = 15     # segundos para recibir la respuesta

# Sondas de disponibilidad: IP directa, sin DNS.
SONDAS = (("1.1.1.1", 53), ("8.8.8.8", 53))

REINTENTOS = 3
ESTADOS_REINTENTABLES = (408, 425, 429, 500, 502, 503, 504)

# ===============================================================
# SEGMENTO 3 --- DISPONIBILIDAD
# ===============================================================

def hay_acceso(timeout: float = TIMEOUT_CONEXION) -> bool:
    """
    Comprueba si existe salida a Internet.
    TCP directo a IP conocida: no depende de DNS ni de HTTP.
    """
    for host, puerto in SONDAS:
        try:
            s = socket.create_connection((host, puerto), timeout=timeout)
            s.close()
            return True
        except OSError:
            continue
    return False


def hay_dns(nombre: str = "example.com", timeout: float = TIMEOUT_CONEXION) -> bool:
    """Comprueba que la resolucion de nombres responde."""
    previo = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        socket.getaddrinfo(nombre, 443, proto=socket.IPPROTO_TCP)
        return True
    except OSError:
        return False
    finally:
        socket.setdefaulttimeout(previo)

# ===============================================================
# SEGMENTO 4 --- CANAL
# ===============================================================

class Canal:
    """
    Canal de acceso a Internet. Se abre una vez y se reutiliza.

        canal = Canal()
        canal.abrir()
        r = canal.obtener("https://ejemplo.com/recurso")
        canal.cerrar()

    Tambien sirve como contexto:

        with Canal() as canal:
            r = canal.obtener("https://ejemplo.com/recurso")
    """

    def __init__(
        self,
        agente: str = AGENTE,
        timeout_conexion: float = TIMEOUT_CONEXION,
        timeout_lectura: float = TIMEOUT_LECTURA,
        reintentos: int = REINTENTOS,
        verificar_tls: bool = True,
    ):
        self.agente = agente
        self.timeout_conexion = timeout_conexion
        self.timeout_lectura = timeout_lectura
        self.reintentos = reintentos
        self.verificar_tls = verificar_tls
        self._sesion = None
        self._abierto = False

    # ----- apertura y cierre -----------------------------------

    def abrir(self) -> None:
        if HAY_REQUESTS:
            s = requests.Session()
            s.headers.update({"User-Agent": self.agente})
            politica = Retry(
                total=self.reintentos,
                backoff_factor=1,
                status_forcelist=list(ESTADOS_REINTENTABLES),
                allowed_methods=("GET", "HEAD"),
                respect_retry_after_header=True,
            )
            adaptador = HTTPAdapter(max_retries=politica)
            s.mount("https://", adaptador)
            s.mount("http://", adaptador)
            self._sesion = s
        else:
            ctx = ssl.create_default_context()
            if not self.verificar_tls:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            self._sesion = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=ctx)
            )
            self._sesion.addheaders = [("User-Agent", self.agente)]
        self._abierto = True

    def cerrar(self) -> None:
        if HAY_REQUESTS and self._sesion is not None:
            self._sesion.close()
        self._sesion = None
        self._abierto = False

    def __enter__(self):
        self.abrir()
        return self

    def __exit__(self, *_):
        self.cerrar()

    @property
    def abierto(self) -> bool:
        return self._abierto

    # ----- acceso ----------------------------------------------

    def obtener(
        self,
        url: str,
        cabeceras: Optional[Dict[str, str]] = None,
        metodo: str = "GET",
    ) -> Dict[str, Any]:
        """
        Trae un recurso. Cualquier URL. Devuelve siempre la misma forma:

            estado      codigo HTTP, o None si no hubo respuesta
            cuerpo      bytes recibidos
            cabeceras   cabeceras de respuesta
            url_final   tras redirecciones
            error       None si hubo respuesta; texto si no la hubo

        No lanza por codigo de estado: 404 y 500 son respuestas.
        Solo hay error cuando no se llego a hablar con nadie.
        """
        if not self._abierto:
            raise RuntimeError("canal cerrado: llamar abrir() antes de obtener()")

        cab = {"User-Agent": self.agente}
        if cabeceras:
            cab.update(cabeceras)

        if HAY_REQUESTS:
            return self._obtener_requests(url, cab, metodo)
        return self._obtener_urllib(url, cab, metodo)

    # ----- implementaciones ------------------------------------

    def _obtener_requests(self, url, cab, metodo) -> Dict[str, Any]:
        try:
            r = self._sesion.request(
                metodo, url,
                headers=cab,
                timeout=(self.timeout_conexion, self.timeout_lectura),
                verify=self.verificar_tls,
                allow_redirects=True,
            )
            return {
                "estado": r.status_code,
                "cuerpo": r.content,
                "cabeceras": dict(r.headers),
                "url_final": r.url,
                "error": None,
            }
        except Exception as e:
            return self._sin_respuesta(url, e)

    def _obtener_urllib(self, url, cab, metodo) -> Dict[str, Any]:
        peticion = urllib.request.Request(url, headers=cab, method=metodo)
        try:
            with self._sesion.open(peticion, timeout=self.timeout_lectura) as resp:
                return {
                    "estado": resp.getcode(),
                    "cuerpo": resp.read(),
                    "cabeceras": dict(resp.headers),
                    "url_final": resp.geturl(),
                    "error": None,
                }
        except urllib.error.HTTPError as e:
            # hubo respuesta, con codigo de error: no es fallo de canal
            return {
                "estado": e.code,
                "cuerpo": e.read(),
                "cabeceras": dict(e.headers or {}),
                "url_final": url,
                "error": None,
            }
        except Exception as e:
            return self._sin_respuesta(url, e)

    @staticmethod
    def _sin_respuesta(url: str, e: Exception) -> Dict[str, Any]:
        return {
            "estado": None,
            "cuerpo": b"",
            "cabeceras": {},
            "url_final": url,
            "error": f"{type(e).__name__}: {e}",
        }

# ===============================================================
# SEGMENTO 5 --- INVENTARIO
# ===============================================================

def inventario() -> Dict[str, Any]:
    return {
        "modulo": "realidad",
        "componente": "acceso",
        "cliente": "requests" if HAY_REQUESTS else "urllib (estandar)",
        "bibliotecas_estandar": ["socket", "ssl", "urllib.request", "http.client"],
        "bibliotecas_opcionales": ["requests", "urllib3", "certifi"],
        "requests_disponible": HAY_REQUESTS,
        "agente": AGENTE,
        "timeout_conexion": TIMEOUT_CONEXION,
        "timeout_lectura": TIMEOUT_LECTURA,
        "reintentos": REINTENTOS,
        "estados_reintentables": list(ESTADOS_REINTENTABLES),
        "acceso": hay_acceso(timeout=2),
    }

# ===============================================================
# SEGMENTO 6 --- EXPORTACION
# ===============================================================

__all__ = [
    "Canal",
    "hay_acceso",
    "hay_dns",
    "inventario",
    "HAY_REQUESTS",
    "AGENTE",
    "TIMEOUT_CONEXION",
    "TIMEOUT_LECTURA",
]
