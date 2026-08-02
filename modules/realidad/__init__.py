"""
VPSI-TRUTH --- modules/realidad/__init__.py

Rol RE — Contenedor de realidad (contraste con lo establecido / calle).

FUNCIÓN
  Anclar el acceso a representaciones de la realidad (Internet y dominios
  de conocimiento humano) sin calcular Tru_Ri ni Tru_total.
  Descubrir funciones/dominios en la carpeta, velar que no se contradigan
  entre sí, y sostener el contrato de simbiosis con el sistema:

    1. La carpeta/dominio declara su oficio y el O con el que pide evaluación.
    2. Engine aplica la fórmula bajo ese O (libertad contractual, no arbitraria).
    3. El material NO sube solo por haber sido calculado: la carpeta debe
       aprobar o rechazar el resultado.
    4. Este init ve todas las carpetas/archivos del módulo y aplica el
       filtro de no-contradicción entre ellas.
    5. Solo entonces el material puede usarse arriba, con el contexto que
       Engine ya maneja.

NO HACE
  - Calcular C, L, K, Tru_Ri ni Tru_total (eso es CA / FO vía Engine).
  - Elegir “qué es verdad” ni privilegiar instituciones.
  - Guardar el Internet como almacén.
  - Sustituir el visto bueno de cada dominio.

ACCESO
  El canal puro está en acceso.py (abrir, traer bytes, cerrar).
  Los dominios (ciencias, rae, …) usan ese canal, etiquetan material y
  piden evaluación al Engine según su propio contrato de entrada.

El Engine dirige. Este módulo solo expone el contrato RE y el centinela
de coherencia interna del módulo de realidad.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from core.diagnostico import DiagnosticoGlobal
except Exception:  # pragma: no cover
    class DiagnosticoGlobal:  # fallback silencioso
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass

from .acceso import Canal, hay_acceso, hay_dns, HAY_REQUESTS

_DIR = Path(__file__).parent
CLAVES_FUNCION = ("nombre", "hace")

# Estados de material tras el bucle dominio ↔ Engine
ESTADOS_MATERIAL = (
    "pendiente",      # traído, aún no evaluado
    "evaluado",       # Engine devolvió resultado; falta visto bueno del dominio
    "aprobado",       # dominio aprobó tras el cálculo
    "rechazado",      # dominio rechazó
    "bloqueado_re",   # init RE detectó choque entre dominios
)


# ===============================================================
# DESCUBRIMIENTO (lógica interna del contenedor)
# ===============================================================

def _descubrir() -> Dict[str, Dict[str, Any]]:
    """
    Recorre la carpeta (y un nivel de subcarpetas de dominio) y recoge
    lo que cada archivo declara en FUNCION.
    Un archivo sin FUNCION no participa: no declara, no pasa.
    """
    registro: Dict[str, Dict[str, Any]] = {}

    candidatos = list(sorted(_DIR.glob("*.py")))
    # Dominios en subcarpeta (ej. conocimiento_humano/*.py)
    for sub in sorted(_DIR.iterdir()):
        if sub.is_dir() and not sub.name.startswith("_"):
            candidatos.extend(sorted(sub.glob("*.py")))

    for f in candidatos:
        if f.name.startswith("_") or f.name == "__init__.py":
            continue
        # Clave estable relativa al módulo
        try:
            rel = f.relative_to(_DIR)
        except ValueError:
            rel = Path(f.name)
        clave = "realidad_{0}".format(str(rel).replace("/", "_").replace("\\", "_"))
        if clave.endswith(".py"):
            clave = clave[:-3]

        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            registro[str(rel)] = {
                "archivo": str(rel),
                "error": "{0}: {1}".format(type(e).__name__, e),
            }
            continue

        meta = getattr(mod, "FUNCION", None)
        if not isinstance(meta, dict):
            continue

        entrada: Dict[str, Any] = {
            "archivo": str(rel),
            "nombre": meta.get("nombre"),
            "hace": meta.get("hace"),
            "provee": list(meta.get("provee") or []),
        }
        # Contrato de simbiosis (opcional en FUNCION)
        if meta.get("o_evaluacion") is not None:
            entrada["o_evaluacion"] = meta.get("o_evaluacion")
        if meta.get("pide_evaluacion_engine") is not None:
            entrada["pide_evaluacion_engine"] = bool(
                meta.get("pide_evaluacion_engine")
            )
        if meta.get("requiere_aprobacion_dominio") is not None:
            entrada["requiere_aprobacion_dominio"] = bool(
                meta.get("requiere_aprobacion_dominio")
            )
        else:
            # Por defecto: si pide evaluación, exige visto bueno del dominio
            entrada["requiere_aprobacion_dominio"] = bool(
                entrada.get("pide_evaluacion_engine")
            )

        registro[str(rel)] = entrada

    return registro


# ===============================================================
# CENTINELA DEL MÓDULO (no-contradicción entre dominios)
# ===============================================================

def barrer() -> Dict[str, Any]:
    """
    Filtro de paso al Engine. Orquesta la coherencia interna de RE:

    1. Descubre FUNCION en archivos y subcarpetas de dominio.
    2. Exige claves mínimas (nombre, hace).
    3. Unicidad: dos archivos no pueden reclamar el mismo nombre de función.
    4. Contrato de simbiosis: si un dominio pide evaluación al Engine,
       queda registrado que el material no sube sin aprobación del dominio.
    5. Carpeta vacía = vacío legítimo (aún no hay anclas/dominios montados).

    No calcula Tru_total. No aprueba material en nombre de un dominio.
    El Engine solo ejecuta lo que el CONTENEDOR declara.
    """
    hallado = _descubrir()
    choques: List[str] = []
    errores: List[str] = []
    notas: List[str] = []
    dominios_con_simbiosis: List[str] = []

    for archivo, meta in sorted(hallado.items()):
        if "error" in meta:
            errores.append("{0}: {1}".format(archivo, meta["error"]))
            continue
        for clave in CLAVES_FUNCION:
            if not meta.get(clave):
                errores.append(
                    "{0}: FUNCION sin '{1}'".format(archivo, clave)
                )
        if meta.get("pide_evaluacion_engine"):
            dominios_con_simbiosis.append(meta.get("nombre") or archivo)
            if not meta.get("requiere_aprobacion_dominio", True):
                # Contrato roto: pedir cálculo y no exigir visto bueno local
                choques.append(
                    "{0}: pide_evaluacion_engine=True pero "
                    "requiere_aprobacion_dominio=False — "
                    "el material no puede subir solo por el cálculo "
                    "(simbiosis dominio↔Engine)".format(archivo)
                )

    # Unicidad de nombre de función
    por_nombre: Dict[str, List[str]] = {}
    for archivo, meta in sorted(hallado.items()):
        if "error" in meta:
            continue
        n = meta.get("nombre")
        if n:
            por_nombre.setdefault(str(n), []).append(archivo)

    for nombre, archivos in sorted(por_nombre.items()):
        if len(archivos) > 1:
            choques.append(
                "funcion '{0}' reclamada por {1}: "
                "no se sabe cuál responde".format(nombre, archivos)
            )

    if not hallado:
        notas.append("ninguna funcion declarada todavía (vacío legítimo)")

    if dominios_con_simbiosis:
        notas.append(
            "simbiosis activa (piden evaluación a Engine, con aprobación "
            "de dominio): {0}".format(sorted(set(dominios_con_simbiosis)))
        )

    if choques or errores:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="realidad",
                errores=(
                    [{"tipo": "choque", "detalle": c} for c in choques]
                    + [{"tipo": "error", "detalle": e} for e in errores]
                ),
            )
        except Exception:
            pass

    return {
        "contenedor": "realidad",
        "rol": "RE",
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "funciones": sorted(por_nombre),
        "dominios_simbiosis": sorted(set(dominios_con_simbiosis)),
        "estados_material": list(ESTADOS_MATERIAL),
        "notas": notas,
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    """Valida la salida de barrer(): coherente o no."""
    return bool(salida.get("coherente", False))


def inventario(peticion: Any = None) -> Dict[str, Any]:
    """Resumen de funciones/dominios descubiertos y del contrato RE."""
    hallado = _descubrir()
    b = barrer()
    return {
        "contenedor": "realidad",
        "version": "1.1",
        "rol": "RE",
        "funciones": {
            m["nombre"]: m
            for m in hallado.values()
            if m.get("nombre") and "error" not in m
        },
        "coherente": b.get("coherente"),
        "dominios_simbiosis": b.get("dominios_simbiosis"),
        "acceso": {
            "canal": "acceso.Canal",
            "hay_requests": HAY_REQUESTS,
            "hay_acceso": hay_acceso(timeout=2),
        },
        "funcion": (
            "Ancla de contraste con representaciones de la realidad. "
            "Canal (acceso) + dominios que piden evaluación al Engine "
            "bajo su O y solo dejan pasar material con aprobación propia. "
            "Este init vela no-contradicción entre dominios. "
            "No calcula Tru."
        ),
        "contrato_simbiosis": {
            "quien_calcula": "Engine → CA/FO bajo O declarado por el dominio",
            "quien_aprueba_material": "la carpeta/dominio que pidió la evaluación",
            "quien_vela_modulo": "realidad/__init__.barrer (no-contradicción)",
            "material_sin_aprobacion": "no sube",
        },
    }


# ===============================================================
# API de apoyo al bucle dominio ↔ Engine (sin calcular Tru aquí)
# ===============================================================

def registrar_resultado_dominio(
    nombre_dominio: str,
    material_id: str,
    resultado_engine: Dict[str, Any],
    aprobacion_dominio: bool,
) -> Dict[str, Any]:
    """
    Cierra el tramo de simbiosis para un material concreto.

    - resultado_engine: lo que devolvió Engine.evaluar bajo el O del dominio.
    - aprobacion_dominio: True solo si la carpeta acepta ese resultado.

    RE no recalcula. Solo registra el estado contractual del material
    para que arriba no se use lo no aprobado. La no-contradicción global
    del módulo sigue siendo barrer().
    """
    if not nombre_dominio or not material_id:
        return {
            "ok": False,
            "estado": "bloqueado_re",
            "error": "nombre_dominio y material_id son obligatorios",
        }

    if not isinstance(resultado_engine, dict):
        return {
            "ok": False,
            "estado": "bloqueado_re",
            "error": "resultado_engine debe ser dict (salida de Engine)",
        }

    estado = "aprobado" if aprobacion_dominio else "rechazado"
    return {
        "ok": True,
        "estado": estado,
        "nombre_dominio": nombre_dominio,
        "material_id": material_id,
        "aprobacion_dominio": bool(aprobacion_dominio),
        "resultado_engine_presente": True,
        "nota": (
            "Material {0} por dominio '{1}'. "
            "Sin aprobación del dominio el material no debe usarse arriba. "
            "barrer() sigue velando choques entre dominios del módulo."
        ).format(estado, nombre_dominio),
    }


# ===============================================================
# CONTENEDOR (contrato con Engine — al final)
# ===============================================================

CONTENEDOR = {
    "nombre": "realidad",
    "rol": "RE",
    "version": "1.1",
    "requiere": [],
    "descripcion": (
        "Contenedor de realidad (RE). Ancla de contraste con representaciones "
        "de la realidad y dominios de conocimiento humano. "
        "Canal de acceso (acceso.py) + dominios que declaran su oficio y el O "
        "con el que piden evaluación a Engine. "
        "Simbiosis: Engine aplica la fórmula bajo ese O; el material solo sube "
        "si el dominio aprueba el resultado; este init vela no-contradicción "
        "entre todas las funciones/carpetas del módulo. "
        "No calcula Tru_Ri ni Tru_total. No privilegia instituciones. "
        "El Engine no tiene poder propio: ejecuta solo lo que este contrato "
        "y los contratos de dominio declaran."
    ),
    "capacidades": {
        "verificar": barrer,
        "inventario": inventario,
        "registrar_resultado_dominio": registrar_resultado_dominio,
    },
}


# ===============================================================
# EXPORTACIÓN
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "Canal",
    "hay_acceso",
    "hay_dns",
    "HAY_REQUESTS",
    "barrer",
    "inventario",
    "verificar_salida",
    "registrar_resultado_dominio",
    "ESTADOS_MATERIAL",
]
