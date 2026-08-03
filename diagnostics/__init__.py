"""
VPSI-TRUTH --- modules/diagnostics/__init__.py

Contenedor de diagnóstico. Rol DG.

Omega Report no calcula. Solo recibe los informes reales que el Engine
ya obtuvo de cada módulo y los presenta de forma objetiva.

Contrato:
  - No recalcula C, L, K, Tru_Ri ni Tru_total.
  - No vuelve a barrer axiomas ni mecánica.
  - Solo valida que los datos recibidos sean completos y consistentes
    con lo que el sistema ya produjo.
  - Puede leer evidencia persistente (diagnostics/evaluaciones.json)
    sin modificarla.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ===============================================================
# CONTENEDOR (Contrato del módulo)
# ===============================================================
# capacidades se rellenan al final con callables reales
CONTENEDOR: Dict[str, Any] = {
    "nombre": "diagnostics",
    "rol": "DG",
    "version": "1.1",
    "requiere": ["CT", "AX", "FO"],
    "descripcion": (
        "Contenedor de diagnóstico. Rol DG. "
        "Recibe los informes reales producidos por el Engine y los módulos "
        "y genera el Omega Report sin recalcular nada. "
        "Lee evidencia persistente si existe; no la escribe."
    ),
    "capacidades": {},  # se asigna al final
}


# ===============================================================
# ERRORES
# ===============================================================
class DiagnosticoError(Exception):
    """Error en la capa de diagnóstico."""
    pass


class EntradaIncompletaError(DiagnosticoError):
    """Faltan informes obligatorios para generar el reporte."""
    pass


# ===============================================================
# LO QUE EL MÓDULO EXIGE RECIBIR DEL ENGINE
# ===============================================================
CAMPOS_OBLIGATORIOS = (
    "estado_engine",          # OPERATIVO | RECHAZADO | NO_INICIADO
    "constantes",             # {"ALPHA": ..., "BETA": ...}
    "informe_axiomas",        # salida de axiomas.barrer()
    "resultados_evaluacion",  # lista de engine.evaluar() si las hubo
)

CAMPOS_OPCIONALES = (
    "informe_formulas",
    "informe_mecanica",
    "informe_self",
    "errores_arranque",
    "registro_modulos",
    "tests",
    "contratos",
    "citacion",
    "taxonomia",
)


def validar_entrada(datos: Dict[str, Any]) -> List[str]:
    """
    Verifica que el Engine haya pasado la información mínima real.
    No recalcula nada. Solo comprueba presencia y forma.
    """
    faltas: List[str] = []

    if not isinstance(datos, dict):
        return ["entrada no es dict"]

    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos:
            faltas.append("falta campo obligatorio: {0}".format(campo))

    if "constantes" in datos:
        c = datos["constantes"]
        if not isinstance(c, dict) or "ALPHA" not in c or "BETA" not in c:
            faltas.append("constantes debe contener ALPHA y BETA")

    if "informe_axiomas" in datos:
        ia = datos["informe_axiomas"]
        if not isinstance(ia, dict):
            faltas.append("informe_axiomas debe ser dict")
        elif "coherente" not in ia:
            faltas.append("informe_axiomas sin clave 'coherente'")

    if "estado_engine" in datos:
        if datos["estado_engine"] not in ("OPERATIVO", "RECHAZADO", "NO_INICIADO"):
            faltas.append(
                "estado_engine invalido: {0}".format(datos["estado_engine"])
            )

    if "resultados_evaluacion" in datos:
        if not isinstance(datos["resultados_evaluacion"], list):
            faltas.append("resultados_evaluacion debe ser list")

    return faltas


# ===============================================================
# LECTURA DE EVIDENCIA PERSISTENTE (solo lectura)
# ===============================================================
def _ruta_evaluaciones() -> Path:
    """
    diagnostics/ en la raiz del repo (donde CI y tests depositan).
    No es modules/diagnostics/.
    """
    # modules/diagnostics/__init__.py -> parents[2] = raiz del repo
    raiz = Path(__file__).resolve().parents[2]
    return raiz / "diagnostics" / "evaluaciones.json"


def leer_evidencia() -> Dict[str, Any]:
    """
    Lee diagnostics/evaluaciones.json si existe.
    No escribe. No fusiona. Solo lectura para el reporte.
    """
    vacio: Dict[str, Any] = {
        "tipo": "evidencia_evaluacion",
        "version": None,
        "origen": None,
        "origenes": [],
        "n": 0,
        "resultados": [],
    }
    ruta = _ruta_evaluaciones()
    if not ruta.exists():
        return vacio
    try:
        doc = json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return vacio
    if not isinstance(doc, dict) or not isinstance(doc.get("resultados"), list):
        return vacio
    return doc


def _extraer_factores(entrada: Any) -> Dict[str, Any]:
    """
    Normaliza una fila de evaluacion a C/L/K/Tru_Ri/Tru_total/estado.
    No calcula: solo lee claves ya presentes.
    """
    if not isinstance(entrada, dict):
        return {
            "C": None, "L": None, "K": None,
            "Tru_Ri": None, "Tru_total": None,
            "estado": None, "taxonomia": None, "citas": None,
        }

    # puede venir anidado en "resultado" o plano
    r = entrada.get("resultado") if isinstance(entrada.get("resultado"), dict) else entrada

    def _get(*claves):
        for k in claves:
            if k in r and r[k] is not None:
                return r[k]
            if k in entrada and entrada[k] is not None:
                return entrada[k]
        return None

    return {
        "C": _get("C", "c"),
        "L": _get("L", "l"),
        "K": _get("K", "k"),
        "Tru_Ri": _get("Tru_Ri", "tru_ri", "TruRi"),
        "Tru_total": _get("Tru_total", "tru_total", "TruTotal"),
        "estado": _get("estado", "state"),
        "taxonomia": _get("taxonomia", "taxonomia_tx", "TX"),
        "citas": _get("citas", "citacion", "ids_cx_relevantes", "teoremas"),
    }


def _bloque_calculo(titulo: str, factores: Dict[str, Any]) -> Dict[str, Any]:
    """Bloque de presentacion. No calcula."""
    return {
        "titulo": titulo,
        "C": factores.get("C"),
        "L": factores.get("L"),
        "K": factores.get("K"),
        "Tru_Ri": factores.get("Tru_Ri"),
        "Tru_total": factores.get("Tru_total"),
        "estado": factores.get("estado"),
        "taxonomia": factores.get("taxonomia") if factores.get("taxonomia") is not None else "none",
        "citas": factores.get("citas"),
    }


def _resumen_evaluaciones(evaluaciones: List[Any]) -> Dict[str, Any]:
    """
    Separa:
      - auditoria del sistema (origen ci / sin origen de test)
      - ultimo test (ultimo con origen test_* o el ultimo de la lista)
    No calcula valores nuevos.
    """
    if not evaluaciones:
        return {
            "sistema": _bloque_calculo("Auditoria del VPSI", {}),
            "ultimo_test": _bloque_calculo("Ultimo test", {}),
            "n": 0,
            "origenes": [],
        }

    origenes = sorted({
        str(e.get("origen"))
        for e in evaluaciones
        if isinstance(e, dict) and e.get("origen")
    })

    # sistema: preferir filas de ci_auditoria / sin test_
    sistema_filas = [
        e for e in evaluaciones
        if isinstance(e, dict)
        and not str(e.get("origen") or "").startswith("test_")
    ]
    if not sistema_filas:
        sistema_filas = [evaluaciones[0]] if evaluaciones else []

    # ultimo test: ultima fila con origen test_* o la ultima de la lista
    test_filas = [
        e for e in evaluaciones
        if isinstance(e, dict)
        and str(e.get("origen") or "").startswith("test_")
    ]
    ultimo = test_filas[-1] if test_filas else (evaluaciones[-1] if evaluaciones else {})

    # para "sistema" tomamos la ultima fila de sistema con factores si hay
    sistema_ref = sistema_filas[-1] if sistema_filas else {}

    return {
        "sistema": _bloque_calculo(
            "Auditoria del VPSI",
            _extraer_factores(sistema_ref),
        ),
        "ultimo_test": _bloque_calculo(
            "Ultimo test",
            _extraer_factores(ultimo),
        ),
        "n": len(evaluaciones),
        "origenes": origenes,
    }


# ===============================================================
# GENERACIÓN DEL REPORTE (solo presentación)
# ===============================================================
def generar_reporte(
    datos: Dict[str, Any],
    salida: Optional[Path] = None,
    incluir_evidencia: bool = True,
) -> Dict[str, Any]:
    """
    Genera el Omega Report a partir de los datos reales del Engine
    y, si existe, de la evidencia persistente.

    No ejecuta barrer(), no llama a tru_ri/tru_total, no recalcula nada.
    Solo lee y formatea.
    """
    faltas = validar_entrada(datos)
    if faltas:
        raise EntradaIncompletaError(
            "No se puede generar Omega Report. Faltan datos reales del sistema:\n  - "
            + "\n  - ".join(faltas)
        )

    # evaluaciones en memoria (Engine)
    evals_memoria = list(datos.get("resultados_evaluacion") or [])

    # evidencia persistente (tests + CI)
    evidencia = leer_evidencia() if incluir_evidencia else {
        "n": 0, "resultados": [], "origenes": [],
    }
    evals_disco = list(evidencia.get("resultados") or [])

    # union: memoria primero, luego disco (sin recalcular)
    # si hay solapamiento de secuencia, se mantienen ambas etiquetadas por origen
    todas = evals_memoria + evals_disco

    resumen = _resumen_evaluaciones(todas)

    reporte: Dict[str, Any] = {
        "titulo": "OMEGA REPORT - VPSI-TRUTH",
        "version_dg": CONTENEDOR["version"],
        "generado": datetime.now(timezone.utc).isoformat(),
        "estado_engine": datos["estado_engine"],
        "constantes": datos["constantes"],
        "axiomas": {
            "coherente": datos["informe_axiomas"].get("coherente"),
            "declaraciones": datos["informe_axiomas"].get("declaraciones"),
            "choques": len(datos["informe_axiomas"].get("choques") or []),
            "errores": len(datos["informe_axiomas"].get("errores") or []),
        },
        "formulas": datos.get("informe_formulas"),
        "mecanica": datos.get("informe_mecanica"),
        "contratos": datos.get("contratos"),
        # bloque principal pedido
        "calculo_sistema": resumen["sistema"],
        "calculo_ultimo_test": resumen["ultimo_test"],
        "evaluaciones": {
            "n": resumen["n"],
            "origenes": resumen["origenes"],
            "memoria_n": len(evals_memoria),
            "disco_n": len(evals_disco),
            "filas": todas,
        },
        "evidencia_persistente": {
            "path": str(_ruta_evaluaciones()),
            "n": evidencia.get("n", 0),
            "origenes": evidencia.get("origenes") or [],
            "version": evidencia.get("version"),
        },
        "errores_arranque": datos.get("errores_arranque") or [],
        "modulos": datos.get("registro_modulos"),
        "tests": datos.get("tests"),
        "citacion": datos.get("citacion"),
        "taxonomia": datos.get("taxonomia"),
        "valido": datos["estado_engine"] == "OPERATIVO",
    }

    if salida is not None:
        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(
            json.dumps(reporte, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    return reporte


# ===============================================================
# VERIFICACIÓN DEL MÓDULO (contrato)
# ===============================================================
def verificar(datos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Capacidad de verificacion del contenedor DG.
    Si se pasan datos, valida que sean suficientes para un reporte objetivo.
    """
    if datos is None:
        return {
            "contenedor": CONTENEDOR["nombre"],
            "estado": "APROBADO",
            "coherente": True,
            "mensaje": "Modulo DG listo. Esperando datos reales del Engine.",
            "evidencia_disponible": _ruta_evaluaciones().exists(),
        }

    faltas = validar_entrada(datos)
    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": "APROBADO" if not faltas else "RECHAZADO",
        "coherente": not faltas,
        "faltas": faltas,
        "evidencia_disponible": _ruta_evaluaciones().exists(),
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "rol": CONTENEDOR["rol"],
        "requiere": list(CONTENEDOR["requiere"]),
        "campos_obligatorios": list(CAMPOS_OBLIGATORIOS),
        "campos_opcionales": list(CAMPOS_OPCIONALES),
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "evidencia_path": str(_ruta_evaluaciones()),
    }


# ===============================================================
# CONTENEDOR — capacidades como callables (patron del resto del repo)
# ===============================================================
CONTENEDOR["capacidades"] = {
    "verificar": verificar,
    "inventario": inventario,
    "generar_reporte": generar_reporte,
    "validar_entrada": validar_entrada,
    "leer_evidencia": leer_evidencia,
}


# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "verificar",
    "inventario",
    "generar_reporte",
    "validar_entrada",
    "leer_evidencia",
    "DiagnosticoError",
    "EntradaIncompletaError",
    "CAMPOS_OBLIGATORIOS",
    "CAMPOS_OPCIONALES",
]
