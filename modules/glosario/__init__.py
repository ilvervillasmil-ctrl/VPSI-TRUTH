"""
modules/glosario/__init__.py
============================

Rol GL — Glosario interno del repositorio.

FUNCIÓN
  Reutiliza literalmente lo que el repositorio ya declara
  (contenedores, roles, contratos, axiomas, capacidades)
  para armar el léxico interno del sistema.

  No inventa entradas. No mantiene listas manuales de términos.
  Lo que el repo declara, entra. Lo que no está declarado, no se fabrica.

  Preparado para roles y contratos nuevos: el descubrimiento es
  estructural. Al agregar un módulo con CONTENEDOR (o axiomas),
  queda disponible sin editar este init.

  El resultado puede depositarse en caché para consulta posterior
  sin re-recorrer el árbol.

NO HACE
  - Calcular C, L, K, Tru.
  - Clasificar O_context.
  - Sustituir el diccionario de idiomas (eso es DI / fuentes de idioma).
  - Escribir a mano el contenido del léxico interno.

-------------------------------------------------------------------------------
NOTA DE AUTOR — Ilver Villasmil
-------------------------------------------------------------------------------
El glosario no se inventa. Se deriva de lo que el repositorio ya sostiene.
Así no se introducen términos ajenos a la coherencia del sistema.

— I.V.
-------------------------------------------------------------------------------
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from core.diagnostico import DiagnosticoGlobal
except Exception:  # pragma: no cover
    class DiagnosticoGlobal:
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass

VERSION = "1.0"

_DIR = Path(__file__).parent
_MODULES_ROOT = _DIR.parent  # modules/

_LEXICO: Dict[str, Dict[str, Any]] = {}
_CARGADO = False


# ===============================================================
# DESCUBRIMIENTO — reutiliza lo declarado en el repositorio
# ===============================================================
def _iter_modulos() -> List[str]:
    """
    Nombres de paquetes bajo modules/.
    No hay lista fija: un rol nuevo con carpeta propia entra solo.
    """
    nombres = []
    if not _MODULES_ROOT.is_dir():
        return nombres
    for p in sorted(_MODULES_ROOT.iterdir()):
        if not p.is_dir():
            continue
        if p.name.startswith("_") or p.name == "glosario":
            continue
        if (p / "__init__.py").is_file():
            nombres.append(p.name)
    return nombres


def _cargar_paquete(nombre: str) -> Optional[Any]:
    try:
        return importlib.import_module("modules.{0}".format(nombre))
    except Exception:
        return None


def _extraer_de_contenedor(nombre: str, cont: Dict[str, Any]) -> None:
    """Reutiliza campos del CONTENEDOR tal como están declarados."""
    if not isinstance(cont, dict):
        return
    clave = str(cont.get("nombre") or nombre).strip().lower()
    if not clave:
        return
    entrada = {
        "origen": "contenedor",
        "modulo": nombre,
        "nombre": cont.get("nombre"),
        "rol": cont.get("rol"),
        "version": cont.get("version"),
        "descripcion": cont.get("descripcion"),
        "requiere": cont.get("requiere"),
        "capacidades": list((cont.get("capacidades") or {}).keys())
        if isinstance(cont.get("capacidades"), dict)
        else cont.get("capacidades"),
    }
    # fusionar si ya existe (más de una fuente)
    if clave in _LEXICO:
        prev = _LEXICO[clave]
        for k, v in entrada.items():
            if v is not None and prev.get(k) in (None, "", [], {}):
                prev[k] = v
        prev.setdefault("fuentes", [])
        if "contenedor" not in prev["fuentes"]:
            prev["fuentes"].append("contenedor")
    else:
        entrada["fuentes"] = ["contenedor"]
        _LEXICO[clave] = entrada


def _extraer_de_axiomas(nombre: str, lista: Any) -> None:
    """Reutiliza axiomas declarados por el módulo."""
    if not isinstance(lista, list):
        return
    for ax in lista:
        if not isinstance(ax, dict):
            continue
        aid = ax.get("id")
        if aid:
            clave = str(aid).strip().lower()
            _LEXICO[clave] = {
                "origen": "axioma",
                "modulo": nombre,
                "id": aid,
                "tipo": ax.get("tipo"),
                "sujeto": ax.get("sujeto"),
                "relacion": ax.get("relacion"),
                "objeto": ax.get("objeto"),
                "enunciado": ax.get("enunciado"),
                "polaridad": ax.get("polaridad"),
                "fuentes": ["axioma"],
            }
        # también indexar sujeto/objeto como anclas de referencia si son str
        for campo in ("sujeto", "objeto", "relacion"):
            val = ax.get(campo)
            if isinstance(val, str) and val.strip():
                c = val.strip().lower()
                if c not in _LEXICO:
                    _LEXICO[c] = {
                        "origen": "axioma_ref",
                        "modulo": nombre,
                        "nombre": val.strip(),
                        "via": campo,
                        "axioma_id": aid,
                        "fuentes": ["axioma_ref"],
                    }


def _descubrir() -> None:
    global _CARGADO
    if _CARGADO:
        return

    for nombre in _iter_modulos():
        mod = _cargar_paquete(nombre)
        if mod is None:
            continue

        cont = getattr(mod, "CONTENEDOR", None)
        if isinstance(cont, dict):
            _extraer_de_contenedor(nombre, cont)

        ax_fn = getattr(mod, "axiomas", None)
        if callable(ax_fn):
            try:
                _extraer_de_axiomas(nombre, ax_fn())
            except Exception:
                pass

        # constante / anclas si el módulo las expone de forma simple
        for attr in ("ALPHA", "BETA", "VERSION"):
            if hasattr(mod, attr):
                clave = attr.lower()
                if clave not in _LEXICO:
                    _LEXICO[clave] = {
                        "origen": "atributo",
                        "modulo": nombre,
                        "nombre": attr,
                        "valor": str(getattr(mod, attr)),
                        "fuentes": ["atributo"],
                    }

    _CARGADO = True


def _asegurar() -> None:
    _descubrir()


# ===============================================================
# API
# ===============================================================
def listar() -> List[str]:
    """Claves del léxico interno derivadas del repositorio."""
    _asegurar()
    return sorted(_LEXICO.keys())


def obtener(clave: str) -> Optional[Dict[str, Any]]:
    """Una entrada del léxico interno, si el repo la declaró."""
    _asegurar()
    return _LEXICO.get((clave or "").strip().lower())


def todo() -> Dict[str, Dict[str, Any]]:
    """Copia del léxico interno completo."""
    _asegurar()
    return {k: dict(v) for k, v in _LEXICO.items()}


def depositar_en_cache(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Deposita el léxico interno en el módulo de caché, si está disponible.
    No falla el sistema si caché no está: reporta y sigue.
    """
    _asegurar()
    payload = {
        "origen": "glosario",
        "version": VERSION,
        "total": len(_LEXICO),
        "lexico": todo(),
    }
    try:
        from modules import cache as cache_mod
        # superficie mínima: si expone registrar / append / guardar
        for nombre in ("registrar", "append", "guardar", "depositar"):
            fn = getattr(cache_mod, nombre, None)
            if callable(fn):
                fn(payload)
                return {"ok": True, "via": nombre, "total": len(_LEXICO)}
        # o CONTENEDOR.capacidades
        cont = getattr(cache_mod, "CONTENEDOR", None)
        if isinstance(cont, dict):
            caps = cont.get("capacidades") or {}
            for nombre in ("registrar", "append", "guardar", "depositar", "resolver"):
                fn = caps.get(nombre)
                if callable(fn):
                    fn(payload if nombre != "resolver" else {"lexico": payload})
                    return {"ok": True, "via": "contenedor.{0}".format(nombre), "total": len(_LEXICO)}
    except Exception as e:
        return {"ok": False, "error": str(e), "total": len(_LEXICO), "payload_listo": True}

    return {
        "ok": False,
        "error": "cache no expone superficie de depósito conocida",
        "total": len(_LEXICO),
        "payload_listo": True,
        "payload": payload,
    }


