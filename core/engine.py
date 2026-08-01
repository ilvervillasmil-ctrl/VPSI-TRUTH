from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.diagnostico import DiagnosticoGlobal

# ===============================================================
# SEGMENTO 0 --- EXCEPCIONES
# ===============================================================
class ArranqueError(RuntimeError):
    """
    Falla que impide arrancar o completar la ejecucion del sistema.

    El Engine NO la lanza durante la operacion normal: sigue reportando a
    DiagnosticoGlobal y devolviendo dicts. Se lanza solo desde los puntos de
    entrada estrictos (ver `arrancar`), donde el CI necesita un fallo duro.
    """


# ===============================================================
# SEGMENTO 1 --- IDENTIDAD (fuente unica; el CONTENEDOR se arma al final)
# ===============================================================
_NOMBRE = "engine"
_ROL = "EN"
_VERSION = "1.1"
_DESCRIPCION = (
    "Orquestador principal del sistema VPSI-TRUTH. Descubre modulos, "
    "obtiene orden de ejecucion y los ejecuta."
)

# ===============================================================
# SEGMENTO 2 --- CONSTANTES
# ===============================================================
_MODULES_DIR = Path(__file__).parent.parent / "modules"

# Directorios que nunca son modulos (__pycache__, .git, .ipynb_checkpoints...)
_PREFIJOS_IGNORADOS = ("_", ".")

# Si True, el Engine solo se declara APROBADO cuando ademas todos los modulos
# ejecutados reportan coherente=True. Ponlo en False para volver al
# comportamiento anterior (aprobar con solo terminar la corrida).
EXIGIR_MODULOS_COHERENTES = True


# ===============================================================
# SEGMENTO 3 --- REPORTE INTERNO
# ===============================================================
def _reportar(tipo: str, detalle: str) -> None:
    """Envia un error al diagnostico global. Nunca lanza."""
    try:
        DiagnosticoGlobal.recibir_reporte(
            modulo=_NOMBRE,
            errores=[{"tipo": tipo, "detalle": detalle}],
        )
    except Exception:  # el diagnostico jamas debe tumbar al Engine
        pass


def _detalle_excepcion(e: BaseException) -> str:
    """Texto util de una excepcion: tipo + mensaje. NO se descarta nunca."""
    return f"{type(e).__name__}: {e}"


# ===============================================================
# SEGMENTO 4 --- ENGINE
# ===============================================================
def descubrir_modulos() -> Dict[str, Any]:
    """
    Descubre automaticamente todos los modulos en `modules/`.
    Retorna {nombre_modulo: CONTENEDOR}.

    Reporta -con el mensaje real de la excepcion- cualquier modulo que no se
    pueda importar o que no exponga CONTENEDOR.
    """
    modulos: Dict[str, Any] = {}

    if not _MODULES_DIR.is_dir():
        _reportar(
            "directorio_ausente",
            f"No existe el directorio de modulos: {_MODULES_DIR}",
        )
        return modulos

    for modulo_dir in sorted(_MODULES_DIR.iterdir()):
        if not modulo_dir.is_dir():
            continue

        modulo_name = modulo_dir.name

        # __pycache__, .git, etc. no son modulos del sistema.
        if modulo_name.startswith(_PREFIJOS_IGNORADOS):
            continue

        if not (modulo_dir / "__init__.py").exists():
            _reportar(
                "sin_init",
                f"'{modulo_name}' no tiene __init__.py; no es un paquete importable, se omite",
            )
            continue

        try:
            # Antes solo se atrapaba ImportError: un SyntaxError o NameError
            # dentro de un modulo tumbaba el Engine entero.
            modulo = importlib.import_module(f"modules.{modulo_name}")
        except Exception as e:
            _reportar(
                "import_error",
                f"No se pudo importar modules.{modulo_name} -> {_detalle_excepcion(e)}",
            )
            continue

        contenedor = getattr(modulo, "CONTENEDOR", None)
        if contenedor is None:
            _reportar(
                "sin_contenedor",
                f"modules.{modulo_name} se importo pero no expone CONTENEDOR",
            )
            continue

        modulos[modulo_name] = contenedor

    return modulos


