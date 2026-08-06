# ==============================================================
# INICIO: core/engine.py — versión corregida (separación arranque / ejecución)
# ==============================================================

# ilver
"""
VPSI-TRUTH --- core/engine.py

Kernel estructural.
Fase de arranque: solo descubre y valida.
Fase de ejecución: se realiza bajo demanda.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ===============================================================
# SECCIÓN 1: EXCEPCIONES Y ESTRUCTURAS BASE
# ===============================================================
class ArranqueError(Exception):
    pass


class Contenedor:
    def __init__(
        self,
        nombre: str,
        rol: str,
        version: str,
        modulo: Any,
        ruta: Path,
        meta: Dict[str, Any],
    ) -> None:
        self.nombre = nombre
        self.rol = rol
        self.version = version
        self.modulo = modulo
        self.ruta = ruta
        self.meta = meta
        self.capacidades = meta.get("capacidades", {})
        self.requiere = list(meta.get("requiere", []))
        self._fn_custom = meta.get("fn") if callable(meta.get("fn")) else None

    def fn(self, clave: str) -> Any:
        if self._fn_custom is not None:
            try:
                res = self._fn_custom(clave)
                if res is not None:
                    return res
            except Exception:
                pass
        ref = self.capacidades.get(clave)
        if callable(ref):
            return ref
        if isinstance(ref, str) and self.modulo is not None:
            return getattr(self.modulo, ref, None)
        return None


class RegistroModulos:
    def __init__(self) -> None:
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {}

    def registrar(self, cont: Contenedor) -> None:
        self.contenedores[cont.nombre] = cont
        self.por_rol.setdefault(cont.rol, []).append(cont)

    def primero(self, clave: str) -> Optional[Contenedor]:
        if clave in self.contenedores:
            return self.contenedores[clave]
        lista = self.por_rol.get(clave)
        return lista[0] if lista else None

    def total(self) -> int:
        return len(self.contenedores)


# ===============================================================
# SECCIÓN 2: ENGINE
# ===============================================================
class Engine:
    VERSION = "17.2-separacion-fases"

    def __init__(
        self,
        raiz_modulos: str | Path,
        invocador_id: str = "core",
        strict: bool = True,
    ) -> None:
        # 2.1 Parámetros
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id = invocador_id
        self.strict = strict

        # 2.2 Estado
        self.estado = "NO_INICIADO"

        # 2.3 Atributos exigidos por auditoría
        self.registro = RegistroModulos()
        self.resultados_evaluacion: List[Any] = []
        self.errores_arranque: List[str] = []
        self.fallos: List[Dict[str, Any]] = []
        self.advertencias: List[str] = []

        # 2.4 Evidencia
        self._modulos_descubiertos: List[Path] = []
        self._exploracion: Dict[str, Any] = {}
        self._inspeccion: Dict[str, Any] = {}
        self._resolucion: Dict[str, Any] = {}
        self._ejecucion: Dict[str, Any] = {}
        self._auditoria: Dict[str, Any] = {}
        self._grafo: Dict[str, Any] = {}
        self._dependencias: Dict[str, Any] = {}
        self._indice_simbolos: Dict[str, Dict[str, Any]] = {}
        self._diagnosticos_causales: List[Dict[str, Any]] = []

        # 2.5 Flujo de ARRANQUE (solo validación estructural)
        self._modulos_descubiertos = self._descubrir_modulos()
        self._cargar_y_validar()
        self._resolver_dependencias()
        self._construir_indice_simbolos()
        self._construir_grafo()

        # 2.6 Cierre
        if self.errores_arranque:
            self.estado = "RECHAZADO"
            if self.strict:
                raise ArranqueError(
                    "Engine no pudo arrancar:\n  - "
                    + "\n  - ".join(self.errores_arranque)
                )
        else:
            self.estado = "OPERATIVO"

    # ===========================================================
    # SECCIÓN 3: DESCUBRIDOR
    # ===========================================================
    def _descubrir_modulos(self) -> List[Path]:
        encontrados: List[Path] = []
        if not self.raiz.is_dir():
            return encontrados
        for path_dir in sorted(self.raiz.iterdir()):
            if path_dir.is_dir() and (path_dir / "__init__.py").is_file():
                encontrados.append(path_dir)
        return encontrados

    # ===========================================================
    # SECCIÓN 4: DIAGNÓSTICO CAUSAL
    # ===========================================================
    def _diagnosticar_import_error(self, path_dir: Path, error: Exception) -> Dict[str, Any]:
        mensaje = str(error)
        diag: Dict[str, Any] = {
            "modulo": path_dir.name,
            "fase": "Carga del contrato",
            "tipo_error": type(error).__name__,
            "mensaje": mensaje,
            "dependencia": None,
            "simbolo": None,
            "exportaciones_disponibles": [],
            "causa_raiz": None,
        }
        if isinstance(error, ImportError) and "cannot import name" in mensaje and " from " in mensaje:
            try:
                parte = mensaje.split("cannot import name ")[1]
                simbolo = parte.split("'")[1]
                modulo_origen = parte.split(" from '")[1].split("'")[0]
                diag["simbolo"] = simbolo
                diag["dependencia"] = modulo_origen
                try:
                    mod_destino = sys.modules.get(modulo_origen)
                    if mod_destino is None:
                        import importlib
                        mod_destino = importlib.import_module(modulo_origen)
                    diag["exportaciones_disponibles"] = [
                        n for n in dir(mod_destino) if not n.startswith("_")
                    ][:50]
                except Exception:
                    pass
                diag["causa_raiz"] = f"Símbolo '{simbolo}' no encontrado en '{modulo_origen}'."
            except Exception:
                diag["causa_raiz"] = "ImportError no parseable"
        else:
            diag["causa_raiz"] = f"{type(error).__name__}: {mensaje}"
        return diag

    # ===========================================================
    # SECCIÓN 5: LECTOR DE CONTRATO
    # ===========================================================
    def _leer_contrato(self, path_dir: Path) -> Optional[Dict[str, Any]]:
        init_path = path_dir / "__init__.py"
        nombre_mod = f"vpsi_dinamico_{path_dir.name}"
        try:
            spec = importlib.util.spec_from_file_location(
                nombre_mod, init_path, submodule_search_locations=[str(path_dir)]
            )
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[nombre_mod] = mod
            spec.loader.exec_module(mod)
            meta = getattr(mod, "CONTENEDOR", None)
            if not isinstance(meta, dict):
                return None
            return {
                "meta": meta,
                "modulo": mod,
                "ruta": init_path,
                "nombre_carpeta": path_dir.name,
            }
        except Exception as e:
            diag = self._diagnosticar_import_error(path_dir, e)
            self._diagnosticos_causales.append(diag)
            self.errores_arranque.append(
                f"{path_dir.name}: [{diag['tipo_error']}] "
                f"dep={diag.get('dependencia')} símbolo={diag.get('simbolo')} "
                f"→ {diag.get('causa_raiz')}"
            )
            return None

    # ===========================================================
    # SECCIÓN 6: VALIDADOR DE CONTRATO
    # ===========================================================
    def _validar_contrato(self, meta: Dict[str, Any], nombre_carpeta: str) -> List[str]:
        errores = []
        if not isinstance(meta.get("nombre"), str) or not meta["nombre"]:
            errores.append(f"{nombre_carpeta}: 'nombre' debe ser str no vacío")
        if not isinstance(meta.get("rol"), str) or not meta["rol"]:
            errores.append(f"{nombre_carpeta}: 'rol' debe ser str no vacío")
        if not isinstance(meta.get("version"), str):
            errores.append(f"{nombre_carpeta}: 'version' debe ser str")
        if not isinstance(meta.get("requiere"), list):
            errores.append(f"{nombre_carpeta}: 'requiere' debe ser list")
        caps = meta.get("capacidades")
        if not isinstance(caps, dict):
            errores.append(f"{nombre_carpeta}: 'capacidades' debe ser dict")
        else:
            for k in caps:
                if not isinstance(k, str):
                    errores.append(f"{nombre_carpeta}: clave de capacidad no es str: {k}")
        return errores

    # ===========================================================
    # SECCIÓN 7: EXPLORADOR
    # ===========================================================
    def _explorar_modulo(self, path_dir: Path) -> Dict[str, Any]:
        archivos, subcarpetas = [], []
        for p in path_dir.rglob("*"):
            if p.is_file():
                archivos.append(str(p.relative_to(self.raiz)))
            elif p.is_dir() and p != path_dir:
                subcarpetas.append(str(p.relative_to(self.raiz)))
        return {
            "archivos": sorted(archivos),
            "subcarpetas": sorted(subcarpetas),
            "total_archivos": len(archivos),
            "total_subcarpetas": len(subcarpetas),
        }

    # ===========================================================
    # SECCIÓN 8: INSPECTOR AST
    # ===========================================================
    def _inspeccionar_archivo(self, archivo: Path) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "funciones": [], "clases": [], "constantes": [],
            "imports": [], "doc": None
        }
        try:
            fuente = archivo.read_text(encoding="utf-8")
            tree = ast.parse(fuente, filename=str(archivo))
            info["doc"] = ast.get_docstring(tree)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    info["funciones"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    info["clases"].append(node.name)
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name) and t.id.isupper():
                            info["constantes"].append(t.id)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    info["imports"].append(ast.dump(node))
        except Exception:
            pass
        return info

    def _inspeccionar_modulo(self, path_dir: Path) -> Dict[str, Any]:
        resultado = {}
        for py in path_dir.rglob("*.py"):
            rel = str(py.relative_to(self.raiz))
            resultado[rel] = self._inspeccionar_archivo(py)
        return resultado

    # ===========================================================
    # SECCIÓN 9: RESOLVER CAPACIDADES
    # ===========================================================
    def _resolver_capacidades(self, cont: Contenedor) -> Dict[str, Any]:
        resultado = {"resolubles": [], "no_resolubles": [], "total": 0}
        for clave in cont.capacidades:
            resultado["total"] += 1
            if callable(cont.fn(clave)):
                resultado["resolubles"].append(clave)
            else:
                resultado["no_resolubles"].append(clave)
        return resultado

    # ===========================================================
    # SECCIÓN 10: EJECUCIÓN DEL CONTRATO (bajo demanda)
    # ===========================================================
    def _ejecutar_contrato(self, cont: Contenedor) -> Dict[str, Any]:
        """
        Ejecuta las capacidades del contrato.
        Esta función NO se llama durante el arranque.
        Se usa solo cuando se solicita explícitamente.
        """
        resultados = {}
        for clave in cont.capacidades:
            fn = cont.fn(clave)
            if not callable(fn):
                resultados[clave] = {
                    "estado": "NO_CALLABLE",
                    "error": "La capacidad declarada no es ejecutable",
                }
                continue

            inicio = time.perf_counter()
            try:
                salida = fn()
                duracion = time.perf_counter() - inicio
                resultados[clave] = {
                    "estado": "EXITO",
                    "resultado": salida,
                    "duracion_s": round(duracion, 6),
                }
            except Exception as e:
                duracion = time.perf_counter() - inicio
                resultados[clave] = {
                    "estado": "ERROR_EJECUCION",
                    "error": f"{type(e).__name__}: {e}",
                    "duracion_s": round(duracion, 6),
                }
        return resultados

    def ejecutar_contrato(self, nombre_o_rol: str) -> Dict[str, Any]:
        """API pública: ejecuta el contrato de un módulo bajo demanda."""
        cont = self.registro.primero(nombre_o_rol)
        if cont is None:
            return {"error": f"No se encontró módulo o rol: {nombre_o_rol}"}
        resultado = self._ejecutar_contrato(cont)
        self._ejecucion[cont.nombre] = resultado
        return resultado

    # ===========================================================
    # SECCIÓN 11: AUDITOR (solo validación estructural)
    # ===========================================================
    def _auditar(self, cont: Contenedor, resolucion: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "nombre": cont.nombre,
            "rol": cont.rol,
            "version": cont.version,
            "requiere": list(cont.requiere),
            "resolucion": resolucion,
            "coherente": len(resolucion.get("no_resolubles", [])) == 0,
        }

    # ===========================================================
    # SECCIÓN 12: RESOLUCIÓN DE DEPENDENCIAS
    # ===========================================================
    def _resolver_dependencias(self) -> None:
        roles_presentes = set(self.registro.por_rol.keys())
        faltantes: Dict[str, List[str]] = defaultdict(list)
        grafo_dep: Dict[str, List[str]] = defaultdict(list)

        for nombre, cont in self.registro.contenedores.items():
            for dep in cont.requiere:
                grafo_dep[nombre].append(dep)
                if dep not in roles_presentes and dep not in self.registro.contenedores:
                    faltantes[nombre].append(dep)
                    self.errores_arranque.append(
                        f"{cont.rol}/{nombre}: dependencia inexistente → '{dep}'"
                    )

        in_degree = {n: 0 for n in self.registro.contenedores}
        for src, dests in grafo_dep.items():
            for d in dests:
                if d in in_degree:
                    in_degree[d] += 1

        cola = deque([n for n, deg in in_degree.items() if deg == 0])
        orden = []
        while cola:
            n = cola.popleft()
            orden.append(n)
            for d in grafo_dep.get(n, []):
                if d in in_degree:
                    in_degree[d] -= 1
                    if in_degree[d] == 0:
                        cola.append(d)

        ciclos = [n for n, deg in in_degree.items() if deg > 0]
        if ciclos:
            self.errores_arranque.append(f"Ciclos de dependencia detectados: {ciclos}")

        self._dependencias = {
            "grafo": dict(grafo_dep),
            "faltantes": dict(faltantes),
            "orden_topologico": orden,
            "ciclos": ciclos,
        }

    # ===========================================================
    # SECCIÓN 13: ÍNDICE DE SÍMBOLOS
    # ===========================================================
    def _construir_indice_simbolos(self) -> None:
        for nombre, cont in self.registro.contenedores.items():
            inspeccion = self._inspeccion.get(nombre, {})
            simbolos = {
                "clases": [],
                "funciones": [],
                "constantes": [],
                "capacidades": list(cont.capacidades.keys()),
            }
            for info in inspeccion.values():
                simbolos["clases"].extend(info.get("clases", []))
                simbolos["funciones"].extend(info.get("funciones", []))
                simbolos["constantes"].extend(info.get("constantes", []))
            for k in ("clases", "funciones", "constantes"):
                simbolos[k] = sorted(set(simbolos[k]))
            self._indice_simbolos[nombre] = simbolos

    # ===========================================================
    # SECCIÓN 14: GRAFO
    # ===========================================================
    def _construir_grafo(self) -> None:
        nodos, aristas = [], []
        for nombre, cont in self.registro.contenedores.items():
            nodos.append({"id": nombre, "tipo": "modulo", "rol": cont.rol})
            aristas.append({"from": nombre, "to": cont.rol, "tipo": "tiene_rol"})
            for cap in cont.capacidades:
                aristas.append({"from": nombre, "to": f"{nombre}.{cap}", "tipo": "declara_capacidad"})
            for dep in cont.requiere:
                aristas.append({"from": nombre, "to": dep, "tipo": "requiere"})
            for archivo in self._exploracion.get(nombre, {}).get("archivos", []):
                aristas.append({"from": nombre, "to": archivo, "tipo": "contiene_archivo"})
        self._grafo = {"nodos": nodos, "aristas": aristas}

    # ===========================================================
    # SECCIÓN 15: ORQUESTACIÓN DE ARRANQUE (solo validación)
    # ===========================================================
    def _cargar_y_validar(self) -> None:
        for path_dir in self._modulos_descubiertos:
            leido = self._leer_contrato(path_dir)
            if leido is None:
                continue

            meta = leido["meta"]
            nombre_carpeta = leido["nombre_carpeta"]

            errores = self._validar_contrato(meta, nombre_carpeta)
            if errores:
                self.errores_arranque.extend(errores)
                continue

            nombre = meta["nombre"]
            rol = meta["rol"]
            version = str(meta.get("version", "1.0"))

            cont = Contenedor(
                nombre=nombre,
                rol=rol,
                version=version,
                modulo=leido["modulo"],
                ruta=leido["ruta"],
                meta=meta,
            )
            self.registro.registrar(cont)

            self._exploracion[nombre] = self._explorar_modulo(path_dir)
            self._inspeccion[nombre] = self._inspeccionar_modulo(path_dir)

            # Solo resolución (no ejecución)
            resolucion = self._resolver_capacidades(cont)
            self._resolucion[nombre] = resolucion

            # Ejecución queda pendiente
            self._ejecucion[nombre] = {"estado": "PENDIENTE"}

            # Auditoría estructural
            auditoria = self._auditar(cont, resolucion)
            self._auditoria[nombre] = auditoria

            if not auditoria["coherente"]:
                self.errores_arranque.append(
                    f"{rol}/{nombre}: capacidades no resolubles: "
                    f"{resolucion.get('no_resolubles')}"
                )

    # ===========================================================
    # SECCIÓN 16: ESTADO GLOBAL
    # ===========================================================
    def estado_global(self) -> Dict[str, Any]:
        return {
            "tipo": "estado_global",
            "version_engine": self.VERSION,
            "estado": self.estado,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_contenedores": self.registro.total(),
            "roles": {
                rol: [c.nombre for c in lista]
                for rol, lista in self.registro.por_rol.items()
            },
            "cargados": [
                {
                    "nombre": c.nombre,
                    "rol": c.rol,
                    "version": c.version,
                    "requiere": list(c.requiere),
                    "capacidades_declaradas": list(c.capacidades.keys()),
                }
                for c in self.registro.contenedores.values()
            ],
            "exploracion": self._exploracion,
            "inspeccion": self._inspeccion,
            "resolucion": self._resolucion,
            "ejecucion": self._ejecucion,
            "auditoria": self._auditoria,
            "grafo": self._grafo,
            "dependencias": self._dependencias,
            "indice_simbolos": self._indice_simbolos,
            "diagnosticos_causales": self._diagnosticos_causales,
            "errores_arranque": list(self.errores_arranque),
            "advertencias": list(self.advertencias),
            "nota": (
                "Estado global. "
                "Arranque = solo validación estructural. "
                "Ejecución de contratos se realiza bajo demanda."
            ),
        }

    # ===========================================================
    # SECCIÓN 17: COMPATIBILIDAD
    # ===========================================================
    def censar(self) -> dict:
        eg = self.estado_global()
        return {
            "total": eg["total_contenedores"],
            "roles": eg["roles"],
            "roles_vacios": [],
            "rechazados": eg["errores_arranque"],
            "cargados": eg["cargados"],
        }

    def ejecutar_contratos_y_explorar(self) -> Dict[str, Any]:
        return self._ejecucion

# ===========================================================
# SECCIÓN 18: LOCALIZADOR UNIVERSAL DE IDs (corregido)
# ===========================================================
def localizar_id(self, identificador: str) -> Dict[str, Any]:
    resultado = {
        "id": identificador,
        "encontrado": False,
        "tipo": None,
        "modulo": None,
        "rol": None,
        "detalle": None,
    }

    # Rol
    if identificador in self.registro.por_rol:
        resultado.update({
            "encontrado": True,
            "tipo": "rol",
            "rol": identificador,
            "detalle": [c.nombre for c in self.registro.por_rol[identificador]],
        })
        return resultado

    # Módulo
    if identificador in self.registro.contenedores:
        cont = self.registro.contenedores[identificador]
        resultado.update({
            "encontrado": True,
            "tipo": "modulo",
            "modulo": cont.nombre,
            "rol": cont.rol,
            "detalle": {
                "version": cont.version,
                "capacidades": list(cont.capacidades.keys()),
                "ruta": str(cont.ruta),
            },
        })
        return resultado

    # Capacidad
    for nombre, cont in self.registro.contenedores.items():
        if identificador in cont.capacidades:
            resultado.update({
                "encontrado": True,
                "tipo": "capacidad",
                "modulo": cont.nombre,
                "rol": cont.rol,
                "detalle": {"capacidad": identificador},
            })
            return resultado

    # Símbolo
    for nombre, simbolos in self._indice_simbolos.items():
        for tipo_sim in ("clases", "funciones", "constantes"):
            if identificador in simbolos.get(tipo_sim, []):
                resultado.update({
                    "encontrado": True,
                    "tipo": tipo_sim[:-1],
                    "modulo": nombre,
                    "detalle": {"simbolo": identificador},
                })
                return resultado

    # Archivo (usa índice de rutas si existe)
    if hasattr(self, "_indice_rutas") and identificador in self._indice_rutas:
        info = self._indice_rutas[identificador]
        resultado.update({
            "encontrado": True,
            "tipo": "archivo",
            "modulo": info.get("modulo"),
            "detalle": info,
        })
        return resultado

    # Fallback: búsqueda lineal en exploración
    for nombre, data in self._exploracion.items():
        if identificador in data.get("archivos", []):
            resultado.update({
                "encontrado": True,
                "tipo": "archivo",
                "modulo": nombre,
                "detalle": {"ruta": identificador},
            })
            return resultado

    return resultado


def buscar_simbolo(self, nombre: str) -> Dict[str, Any]:
    return self.localizar_id(nombre)

def buscar_rol(self, rol: str) -> Dict[str, Any]:
    return self.localizar_id(rol)

def buscar_capacidad(self, nombre: str) -> Dict[str, Any]:
    return self.localizar_id(nombre)

def buscar_modulo(self, nombre: str) -> Dict[str, Any]:
    return self.localizar_id(nombre)

def buscar_archivo(self, ruta: str) -> Dict[str, Any]:
    return self.localizar_id(ruta)


# ===========================================================
# SECCIÓN 19: RESOLVEDOR UNIVERSAL (corregido)
# ===========================================================
def _invocar_capacidad(self, fn, cont: Contenedor) -> Any:
    """
    Invoca la función de forma determinista inspeccionando la firma.
    No usa TypeError para adivinar.
    """
    import inspect
    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        # Si acepta al menos un parámetro posicional o keyword, intentamos pasar contexto
        if params and (
            params[0].kind in (inspect.Parameter.POSITIONAL_ONLY,
                               inspect.Parameter.POSITIONAL_OR_KEYWORD)
            or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)
        ):
            ctx = self._preparar_contexto(cont)
            return fn(ctx)
        return fn()
    except Exception:
        # Si la inspección falla, se intenta sin argumentos
        return fn()


def ejecutar_capacidad(self, modulo_o_rol: str, capacidad: str) -> Dict[str, Any]:
    cont = self.registro.primero(modulo_o_rol)
    if cont is None:
        return {"error": f"Módulo/rol no encontrado: {modulo_o_rol}"}

    fn = cont.fn(capacidad)
    if not callable(fn):
        return {"error": f"Capacidad '{capacidad}' no es ejecutable"}

    inicio = time.perf_counter()
    try:
        resultado = self._invocar_capacidad(fn, cont)
        duracion = time.perf_counter() - inicio
        validacion = self._validar_resultado(capacidad, resultado)
        salida = {
            "estado": "EXITO",
            "resultado": resultado,
            "duracion_s": round(duracion, 6),
            "validacion": validacion,
        }
        self._registrar_traza("ejecutar_capacidad", {
            "modulo": cont.nombre,
            "capacidad": capacidad,
            "estado": "EXITO",
        })
        return salida
    except Exception as e:
        duracion = time.perf_counter() - inicio
        self._registrar_traza("ejecutar_capacidad", {
            "modulo": cont.nombre,
            "capacidad": capacidad,
            "estado": "ERROR",
            "error": str(e),
        })
        return {
            "estado": "ERROR_EJECUCION",
            "error": f"{type(e).__name__}: {e}",
            "duracion_s": round(duracion, 6),
        }


def ejecutar_contrato(self, nombre_o_rol: str) -> Dict[str, Any]:
    cont = self.registro.primero(nombre_o_rol)
    if cont is None:
        return {"error": f"No se encontró módulo o rol: {nombre_o_rol}"}

    resultados = {}
    for clave in cont.capacidades:
        resultados[clave] = self.ejecutar_capacidad(cont.nombre, clave)

    self._ejecucion[cont.nombre] = resultados
    self._registrar_traza("ejecutar_contrato", {
        "modulo": cont.nombre,
        "capacidades": list(resultados.keys()),
    })
    return resultados


def ejecutar_modulo(self, nombre_o_rol: str) -> Dict[str, Any]:
    return self.ejecutar_contrato(nombre_o_rol)


def ejecutar_rol(self, rol: str) -> Dict[str, Any]:
    resultados = {}
    for cont in self.registro.por_rol.get(rol, []):
        resultados[cont.nombre] = self.ejecutar_contrato(cont.nombre)
    return resultados


def ejecutar_todo(self) -> Dict[str, Any]:
    resultados = {}
    for nombre in list(self.registro.contenedores.keys()):
        resultados[nombre] = self.ejecutar_contrato(nombre)
    return resultados


# ===========================================================
# SECCIÓN 20: CONTEXTO DE EJECUCIÓN
# ===========================================================
def _preparar_contexto(self, cont: Contenedor) -> Dict[str, Any]:
    return {
        "engine": self,
        "contenedor": cont,
        "nombre": cont.nombre,
        "rol": cont.rol,
        "registro": self.registro,
    }


# ===========================================================
# SECCIÓN 21: VALIDADOR DEL RESULTADO
# ===========================================================
def _validar_resultado(self, capacidad: str, resultado: Any) -> Dict[str, Any]:
    informe = {
        "capacidad": capacidad,
        "valido": True,
        "problemas": [],
    }
    if resultado is None:
        informe["valido"] = False
        informe["problemas"].append("resultado es None")
    return informe


# ===========================================================
# SECCIÓN 22: DETECTOR DE CONTRADICCIONES
# ===========================================================
def detectar_contradicciones(self) -> List[Dict[str, Any]]:
    contradicciones = []
    for nombre, resol in self._resolucion.items():
        for cap in resol.get("no_resolubles", []):
            contradicciones.append({
                "tipo": "capacidad_no_resoluble",
                "modulo": nombre,
                "capacidad": cap,
            })
    for nombre, deps in self._dependencias.get("faltantes", {}).items():
        for dep in deps:
            contradicciones.append({
                "tipo": "dependencia_inexistente",
                "modulo": nombre,
                "dependencia": dep,
            })
    for ciclo in self._dependencias.get("ciclos", []):
        contradicciones.append({
            "tipo": "ciclo_dependencia",
            "modulo": ciclo,
        })
    return contradicciones


# ===========================================================
# SECCIÓN 23: INVENTARIO GLOBAL
# ===========================================================
def inventario_global(self) -> Dict[str, Any]:
    return {
        "modulos": list(self.registro.contenedores.keys()),
        "roles": list(self.registro.por_rol.keys()),
        "total_modulos": self.registro.total(),
        "total_roles": len(self.registro.por_rol),
        "capacidades": {
            nombre: list(cont.capacidades.keys())
            for nombre, cont in self.registro.contenedores.items()
        },
        "simbolos": self._indice_simbolos,
        "archivos": {
            nombre: data.get("archivos", [])
            for nombre, data in self._exploracion.items()
        },
        "dependencias": self._dependencias,
        "grafo": self._grafo,
        "contradicciones": self.detectar_contradicciones(),
    }


# ===========================================================
# SECCIÓN 24: ÍNDICE GLOBAL + ÍNDICE DE RUTAS
# ===========================================================
def _construir_indice_rutas(self) -> None:
    """Construye índice de rutas durante el arranque (O(1) después)."""
    self._indice_rutas: Dict[str, Dict[str, Any]] = {}
    for nombre, data in self._exploracion.items():
        for ruta in data.get("archivos", []):
            self._indice_rutas[ruta] = {
                "modulo": nombre,
                "ruta": ruta,
            }


def indice_global(self) -> Dict[str, Any]:
    indice: Dict[str, List[Dict[str, Any]]] = {}
    for rol in self.registro.por_rol:
        indice.setdefault(rol, []).append({"tipo": "rol"})
    for nombre, cont in self.registro.contenedores.items():
        indice.setdefault(nombre, []).append({"tipo": "modulo", "rol": cont.rol})
        for cap in cont.capacidades:
            indice.setdefault(cap, []).append({"tipo": "capacidad", "modulo": nombre})
    for nombre, simbolos in self._indice_simbolos.items():
        for tipo_sim, lista in simbolos.items():
            if tipo_sim == "capacidades":
                continue
            for sim in lista:
                indice.setdefault(sim, []).append({"tipo": tipo_sim[:-1], "modulo": nombre})
    return indice


# ===========================================================
# SECCIÓN 25: TRAZABILIDAD
# ===========================================================
def _registrar_traza(self, evento: str, detalle: Dict[str, Any]) -> None:
    if not hasattr(self, "_trazas"):
        self._trazas: List[Dict[str, Any]] = []
    self._trazas.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evento": evento,
        "detalle": detalle,
    })


def obtener_trazas(self) -> List[Dict[str, Any]]:
    return list(getattr(self, "_trazas", []))


# ===========================================================
# SECCIÓN 26: API UNIVERSAL + LECTOR DE ARCHIVOS
# ===========================================================
def leer_archivo(self, ruta_relativa: str, modo: str = "texto") -> Any:
    """
    Lector universal de archivos del repositorio.
    modo: "texto" | "bytes" | "json"
    """
    # Buscar la ruta absoluta a partir del índice o de la exploración
    ruta_abs = None
    if hasattr(self, "_indice_rutas") and ruta_relativa in self._indice_rutas:
        # Reconstruir ruta absoluta
        for nombre, data in self._exploracion.items():
            if ruta_relativa in data.get("archivos", []):
                # La ruta relativa es respecto a self.raiz
                ruta_abs = self.raiz / ruta_relativa
                break
    else:
        ruta_abs = self.raiz / ruta_relativa

    if ruta_abs is None or not ruta_abs.is_file():
        return {"error": f"Archivo no encontrado: {ruta_relativa}"}

    try:
        if modo == "bytes":
            return ruta_abs.read_bytes()
        if modo == "json":
            import json
            return json.loads(ruta_abs.read_text(encoding="utf-8"))
        # por defecto texto
        return ruta_abs.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def grafo_global(self) -> Dict[str, Any]:
    return self._grafo

def dependencias_globales(self) -> Dict[str, Any]:
    return self._dependencias

def auditoria_global(self) -> Dict[str, Any]:
    return self._auditoria

def indice_simbolos(self) -> Dict[str, Any]:
    return self._indice_simbolos

# ===========================================================
# SECCIÓN 27: ÍNDICE DE RUTAS + LECTOR UNIVERSAL (corregida)
# ===========================================================

def _construir_indice_rutas(self) -> None:
    """
    Construye el índice de rutas y el índice inverso por nombre de archivo.
    Debe llamarse una vez durante el arranque.
    """
    self._indice_rutas = {}
    self._indice_nombre_archivo = {}

    for nombre_modulo, data in self._exploracion.items():
        for ruta_rel in data.get("archivos", []):
            ruta_abs = str((self.raiz / ruta_rel).resolve())
            self._indice_rutas[ruta_rel] = {
                "modulo": nombre_modulo,
                "ruta_relativa": ruta_rel,
                "ruta_absoluta": ruta_abs,
            }
            nombre = Path(ruta_rel).name
            self._indice_nombre_archivo.setdefault(nombre, []).append(ruta_rel)


def leer_archivo(self, identificador: str, modo: str = "texto") -> Any:
    """
    Lector universal de archivos del repositorio.

    identificador: ruta relativa o nombre de archivo.
    modo: "texto" | "bytes" | "json" | "lineas"
    """
    info = self._indice_rutas.get(identificador)

    # Si no se encontró por ruta exacta, intentar por nombre de archivo
    if info is None:
        rutas = self._indice_nombre_archivo.get(identificador, [])
        if len(rutas) == 1:
            info = self._indice_rutas.get(rutas[0])
        elif len(rutas) > 1:
            return {
                "encontrado": False,
                "error": f"Nombre ambiguo '{identificador}'. Rutas posibles: {rutas}",
            }

    if info is None:
        return {
            "encontrado": False,
            "error": f"Archivo no encontrado: {identificador}",
        }

    ruta_abs = Path(info["ruta_absoluta"])
    if not ruta_abs.is_file():
        return {
            "encontrado": False,
            "error": f"Ruta indexada pero archivo inexistente en disco: {ruta_abs}",
        }

    try:
        if modo == "bytes":
            contenido = ruta_abs.read_bytes()
        elif modo == "json":
            import json
            contenido = json.loads(ruta_abs.read_text(encoding="utf-8"))
        elif modo == "lineas":
            contenido = ruta_abs.read_text(encoding="utf-8").splitlines()
        else:
            contenido = ruta_abs.read_text(encoding="utf-8")

        return {
            "encontrado": True,
            "ruta_relativa": info["ruta_relativa"],
            "ruta_absoluta": info["ruta_absoluta"],
            "modulo": info["modulo"],
            "modo": modo,
            "contenido": contenido,
        }
    except Exception as e:
        return {
            "encontrado": True,
            "error": f"{type(e).__name__}: {e}",
            "ruta_relativa": info["ruta_relativa"],
            "modulo": info["modulo"],
        }


def leer_texto(self, identificador: str) -> Any:
    return self.leer_archivo(identificador, modo="texto")


def leer_bytes(self, identificador: str) -> Any:
    return self.leer_archivo(identificador, modo="bytes")


def leer_json(self, identificador: str) -> Any:
    return self.leer_archivo(identificador, modo="json")


def leer_lineas(self, identificador: str) -> Any:
    return self.leer_archivo(identificador, modo="lineas")


def listar_archivos(self, modulo: str = None) -> List[str]:
    if modulo is None:
        return sorted(self._indice_rutas.keys())
    return sorted(
        ruta for ruta, info in self._indice_rutas.items()
        if info.get("modulo") == modulo
    )
# ==============================================================
# FIN: core/engine.py — versión corregida (separación arranque / ejecución)
# ==============================================================