# ===============================================================
# CENTINELA
# ===============================================================
def barrer() -> Dict[str, Any]:
    _asegurar()
    return {
        "contenedor": "glosario",
        "rol": "GL",
        "coherente": True,
        "total": len(_LEXICO),
        "modulos_vistos": _iter_modulos(),
        "notas": [
            "Léxico derivado del repositorio. Sin listas manuales. "
            "Roles y contratos nuevos se incorporan al descubrir."
        ],
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    b = barrer()
    return {
        "contenedor": "glosario",
        "version": VERSION,
        "rol": "GL",
        "total": b["total"],
        "modulos_vistos": b["modulos_vistos"],
        "claves_n": len(listar()),
        "funcion": (
            "Reutiliza lo declarado en el repositorio para el léxico interno. "
            "Preparado para roles y contratos nuevos. Puede depositar en caché."
        ),
    }


def axiomas() -> List[Dict[str, Any]]:
    return [
        {
            "id": "GL-OP-1",
            "tipo": "axioma",
            "sujeto": "glosario",
            "relacion": "reutiliza",
            "objeto": "lo_declarado_en_el_repositorio",
            "polaridad": True,
            "enunciado": (
                "El glosario reutiliza literalmente lo que el repositorio "
                "ya declara. No inventa entradas ni mantiene listas manuales."
            ),
            "depende_de": [],
            "gobierna": ["glosario"],
        },
        {
            "id": "GL-OP-2",
            "tipo": "axioma",
            "sujeto": "glosario",
            "relacion": "admite",
            "objeto": "roles_y_contratos_nuevos",
            "polaridad": True,
            "enunciado": (
                "Al agregar un módulo con CONTENEDOR o axiomas, el glosario "
                "lo incorpora por descubrimiento. No hay que editar este init."
            ),
            "depende_de": [],
            "gobierna": ["glosario"],
        },
        {
            "id": "GL-OP-3",
            "tipo": "axioma",
            "sujeto": "glosario",
            "relacion": "puede_depositar",
            "objeto": "en_cache",
            "polaridad": True,
            "enunciado": (
                "El léxico interno puede depositarse en caché para consulta "
                "posterior sin re-recorrer el repositorio."
            ),
            "depende_de": [],
            "gobierna": ["glosario", "cache"],
        },
    ]


def resolver(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    peticion = dict(peticion or {})
    _asegurar()

    if peticion.get("depositar") or peticion.get("cache"):
        dep = depositar_en_cache(peticion)
        return {
            "ok": bool(dep.get("ok")),
            "modulo": "glosario",
            "rol": "GL",
            "deposito": dep,
            "total": len(_LEXICO),
            "coherente": True,
        }

    clave = peticion.get("clave") or peticion.get("nombre") or peticion.get("termino")
    if clave:
        r = obtener(str(clave))
        return {
            "ok": r is not None,
            "modulo": "glosario",
            "rol": "GL",
            "resultado": r,
            "coherente": True,
        }

    return {
        "ok": True,
        "modulo": "glosario",
        "rol": "GL",
        "total": len(_LEXICO),
        "claves": listar(),
        "inventario": inventario(),
        "coherente": True,
    }


CONTENEDOR = {
    "nombre": "glosario",
    "rol": "GL",
    "version": VERSION,
    "requiere": [],
    "descripcion": (
        "Glosario interno. Reutiliza literalmente lo declarado en el "
        "repositorio (contenedores, roles, contratos, axiomas). "
        "Preparado para roles y contratos nuevos por descubrimiento. "
        "Puede depositar el léxico en caché. No inventa entradas. "
        "No calcula Tru. No clasifica O."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "axiomas": axiomas,
        "resolver": resolver,
        "listar": listar,
        "obtener": obtener,
        "todo": todo,
        "depositar_en_cache": depositar_en_cache,
    },
}