def _resolver_orden() -> Tuple[Optional[List[str]], str]:
    """
    Consulta `correlacion_mecanica/` y devuelve (orden, motivo).

    Distingue las fallas que antes se confundian en un mismo None:
      - el modulo no existe / no importa
      - el modulo no expone la capacidad 'verificar'
      - 'verificar' revento
      - la respuesta no tiene la forma esperada
      - hay choques (incoherente)
    `motivo` es "ok" solo cuando orden es una lista valida.
    """
    try:
        from modules.correlacion_mecanica import CONTENEDOR as correlacion_contenedor
    except Exception as e:
        motivo = f"No se pudo importar correlacion_mecanica -> {_detalle_excepcion(e)}"
        _reportar("import_error", motivo)
        return None, motivo

    capacidades = correlacion_contenedor.get("capacidades") or {}
    verificar = capacidades.get("verificar")
    if not callable(verificar):
        motivo = "correlacion_mecanica no expone una capacidad 'verificar' invocable"
        _reportar("capacidad_no_encontrada", motivo)
        return None, motivo

    try:
        resultado = verificar()
    except Exception as e:
        motivo = f"correlacion_mecanica.verificar() fallo -> {_detalle_excepcion(e)}"
        _reportar("error_ejecucion", motivo)
        return None, motivo

    if not isinstance(resultado, dict):
        motivo = (
            "correlacion_mecanica.verificar() devolvio "
            f"{type(resultado).__name__}, se esperaba dict"
        )
        _reportar("salida_invalida", motivo)
        return None, motivo

    if not resultado.get("coherente", False):
        motivo = "correlacion_mecanica reporta INCOHERENCIA: hay choques sin resolver"
        _reportar("orden_incoherente", motivo)
        return None, motivo

    orden = resultado.get("mecanica")
    if not isinstance(orden, list):
        motivo = (
            "correlacion_mecanica se declara coherente pero 'mecanica' es "
            f"{type(orden).__name__}, se esperaba list"
        )
        _reportar("salida_invalida", motivo)
        return None, motivo

    return orden, "ok"


def obtener_orden_ejecucion() -> Optional[List[str]]:
    """
    Orden valido de ejecucion, o None si no lo hay.
    (Firma preservada por compatibilidad; el motivo va al diagnostico.)
    """
    orden, _motivo = _resolver_orden()
    return orden


def ejecutar_modulo(modulo_name: str, capacidad: str, *args, **kwargs) -> Any:
    """Ejecuta una capacidad especifica de un modulo. Devuelve None si falla."""
    try:
        modulo = importlib.import_module(f"modules.{modulo_name}")
    except Exception as e:
        _reportar(
            "import_error",
            f"No se pudo importar modules.{modulo_name} -> {_detalle_excepcion(e)}",
        )
        return None

    contenedor = getattr(modulo, "CONTENEDOR", None)
    if contenedor is None:
        _reportar(
            "sin_contenedor",
            f"modules.{modulo_name} no tiene CONTENEDOR",
        )
        return None

    funcion = (contenedor.get("capacidades") or {}).get(capacidad)
    if not callable(funcion):
        _reportar(
            "capacidad_no_encontrada",
            f"Capacidad '{capacidad}' no encontrada (o no invocable) en {modulo_name}",
        )
        return None

    try:
        return funcion(*args, **kwargs)
    except Exception as e:
        _reportar(
            "error_ejecucion",
            f"Error al ejecutar {modulo_name}/{capacidad} -> {_detalle_excepcion(e)}",
        )
        return None


