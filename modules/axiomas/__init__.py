"""
VPSI-TRUTH / modules/axiomas

Contenedor de axiomas. Rol AX.

QUE ES ESTE MODULO
  La definicion de lo que es un axioma, un lema, un teorema y un
  corolario, y la vigilancia sobre ellos. No pertenece a ninguna teoria
  y no conoce ninguna. Vela por lo que se deje caer dentro.

QUE VIGILA
  Una regla: no se contradicen entre si.

    contradiccion_directa    misma tripleta, polaridad opuesta
    contradiccion_de_cota    mismo sujeto y relacion, dos cotas distintas

  Si hay contradiccion, barrer() devuelve coherente=False y el sistema
  no arranca.

FORMA DE UNA DECLARACION

    {
      "id":         str,
      "tipo":       "axioma" | "lema" | "teorema" | "corolario",
      "sujeto":     str,
      "relacion":   str,
      "objeto":     str,
      "polaridad":  bool,
      "cota":       str | None,
      "depende_de": [id, ...],
      "gobierna":   [nombre_de_modulo, ...],
      "enunciado":  str,
    }

  Obligatorios: id, tipo, sujeto, relacion, objeto, polaridad.
  El resto es contenido.

FORMA DE UN CUERPO

  Un subdirectorio con __init__.py que expone:

      CUERPO = {"nombre": str, "version": str}

      def declaraciones() -> lista
"""

import importlib.util
import sys
from pathlib import Path


CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX",
    "version": "1.0",
    "requiere": [],
}


_DIR = Path(__file__).parent


# ===============================================================
# TIPOS
# ===============================================================

AXIOMA = "axioma"
LEMA = "lema"
TEOREMA = "teorema"
COROLARIO = "corolario"

TIPOS = (AXIOMA, LEMA, TEOREMA, COROLARIO)

OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")


# ===============================================================
# NORMALIZACION
# ===============================================================

def normalizar(decl, cuerpo):
    """Valida los campos obligatorios y completa el resto."""
    if not isinstance(decl, dict):
        raise ValueError(f"{cuerpo}: declaracion no es dict")

    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(
                f"{cuerpo}:{decl.get('id', '?')} sin clave '{k}'"
            )

    tipo = str(decl["tipo"]).lower()
    if tipo not in TIPOS:
        raise ValueError(
            f"{cuerpo}:{decl['id']} tipo '{tipo}' no valido. "
            f"Admitidos: {TIPOS}"
        )

    if not isinstance(decl["polaridad"], bool):
        raise ValueError(
            f"{cuerpo}:{decl['id']} polaridad debe ser bool"
        )

    return {
        "id": str(decl["id"]),
        "cuerpo": cuerpo,
        "tipo": tipo,
        "sujeto": str(decl["sujeto"]),
        "relacion": str(decl["relacion"]),
        "objeto": str(decl["objeto"]),
        "polaridad": bool(decl["polaridad"]),
        "cota": None if decl.get("cota") is None else str(decl["cota"]),
        "depende_de": [str(x) for x in decl.get("depende_de", [])],
        "gobierna": [str(x) for x in decl.get("gobierna", [])],
        "enunciado": str(decl.get("enunciado", "")),
    }


def clave(d):
    """Tripleta canonica sobre la que se compara."""
    return (
        d["sujeto"].lower().strip(),
        d["relacion"].lower().strip(),
        d["objeto"].lower().strip(),
    )


def ref(d):
    return f"{d['cuerpo']}:{d['id']}"


# ===============================================================
# CUERPOS
# ===============================================================

def _cargar(directorio):
    init = directorio / "__init__.py"
    if not init.exists():
        return None, "sin __init__.py"

    nombre_mod = "axcuerpo_" + directorio.name
    spec = importlib.util.spec_from_file_location(
        nombre_mod, init, submodule_search_locations=[str(directorio)]
    )
    if spec is None or spec.loader is None:
        return None, "spec no construible"

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)

    meta = getattr(mod, "CUERPO", None)
    if not isinstance(meta, dict):
        return None, "falta el diccionario CUERPO"
    for k in ("nombre", "version"):
        if k not in meta:
            return None, f"CUERPO sin clave '{k}'"
    if not callable(getattr(mod, "declaraciones", None)):
        return None, "no expone declaraciones()"

    return mod, None


def cuerpos():
    """Cuerpos cargados y rechazados."""
    cargados = {}
    rechazados = []

    for d in sorted(p for p in _DIR.iterdir() if p.is_dir()):
        if d.name.startswith(("_", ".")):
            continue
        try:
            mod, razon = _cargar(d)
        except Exception as e:
            rechazados.append({
                "cuerpo": d.name,
                "razon": f"{type(e).__name__}: {e}",
            })
            continue
        if mod is None:
            rechazados.append({"cuerpo": d.name, "razon": razon})
            continue

        n = mod.CUERPO["nombre"]
        if n in cargados:
            rechazados.append({
                "cuerpo": d.name,
                "razon": f"nombre duplicado: {n}",
            })
            continue
        cargados[n] = mod

    return cargados, rechazados


