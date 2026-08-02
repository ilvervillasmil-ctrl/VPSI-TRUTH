"""
VPSI-TRUTH --- modules/interfaz

Rol UI: diseño de presentación.

- Observa pedido de interfaz + evidencia legible (p. ej. CACHE).
- Compone descripciones de diseño (layout, zonas, superficies).
- Inventaria y admite paquetes de herramientas bajo paquetes/.
- Vela la coherencia de SUS propios archivos (centinela de carpeta).
- No calcula Tru. No escribe C/L/K. No orquesta el ciclo.
- Salida de diseño auditable por Centinela de core.

La actualización de herramientas = nuevos paquetes descubiertos bajo
paquetes/, no reescritura opaca del contrato.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ===============================================================
# CONTENEDOR (contrato Engine)
# ===============================================================
CONTENEDOR = {
    "nombre": "interfaz",
    "rol": "UI",
    "version": "1.0",
    "requiere": [],  # lectura de CH es opcional en runtime, no bloquea arranque
    "descripcion": (
        "Diseño de presentación del sistema. Compone descripciones de "
        "interfaz bajo un pedido explícito y lo observable (CACHE). "
        "Cero actuación sobre evaluación. Paquetes de diseño actualizables "
        "bajo paquetes/. Alcance: superficies web/desktop/mobile/cli y "
        "empaquetado multi-dispositivo como previsión de contrato."
    ),
    "capacidades": {
        "verificar": "barrer",
        "barrer": "barrer",
        "componer": "componer",
        "inventario": "inventario",
        "inventario_paquetes": "inventario_paquetes",
        "observar": "observar",
        "axiomas": "axiomas",
    },
    "prohibiciones": [
        "calcular_o_modificar_C_L_K_Tru",
        "orquestar_ciclo_Engine",
        "aprobar_su_propia_salida_de_diseno",  # Centinela / Engine
        "inventar_controles_sin_componente_o_capacidad_real",
        "ocultar_estado_indefinido_como_OK",
    ],
    "alcance": {
        "superficies": ["web", "desktop", "mobile", "cli", "embebido"],
        "paquetes_dir": "paquetes",
        "actualizacion_herramientas": (
            "descubrimiento de subcarpetas/manifiestos en paquetes/; "
            "versionado por manifiesto; sin congelar un kit único"
        ),
        "empaquetado": (
            "contempla especificación de UI + runtime de superficie para "
            "distribución en PC/teléfono/web; el build concreto es fase posterior"
        ),
        "auditoria": "salida de componer() es paquete verificable por Centinela",
    },
}

_DIR = Path(__file__).parent
_PAQUETES = _DIR / "paquetes"

SUPERFICIES_ADMITIDAS = tuple(CONTENEDOR["alcance"]["superficies"])


# ===============================================================
# Centinela de carpeta — coherencia interna del módulo
# ===============================================================
def _leer_manifiesto(ruta: Path) -> Optional[Dict[str, Any]]:
    for nombre in ("manifiesto.json", "manifest.json", "paquete.json"):
        f = ruta / nombre
        if f.is_file():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else None
            except Exception:
                return {"_error": f"manifiesto ilegible: {f.name}"}
    # paquete mínimo: carpeta con __init__.py o README de diseño
    if (ruta / "__init__.py").is_file() or any(ruta.glob("*.py")):
        return {
            "id": ruta.name,
            "nombre": ruta.name,
            "version": "0.0",
            "superficie": ["web"],
            "implicit": True,
        }
    return None


def _descubrir_paquetes() -> Dict[str, Dict[str, Any]]:
    hallado: Dict[str, Dict[str, Any]] = {}
    if not _PAQUETES.is_dir():
        return hallado
    for child in sorted(_PAQUETES.iterdir()):
        if not child.is_dir() or child.name.startswith(("_", ".")):
            continue
        meta = _leer_manifiesto(child)
        if meta is None:
            hallado[child.name] = {
                "id": child.name,
                "error": "sin manifiesto ni código de paquete",
                "ruta": str(child),
            }
            continue
        if meta.get("_error"):
            hallado[child.name] = {
                "id": child.name,
                "error": meta["_error"],
                "ruta": str(child),
            }
            continue
        pid = str(meta.get("id") or child.name)
        hallado[pid] = {
            "id": pid,
            "nombre": meta.get("nombre") or child.name,
            "version": str(meta.get("version") or "0.0"),
            "superficies": list(
                meta.get("superficies") or meta.get("superficie") or ["web"]
            ),
            "componentes": list(meta.get("componentes") or []),
            "ruta": str(child),
            "implicit": bool(meta.get("implicit")),
        }
    return hallado


def _detectar_choques_paquetes(
    paquetes: Dict[str, Dict[str, Any]],
) -> List[str]:
    choques: List[str] = []
    ids = list(paquetes.keys())
    # id duplicado por nombre de carpeta vs id de manifiesto ya unificado en dict
    for pid, meta in paquetes.items():
        if meta.get("error"):
            choques.append(f"paquete '{pid}': {meta['error']}")
            continue
        for s in meta.get("superficies") or []:
            if s not in SUPERFICIES_ADMITIDAS:
                choques.append(
                    f"paquete '{pid}': superficie no admitida {s!r} "
                    f"(admitidas: {SUPERFICIES_ADMITIDAS})"
                )
        # componentes no pueden invocar evaluación
        for c in meta.get("componentes") or []:
            cl = str(c).lower()
            if any(
                x in cl
                for x in (
                    "tru_total",
                    "tru_ri",
                    "escribir_k",
                    "set_c",
                    "set_l",
                    "forzar_ok",
                )
            ):
                choques.append(
                    f"paquete '{pid}': componente sospechoso de actuación "
                    f"sobre evaluación: {c!r}"
                )
    return choques


def barrer() -> Dict[str, Any]:
    """
    Verificador del módulo (centinela de carpeta).
    No valida Tru; valida coherencia de paquetes y contrato UI.
    """
    paquetes = _descubrir_paquetes()
    choques = _detectar_choques_paquetes(paquetes)
    errores: List[str] = []

    if not _PAQUETES.exists():
        # vacío legítimo en fase: se puede crear la carpeta después
        errores.append(
            "paquetes/ aún no existe (vacío legítimo hasta montar herramientas)"
        )

    limpio = len(choques) == 0  # errores de “aún no existe” no tumba coherencia dura
    # política: sin choques de manifiesto → coherente; aviso de carpeta ausente es nota
    coherente = len(choques) == 0

    return {
        "contenedor": CONTENEDOR["nombre"],
        "rol": CONTENEDOR["rol"],
        "coherente": coherente,
        "choques": choques,
        "errores": errores,
        "paquetes_n": len(paquetes),
        "paquetes": sorted(paquetes.keys()),
        "superficies_admitidas": list(SUPERFICIES_ADMITIDAS),
        "prohibiciones": list(CONTENEDOR["prohibiciones"]),
    }


# ===============================================================
# Observación (solo lectura)
# ===============================================================
def observar(
    pedido: Optional[Dict[str, Any]] = None,
    cache_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Reúne lo que el diseñador puede ver: pedido + evidencia CACHE (si se inyecta).
    No escribe en CACHE. No llama a FO/CA.
    """
    pedido = dict(pedido or {})
    snap = dict(cache_snapshot or {})
    return {
        "pedido": {
            "O_uso": pedido.get("O_uso")
            or pedido.get("contexto")
            or pedido.get("enunciado")
            or pedido.get("descripcion"),
            "superficie": pedido.get("superficie") or "web",
            "zonas_solicitadas": list(
                pedido.get("zonas") or pedido.get("paneles") or []
            ),
            "restricciones": list(pedido.get("restricciones") or []),
        },
        "evidencia_cache": {
            "disponible": bool(snap),
            "claves": sorted(snap.keys()) if snap else [],
            "ciclo_id": snap.get("ciclo_id"),
            "estado_sistema": snap.get("estado") or snap.get("estado_engine"),
        },
        "nota": (
            "Observación de solo lectura. El diseño depende del pedido; "
            "sin O_uso claro la composición queda PARCIAL."
        ),
    }