def ejecutar_sistema() -> Dict[str, Any]:
    """
    Ejecuta los modulos en el orden definido por `correlacion_mecanica/`.

    Retorna:
      {"status": "ok"|"error", "mensaje": str, "resultados": {...},
       "fallidos": [...], "no_planificados": [...], "no_descubiertos": [...]}
    """
    modulos = descubrir_modulos()
    if not modulos:
        mensaje = f"No se encontraron modulos importables en {_MODULES_DIR}"
        _reportar("sin_modulos", mensaje)
        return {"status": "error", "mensaje": mensaje, "resultados": {}}

    orden, motivo = _resolver_orden()
    if orden is None:
        return {
            "status": "error",
            "mensaje": f"No hay orden valido de ejecucion: {motivo}",
            "resultados": {},
        }

    if not orden:
        mensaje = "correlacion_mecanica devolvio un orden VACIO: no hay nada que ejecutar"
        _reportar("orden_vacio", mensaje)
        return {"status": "error", "mensaje": mensaje, "resultados": {}}

    # Modulos descubiertos que nadie planifico: antes se ignoraban en silencio.
    no_planificados = [m for m in sorted(modulos) if m not in orden]
    for modulo_name in no_planificados:
        _reportar(
            "modulo_no_planificado",
            f"El modulo '{modulo_name}' existe en modules/ pero no aparece en el "
            f"orden de correlacion_mecanica: NO se ejecutara",
        )

    resultados: Dict[str, Any] = {}
    no_descubiertos: List[str] = []
    fallidos: List[str] = []

    for modulo_name in orden:
        if modulo_name not in modulos:
            # Mensaje corregido: el modulo SI esta en el orden, lo que falta es el modulo.
            no_descubiertos.append(modulo_name)
            _reportar(
                "modulo_no_descubierto",
                f"El orden exige '{modulo_name}' pero ese modulo no se pudo "
                f"descubrir en modules/ (revisa errores de import previos)",
            )
            continue

        resultado = ejecutar_modulo(modulo_name, "verificar")
        resultados[modulo_name] = resultado

        coherente = bool(resultado.get("coherente", False)) if isinstance(resultado, dict) else False
        if not coherente:
            fallidos.append(modulo_name)

    if no_descubiertos:
        status = "error"
        mensaje = f"Faltan modulos exigidos por el orden: {', '.join(no_descubiertos)}"
    elif fallidos and EXIGIR_MODULOS_COHERENTES:
        status = "error"
        mensaje = f"Modulos incoherentes o sin resultado: {', '.join(fallidos)}"
    else:
        status = "ok"
        mensaje = f"{len(resultados)} modulo(s) ejecutados en orden"

    return {
        "status": status,
        "mensaje": mensaje,
        "resultados": resultados,
        "fallidos": fallidos,
        "no_planificados": no_planificados,
        "no_descubiertos": no_descubiertos,
    }


def obtener_autorizaciones() -> Dict[str, bool]:
    """Qué modulos estan autorizados (verificar -> coherente=True)."""
    modulos = descubrir_modulos()
    autorizaciones: Dict[str, bool] = {}

    for modulo_name in modulos:
        resultado = ejecutar_modulo(modulo_name, "verificar")
        autorizaciones[modulo_name] = (
            bool(resultado.get("coherente", False)) if isinstance(resultado, dict) else False
        )

    return autorizaciones


def barrer() -> Dict[str, Any]:
    """Capacidad de verificacion del Engine: ejecuta el sistema y reporta estado global."""
    resultado = ejecutar_sistema()
    coherente = resultado.get("status") == "ok"
    return {
        "contenedor": _NOMBRE,
        "estado": "APROBADO" if coherente else "RECHAZADO",
        "coherente": coherente,
        "mensaje": resultado.get("mensaje", ""),
        "resultado": resultado,
    }


def arrancar() -> Dict[str, Any]:
    """
    Punto de entrada estricto (CI). Igual que `barrer`, pero si el sistema no
    es coherente lanza ArranqueError con el motivo dentro.
    """
    salida = barrer()
    if not verificar_salida(salida):
        raise ArranqueError(salida.get("mensaje") or "El sistema no es coherente")
    return salida


# ===============================================================
# SEGMENTO 5 --- CENTINELA
# ===============================================================
def verificar_salida(salida: Any) -> bool:
    """Valida la salida del Engine (barrer)."""
    if not isinstance(salida, dict):
        return False
    return bool(salida.get("coherente", False))


# ===============================================================
# SEGMENTO 6 --- CONTENEDOR (contrato final, definido UNA sola vez)
# ===============================================================
CONTENEDOR = {
    "nombre": _NOMBRE,
    "rol": _ROL,
    "version": _VERSION,
    "requiere": [],
    "descripcion": _DESCRIPCION,
    "capacidades": {
        "verificar": barrer,
        "evaluar": barrer,
        "descubrir": descubrir_modulos,
        "ejecutar": ejecutar_sistema,
        "autorizaciones": obtener_autorizaciones,
        "orden": obtener_orden_ejecucion,
        "arrancar": arrancar,
        "validar_salida": verificar_salida,
    },
}

# ===============================================================
# EXPORTACION
# ===============================================================
# Alias de compatibilidad (por si alguien aun importa Engine)
Engine = CONTENEDOR
GlobalEngine = CONTENEDOR

__all__ = [
    "ArranqueError",
    "CONTENEDOR",
    "Engine",
    "GlobalEngine",
    "arrancar",
    "barrer",
    "descubrir_modulos",
    "obtener_orden_ejecucion",
    "ejecutar_modulo",
    "ejecutar_sistema",
    "obtener_autorizaciones",
    "verificar_salida",
]
