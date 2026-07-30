# modules/axiomas/__init__.py

CONTAINER = {
    "name": "axiomas",
    "role": "AX",
    "version": "1.0",
    "requires": []
}

def inventory() -> dict:
    return {
        "container": CONTAINER["name"],
        "version": CONTAINER["version"],
        "dependencies": CONTAINER["requires"]
    }

# IMPORTANTE: No incluyas ninguna función def axiomas(): aquí.
# Deja que el Engine lea directamente de los archivos .py internos.

__all__ = ["CONTAINER", "inventory"]
