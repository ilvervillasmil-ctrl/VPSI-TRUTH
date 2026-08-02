"""
modules/contexto/__init__.py
============================

Rol CX — Contenedor de Contexto (clasificación operativa).

FUNCIÓN
  Clasificar y amarrar el marco evaluable O_context a nivel máquina.
  No calcula Tru_Ri ni Tru_total (eso es CA / FO).
  No juzga el grafo axiomático (eso es AX).
  No define el orden causal global (eso es MC); puede consultar
  contexto_MC.permite_k cuando exista.

DOS ESCALAS
  1. Micro — registro operativo de una petición / tramo / conversación.
  2. Macro — coherencia contextual del repositorio (CT, AX, MC).

CLASIFICACIÓN (dominio contexto)
  - modo_entrada: conversacion | afirmacion | teorema | auditoria | texto_libre | ...
  - estado_O:     estable | cambio | indefinido
  - evento:       mismo_O | expansion | cambio | indefinido
  - ligaduras:    forma → definición bajo O_id (unicidad; variantes permitidas)
  - permite_k:    True solo si hay O estable (alineado a CX-A1 / Def-5.3.1 / MC)

ARCHIVOS INTERNOS
  Cada *.py (excepto __init__ y _*) puede exponer:
    REGLA: dict
    validar() -> dict  o  clasificar(peticion) -> dict
  El init vela que no se contradigan (id/nombre duplicados).

El Engine dirige. Este módulo solo entrega el marco clasificado.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from core.diagnostico import DiagnosticoGlobal
except Exception:  # pragma: no cover
    class DiagnosticoGlobal:  # fallback silencioso
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass


_DIR = Path(__file__).parent

# Modos de entrada admitidos (CX-C10) — extensibles por reglas internas
MODOS_ENTRADA = (
    "conversacion",
    "afirmacion",
    "teorema",
    "auditoria",
    "texto_libre",
    "repositorio",  # macro sin petición micro
)

ESTADOS_O = ("estable", "cambio", "indefinido")
EVENTOS = ("mismo_O", "expansion", "cambio", "indefinido")


# ===============================================================
# UNDEFINED (sin evidencia / sin O estable)
# ===============================================================
class _Undefined:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, other):
        return isinstance(other, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")


UNDEFINED = _Undefined()


def es_undefined(v: Any) -> bool:
    return v is UNDEFINED or isinstance(v, _Undefined)


class ContextoError(Exception):
    """Error de coherencia o de regla contextual."""


# ===============================================================
# REGISTRO OPERATIVO (CX-D12 / CX-A14)
# ===============================================================
def _registro_vacio() -> Dict[str, Any]:
    return {
        "O_id": None,
        "escala": None,
        "enunciado_O": None,
        "ligaduras": {},          # forma -> definicion (str)
        "estado": "indefinido",   # estable | cambio | indefinido
        "modo_entrada": None,
        "evento": "indefinido",   # mismo_O | expansion | cambio | indefinido
    }


def _normalizar_registro(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye registro operativo desde la petición.
    No inventa O: si falta O_id / enunciado, estado = indefinido.
    """
    reg = _registro_vacio()

    o_id = peticion.get("O_id") or peticion.get("o_id")
    enunciado = (
        peticion.get("enunciado_O")
        or peticion.get("enunciado")
        or peticion.get("contexto")
        or peticion.get("O_context")
    )
    escala = peticion.get("escala")
    modo = peticion.get("modo_entrada") or peticion.get("modo")
    ligaduras = peticion.get("ligaduras") or {}
    estado_decl = peticion.get("estado")

    if isinstance(ligaduras, dict):
        reg["ligaduras"] = {
            str(k).strip(): str(v).strip()
            for k, v in ligaduras.items()
            if str(k).strip() and str(v).strip()
        }
    else:
        reg["ligaduras"] = {}

    reg["O_id"] = str(o_id).strip() if o_id else None
    reg["enunciado_O"] = str(enunciado).strip() if enunciado else None
    reg["escala"] = str(escala).strip() if escala else None
    reg["modo_entrada"] = str(modo).strip() if modo else None

    if estado_decl in ESTADOS_O:
        reg["estado"] = estado_decl
    elif reg["O_id"] and reg["enunciado_O"]:
        reg["estado"] = "estable"
    else:
        reg["estado"] = "indefinido"

    evento = peticion.get("evento")
    if evento in EVENTOS:
        reg["evento"] = evento
    elif reg["estado"] == "estable":
        reg["evento"] = "mismo_O"
    else:
        reg["evento"] = "indefinido"

    return reg


