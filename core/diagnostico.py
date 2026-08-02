"""
core/diagnostico.py
===================
Diagnóstico global del sistema VPSI-TRUTH.

Poder: conocer todo lo observable del grafo.
Poder de actuación: ninguno.

- No arranca ni detiene el Engine.
- No modifica módulos, axiomas ni estado de negocio.
- No calcula Tru_total.
- Solo inspecciona y agrega.

Omega Report señala la herida (dónde).
Este módulo señala la causa raíz y el % global (por qué / cuánto).

Uso típico:
    from core.engine import Engine
    from core.diagnostico import DiagnosticoGlobal

    eng = Engine(...)
    informe = DiagnosticoGlobal.censo(eng, repo_root=Path("."))
    # anexar informe a Omega / JSON
"""

from __future__ import annotations

import ast
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Errores propios (no de negocio)
# ---------------------------------------------------------------------------
class DiagnosticoError(Exception):
    """Error interno del diagnóstico (forma de entrada, no del sistema medido)."""


# ---------------------------------------------------------------------------
# Pesos del % global (explícitos, auditables, fase actual)
# Suma = 1.0
# ---------------------------------------------------------------------------
PESOS: Dict[str, float] = {
    "engine_operativo": 0.15,
    "obligatorios_presentes": 0.12,
    "sin_rechazados": 0.08,
    "axiomas_coherente": 0.12,
    "formulas_coherente": 0.08,
    "mecanica_coherente": 0.06,
    "capacidades_resolubles": 0.12,
    "tr1_canonica_completa": 0.10,
    "tr1_generativo_minimo": 0.07,
    "tests_ok": 0.10,
}

# Roles que el mapa trata como pendientes de modules/ (no son fallo de core)
ROLES_FASE_PENDIENTE = frozenset({"SF"})  # DG ya no es módulo


# ---------------------------------------------------------------------------
# Helpers de lectura (sin side-effects de negocio)
# ---------------------------------------------------------------------------
def _safe_undefined_check(obj: Any) -> bool:
    try:
        from core.engine import es_undefined
        return bool(es_undefined(obj))
    except Exception:
        return obj is None


def _listar_py(dir_path: Path) -> List[str]:
    if not dir_path.is_dir():
        return []
    return sorted(
        p.name for p in dir_path.iterdir()
        if p.is_file() and p.suffix == ".py" and not p.name.startswith(".")
    )


