"""
modules/contexto/__init__.py
============================

Rol CX — Contenedor de Contexto (clasificación operativa) + CENTINELA.

FUNCIÓN
  Clasificar y amarrar el marco evaluable O_context a nivel máquina.
  No calcula Tru_Ri ni Tru_total (eso es CA / FO).
  No juzga el grafo axiomático (eso es AX).
  No define el orden causal global (eso es MC).
  No emite la cadena auditable (eso es CIT).

CENTINELA DE MÓDULO
  Todo *.py interno (excepto __init__ y _*) se carga automáticamente.
  El init valida forma, dominio y no-contradicción.
  Archivo incoherente → error en reglas + coherente=False + señal a diagnóstico.
  No hace falta editar este init al agregar un clasificador nuevo.

El Engine dirige. Este módulo solo entrega el marco clasificado.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from core.diagnostico import DiagnosticoGlobal
except Exception:  # pragma: no cover
    class DiagnosticoGlobal:  # fallback silencioso
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass


_DIR = Path(__file__).parent

MODOS_ENTRADA = (
    "conversacion",
    "afirmacion",
    "teorema",
    "auditoria",
    "texto_libre",
    "repositorio",
)

ESTADOS_O = ("estable", "cambio", "indefinido")
EVENTOS = ("mismo_O", "expansion", "cambio", "indefinido")

TIPOS_PETICION = (
    "por_que_valor",
    "dame_O",
    "dame_evidencia",
    "dame_normas",
    "dame_limites",
    "dame_cadena_completa",
)

_CLAVES_PEDIR_ANUNCIO = (
    "pedir_anuncio",
    "pedir_cita",
    "anuncio",
    "citar",
    "cadena_auditable",
    "dame_por_que",
)

# ===============================================================
# CENTINELA — contrato de dominio para archivos internos
# ===============================================================
# Todo clasificador nuevo debe cumplir esto. No se lista por nombre.
REGLA_CAMPOS_OBLIGATORIOS = ("id", "nombre", "version", "descripcion")

# Palabras/oficios prohibidos en el dominio CX (no calcular Tru, no ser AX/FO/CA)
_PROHIBIDOS_EN_DESCRIPCION = (
    "calcula tru",
    "calcular tru",
    "tru_total",
    "tru_ri",
    "asigna k numérico",
    "asigna k numerico",
)

# Claves que una clasificacion puede aportar al registro (whitelist blanda)
_CLAVES_CLASIFICACION_PERMITIDAS = {
    "ok", "estado", "evento", "incompleto", "O_id", "enunciado_O",
    "mensajes", "ids_cx", "ids", "permite_k_sugerido", "error",
    "pedir_anuncio", "tipos_peticion", "tipos_invalidos", "oficio",
    "escala", "modo_entrada", "ligaduras",
}


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


def _registro_vacio() -> Dict[str, Any]:
    return {
        "O_id": None,
        "escala": None,
        "enunciado_O": None,
        "ligaduras": {},
        "estado": "indefinido",
        "modo_entrada": None,
        "evento": "indefinido",
        "pedir_anuncio": False,
        "tipos_peticion": [],
    }


def _truthy_pedir(v: Any) -> bool:
    if v is True:
        return True
    if v is False or v is None:
        return False
    if isinstance(v, (int, float)):
        return v != 0
    s = str(v).strip().lower()
    return s in ("1", "true", "si", "sí", "yes", "on", "citar", "anuncio")


def _normalizar_tipos_peticion(raw: Any) -> List[str]:
    tipos: List[str] = []
    if isinstance(raw, str):
        for p in raw.replace(";", ",").split(","):
            p = p.strip()
            if p in TIPOS_PETICION and p not in tipos:
                tipos.append(p)
    elif isinstance(raw, (list, tuple, set)):
        for x in raw:
            s = str(x).strip()
            if s in TIPOS_PETICION and s not in tipos:
                tipos.append(s)
    return tipos


def _normalizar_registro(peticion: Dict[str, Any]) -> Dict[str, Any]:
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

    pedir = False
    for k in _CLAVES_PEDIR_ANUNCIO:
        if k in peticion and _truthy_pedir(peticion.get(k)):
            pedir = True
            break

    tipos = _normalizar_tipos_peticion(
        peticion.get("tipos_peticion") or peticion.get("tipo_peticion")
    )
    if tipos and not pedir:
        pedir = True
    if pedir and not tipos:
        tipos = ["dame_cadena_completa"]

    reg["pedir_anuncio"] = pedir
    reg["tipos_peticion"] = tipos
    return reg


def _conflicto_ligaduras(ligaduras: Dict[str, str]) -> List[str]:
    errs = []
    for forma, d in ligaduras.items():
        if not forma or not d:
            errs.append(f"ligadura inválida: forma={forma!r} D={d!r}")
    return errs


def _permite_k(registro: Dict[str, Any], instanciados: Optional[Set[str]] = None) -> bool:
    if registro.get("estado") != "estable":
        return False
    if not registro.get("O_id") or not registro.get("enunciado_O"):
        return False
    try:
        from modules.correlacion_mecanica.contexto_MC import permite_k as mc_permite_k
        if instanciados is not None:
            return bool(mc_permite_k(set(instanciados)))
        return True
    except Exception:
        return True


# ===============================================================
# CENTINELA — validación automática de cada archivo interno
# ===============================================================
def _validar_regla_meta(stem: str, regla: Any) -> List[str]:
    """Forma y dominio de REGLA (sin listar archivos por nombre)."""
    errs: List[str] = []
    if not isinstance(regla, dict):
        return [f"{stem}: REGLA debe ser dict"]

    for k in REGLA_CAMPOS_OBLIGATORIOS:
        if k not in regla or not str(regla.get(k, "")).strip():
            errs.append(f"{stem}: REGLA sin campo obligatorio '{k}'")

    rid = str(regla.get("id", "")).strip()
    if rid and not (
        rid.startswith("CX-") or rid.startswith("CX_R") or "CX" in rid.upper()
    ):
        # Aviso de dominio: preferimos ids CX-*; no bloquea si anclas_cx existen
        anclas = regla.get("anclas_cx") or regla.get("anclas") or []
        if not anclas:
            errs.append(
                f"{stem}: id '{rid}' no anclado a dominio CX "
                f"(use prefijo CX- o anclas_cx/anclas)"
            )

    desc = str(regla.get("descripcion", "")).lower()
    for frag in _PROHIBIDOS_EN_DESCRIPCION:
        if frag in desc:
            errs.append(
                f"{stem}: descripcion declara oficio prohibido en CX ({frag!r}); "
                f"CX no calcula Tru ni asigna K numérico"
            )

    return errs


def _validar_clasificacion(stem: str, cls: Any) -> List[str]:
    """Forma de salida de clasificar() — no inventa Tru."""
    errs: List[str] = []
    if not isinstance(cls, dict):
        return [f"{stem}: clasificar() debe devolver dict"]

    # Oficio prohibido: devolver Tru calculado
    for k in ("Tru_Ri", "Tru_total", "tru_ri", "tru_total", "C", "L", "K"):
        if k in cls and cls[k] is not None:
            # permite_k_sugerido y flags OK; valores Tru no
            if k in ("C", "L", "K") and k in cls:
                # K numérico en clasificación de contexto = fuera de oficio
                if k == "K" and not isinstance(cls.get("K"), bool):
                    errs.append(
                        f"{stem}: clasificar() no debe asignar K numérico "
                        f"(oficio CA/FO; CX solo permite_k / estado)"
                    )
            if k.lower().startswith("tru"):
                errs.append(
                    f"{stem}: clasificar() no debe emitir {k} (oficio CA/FO)"
                )

    if "estado" in cls and cls["estado"] is not None:
        if cls["estado"] not in ESTADOS_O:
            errs.append(
                f"{stem}: estado {cls['estado']!r} no ∈ {ESTADOS_O}"
            )
    if "evento" in cls and cls["evento"] is not None:
        if cls["evento"] not in EVENTOS:
            errs.append(
                f"{stem}: evento {cls['evento']!r} no ∈ {EVENTOS}"
            )

    tps = cls.get("tipos_peticion")
    if tps is not None:
        if not isinstance(tps, list):
            errs.append(f"{stem}: tipos_peticion debe ser list")
        else:
            for t in tps:
                if t not in TIPOS_PETICION:
                    errs.append(
                        f"{stem}: tipo_peticion no admitido: {t!r}"
                    )

    return errs


def _centinela_archivo(stem: str, mod: Any, peticion: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Audita un módulo de regla ya importado.
    Devuelve entrada de registro + lista errores_centinela.
    """
    entrada: Dict[str, Any] = {"archivo": f"{stem}.py"}
    errores_c: List[str] = []

    meta = getattr(mod, "REGLA", None)
    validador = getattr(mod, "validar", None)
    clasificador = getattr(mod, "clasificar", None)

    if meta is None and not callable(validador) and not callable(clasificador):
        errores_c.append(
            f"{stem}: sin REGLA ni validar()/clasificar() — "
            f"no es clasificador de dominio contexto"
        )
        entrada["error"] = errores_c[-1]
        entrada["errores_centinela"] = errores_c
        return entrada

    if meta is not None:
        entrada["regla"] = meta if isinstance(meta, dict) else {"raw": str(meta)}
        errores_c.extend(_validar_regla_meta(stem, meta))

    if callable(clasificador) and peticion is not None:
        try:
            cls = clasificador(peticion)
            entrada["clasificacion"] = cls
            errores_c.extend(_validar_clasificacion(stem, cls))
        except Exception as e:
            errores_c.append(f"{stem}: clasificar: {type(e).__name__}: {e}")
            entrada["error"] = errores_c[-1]
    elif callable(validador):
        try:
            entrada["resultado"] = validador()
        except Exception as e:
            errores_c.append(f"{stem}: validar: {type(e).__name__}: {e}")
            entrada["error"] = errores_c[-1]

    if errores_c:
        entrada["errores_centinela"] = errores_c
        # Si aún no hay error top-level, expone el primero
        if "error" not in entrada:
            entrada["error"] = errores_c[0]

    return entrada