def _conflicto_ligaduras(ligaduras: Dict[str, str]) -> List[str]:
    """
    Unicidad forma -> una sola D (CX-A15).
    En un dict bien formado no hay claves duplicadas; se reserva para
    listas de pares o fusiones futuras. Conflicto = misma forma con
    dos D distintas si el caller pasa estructura extendida.
    """
    # Estructura actual: dict forma->D ya garantiza una D por forma.
    # Validación explícita de valores vacíos.
    errs = []
    for forma, d in ligaduras.items():
        if not forma or not d:
            errs.append(f"ligadura inválida: forma={forma!r} D={d!r}")
    return errs


def _permite_k(registro: Dict[str, Any], instanciados: Optional[Set[str]] = None) -> bool:
    """
    K solo con O estable (CX-A1, CX-A10, CX-C4).
    Si contexto_MC está disponible, se alinea a su sub-ruta.
    """
    if registro.get("estado") != "estable":
        return False
    if not registro.get("O_id") or not registro.get("enunciado_O"):
        return False

    try:
        from modules.correlacion_mecanica.contexto_MC import permite_k as mc_permite_k
        base = {"Ciclo_Id", "Declaracion_O", "Escala_O", "Regla_Significado"}
        if instanciados is not None:
            return bool(mc_permite_k(set(instanciados)))
        # Sin detalle de pasos: O estable + enunciado equivale a declaración mínima
        return True
    except Exception:
        return True  # sin MC: criterio local de registro estable