def _intentar_contenedor(mod_dir: Path) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Lee CONTENEDOR sin ejecutar lógica de negocio pesada.
    Preferencia: import del paquete; fallback: AST del __init__.py.
    """
    init = mod_dir / "__init__.py"
    if not init.exists():
        return None, "sin __init__.py"

    # 1) import
    nombre = mod_dir.name
    try:
        # garantiza root en path
        root = mod_dir.parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        import importlib
        pkg = f"modules.{nombre}"
        if pkg in sys.modules:
            mod = importlib.reload(sys.modules[pkg])
        else:
            mod = importlib.import_module(pkg)
        cont = getattr(mod, "CONTENEDOR", None)
        if isinstance(cont, dict) and cont.get("rol"):
            return dict(cont), None
        return None, "CONTENEDOR ausente o sin rol"
    except Exception as e:
        err_import = f"{type(e).__name__}: {e}"

    # 2) AST mínimo (solo literales del dict CONTENEDOR si es posible)
    try:
        tree = ast.parse(init.read_text(encoding="utf-8"), filename=str(init))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "CONTENEDOR":
                        if isinstance(node.value, ast.Dict):
                            # no evaluamos callables; solo metadatos literales
                            meta: Dict[str, Any] = {}
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, ast.Constant) and isinstance(
                                    v, (ast.Constant, ast.List, ast.Tuple)
                                ):
                                    try:
                                        meta[str(k.value)] = ast.literal_eval(v)
                                    except Exception:
                                        pass
                            if meta.get("rol"):
                                return meta, f"parcial_ast; import_fallo={err_import}"
        return None, err_import
    except Exception as e:
        return None, f"import:{err_import}; ast:{type(e).__name__}: {e}"


def _cargar_tests_xml(diagnostics_dir: Path) -> Optional[Dict[str, Any]]:
    xml_path = diagnostics_dir / "test_results.xml"
    if not xml_path.exists():
        return None
    try:
        import xml.etree.ElementTree as ET
        raiz = ET.parse(xml_path).getroot()
        suites = (
            [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
        )
        total = fallos = errores = omitidos = 0
        for s in suites:
            total += int(s.get("tests", 0) or 0)
            fallos += int(s.get("failures", 0) or 0)
            errores += int(s.get("errors", 0) or 0)
            omitidos += int(s.get("skipped", 0) or 0)
        fallidos = fallos + errores
        pasados = max(total - fallidos - omitidos, 0)
        tasa = (pasados / total * 100.0) if total else 0.0
        return {
            "total": total,
            "pasados": pasados,
            "fallidos": fallidos,
            "omitidos": omitidos,
            "tasa": round(tasa, 2),
            "fuente": str(xml_path),
        }
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Núcleo de censo
# ---------------------------------------------------------------------------
class DiagnosticoGlobal:
    """
    Censo de solo lectura del grafo VPSI-TRUTH.
    No actúa. Solo reporta.
    """

    @staticmethod
    def censo(
        engine: Any,
        repo_root: Optional[Path] = None,
        diagnostics_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Inspección completa.

        Parámetros
        ----------
        engine : instancia ya construida de core.engine.Engine
        repo_root : raíz del repo (padre de core/ y modules/)
        diagnostics_dir : donde está test_results.xml / omega artifacts

        Retorna dict listo para JSON y para anexar al Omega Report.
        """
        if engine is None:
            raise DiagnosticoError("engine es obligatorio para el censo")

        root = Path(repo_root) if repo_root else Path.cwd()
        modules_dir = root / "modules"
        core_dir = root / "core"
        diag_dir = (
            Path(diagnostics_dir)
            if diagnostics_dir
            else root / "diagnostics"
        )

        stamp = datetime.now(timezone.utc).isoformat()
        factores: Dict[str, Dict[str, Any]] = {}
        causas: List[Dict[str, str]] = []
        detalle_modulos: List[Dict[str, Any]] = []

        # ----- 1. Engine -----
        estado = getattr(engine, "estado", None)
        errores_arr = list(getattr(engine, "errores_arranque", None) or [])
        engine_ok = estado == "OPERATIVO"
        factores["engine_operativo"] = {
            "ok": engine_ok,
            "valor": 1.0 if engine_ok else 0.0,
            "detalle": {"estado": estado, "errores_arranque": errores_arr[:10]},
        }
        if not engine_ok:
            causas.append({
                "factor": "engine_operativo",
                "herida": "Engine no OPERATIVO",
                "raiz": "; ".join(str(e) for e in errores_arr[:5]) or "estado ≠ OPERATIVO",
            })

        # ----- 2. Registro -----
        registro: Dict[str, Any] = {}
        try:
            if hasattr(engine, "censar"):
                registro = engine.censar() or {}
            elif hasattr(engine, "registro") and hasattr(engine.registro, "resumen"):
                registro = engine.registro.resumen() or {}
        except Exception as e:
            registro = {"error": f"{type(e).__name__}: {e}"}

        roles = registro.get("roles") or {}
        vacios = list(registro.get("roles_vacios") or [])
        rechazados = list(registro.get("rechazados") or [])
        total_cont = int(registro.get("total") or 0)

        # obligatorios
        try:
            from core.engine import OBLIGATORIOS
            oblig = tuple(OBLIGATORIOS)
        except Exception:
            oblig = ("AX", "CT", "FO", "MC")  # mínimo defensivo

        faltan_obl = [r for r in oblig if not (roles.get(r))]
        obl_ok = len(faltan_obl) == 0
        factores["obligatorios_presentes"] = {
            "ok": obl_ok,
            "valor": 1.0 if obl_ok else max(0.0, 1.0 - len(faltan_obl) / max(len(oblig), 1)),
            "detalle": {"obligatorios": list(oblig), "faltan": faltan_obl},
        }
        if not obl_ok:
            causas.append({
                "factor": "obligatorios_presentes",
                "herida": f"faltan roles {faltan_obl}",
                "raiz": "CONTENEDOR ausente, rol mal declarado o rechazo en arranque",
            })

        sin_rech = len(rechazados) == 0
        factores["sin_rechazados"] = {
            "ok": sin_rech,
            "valor": 1.0 if sin_rech else 0.0,
            "detalle": {"n": len(rechazados), "muestra": rechazados[:5]},
        }
        if not sin_rech:
            causas.append({
                "factor": "sin_rechazados",
                "herida": f"{len(rechazados)} módulo(s) rechazado(s)",
                "raiz": "rol no admitido o CONTENEDOR inválido",
            })

        # ----- 3. Axiomas / FO / MC -----
        ia = getattr(engine, "informe_axiomas", None) or {}
        if not ia and hasattr(engine, "ejecutar_capacidad"):
            try:
                out = engine.ejecutar_capacidad("AX", "verificar")
                if not _safe_undefined_check(out) and isinstance(out, dict):
                    ia = out
            except Exception:
                pass
        ax_ok = bool(ia.get("coherente")) if ia else False
        factores["axiomas_coherente"] = {
            "ok": ax_ok,
            "valor": 1.0 if ax_ok else 0.0,
            "detalle": {
                "declaraciones": ia.get("declaraciones"),
                "choques": len(ia.get("choques") or []),
                "errores": len(ia.get("errores") or []),
            },
        }
        if not ax_ok:
            causas.append({
                "factor": "axiomas_coherente",
                "herida": "AX incoherente o sin informe",
                "raiz": "choques/errores en declaraciones o capacidad verificar fallida",
            })

        fo: Dict[str, Any] = {}
        if hasattr(engine, "ejecutar_capacidad"):
            for cap in ("verificar", "barrer"):
                try:
                    out = engine.ejecutar_capacidad("FO", cap)
                    if not _safe_undefined_check(out) and isinstance(out, dict):
                        fo = out
                        break
                except Exception:
                    continue
        fo_ok = bool(fo.get("coherente")) if fo else False
        factores["formulas_coherente"] = {
            "ok": fo_ok,
            "valor": 1.0 if fo_ok else 0.0,
            "detalle": {" cohere": fo.get("coherente"), "faltas": fo.get("faltas")},
        }
        if not fo_ok:
            causas.append({
                "factor": "formulas_coherente",
                "herida": "FO incoherente o no respondió",
                "raiz": "barrer/verificar FO o CONTENEDOR FO",
            })

        im = getattr(engine, "informe_mecanica", None) or {}
        if not im and hasattr(engine, "ejecutar_capacidad"):
            for cap in ("verificar", "barrer"):
                try:
                    out = engine.ejecutar_capacidad("MC", cap)
                    if not _safe_undefined_check(out) and isinstance(out, dict):
                        im = out
                        break
                except Exception:
                    continue
        mc_ok = bool(im.get("coherente")) if im else False
        factores["mecanica_coherente"] = {
            "ok": mc_ok,
            "valor": 1.0 if mc_ok else 0.0,
            "detalle": {"coherente": im.get("coherente")},
        }
        if not mc_ok:
            causas.append({
                "factor": "mecanica_coherente",
                "herida": "MC incoherente o sin informe",
                "raiz": "correlacion_mecanica no verificó o no está montada",
            })

        # ----- 4. Capacidades resolubles (vía Engine) -----
        cap_total = 0
        cap_ok = 0
        cap_detalle: List[str] = []
        try:
            contenedores = []
            if hasattr(engine, "registro") and hasattr(engine.registro, "contenedores"):
                contenedores = list(engine.registro.contenedores.values())
            for c in contenedores:
                caps = list(getattr(c, "capacidades", None) or [])
                for cap in caps:
                    cap_total += 1
                    fn = None
                    try:
                        fn = c.fn(cap) if hasattr(c, "fn") else None
                    except Exception:
                        fn = None
                    if callable(fn):
                        cap_ok += 1
                    else:
                        cap_detalle.append(f"{getattr(c, 'nombre', '?')}.{cap}")
        except Exception as e:
            cap_detalle.append(f"error_barrido:{type(e).__name__}")

        ratio_cap = (cap_ok / cap_total) if cap_total else 0.0
        factores["capacidades_resolubles"] = {
            "ok": cap_total > 0 and ratio_cap >= 0.99,
            "valor": ratio_cap,
            "detalle": {
                "resolubles": cap_ok,
                "declaradas": cap_total,
                "no_resolubles": cap_detalle[:20],
            },
        }
        if cap_total == 0 or ratio_cap < 0.99:
            causas.append({
                "factor": "capacidades_resolubles",
                "herida": f"{cap_ok}/{cap_total} capacidades resolubles",
                "raiz": "fn no callable o nombre de capacidad no enlazado en CONTENEDOR",
            })

        # ----- 5. TR1 / generatividad -----
        gen: Dict[str, Any] = {}
        try:
            if hasattr(engine, "censar_generatividad"):
                gen = engine.censar_generatividad() or {}
            elif hasattr(engine, "ejecutar_capacidad"):
                out = engine.ejecutar_capacidad("AX", "generatividad")
                if not _safe_undefined_check(out) and isinstance(out, dict):
                    gen = out
        except Exception as e:
            gen = {"estado": "UNDEFINED", "razon": f"{type(e).__name__}: {e}"}

        can = gen.get("canonica") if isinstance(gen, dict) else None
        can = can if isinstance(can, dict) else {}
        theta_can = can.get("theta_n")
        faltan_ids = can.get("ids_faltantes") or []
        sin_dom = can.get("ids_sin_dominio") or []
        tr1_completa = (
            theta_can == 24
            and list(faltan_ids) == []
            and list(sin_dom) == []
        )
        factores["tr1_canonica_completa"] = {
            "ok": bool(tr1_completa),
            "valor": 1.0 if tr1_completa else (
                (theta_can / 24.0) if isinstance(theta_can, int) and theta_can >= 0 else 0.0
            ),
            "detalle": {
                "theta_n": theta_can,
                "ids_faltantes": faltan_ids,
                "ids_sin_dominio": sin_dom,
            },
        }
        if not tr1_completa:
            causas.append({
                "factor": "tr1_canonica_completa",
                "herida": f"canónica {theta_can}/24",
                "raiz": "ids TR1 ausentes o sin gobierna en AX",
            })

        nov = can.get("pares_novedosos")
        im_flag = can.get("im_vs_theta")
        gen_min = (
            isinstance(nov, int)
            and nov > 0
            and im_flag == "GENERATIVO"
            and isinstance(theta_can, int)
            and nov > theta_can
        )
        factores["tr1_generativo_minimo"] = {
            "ok": bool(gen_min),
            "valor": 1.0 if gen_min else 0.0,
            "detalle": {
                "pares_novedosos": nov,
                "im_vs_theta": im_flag,
                "operativa_novedosos": gen.get("pares_novedosos") if isinstance(gen, dict) else None,
            },
        }
        if not gen_min:
            causas.append({
                "factor": "tr1_generativo_minimo",
                "herida": "capa canónica no supera umbral generativo mínimo",
                "raiz": "gobierna sin cruces expandibles o generatividad no disponible",
            })

        # ----- 6. Tests -----
        tests = _cargar_tests_xml(diag_dir)
        if tests and "error" not in tests and tests.get("total", 0) > 0:
            t_ok = tests.get("fallidos", 1) == 0
            tasa = float(tests.get("tasa") or 0.0) / 100.0
            factores["tests_ok"] = {
                "ok": t_ok,
                "valor": tasa,
                "detalle": tests,
            }
            if not t_ok:
                causas.append({
                    "factor": "tests_ok",
                    "herida": f"tests fallidos={tests.get('fallidos')}",
                    "raiz": "regresión en suite; ver diagnostics/test_results.xml",
                })
        else:
            factores["tests_ok"] = {
                "ok": False,
                "valor": 0.0,
                "detalle": tests or {"aviso": "sin test_results.xml"},
            }
            causas.append({
                "factor": "tests_ok",
                "herida": "sin resultados de tests",
                "raiz": "pytest no generó diagnostics/test_results.xml en este entorno",
            })

                # ----- 7. Censo de disco modules/ (cobertura estructural) -----
        if modules_dir.is_dir():
            for child in sorted(modules_dir.iterdir()):
                if not child.is_dir() or child.name.startswith(("_", ".")):
                    continue
                cont, err = _intentar_contenedor(child)
                archivos = _listar_py(child)
                subdirs = sorted(
                    p.name for p in child.iterdir()
                    if p.is_dir() and not p.name.startswith(("_", "."))
                )
                detalle_modulos.append({
                    "carpeta": child.name,
                    "rol": (cont or {}).get("rol"),
                    "nombre_contrato": (cont or {}).get("nombre"),
                    "version": (cont or {}).get("version"),
                    "archivos_py": archivos,
                    "subdirs": subdirs,
                    "n_py": len(archivos),
                    "error_carga": err,
                    "capacidades_declaradas": list(
                        ((cont or {}).get("capacidades") or {}).keys()
                    ) if isinstance((cont or {}).get("capacidades"), dict)
                    else list((cont or {}).get("capacidades") or []),
                })
        else:
            causas.append({
                "factor": "modules_dir",
                "herida": f"no existe {modules_dir}",
                "raiz": "repo_root incorrecto o árbol incompleto",
            })

        # ----- 8. Core presente -----
        core_files = _listar_py(core_dir) if core_dir.is_dir() else []
        core_esperado = {"engine.py", "diagnostico.py"}
        core_ok = core_esperado.issubset(set(core_files))

        # ----- 9. Roles vacíos de fase (informativo, no tumba % igual que obligatorios) -----
        vacios_fase = [r for r in vacios if r in ROLES_FASE_PENDIENTE or r == "SF"]
        vacios_otros = [r for r in vacios if r not in ROLES_FASE_PENDIENTE and r != "DG"]

        # ----- 10. % global -----
        score = 0.0
        desglose_pesos: Dict[str, float] = {}
        for nombre, peso in PESOS.items():
            val = float((factores.get(nombre) or {}).get("valor") or 0.0)
            aporte = peso * val
            desglose_pesos[nombre] = round(aporte * 100.0, 2)
            score += aporte
        pct = round(score * 100.0, 2)

        # ----- 11. Reportes pasivos de módulos (recibir_reporte) -----
        reportes_buf = list(getattr(DiagnosticoGlobal, "_reportes", None) or [])
        reportes_n = len(reportes_buf)
        reportes_cola = reportes_buf[-20:]  # cola: no volcar historial entero

        # ----- informe -----
        informe = {
            "tipo": "diagnostico_global",
            "version": "1.1",
            "timestamp": stamp,
            "repo_root": str(root.resolve()),
            "pct_global": pct,
            "pesos": dict(PESOS),
            "aporte_por_factor_pct": desglose_pesos,
            "factores": factores,
            "causas_raiz": causas,
            "registro": {
                "total_contenedores": total_cont,
                "roles": {
                    k: list(v) if isinstance(v, list) else v
                    for k, v in roles.items()
                },
                "roles_vacios": vacios,
                "roles_vacios_fase": vacios_fase,
                "roles_vacios_otros": vacios_otros,
                "rechazados_n": len(rechazados),
            },
            "modulos_disco": detalle_modulos,
            "core_files": core_files,
            "core_completo": core_ok,
            "generatividad": {
                "theta_n": gen.get("theta_n") if isinstance(gen, dict) else None,
                "im_vs_theta": gen.get("im_vs_theta") if isinstance(gen, dict) else None,
                "canonica": can,
            },
            "reportes_modulos_n": reportes_n,
            "reportes_modulos": reportes_cola,
            "nota": (
                "Solo lectura. Cero actuación. "
                "Omega señala la herida; este informe señala causa raíz y % global. "
                "reportes_modulos = cola de DiagnosticoGlobal.recibir_reporte."
            ),
        }
        return informe

    # ------------------------------------------------------------------
    # Presentación texto (para anexar al Omega)
    # ------------------------------------------------------------------
    @staticmethod
    def presentar(informe: Dict[str, Any]) -> str:
        if not isinstance(informe, dict):
            return "[DG] informe inválido"
        lineas: List[str] = [
            "=" * 80,
            "DIAGNÓSTICO GLOBAL (core — solo lectura)",
            "=" * 80,
            f"  timestamp     : {informe.get('timestamp')}",
            f"  % global      : {informe.get('pct_global')} %",
            f"  repo_root     : {informe.get('repo_root')}",
            "",
            "  Aporte por factor (% del total):",
        ]
        aportes = informe.get("aporte_por_factor_pct") or {}
        for k, v in aportes.items():
            fac = (informe.get("factores") or {}).get(k) or {}
            marca = "OK" if fac.get("ok") else "NO"
            lineas.append(f"    [{marca}] {k}: {v}")

        causas = informe.get("causas_raiz") or []
        lineas.append("")
        lineas.append(f"  Causas raíz ({len(causas)}):")
        if not causas:
            lineas.append("    (ninguna — todos los factores bajo umbral OK)")
        else:
            for i, c in enumerate(causas, 1):
                lineas.append(f"    {i}. [{c.get('factor')}] {c.get('herida')}")
                lineas.append(f"       raíz: {c.get('raiz')}")

        reg = informe.get("registro") or {}
        lineas += [
            "",
            f"  contenedores  : {reg.get('total_contenedores')}",
            f"  vacíos fase   : {reg.get('roles_vacios_fase')}",
            f"  vacíos otros  : {reg.get('roles_vacios_otros')}",
            f"  core_files    : {informe.get('core_files')}",
            f"  core_completo : {informe.get('core_completo')}",
        ]
        can = (informe.get("generatividad") or {}).get("canonica") or {}
        if can:
            lineas += [
                f"  TR1 canónica  : {can.get('theta_n')}/24  "
                f"novedosos={can.get('pares_novedosos')}  {can.get('im_vs_theta')}",
            ]
        lineas += [
            "",
            f"  nota: {informe.get('nota')}",
            "=" * 80,
        ]
        return "\n".join(lineas)

    @staticmethod
    def censo_y_texto(engine: Any, **kwargs: Any) -> Tuple[Dict[str, Any], str]:
        inf = DiagnosticoGlobal.censo(engine, **kwargs)
        return inf, DiagnosticoGlobal.presentar(inf)


# ---------------------------------------------------------------------------
# API mínima de compatibilidad (sin actuación)
# ---------------------------------------------------------------------------
def barrer_diagnostico(engine: Any, **kwargs: Any) -> Dict[str, Any]:
    """Alias de censo para quien espere un 'barrer' de solo lectura."""
    return DiagnosticoGlobal.censo(engine, **kwargs)


__all__ = [
    "DiagnosticoGlobal",
    "DiagnosticoError",
    "PESOS",
    "barrer_diagnostico",
]
