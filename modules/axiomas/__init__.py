# modules/axiomas/__init__.py

from pathlib import Path
from typing import Dict, List, Any, Tuple
import importlib.util
import sys

# ===============================================================
# METADATOS DEL CONTENEDOR
# ===============================================================
CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX", 
    "version": "1.0",
    "requiere": [],
}

# ===============================================================
# CARGA DE DECLARACIONES DESDE ARCHIVOS PLANOS
# ===============================================================
def _cargar_declaraciones_desde_archivo(archivo: Path) -> List[Dict]:
    # ... (deja esta función exactamente como la tenías) ...
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
# NORMALIZACIÓN DE DECLARACIONES (¡AQUÍ VA EL CAMBIO!)
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
    "cota": "cota"
}

def normalizar(decl_original: Dict, cuerpo: str) -> Dict:
    """Valida los campos obligatorios soportando inglés y español."""
    if not isinstance(decl_original, dict):
        raise ValueError(f"{cuerpo}: declaración no es dict")

    # 1. Traducir las llaves al español internamente
    decl = {}
    for clave, valor in decl_original.items():
        clave_esp = TRADUCCION_CLAVES.get(clave, clave)
        decl[clave_esp] = valor

    # 2. Validar que no falten los campos obligatorios
    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(f"{cuerpo}:{decl.get('id', '?')} sin clave obligatoria '{k}'")

    # 3. Validar el tipo y la polaridad
    tipo = str(decl["tipo"]).lower()
    if tipo == "axiom": tipo = "axioma"
    if tipo == "theorem": tipo = "teorema"
    if tipo == "corollary": tipo = "corolario"
    if tipo == "lemma": tipo = "lema"
    if tipo == "definition": tipo = "definicion"

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
# DETECCIÓN DE CONTRADICCIONES Y BARRIDO (DEJA TODO ESTO IGUAL)
# ===============================================================
# ... (tu código de clave(), ref(), contradiccion_directa(), contradiccion_de_cota(), barrer()) ...

# ===============================================================
# FUNCIÓN axiomas() PARA EL ENGINE (¡RECUERDA ESTE CAMBIO!)
# ===============================================================
def axiomas() -> List[Dict]:
    """
    Devuelve vacío para evitar la doble carga. 
    El Engine ya lee directamente de DECLARACIONES en los archivos .py.
    """
    return []

# ===============================================================
# INVENTARIO Y EXPORTACIÓN (DEJA ESTO IGUAL)
# ===============================================================
# ... (tu código de inventario() y __all__) ...
