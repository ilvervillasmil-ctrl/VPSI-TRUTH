# conocimiento_humano

Categoría de **contraste con representaciones del saber humano** dentro del módulo `realidad` (RE).

No es un segundo motor de verdad.  
No calcula Tru.  
No guarda Internet.  
No afirma que una fuente “sea” la realidad.

Es la carpeta donde viven los **contratos de disciplina**: física, matemáticas, léxico, medicina, etc. Cada archivo declara un oficio y un O de evaluación. El material que entra por Internet solo sube si sobrevive al bucle de simbiosis con el sistema.

---

## Dónde está

```text
modules/realidad/
├── __init__.py              ← centinela RE (único filtro del módulo)
├── acceso.py                ← canal HTTP (bytes; sin juicio)
├── _base_dominio.py         ← utilidades compartidas (sin FUNCION)
└── conocimiento_humano/     ← ESTA carpeta
    ├── README.md            ← este documento
    ├── matematicas.py
    ├── logica.py
    ├── fisica.py
    ├── lexico.py
    └── …                    ← una disciplina = un archivo


## Plantilla de archivo (borrador)

Todo archivo nuevo en esta carpeta debe seguir este formato.  
Copiar, renombrar y rellenar solo los campos marcados.

```python
"""
VPSI-TRUTH --- modules/realidad/conocimiento_humano/<NOMBRE_ARCHIVO>.py

Disciplina: <NOMBRE> (categoría conocimiento_humano / bloque <BLOQUE>).

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
    "nombre": "<NOMBRE>",
    "hace": (
        "Traer y etiquetar <DESCRIPCION_DEL_MATERIAL>; "
        "pedir evaluación a Engine bajo el O de esta disciplina; "
        "aprobar o rechazar el material antes de que suba."
    ),
    "provee": [
        "material_etiquetado_<NOMBRE>",
        "peticion_evaluacion_engine",
        "aprobacion_dominio",
    ],
    "categoria": "conocimiento_humano",
    "bloque": "<BLOQUE>",
    "pide_evaluacion_engine": True,
    "requiere_aprobacion_dominio": True,
    "o_evaluacion": (
        "<ENUNCIADO_O_DE_ESTA_DISCIPLINA>. "
        "Candidato a K bajo este O; no es ancla de R."
    ),
}

DOMINIO = "<NOMBRE>"
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
