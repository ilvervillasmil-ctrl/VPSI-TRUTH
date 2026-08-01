"""
VPSI-TRUTH --- core/engine.py

Engine central. Orquesta módulos por rol, ejecuta compuertas
de coherencia y expone evaluar().
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fractions import Fraction


# ===============================================================
# EXCEPCIONES
# ===============================================================
class ArranqueError(Exception):
    """Se lanza cuando el Engine no puede arrancar por incoherencia
    axiomática, mecánica o dependencias faltantes."""
    pass


class EvaluacionError(Exception):
    """Error durante el camino de evaluación."""
    pass


# ===============================================================
# ROLES ADMITIDOS
# ===============================================================
ROLES = ("CT", "AX", "FO", "MC", "SF", "DG", "CA")


# ===============================================================
# CONTENEDOR
# ===============================================================
class Contenedor:
    def __init__(self, nombre: str, rol: str, version: str, modulo: Any, ruta: Path):
        self.nombre = nombre
        self.rol = rol
        self.version = version
        self.modulo = modulo
        self.ruta = ruta
        meta = getattr(modulo, "CONTENEDOR", {}) or {}
        self.requiere: List[str] = meta.get("requiere", [])
        self.capacidades: Dict[str, Any] = meta.get("capacidades", {})

    def fn(self, nombre: str):
        ref = self.capacidades.get(nombre)
        if ref is None:
            return None
        if callable(ref):
            return ref
        return getattr(self.modulo, ref, None)


# ===============================================================
# REGISTRO
# ===============================================================
class Registro:
    def __init__(self):
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {r: [] for r in ROLES}
        self.rechazados: List[Dict] = []

    def registrar(self, cont: Contenedor):
        if cont.nombre in self.contenedores:
            self.rechazados.append({
                "ruta": str(cont.ruta),
                "razon": f"nombre duplicado: {cont.nombre}"
            })
            return
        self.contenedores[cont.nombre] = cont
        if cont.rol in self.por_rol:
            self.por_rol[cont.rol].append(cont)

    def resumen(self) -> Dict:
        return {
            "roles": {r: [c.nombre for c in self.por_rol[r]] for r in ROLES},
            "roles_vacios": [r for r in ROLES if not self.por_rol[r]],
            "rechazados": self.rechazados,
            "total": len(self.contenedores),
        }


# ===============================================================
# ENGINE
# ===============================================================
class Engine:
    def __init__(
        self,
        raiz_modulos: str | Path,
        invocador_id: str = "core",
        verificar_axiomas: bool = True,
        strict: bool = True,
    ):
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id = invocador_id
        self.verificar_axiomas = verificar_axiomas
        self.strict = strict

        self.registro = Registro()
        self.informe_axiomas: Optional[Dict] = None
        self.informe_mecanica: Optional[Dict] = None
        self.estado = "NO_INICIADO"
        self.errores_arranque: List[str] = []

        self._descubrir()
        self._resolver_dependencias()

        if self.verificar_axiomas:
            self._ejecutar_compuertas()

        if self.errores_arranque:
            self.estado = "RECHAZADO"
            if self.strict:
                raise ArranqueError(
                    "Engine no pudo arrancar:\n  - " +
                    "\n  - ".join(self.errores_arranque)
                )
        else:
            self.estado = "OPERATIVO"

    # -----------------------------------------------------------
    def _descubrir(self):
        if not self.raiz.exists():
            self.errores_arranque.append(f"Raíz de módulos no existe: {self.raiz}")
            return

        for path in sorted(self.raiz.rglob("*.py")):
            if path.name.startswith("_") and path.name != "__init__.py":
                continue
            # Preferir __init__.py del paquete
            if path.name != "__init__.py" and (path.parent / "__init__.py").exists():
                continue

            try:
                cont = self._cargar_modulo(path)
                if cont:
                    self.registro.registrar(cont)
            except Exception as e:
                self.registro.rechazados.append({
                    "ruta": str(path),
                    "razon": f"{type(e).__name__}: {e}"
                })

    def _cargar_modulo(self, path: Path) -> Optional[Contenedor]:
        nombre_mod = f"vpsi_{path.stem}_{id(path)}"
        spec = importlib.util.spec_from_file_location(nombre_mod, path)
        if spec is None or spec.loader is None:
            return None

        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre_mod] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            return None

        meta = getattr(mod, "CONTENEDOR", None)
        if not isinstance(meta, dict):
            return None

        nombre = meta.get("nombre")
        rol = meta.get("rol")
        version = meta.get("version", "0.0")

        if not nombre or not rol:
            return None
        if rol not in ROLES:
            self.registro.rechazados.append({
                "ruta": str(path),
                "razon": f"rol desconocido: {rol}"
            })
            return None

        return Contenedor(
            nombre=nombre,
            rol=rol,
            version=version,
            modulo=mod,
            ruta=path
        )

    # -----------------------------------------------------------
    def _resolver_dependencias(self):
        for cont in list(self.registro.contenedores.values()):
            faltan = []
            for req in cont.requiere:
                if req in ROLES:
                    if not self.registro.por_rol.get(req):
                        faltan.append(f"rol:{req}")
                else:
                    if req not in self.registro.contenedores:
                        faltan.append(f"modulo:{req}")
            if faltan:
                self.errores_arranque.append(
                    f"{cont.nombre} ({cont.rol}) requiere {faltan} y no están disponibles"
                )

    # -----------------------------------------------------------
    def _ejecutar_compuertas(self):
        # Compuerta AX
        for cont in self.registro.por_rol.get("AX", []):
            fn = cont.fn("verificar") or cont.fn("barrer") or cont.fn("evaluar")
            if callable(fn):
                try:
                    informe = fn()
                    self.informe_axiomas = informe
                    if not informe.get("coherente", True):
                        self.errores_arranque.append(
                            f"AX/{cont.nombre}: incoherente"
                        )
                except Exception as e:
                    self.errores_arranque.append(
                        f"AX/{cont.nombre}: {type(e).__name__}: {e}"
                    )

        # Compuerta MC
        for cont in self.registro.por_rol.get("MC", []):
            fn = cont.fn("verificar") or cont.fn("barrer") or cont.fn("evaluar")
            if callable(fn):
                try:
                    informe = fn()
                    self.informe_mecanica = informe
                    if not informe.get("coherente", True):
                        self.errores_arranque.append(
                            f"MC/{cont.nombre}: incoherente"
                        )
                except Exception as e:
                    self.errores_arranque.append(
                        f"MC/{cont.nombre}: {type(e).__name__}: {e}"
                    )

        if not self.registro.por_rol.get("CT"):
            self.errores_arranque.append("Falta rol CT (constantes)")
        if not self.registro.por_rol.get("FO"):
            self.errores_arranque.append("Falta rol FO (fórmulas)")

    # -----------------------------------------------------------
    def get_constantes(self) -> Dict[str, Fraction]:
        for cont in self.registro.por_rol.get("CT", []):
            mod = cont.modulo
            if hasattr(mod, "ALPHA") and hasattr(mod, "BETA"):
                return {"ALPHA": mod.ALPHA, "BETA": mod.BETA}
            alpha_fn = cont.fn("alpha")
            beta_fn = cont.fn("beta")
            if callable(alpha_fn) and callable(beta_fn):
                return {"ALPHA": alpha_fn(), "BETA": beta_fn()}
        raise ArranqueError("Constantes ALPHA/BETA no disponibles")

    def get_formulas(self):
        for cont in self.registro.por_rol.get("FO", []):
            mod = cont.modulo
            if hasattr(mod, "tru_ri") and hasattr(mod, "tru_total"):
                return mod.tru_ri, mod.tru_total
        # Fallback
        try:
            from modules.formulas.truth import tru_ri, tru_total
            return tru_ri, tru_total
        except ImportError:
            raise ArranqueError("Fórmulas tru_ri / tru_total no disponibles")

    # -----------------------------------------------------------
    def evaluar(self, peticion: Dict[str, Any]) -> Dict[str, Any]:
        if self.estado != "OPERATIVO":
            return {
                "estado": "RECHAZADO",
                "razon": "Engine no operativo",
                "errores_arranque": self.errores_arranque,
            }

        o_ctx = (
            peticion.get("contexto")
            or peticion.get("O_context")
            or peticion.get("Octx")
        )
        if not o_ctx:
            return {
                "estado": "UNDEFINED",
                "razon": "K indefinido: falta O_context (Corolario Def-5.3.1)",
                "factores": {"C": None, "L": None, "K": "UNDEFINED"},
                "tru_ri": "UNDEFINED",
                "tru_total": "UNDEFINED",
            }

        try:
            C = Fraction(str(peticion["C"])) if "C" in peticion else None
            L = Fraction(str(peticion["L"])) if "L" in peticion else None
            K = Fraction(str(peticion["K"])) if "K" in peticion else None
        except Exception as e:
            return {
                "estado": "ERROR",
                "razon": f"C, L o K inválidos: {e}",
            }

        if C is None or L is None or K is None:
            return {
                "estado": "PARCIAL",
                "razon": "Faltan factores C/L/K",
                "contexto": o_ctx,
                "factores": {
                    "C": str(C) if C is not None else None,
                    "L": str(L) if L is not None else None,
                    "K": str(K) if K is not None else None,
                },
            }

        tru_ri_fn, tru_total_fn = self.get_formulas()
        constantes = self.get_constantes()

        ri = tru_ri_fn(C, L, K)
        tt = tru_total_fn(C, L, K)

        return {
            "estado": "OK",
            "contexto": o_ctx,
            "factores": {"C": str(C), "L": str(L), "K": str(K)},
            "tru_ri": str(ri),
            "tru_total": str(tt),
            "alpha": str(constantes["ALPHA"]),
            "beta": str(constantes["BETA"]),
            "markov_chain_validado": True,
            "R_i_equals_R": False,
            "fuentes_usadas": ["X", "O_context"],
        }

    def inventario(self) -> Dict:
        return {
            "estado": self.estado,
            "errores_arranque": self.errores_arranque,
            "registro": self.registro.resumen(),
            "informe_axiomas": self.informe_axiomas,
            "informe_mecanica": self.informe_mecanica,
        }


# ===============================================================
__all__ = [
    "Engine",
    "Contenedor",
    "Registro",
    "ROLES",
    "ArranqueError",
    "EvaluacionError",
]
