"""
VPSI-TRUTH / modules/axiomas

Contenedor de axiomas. Rol AX.
"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import importlib.util
import sys

# ===============================================================
# CARGA DE DECLARACIONES DESDE ARCHIVOS PLANOS Y EL AXIOMA CERO (VPSI.py)
# ===============================================================

def _cargar_declaraciones_desde_archivo(archivo: Path) -> List[Dict]:
    """Carga las declaraciones de un archivo .py en el directorio axiomas/."""
    if archivo.name.startswith("_"):
        return []

    nombre_mod = f"axiomas_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return []

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)

    # 1. Intentar buscar atributo DECLARACIONES (correlacion.py, self.py)
    declaraciones = getattr(mod, "DECLARACIONES", None)

    # 2. Si no existe, intentar buscar la función declaraciones() (VPSI.py)
    if declaraciones is None and callable(getattr(mod, "declaraciones", None)):
        try:
            declaraciones = mod.declaraciones()
        except Exception:
            declaraciones = []

    return declaraciones if isinstance(declaraciones, list) else []


# ===============================================================
# NORMALIZACIÓN DE DECLARACIONES (CON TRADUCTOR)
# ===============================================================

OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")
TIPOS = ("axioma", "lema", "teorema", "corolario", "definicion")

# Mapeo de llaves en inglés a español
TRADUCCION_CLAVES = {
    "type": "tipo",
    "subject": "sujeto",
    "relation": "relacion",
    "object": "objeto",
    "polarity": "polaridad",
    "statement": "enunciado",
    "depends_on": "depende_de",
    "governs": "gobierna",
    "cota": "cota",
}


def normalizar(decl_original: Dict, cuerpo: str) -> Dict:
    """Valida los campos obligatorios soportando inglés y español."""
    if not isinstance(decl_original, dict):
        raise ValueError(f"{cuerpo}: declaración no es dict")

    # 1. Traducir las llaves al español internamente
    decl = {}
    for clave_orig, valor in decl_original.items():
        clave_esp = TRADUCCION_CLAVES.get(clave_orig, clave_orig)
        decl[clave_esp] = valor

    # 2. Validar que no falten los campos obligatorios
    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(f"{cuerpo}:{decl.get('id', '?')} sin clave obligatoria '{k}'")

    # 3. Validar el tipo y la polaridad
    tipo = str(decl["tipo"]).lower()
    if tipo == "axiom":
        tipo = "axioma"
    if tipo == "theorem":
        tipo = "teorema"
    if tipo == "corollary":
        tipo = "corolario"
    if tipo == "lemma":
        tipo = "lema"
    if tipo == "definition":
        tipo = "definicion"

    if tipo not in TIPOS:
        raise ValueError(f"{cuerpo}:{decl['id']} tipo '{tipo}' no válido. Admitidos: {TIPOS}")

    if not isinstance(decl["polaridad"], bool):
        raise ValueError(f"{cuerpo}:{decl['id']} polaridad debe ser bool")

    # 4. Devolver estandarizado
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
    return (
        d["sujeto"].lower().strip(),
        d["relacion"].lower().strip(),
        d["objeto"].lower().strip(),
    )


def ref(d: Dict) -> str:
    return f"{d['cuerpo']}:{d['id']}"


def contradiccion_directa(decls: List[Dict]) -> List[Dict]:
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
                        f"Contradicción en '{' - '.join(k)}': "
                        f"{ref(a)} AFIRMA vs {ref(n)} NIEGA"
                    ),
                })
    return choques


def contradiccion_de_cota(decls: List[Dict]) -> List[Dict]:
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
            cota_keys = list(porcota.keys())
            choques.append({
                "tipo": "contradiccion_de_cota",
                "sujeto": suj,
                "relacion": rel,
                "mensaje": f"Contradicción de cota en '{suj} {rel}'. Cotas: {cota_keys}",
            })
    return choques


# ===============================================================
# BARRIDO AXIOMÁTICO (capacidad "verificar")
# ===============================================================

def barrer(declaraciones_externas: Dict[str, List[Dict]] = None) -> Dict:
    """
    Capacidad principal de verificación axiomática.
    El Engine llama a esta función a través del contrato.
    """
    decls = []
    errores = []
    directorio = Path(__file__).parent

    # Buscar tanto en la carpeta actual como en la raíz (para encontrar VPSI.py)
    archivos_a_procesar = list(directorio.glob("*.py"))
    vpsi_raiz = directorio.parent.parent / "VPSI.py"
    if not vpsi_raiz.exists():
        vpsi_raiz = directorio.parent / "VPSI.py"

    for archivo in sorted(archivos_a_procesar):
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

    # Cargar explícitamente VPSI desde la raíz si se encuentra
    if vpsi_raiz.exists():
        try:
            declaraciones_vpsi = _cargar_declaraciones_desde_archivo(vpsi_raiz)
            for decl in declaraciones_vpsi:
                decls.append(normalizar(decl, "VPSI"))
        except Exception as e:
            errores.append({
                "archivo": "VPSI.py",
                "error": f"{type(e).__name__}: {e}",
            })

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
                    errores.append({"modulo": nombre, "error": str(e)})

    choques = contradiccion_directa(decls) + contradiccion_de_cota(decls)

    return {
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "declaraciones": len(decls),
    }


# ===============================================================
# FUNCIÓN axiomas() (capacidad "axiomas")
# ===============================================================

def axiomas() -> List[Dict]:
    """
    Capacidad que el Engine puede solicitar para obtener las declaraciones
    de este módulo. Devuelve lista vacía porque las declaraciones se leen
    directamente de los archivos .py del directorio.
    """
    return []


# ===============================================================
# INVENTARIO (capacidad "inventario")
# ===============================================================

def inventario(peticion=None) -> Dict:
    """Capacidad de inventario del módulo."""
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
            errores.append({"archivo": archivo.name, "error": str(e)})

    return {
        "contenedor": "axiomas",
        "version": "1.0",
        "tipos": list(TIPOS),
        "declaraciones": len(decls),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS},
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
    }


# ===============================================================
# CONTENEDOR (contrato único y definitivo)
# ===============================================================

CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX",
    "version": "1.0",
    "requiere": [],
    "descripcion": "Contenedor de axiomas. Rol AX. Detecta contradicciones directas y de cota.",
    "capacidades": {
        "verificar": "barrer",      # capacidad que usa el Engine para arranque
        "axiomas": "axiomas",       # capacidad que el Engine puede consultar
        "evaluar": "barrer",        # capacidad canónica de evaluación
        "inventario": "inventario", # capacidad de introspección
    },
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
