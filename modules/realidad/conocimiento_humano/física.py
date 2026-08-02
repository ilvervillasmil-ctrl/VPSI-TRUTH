"""
VPSI-TRUTH --- modules/realidad/conocimiento_humano/fisica.py

Disciplina: fisica (categoría conocimiento_humano / bloque naturales).

Contrato de simbiosis (realidad/__init__.py):
  - Trae y etiqueta material vía acceso.Canal.
  - Pide evaluación a Engine bajo SU O.
  - Solo deja pasar material con aprobación de este dominio.
  - No calcula C, L, K ni Tru. No afirma R.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.realidad._base_dominio import (
    aprobar_por_defecto,
    filtrar_lote as _filtrar_lote,
    peticion_evaluacion_engine,
    traer_url,
)

# ===============================================================
# CONTRATO DE DOMINIO (descubierto por realidad/__init__)
# ===============================================================

FUNCION = {
    "nombre": "fisica",
    "hace": (
        "Traer y etiquetar material de física (teorías, experimentos, constantes, modelos); "
        "pedir evaluación a Engine bajo el O de esta disciplina; "
        "aprobar o rechazar el material antes de que suba."
    ),
    "provee": [
        "material_etiquetado_fisica",
        "peticion_evaluacion_engine",
        "aprobacion_dominio",
    ],
    "categoria": "conocimiento_humano",
    "bloque": "naturales",
    "pide_evaluacion_engine": True,
    "requiere_aprobacion_dominio": True,
    "o_evaluacion": (
        "Contraste de material de física: teorías, datos experimentales y modelos. "
        "Candidato a K bajo este O; no es ancla de R."
    ),
}

DOMINIO = "fisica"
O_EVALUACION = FUNCION["o_evaluacion"]


# ===============================================================
# OFICIO
# ===============================================================

def traer(
    url: str,
    *,
    tipo: str = "recurso",
    metadatos: Optional[Dict[str, Any]] = None,
    canal: Any = None,
) -> Dict[str, Any]:
    return traer_url(
        dominio=DOMINIO,
        url=url,
        tipo=tipo,
        metadatos=metadatos,
        canal=canal,
    )


def armar_peticion_engine(material: Dict[str, Any]) -> Dict[str, Any]:
    return peticion_evaluacion_engine(
        dominio=DOMINIO,
        material=material,
        o_evaluacion=O_EVALUACION,
        modo_entrada="auditoria",
    )


def aprobar_material(
    material: Dict[str, Any],
    resultado_engine: Dict[str, Any],
    *,
    aprobar: Optional[bool] = None,
    motivo: str = "",
) -> Dict[str, Any]:
    return aprobar_por_defecto(
        material,
        resultado_engine,
        aprobar=aprobar,
        motivo=motivo,
    )


def filtrar_lote(
    materiales: List[Dict[str, Any]],
    resultados_por_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    return _filtrar_lote(DOMINIO, materiales, resultados_por_id)