# ===============================================================
# Composición de diseño (descripción, no runtime gráfico)
# ===============================================================
_ZONAS_CANONICAS = (
    "contexto",          # casilla O / entrada natural
    "estado_marco",      # estable|indefinido|cambio, permite_k
    "reporte_simple",
    "reporte_detalle",
    "sistema",           # Engine/AX/MC/DG
    "centinela",         # veredicto si existe
    "correlacion",       # vista de orden MC si se solicita
)


def componer(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Genera descripción de interfaz (esquema), no un binario.

    peticion típica:
      {
        "O_uso": "auditoría de conversación con casilla de contexto",
        "superficie": "web",
        "zonas": ["contexto", "reporte_simple", "reporte_detalle", "centinela"],
        "layout": "1x4",
        "cache_snapshot": {...}  # opcional
      }
    """
    peticion = dict(peticion or {})
    obs = observar(peticion, peticion.get("cache_snapshot"))
    o_uso = obs["pedido"]["O_uso"]
    superficie = obs["pedido"]["superficie"]
    if superficie not in SUPERFICIES_ADMITIDAS:
        return {
            "estado": "RETENIDO",
            "razon": f"superficie no admitida: {superficie!r}",
            "esquema": None,
            "auditable_por_centinela": True,
        }

    if not o_uso or not str(o_uso).strip():
        return {
            "estado": "PARCIAL",
            "razon": "sin O_uso / pedido de diseño: no se inventa la casa",
            "observacion": obs,
            "esquema": None,
            "auditable_por_centinela": True,
        }

    zonas_req = obs["pedido"]["zonas_solicitadas"] or list(_ZONAS_CANONICAS[:4])
    zonas: List[Dict[str, Any]] = []
    for z in zonas_req:
        zid = str(z)
        if zid not in _ZONAS_CANONICAS:
            # zona desconocida: se declara pero se marca para Centinela
            zonas.append({
                "id": zid,
                "canonica": False,
                "aviso": "zona no canónica: Centinela debe validar mapeo",
            })
        else:
            zonas.append({
                "id": zid,
                "canonica": True,
                "actuacion_evaluacion": False,
            })

    layout = peticion.get("layout") or "1x4"
    paquetes = _descubrir_paquetes()
    paquetes_ok = {
        k: v for k, v in paquetes.items() if not v.get("error")
    }

    esquema = {
        "tipo": "descripcion_interfaz",
        "version": "1.0",
        "O_uso": str(o_uso).strip(),
        "superficie": superficie,
        "layout": layout,
        "zonas": zonas,
        "paquetes_aplicables": [
            pid
            for pid, meta in paquetes_ok.items()
            if superficie in (meta.get("superficies") or [])
        ],
        "prohibido_en_ui": list(CONTENEDOR["prohibiciones"]),
        "mapeo_mecanismo": {
            "contexto": "modules.contexto.resolver / entrada_natural",
            "estado_marco": "registro CX permite_k",
            "reporte_simple": "salida Engine resumida",
            "reporte_detalle": "factores + tru + ids (cuando existan)",
            "sistema": "Engine.censar / DG.censo",
            "centinela": "core.centinela.verificar",
            "correlacion": "MC inventario / orden (solo lectura)",
        },
    }

    return {
        "estado": "PROPUESTO",
        "observacion": obs,
        "esquema": esquema,
        "barrido_local": barrer(),
        "auditable_por_centinela": True,
        "nota": (
            "Descripción de diseño únicamente. "
            "No aprueba salida de negocio ni modifica evaluación. "
            "Centinela debe verificar este paquete antes de adoptar la UI."
        ),
    }


# ===============================================================
# Inventarios
# ===============================================================
def inventario_paquetes() -> Dict[str, Any]:
    paquetes = _descubrir_paquetes()
    return {
        "dir": str(_PAQUETES),
        "n": len(paquetes),
        "paquetes": paquetes,
        "actualizacion": CONTENEDOR["alcance"]["actualizacion_herramientas"],
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    return {
        "contenedor": CONTENEDOR["nombre"],
        "rol": CONTENEDOR["rol"],
        "version": CONTENEDOR["version"],
        "superficies": list(SUPERFICIES_ADMITIDAS),
        "zonas_canónicas": list(_ZONAS_CANONICAS),
        "paquetes": inventario_paquetes(),
        "alcance": dict(CONTENEDOR["alcance"]),
        "prohibiciones": list(CONTENEDOR["prohibiciones"]),
        "funcion": (
            "Diseña descripciones de interfaz correlacionadas al mecanismo; "
            "vela sus paquetes; no calcula Tru."
        ),
    }


def axiomas() -> List[Dict[str, Any]]:
    """Declaraciones operativas del módulo (no sustituyen un cuerpo UI_AX futuro)."""
    return [
        {
            "id": "UI-OP-1",
            "tipo": "axioma",
            "sujeto": "modulo_interfaz",
            "relacion": "compone_descripcion_y_no_calcula",
            "objeto": "Tru_ni_factores",
            "polaridad": True,
            "enunciado": (
                "El módulo interfaz compone descripciones de presentación; "
                "no calcula ni modifica C, L, K ni Tru."
            ),
            "depende_de": [],
            "gobierna": ["interfaz"],
        },
        {
            "id": "UI-OP-2",
            "tipo": "axioma",
            "sujeto": "composicion_de_interfaz",
            "relacion": "exige",
            "objeto": "pedido_O_uso_explicito",
            "polaridad": True,
            "enunciado": (
                "Sin pedido de diseño (O_uso) no se inventa la interfaz completa; "
                "estado PARCIAL."
            ),
            "depende_de": [],
            "gobierna": ["interfaz"],
        },
        {
            "id": "UI-OP-3",
            "tipo": "axioma",
            "sujeto": "paquetes_de_diseno",
            "relacion": "deben",
            "objeto": "pasar_barrido_local_sin_actuacion_evaluacion",
            "polaridad": True,
            "enunciado": (
                "Los paquetes bajo interfaz/paquetes/ no pueden declarar "
                "componentes de actuación sobre evaluación; el init los barre."
            ),
            "depende_de": [],
            "gobierna": ["interfaz"],
        },
        {
            "id": "UI-OP-4",
            "tipo": "axioma",
            "sujeto": "salida_de_componer",
            "relacion": "es",
            "objeto": "auditable_por_Centinela",
            "polaridad": True,
            "enunciado": (
                "Toda descripción de interfaz es paquete verificable por "
                "Centinela antes de adoptarse como UI admisible."
            ),
            "depende_de": [],
            "gobierna": ["interfaz"],
        },
    ]


__all__ = [
    "CONTENEDOR",
    "SUPERFICIES_ADMITIDAS",
    "barrer",
    "observar",
    "componer",
    "inventario",
    "inventario_paquetes",
    "axiomas",
]