def recolectar():
    """Todas las declaraciones de todos los cuerpos."""
    cargados, errores = cuerpos()
    decls = []

    for n, mod in cargados.items():
        try:
            lista = mod.declaraciones()
        except Exception as e:
            errores.append({
                "cuerpo": n,
                "razon": f"declaraciones() levanto {type(e).__name__}: {e}",
            })
            continue
        if not isinstance(lista, list):
            errores.append({
                "cuerpo": n,
                "razon": "declaraciones() no devolvio lista",
            })
            continue
        for d in lista:
            try:
                decls.append(normalizar(d, n))
            except ValueError as e:
                errores.append({"cuerpo": n, "razon": str(e)})

    return decls, errores


# ===============================================================
# CONTRADICCION DIRECTA
# ===============================================================

def contradiccion_directa(decls):
    """Misma tripleta, polaridad opuesta."""
    grupos = {}
    for d in decls:
        grupos.setdefault(clave(d), []).append(d)

    choques = []
    for k, grupo in grupos.items():
        afirman = [d for d in grupo if d["polaridad"]]
        niegan = [d for d in grupo if not d["polaridad"]]
        for a in afirman:
            for n in niegan:
                choques.append({
                    "tipo": "contradiccion_directa",
                    "tripleta": " ".join(k),
                    "afirma": ref(a),
                    "afirma_tipo": a["tipo"],
                    "niega": ref(n),
                    "niega_tipo": n["tipo"],
                    "enunciado_afirma": a["enunciado"],
                    "enunciado_niega": n["enunciado"],
                })
    return choques


# ===============================================================
# CONTRADICCION DE COTA
# ===============================================================

def contradiccion_de_cota(decls):
    """Mismo sujeto y relacion acotados a valores distintos."""
    grupos = {}
    for d in decls:
        if d["cota"] is None:
            continue
        grupos.setdefault(
            (d["sujeto"].lower().strip(), d["relacion"].lower().strip()), []
        ).append(d)

    choques = []
    for (suj, rel), grupo in grupos.items():
        porcota = {}
        for d in grupo:
            porcota.setdefault(d["cota"], []).append(ref(d))
        if len(porcota) > 1:
            choques.append({
                "tipo": "contradiccion_de_cota",
                "sujeto": suj,
                "relacion": rel,
                "cotas": porcota,
            })
    return choques


# ===============================================================
# APLICACION
# ===============================================================

def sin_gobernar(decls, modulos_presentes):
    """
    Declaraciones que nombran un modulo gobernante ausente. Se reporta.
    No detiene el arranque: no es contradiccion.
    """
    presentes = set(modulos_presentes or ())
    huerfanos = []

    for d in decls:
        if not d["gobierna"]:
            continue
        ausentes = [m for m in d["gobierna"] if m not in presentes]
        if ausentes:
            huerfanos.append({
                "declaracion": ref(d),
                "tipo": d["tipo"],
                "gobernantes_ausentes": ausentes,
            })
    return huerfanos


# ===============================================================
# BARRIDO
# ===============================================================

def barrer(declaraciones_externas=None):
    """
    Entrada del Engine:
        {nombre_de_modulo: [declaraciones]}

    Salida:
        coherente    False detiene el arranque
        choques      contradicciones halladas
        errores      declaraciones mal formadas
        aplicacion   gobernantes ausentes, informativo
    """
    decls, errores = recolectar()

    modulos = []
    if declaraciones_externas:
        for nombre, lista in declaraciones_externas.items():
            modulos.append(nombre)
            if not isinstance(lista, list):
                errores.append({
                    "cuerpo": nombre,
                    "razon": "declaracion externa no es lista",
                })
                continue
            for d in lista:
                try:
                    decls.append(normalizar(d, nombre))
                except ValueError as e:
                    errores.append({"cuerpo": nombre, "razon": str(e)})

    choques = contradiccion_directa(decls) + contradiccion_de_cota(decls)

    return {
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "aplicacion": sin_gobernar(decls, modulos),
        "declaraciones": len(decls),
        "cuerpos": sorted({d["cuerpo"] for d in decls}),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t)
                     for t in TIPOS},
    }


# ===============================================================
# INVENTARIO
# ===============================================================

def inventario():
    cargados, rechazados = cuerpos()
    decls, errores = recolectar()

    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "tipos": list(TIPOS),
        "cuerpos": {
            n: {
                "version": m.CUERPO["version"],
                "por_tipo": {
                    t: sum(1 for d in decls
                           if d["cuerpo"] == n and d["tipo"] == t)
                    for t in TIPOS
                },
            }
            for n, m in cargados.items()
        },
        "rechazados": rechazados,
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
    }


__all__ = [
    "CONTENEDOR",
    "AXIOMA", "LEMA", "TEOREMA", "COROLARIO", "TIPOS",
    "normalizar", "clave", "ref",
    "cuerpos", "recolectar",
    "contradiccion_directa", "contradiccion_de_cota",
    "sin_gobernar",
    "barrer", "inventario",
]