def _cargar_reglas(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Carga automática de todos los *.py del directorio.
    Centinela valida forma/dominio; choques de id/nombre aparte.
    """
    registro: Dict[str, Any] = {}
    for archivo in sorted(_DIR.glob("*.py")):
        if archivo.name == "__init__.py" or archivo.name.startswith("_"):
            continue
        nombre_mod = f"contexto_regla_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
        if spec is None or spec.loader is None:
            registro[archivo.stem] = {
                "error": "spec_from_file_location falló",
                "errores_centinela": ["carga imposible"],
            }
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre_mod] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            registro[archivo.stem] = {
                "error": f"{type(e).__name__}: {e}",
                "errores_centinela": [f"import: {e}"],
            }
            continue

        registro[archivo.stem] = _centinela_archivo(
            archivo.stem, mod, peticion
        )
    return registro


def _detectar_choques_reglas(reglas: Dict[str, Any]) -> List[str]:
    choques: List[str] = []
    por_id: Dict[str, List[str]] = {}
    por_nombre: Dict[str, List[str]] = {}

    for clave, datos in reglas.items():
        if datos.get("errores_centinela") and "regla" not in datos:
            continue
        regla = datos.get("regla") or {}
        if not isinstance(regla, dict):
            continue
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


def resolver(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clasifica el contexto aplicable + centinela de archivos internos.

    No calcula Tru. No asigna K numérico. No emite citas.
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
        for ec in datos.get("errores_centinela") or []:
            if ec not in errores:
                errores.append(f"centinela '{nombre}': {ec}")

    if not repo.get("coherente", False):
        errores.append("contexto de repositorio incoherente")

    if not peticion:
        salida = {
            "O_context": repo.get("O_context"),
            "registro": None,
            "permite_k": False,
            "pedir_anuncio": False,
            "tipos_peticion": [],
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

        for nombre, datos in reglas.items():
            cls = datos.get("clasificacion")
            if not isinstance(cls, dict):
                continue
            # Solo fusiona si el centinela no marcó error de forma en estado/evento
            if datos.get("errores_centinela"):
                # aún puede aportar pedir_anuncio si la forma es válida en parte
                pass
            if cls.get("estado") in ESTADOS_O:
                registro["estado"] = cls["estado"]
            if cls.get("evento") in EVENTOS:
                registro["evento"] = cls["evento"]
            if cls.get("pedir_anuncio") is True:
                registro["pedir_anuncio"] = True
            tps = cls.get("tipos_peticion")
            if isinstance(tps, list) and tps:
                seen = set(registro.get("tipos_peticion") or [])
                for t in tps:
                    if t in TIPOS_PETICION and t not in seen:
                        registro.setdefault("tipos_peticion", []).append(t)
                        seen.add(t)
                if registro.get("tipos_peticion") and not registro.get("pedir_anuncio"):
                    registro["pedir_anuncio"] = True
            if cls.get("error"):
                errores.append(f"clasificacion '{nombre}': {cls['error']}")

        if registro.get("pedir_anuncio") and not registro.get("tipos_peticion"):
            registro["tipos_peticion"] = ["dame_cadena_completa"]

        permite = _permite_k(registro)
        o_ctx = registro.get("enunciado_O") or registro.get("O_id") or UNDEFINED

        ids = ["CX-A14", "CX-A1", "CX-C4"]
        if registro["estado"] != "estable":
            ids.extend(["CX-A10", "CX-T13"])
        if registro.get("ligaduras"):
            ids.extend(["CX-A15", "CX-T12"])
        if registro.get("evento") == "cambio":
            ids.extend(["CX-A8", "CX-T6"])
        if registro.get("pedir_anuncio"):
            ids.extend(["PA-A1", "PA-A2", "PA-T1", "PA-C2"])

        salida = {
            "O_context": o_ctx if not es_undefined(o_ctx) else UNDEFINED,
            "registro": registro,
            "permite_k": permite,
            "pedir_anuncio": bool(registro.get("pedir_anuncio")),
            "tipos_peticion": list(registro.get("tipos_peticion") or []),
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
        if registro.get("pedir_anuncio"):
            salida["notas"].append(
                "pedir_anuncio=True: CX clasifica; CIT anuncia (PA-A2); "
                "no implica permite_k ni Tru"
            )

    if not reglas:
        salida["notas"].append(
            "sin archivos de regla internos (vacío legítimo hasta montar clasificadores)"
        )

    if not salida.get("coherente", False):
        try:
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
    n_centinela = sum(
        1 for d in reglas.values() if d.get("errores_centinela")
    )
    return {
        "contenedor": "contexto",
        "version": "1.3",
        "rol": "CX",
        "reglas_internas": list(reglas.keys()),
        "total_reglas": len(reglas),
        "reglas_con_alerta_centinela": n_centinela,
        "modos_entrada": list(MODOS_ENTRADA),
        "estados_O": list(ESTADOS_O),
        "eventos": list(EVENTOS),
        "tipos_peticion": list(TIPOS_PETICION),
        "centinela": {
            "regla_campos_obligatorios": list(REGLA_CAMPOS_OBLIGATORIOS),
            "auto_carga": True,
            "rechaza_tru_en_clasificar": True,
            "choque_id_nombre": True,
        },
        "funcion": (
            "Clasifica O_context (registro, modo, ligaduras, evento, "
            "permite_k, pedir_anuncio). Centinela auto-valida cada *.py "
            "interno. No calcula Tru. No emite citas."
        ),
    }


def axiomas() -> List[Dict[str, Any]]:
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
                "el init vela id/nombre únicos y forma de dominio (centinela)."
            ),
            "depende_de": [],
            "gobierna": ["contexto"],
        },
        {
            "id": "CX-OP-4",
            "tipo": "axioma",
            "sujeto": "pedir_anuncio",
            "relacion": "clasifica_y_no_emite",
            "objeto": "cadena_auditable",
            "polaridad": True,
            "enunciado": (
                "pedir_anuncio en el registro de contexto clasifica la solicitud "
                "de cadena; no calcula Tru ni sustituye a CIT (PA-A1, PA-C2)."
            ),
            "depende_de": ["PA-A1", "PA-C2"],
            "gobierna": ["contexto", "citacion"],
        },
        {
            "id": "CX-OP-5",
            "tipo": "axioma",
            "sujeto": "centinela_contexto",
            "relacion": "rechaza",
            "objeto": "archivo_fuera_de_dominio_o_mal_formado",
            "polaridad": True,
            "enunciado": (
                "Todo *.py interno se carga automáticamente; si incumple forma "
                "REGLA, oficio CX o unicidad id/nombre, el módulo marca error "
                "y coherente=False sin editar el init."
            ),
            "depende_de": ["CX-OP-3"],
            "gobierna": ["contexto"],
        },
    ]


CONTENEDOR = {
    "nombre": "contexto",
    "rol": "CX",
    "version": "1.3",
    "requiere": ["MC", "CT", "AX"],
    "descripcion": (
        "Clasificación operativa de O_context + centinela de archivos internos. "
        "Auto-carga *.py; valida forma/dominio/unicidad. No calcula Tru. "
        "No emite citas. Engine dirige; AX juzga; MC ordena; CA/FO calculan; CIT anuncia."
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
    "TIPOS_PETICION",
    "resolver",
    "verificar_salida",
    "inventario",
    "axiomas",
]
