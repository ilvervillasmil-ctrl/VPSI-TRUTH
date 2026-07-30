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
"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import importlib.util
import sys

# ===============================================================
# METADATOS DEL CONTENEDOR
# ===============================================================

CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX",  # Rol obligatorio para el Engine
    "version": "1.0",
    "requiere": [],  # No requiere claves externas
}

# ===============================================================
# CARGA DE DECLARACIONES DESDE ARCHIVOS PLANOS
# ===============================================================

def _cargar_declaraciones_desde_archivo(archivo: Path) -> List[Dict]:
    """
    Carga las declaraciones de un archivo .py en el directorio axiomas/.
    Cada archivo debe definir una lista DECLARACIONES.
    """
    if archivo.name.startswith("_"):
        return []

    nombre_mod = f"axiomas_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return []

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)

    declaraciones = getattr(mod, "DECLARACIONES", [])
    return declaraciones if isinstance(declaraciones, list) else []

# ===============================================================
# NORMALIZACIÓN DE DECLARACIONES
# ===============================================================

OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")
TIPOS = ("axioma", "lema", "teorema", "corolario", "definicion")

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
                    "tripleta": " - ".join(k),
                    "declaracion_1": {
                        "id": a["id"],
                        "ubicacion": ref(a),
                        "enunciado": a["enunciado"],
                    },
                    "declaracion_2": {
                        "id": n["id"],
                        "ubicacion": ref(n),
                        "enunciado": n["enunciado"],
                    },
                    "mensaje": (
                        f"Contradicción directa en la tripleta '{' - '.join(k)}':\n"
                        f"  - {ref(a)} AFIRMA: {a['enunciado']}\n"
                        f"  - {ref(n)} NIEGA: {n['enunciado']}"
                    )
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
            for cota1, refs1 in porcota.items():
                for cota2, refs2 in porcota.items():
                    if cota1 != cota2:
                        for r1 in refs1:
                            for r2 in refs2:
                                choques.append({
                                    "tipo": "contradiccion_de_cota",
                                    "sujeto": suj,
                                    "relacion": rel,
                                    "cota_1": cota1,
                                    "cota_2": cota2,
                                    "declaracion_1": {"ubicacion": r1},
                                    "declaracion_2": {"ubicacion": r2},
                                    "mensaje": (
                                        f"Contradicción de cota en '{suj} {rel}':\n"
                                        f"  - {r1} define cota = {cota1}\n"
                                        f"  - {r2} define cota = {cota2}"
                                    )
                                })
    return choques

# ===============================================================
# BARRIDO AXIOMÁTICO
# ===============================================================

def barrer(declaraciones_externas: Dict[str, List[Dict]] = None) -> Dict:
    """
    Entrada:
        {nombre_de_modulo: [declaraciones]}

    Salida:
        coherente: False si hay contradicciones
        choques: lista de contradicciones detalladas
        errores: declaraciones mal formadas
        declaraciones: total de declaraciones cargadas
    """
    # Cargar declaraciones desde archivos en este directorio
    decls = []
    errores = []
    directorio = Path(__file__).parent

    for archivo in sorted(directorio.glob("*.py")):
        if archivo.name == "__init__.py":
            continue

        try:
            declaraciones_archivo = _cargar_declaraciones_desde_archivo(archivo)
            for decl in declaraciones_archivo:
                decl_normalizada = normalizar(decl, archivo.stem)
                decls.append(decl_normalizada)
        except Exception as e:
            errores.append({
                "archivo": archivo.name,
                "error": f"{type(e).__name__}: {e}",
            })

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
# FUNCIÓN axiomas() PARA EL ENGINE
# ===============================================================

def axiomas() -> List[Dict]:
    """
    Devuelve las declaraciones axiomáticas de este contenedor para el barrido axiomático.
    """
    decls = []
    directorio = Path(__file__).parent

    for archivo in sorted(directorio.glob("*.py")):
        if archivo.name == "__init__.py":
            continue
        try:
            declaraciones_archivo = _cargar_declaraciones_desde_archivo(archivo)
            for decl in declaraciones_archivo:
                decl_normalizada = normalizar(decl, archivo.stem)
                decls.append(decl_normalizada)
        except Exception:
            continue

    return decls

# ===============================================================
# INVENTARIO
# ===============================================================

def inventario() -> Dict:
    """Devuelve el inventario de axiomas cargados."""
    decls, errores = [], []
    directorio = Path(__file__).parent

    for archivo in sorted(directorio.glob("*.py")):
        if archivo.name == "__init__.py":
            continue
        try:
            declaraciones_archivo = _cargar_declaraciones_desde_archivo(archivo)
            for decl in declaraciones_archivo:
                decl_normalizada = normalizar(decl, archivo.stem)
                decls.append(decl_normalizada)
        except Exception as e:
            errores.append({
                "archivo": archivo.name,
                "error": str(e),
            })

    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "tipos": list(TIPOS),
        "declaraciones": len(decls),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS},
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
    }

# ===============================================================
# EXPORTACIÓN
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "barrer",
    "axiomas",
    "inventario",
    "normalizar",
    "contradiccion_directa",
    "contradiccion_de_cota",
]