# ===============================================================
# CARGA DE REGLAS INTERNAS
# ===============================================================
def _cargar_reglas(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Cada archivo .py (excepto __init__ y _*) puede declarar:
      - REGLA: dict
      - validar() y/o clasificar(peticion)
    """
    registro: Dict[str, Any] = {}
    for archivo in sorted(_DIR.glob("*.py")):
        if archivo.name == "__init__.py" or archivo.name.startswith("_"):
            continue
        nombre_mod = f"contexto_regla_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre_mod] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            registro[archivo.stem] = {"error": f"{type(e).__name__}: {e}"}
            continue

        meta = getattr(mod, "REGLA", None)
        validador = getattr(mod, "validar", None)
        clasificador = getattr(mod, "clasificar", None)

        entrada: Dict[str, Any] = {"archivo": archivo.name}
        if isinstance(meta, dict):
            entrada["regla"] = meta

        if callable(clasificador) and peticion is not None:
            try:
                entrada["clasificacion"] = clasificador(peticion)
            except Exception as e:
                entrada["error"] = f"clasificar: {e}"
        elif callable(validador):
            try:
                entrada["resultado"] = validador()
            except Exception as e:
                entrada["error"] = str(e)

        if (
            "regla" not in entrada
            and "resultado" not in entrada
            and "clasificacion" not in entrada
            and "error" not in entrada
        ):
            entrada["error"] = "sin REGLA ni validar()/clasificar()"

        registro[archivo.stem] = entrada
    return registro


def _detectar_choques_reglas(reglas: Dict[str, Any]) -> List[str]:
    choques: List[str] = []
    por_id: Dict[str, List[str]] = {}
    por_nombre: Dict[str, List[str]] = {}

    for clave, datos in reglas.items():
        if "error" in datos:
            continue
        regla = datos.get("regla") or {}
        rid = str(regla.get("id", "")).strip()
        nom = str(regla.get("nombre", "")).strip()
        if rid:
            por_id.setdefault(rid, []).append(clave)
        if nom:
            por_nombre.setdefault(nom, []).append(clave)

    for rid, archivos in por_id.items():
        if len(archivos) > 1:
            choques.append(f"id de regla '{rid}' repetido en {archivos}")
    for nom, archivos in por_nombre.items():
        if len(archivos) > 1:
            choques.append(f"nombre de regla '{nom}' repetido en {archivos}")
    return choques


# ===============================================================
# CONTEXTO DE REPOSITORIO (macro)
# ===============================================================
def _contexto_repositorio() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "O_context": "VPSI-TRUTH / repositorio",
        "descripcion": (
            "Contexto macro: coherencia del sistema de módulos, "
            "contratos CONTENEDOR y reportes de diagnóstico."
        ),
        "modo_entrada": "repositorio",
    }

    try:
        from fractions import Fraction
        from modules.constante import ALPHA, BETA
        info["constantes"] = {
            "ALPHA": str(ALPHA),
            "BETA": str(BETA),
            "valido": ALPHA + BETA == Fraction(1),
        }
    except Exception as e:
        info["constantes"] = {"error": str(e), "valido": False}

    try:
        from modules.axiomas import barrer as barrer_ax
        ia = barrer_ax()
        info["axiomas"] = {
            "coherente": ia.get("coherente", False),
            "declaraciones": ia.get("declaraciones", 0),
            "choques": len(ia.get("choques", [])),
        }
    except Exception as e:
        info["axiomas"] = {"coherente": False, "error": str(e)}

    try:
        from modules.correlacion_mecanica import barrer as barrer_mc
        im = barrer_mc()
        info["mecanica"] = {
            "coherente": im.get("coherente", False),
            "choques": im.get("choques", []),
        }
    except Exception as e:
        info["mecanica"] = {"coherente": False, "error": str(e)}

    info["coherente"] = (
        info.get("constantes", {}).get("valido", False)
        and info.get("axiomas", {}).get("coherente", False)
        and info.get("mecanica", {}).get("coherente", False)
    )
    return info


# ===============================================================
# API PRINCIPAL — clasificación (no Tru)
# ===============================================================
def resolver(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clasifica el contexto aplicable.

    Sin petición  → solo macro (repositorio).
    Con petición  → registro operativo + reglas internas + permite_k.

    No calcula Tru. No asigna K numérico.
    """
    peticion = dict(peticion or {})
    repo = _contexto_repositorio()
    reglas = _cargar_reglas(peticion if peticion else None)
    choques_reglas = _detectar_choques_reglas(reglas)

    errores: List[str] = []
    if choques_reglas:
        errores.extend(choques_reglas)
    for nombre, datos in reglas.items():
        if "error" in datos:
            errores.append(f"regla '{nombre}': {datos['error']}")

    if not repo.get("coherente", False):
        errores.append("contexto de repositorio incoherente")

    if not peticion:
        # Solo macro
        salida = {
            "O_context": repo.get("O_context"),
            "registro": None,
            "permite_k": False,
            "coherente": (not errores) and repo.get("coherente", False),
            "escala": "macro",
            "modo_entrada": "repositorio",
            "reglas_internas": {
                "total": len(reglas),
                "choques": choques_reglas,
                "detalle": reglas,
            },
            "repositorio": repo,
            "errores": errores,
            "notas": [
                "sin petición micro: solo contexto de repositorio; "
                "K no reclamable sin registro O estable"
            ],
            "ids_cx_relevantes": ["CX-A1", "CX-C4", "Def-5.3.1"],
        }
    else:
        registro = _normalizar_registro(peticion)
        errores.extend(_conflicto_ligaduras(registro.get("ligaduras") or {}))

        if registro.get("modo_entrada") and registro["modo_entrada"] not in MODOS_ENTRADA:
            errores.append(
                f"modo_entrada no reconocido: {registro['modo_entrada']!r} "
                f"(admitidos: {MODOS_ENTRADA})"
            )

        # Fusionar clasificaciones de reglas internas (si aportan evento/estado)
        for nombre, datos in reglas.items():
            cls = datos.get("clasificacion")
            if not isinstance(cls, dict):
                continue
            if cls.get("estado") in ESTADOS_O:
                registro["estado"] = cls["estado"]
            if cls.get("evento") in EVENTOS:
                registro["evento"] = cls["evento"]
            if cls.get("error"):
                errores.append(f"clasificacion '{nombre}': {cls['error']}")

        permite = _permite_k(registro)
        o_ctx = registro.get("enunciado_O") or registro.get("O_id") or UNDEFINED

        ids = ["CX-A14", "CX-A1", "CX-C4"]
        if registro["estado"] != "estable":
            ids.extend(["CX-A10", "CX-T13"])
        if registro.get("ligaduras"):
            ids.extend(["CX-A15", "CX-T12"])
        if registro.get("evento") == "cambio":
            ids.extend(["CX-A8", "CX-T6"])

        salida = {
            "O_context": o_ctx if not es_undefined(o_ctx) else UNDEFINED,
            "registro": registro,
            "permite_k": permite,
            "coherente": (not errores) and repo.get("coherente", False),
            "escala": "micro+macro",
            "modo_entrada": registro.get("modo_entrada"),
            "reglas_internas": {
                "total": len(reglas),
                "choques": choques_reglas,
                "detalle": reglas,
            },
            "repositorio": repo,
            "errores": errores,
            "notas": [],
            "ids_cx_relevantes": ids,
        }
        if not registro.get("O_id") or not registro.get("enunciado_O"):
            salida["notas"].append(
                "registro incompleto: sin O_id o enunciado_O → estado indefinido; "
                "no reclamar Tru/K completo (CX-A14, CX-C4)"
            )
        if not permite:
            salida["notas"].append(
                "permite_k=False: O no estable o sub-ruta incompleta"
            )

    if not reglas:
        salida["notas"].append(
            "sin archivos de regla internos (vacío legítimo hasta montar clasificadores)"
        )

    if not salida.get("coherente", False):
        try:
            from core.diagnostico import DiagnosticoGlobal
            fn = getattr(DiagnosticoGlobal, "recibir_reporte", None)
            if callable(fn):
                fn(
                    modulo="contexto",
                    errores=[
                        {"tipo": "error_contexto", "detalle": e}
                        for e in (errores or [])
                    ],
                )
        except Exception:
            pass

    return salida


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return bool(salida.get("coherente", False))


def inventario(peticion: Any = None) -> Dict[str, Any]:
    reglas = _cargar_reglas()
    return {
        "contenedor": "contexto",
        "version": "1.1",
        "rol": "CX",
        "reglas_internas": list(reglas.keys()),
        "total_reglas": len(reglas),
        "modos_entrada": list(MODOS_ENTRADA),
        "estados_O": list(ESTADOS_O),
        "eventos": list(EVENTOS),
        "funcion": (
            "Clasifica O_context a nivel máquina (registro, modo de entrada, "
            "ligaduras, evento, permite_k). No calcula Tru. "
            "AX juzga; MC ordena; CA/FO calculan."
        ),
    }


def axiomas() -> List[Dict[str, Any]]:
    """Declaraciones mínimas del módulo operativo CX (no sustituyen contexto_AX)."""
    return [
        {
            "id": "CX-OP-1",
            "tipo": "axioma",
            "sujeto": "contexto_modulo",
            "relacion": "clasifica_y_no_calcula",
            "objeto": "Tru_Ri_ni_Tru_total",
            "polaridad": True,
            "enunciado": (
                "El módulo contexto clasifica el marco O; no calcula Tru_Ri ni Tru_total."
            ),
            "depende_de": [],
            "gobierna": ["contexto"],
        },
        {
            "id": "CX-OP-2",
            "tipo": "axioma",
            "sujeto": "K",
            "relacion": "requiere",
            "objeto": "registro_O_estable",
            "polaridad": True,
            "enunciado": (
                "Sin registro O estable, K no es reclamable (Def-5.3.1, CX-A14, CX-C4)."
            ),
            "depende_de": ["Def-5.3.1", "CX-A14"],
            "gobierna": ["contexto", "evaluacion"],
        },
        {
            "id": "CX-OP-3",
            "tipo": "axioma",
            "sujeto": "reglas_internas_de_contexto",
            "relacion": "no_deben",
            "objeto": "contradecirse",
            "polaridad": True,
            "enunciado": (
                "Los archivos de regla dentro de contexto/ no pueden contradecirse; "
                "el init vela id/nombre únicos."
            ),
            "depende_de": [],
            "gobierna": ["contexto"],
        },
    ]


# ===============================================================
# CONTENEDOR
# ===============================================================
CONTENEDOR = {
    "nombre": "contexto",
    "rol": "CX",
    "version": "1.1",
    "requiere": ["MC", "CT", "AX"],
    "descripcion": (
        "Clasificación operativa de O_context (micro/macro). "
        "Registro, modo de entrada, ligaduras, evento, permite_k. "
        "No calcula Tru. Engine dirige; AX juzga; MC ordena; CA/FO calculan."
    ),
    "capacidades": {
        "verificar": resolver,
        "evaluar": resolver,
        "inventario": inventario,
        "axiomas": axiomas,
    },
}

__all__ = [
    "CONTENEDOR",
    "UNDEFINED",
    "es_undefined",
    "ContextoError",
    "MODOS_ENTRADA",
    "ESTADOS_O",
    "EVENTOS",
    "resolver",
    "verificar_salida",
    "inventario",
    "axiomas",
]
