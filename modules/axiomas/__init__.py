"""
VPSI-TRUTH / modules/axiomas

Contenedor de axiomas. Rol AX.

QUE ES ESTE MÓDULO:
  La definición de lo que es un axioma, un lema, un teorema y un
  corolario, y la vigilancia sobre ellos. No pertenece a ninguna teoría
  y no conoce ninguna. Vela por lo que se deje caer dentro.

QUE VIGILA:
  Una regla: no se contradicen entre sí.
    - contradiccion_directa: misma tripleta, polaridad opuesta.
    - contradiccion_de_cota: mismo sujeto y relación, dos cotas distintas.

  Si hay contradicción, barrer() devuelve coherente=False y el sistema no arranca.

FORMA DE UNA DECLARACIÓN:
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
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX",
    "version": "9.4",
    "requiere": [],
}

_DIR = Path(__file__).parent

# ===============================================================
# TIPOS DE DECLARACIONES
# ===============================================================

AXIOMA = "axioma"
LEMA = "lema"
TEOREMA = "teorema"
COROLARIO = "corolario"
TIPOS = (AXIOMA, LEMA, TEOREMA, COROLARIO)
OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")

# ===============================================================
# NORMALIZACIÓN
# ===============================================================

def normalizar(decl: Dict, cuerpo: str) -> Dict:
    """Valida los campos obligatorios y completa el resto."""
    if not isinstance(decl, dict):
        raise ValueError(f"{cuerpo}: declaración no es dict")

    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(f"{cuerpo}:{decl.get('id', '?')} sin clave '{k}'")

    tipo = str(decl["tipo"]).lower()
    if tipo not in TIPOS:
        raise ValueError(f"{cuerpo}:{decl['id']} tipo '{tipo}' no válido. Admitidos: {TIPOS}")

    if not isinstance(decl["polaridad"], bool):
        raise ValueError(f"{cuerpo}:{decl['id']} polaridad debe ser bool")

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

# ===============================================================
# CARGA DE ARCHIVOS PLANOS
# ===============================================================

def _cargar_archivo(archivo: Path) -> List[Dict]:
    """Carga las declaraciones de un archivo .py."""
    if archivo.name.startswith("_"):
        return []

    nombre_mod = f"axiomas_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return []

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)

    # Buscar DECLARACIONES en el módulo
    declaraciones = getattr(mod, "DECLARACIONES", [])
    if not isinstance(declaraciones, list):
        return []

    return declaraciones

def _cargar_todos_los_archivos() -> Tuple[List[Dict], List[Dict]]:
    """Carga todas las declaraciones de todos los archivos .py en este directorio."""
    decls = []
    errores = []

    for archivo in sorted(_DIR.glob("*.py")):
        if archivo.name == "__init__.py":
            continue  # Saltar este mismo archivo

        try:
            decls_archivo = _cargar_archivo(archivo)
            for decl in decls_archivo:
                decl_normalizada = normalizar(decl, archivo.stem)
                decls.append(decl_normalizada)
        except Exception as e:
            errores.append({
                "archivo": archivo.name,
                "error": f"{type(e).__name__}: {e}",
            })
            continue

    return decls, errores

# ===============================================================
# DETECCIÓN DE CONTRADICCIONES
# ===============================================================

def clave(d: Dict) -> Tuple[str, str, str]:
    """Tripleta canónica para comparación."""
    return (
        d["sujeto"].lower().strip(),
        d["relacion"].lower().strip(),
        d["objeto"].lower().strip(),
    )

def ref(d: Dict) -> str:
    """Referencia a una declaración."""
    return f"{d['cuerpo']}:{d['id']}"

def contradiccion_directa(decls: List[Dict]) -> List[Dict]:
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

def contradiccion_de_cota(decls: List[Dict]) -> List[Dict]:
    """Mismo sujeto y relación acotados a valores distintos."""
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
# BARRIDO AXIOMÁTICO
# ===============================================================

def barrer(declaraciones_externas: Dict[str, List[Dict]] = None) -> Dict:
    """
    Entrada del Engine:
        {nombre_de_modulo: [declaraciones]}

    Salida:
        coherente    False detiene el arranque
        choques      contradicciones halladas
        errores      declaraciones mal formadas
        declaraciones   total de declaraciones cargadas
    """
    decls, errores = _cargar_todos_los_archivos()

    # Añadir declaraciones externas (si las hay)
    if declaraciones_externas:
        for nombre, lista in declaraciones_externas.items():
            if not isinstance(lista, list):
                errores.append({
                    "modulo": nombre,
                    "error": "declaraciones externas no es lista",
                })
                continue
            for d in lista:
                try:
                    decls.append(normalizar(d, nombre))
                except ValueError as e:
                    errores.append({
                        "modulo": nombre,
                        "error": str(e),
                    })

    # Detectar contradicciones
    choques = contradiccion_directa(decls) + contradiccion_de_cota(decls)

    return {
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "declaraciones": len(decls),
    }

# ===============================================================
# INVENTARIO
# ===============================================================

def inventario() -> Dict:
    """Devuelve el inventario de axiomas cargados."""
    decls, errores = _cargar_todos_los_archivos()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "tipos": list(TIPOS),
        "declaraciones": len(decls),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS},
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
    }

__all__ = [
    "CONTENEDOR",
    "AXIOMA", "LEMA", "TEOREMA", "COROLARIO", "TIPOS",
    "normalizar", "clave", "ref",
    "barrer", "inventario",
]
