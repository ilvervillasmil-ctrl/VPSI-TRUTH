#!/usr/bin/env python3
"""
OMEGA REPORT - VPSI-TRUTH (Versión 9.4)
======================================
Descripción:
-----------
Este script genera un reporte de diagnóstico automático para validar la coherencia de un sistema
basado en el framework VPSI-TRUTH (Universal Integration System). Su objetivo es verificar que:
1. Las constantes fundamentales (ALPHA, BETA) cumplan con las leyes del framework.
2. Los módulos y roles estén cargados correctamente y no violen el Axioma TA4 (R ⊥ observer).
3. Las declaraciones axiomáticas no tengan contradicciones y cumplan con el Corolario Def-5.3.1.
4. Las fórmulas (Tru_Ri, Tru_total) operen según lo esperado y cumplan con los Teoremas 16 y 17.
5. El camino de evaluación (engine) funcione sin errores y cumpla con el Axioma TA7 (Sin Acceso Directo).
6. Los tests (pytest) pasen sin fallos y cubran los módulos críticos.
7. El sistema sea generativo (Teorema TR1).
8. El sistema no entre en estancamiento (Teorema U1).
Estados:
--------
OK:        La compuerta corrió y el resultado es el exigido.
FALLO:     La compuerta corrió y el resultado no es el exigido.
PENDIENTE: La compuerta no pudo correr por una pieza ausente.
Autor: Ilver Villasmil (ilvervillasmil@gmail.com)
ORCID: 0009-0009-3413-4270
Versión: 9.4
"""
from __future__ import annotations
import importlib.util
import json
import os
import sys
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from itertools import combinations
# =============================================================================
# CONSTANTES FUNDAMENTALES DEL FRAMEWORK VPSI
# =============================================================================
CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# Modo STRICT: Si STRICT=1, un FALLO devuelve exit code 1 y el CI se pone rojo.
STRICT = os.getenv("OMEGA_STRICT", "0") == "1"
OK = "OK"
FALLO = "FALLO"
PENDIENTE = "PENDIENTE"
# Constantes geométricas del cubo 3x3x3
ALPHA = Fraction(26, 27)  # Fracción observable
BETA = Fraction(1, 27)    # Fracción interior irreducible
# =============================================================================
# CLASE COMPUERTA
# =============================================================================
class Compuerta:
    """Clase para representar una compuerta de diagnóstico."""
    
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.estado = PENDIENTE
        self.detalle: List[str] = []
        self.datos: Dict[str, Any] = {}
    def ok(self, msg: str = "") -> "Compuerta":
        self.estado = OK
        if msg:
            self.detalle.append(msg)
        return self
    def fallo(self, msg: str) -> "Compuerta":
        self.estado = FALLO
        self.detalle.append(msg)
        return self
    def pendiente(self, msg: str) -> "Compuerta":
        self.estado = PENDIENTE
        self.detalle.append(msg)
        return self
    def nota(self, msg: str) -> "Compuerta":
        self.detalle.append(msg)
        return self
# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def frac(v: Fraction) -> str:
    """Representa una Fraction como fracción exacta y decimal de lectura."""
    return f"{v}  ({float(v):.6f})"
def bloque(c: Compuerta) -> str:
    """Formatea una compuerta para su visualización en el reporte."""
    marca = {OK: "[OK]", FALLO: "[FALLO]", PENDIENTE: "[PENDIENTE]"}[c.estado]
    out = [f"{marca} {c.nombre}"]
    for d in c.detalle:
        out.append(f"    {d}" if d else "")
    return "\n".join(out)
# =============================================================================
# COMPUERTA 1 - CONSTANTES (ALPHA / BETA)
# =============================================================================
def compuerta_constantes() -> Tuple[Compuerta, Optional[Fraction], Optional[Fraction]]:
    """
    Verifica que ALPHA y BETA sean Fraction, sumen 1, y sean derivados del cubo 3x3x3.
    
    Axiomas y Teoremas Relacionados:
    - Axioma β (Irreducible Structural Minimum)
    - Teorema M.1 (Minimalidad de N=3)
    - Corolario 2.4 (Uniqueness of the Minimum)
    """
    c = Compuerta("Constantes ALPHA / BETA")
    
    try:
        from modules.constante import ALPHA as ALPHA_MODULE, BETA as BETA_MODULE
    except Exception as e:
        c.pendiente(f"No se pudo importar modules.constante: {type(e).__name__}: {e}")
        return c, None, None
    c.datos["alpha"] = str(ALPHA_MODULE)
    c.datos["beta"] = str(BETA_MODULE)
    c.datos["tipo_alpha"] = type(ALPHA_MODULE).__name__
    c.datos["tipo_beta"] = type(BETA_MODULE).__name__
    # Verificar que sean Fraction
    if not isinstance(ALPHA_MODULE, Fraction) or not isinstance(BETA_MODULE, Fraction):
        c.fallo(
            f"ALPHA y BETA deben ser Fraction. "
            f"ALPHA={type(ALPHA_MODULE).__name__}, BETA={type(BETA_MODULE).__name__}"
        )
        return c, None, None
    c.nota(f"ALPHA = {frac(ALPHA_MODULE)}")
    c.nota(f"BETA  = {frac(BETA_MODULE)}")
    # Verificar que sumen 1 (Ley de Conservación)
    suma = ALPHA_MODULE + BETA_MODULE
    c.datos["suma"] = str(suma)
    if suma != Fraction(1):
        c.fallo(f"Invariante roto: ALPHA + BETA = {suma}, se exige 1 exacto")
        return c, ALPHA_MODULE, BETA_MODULE
    # Verificar valores geométricos del cubo 3x3x3
    if ALPHA_MODULE != ALPHA or BETA_MODULE != BETA:
        c.fallo(
            f"ALPHA y BETA deben ser 26/27 y 1/27 respectivamente (derivados del cubo 3x3x3). "
            f"ALPHA={ALPHA_MODULE}, BETA={BETA_MODULE}"
        )
        return c, ALPHA_MODULE, BETA_MODULE
    c.nota("ALPHA + BETA = 1 exacto (Ley de Conservación)")
    c.nota("ALPHA = 26/27 y BETA = 1/27 (derivados del cubo 3x3x3)")
    c.ok()
    return c, ALPHA_MODULE, BETA_MODULE
# =============================================================================
# COMPUERTA 2 - MÓDULOS Y ROLES
# =============================================================================
OBLIGATORIOS = ("AX", "CT", "FO")
def _roles_del_engine() -> tuple:
    """Obtiene los roles definidos en el engine."""
    try:
        from core.engine import ROLES
        return tuple(ROLES)
    except Exception:
        return ()
def _contenedor_por_rol(eng, rol: str):
    """Obtiene el contenedor asociado a un rol."""
    for cont in eng.registro.contenedores.values():
        if getattr(cont, "rol", None) == rol:
            return cont
    return None
def compuerta_modulos(eng) -> Compuerta:
    """
    Verifica que los módulos y roles estén cargados correctamente y no violen el Axioma TA4 (R ⊥ observer).
    
    Axiomas y Teoremas Relacionados:
    - Axioma TA4 (Independencia de la Realidad)
    - Teorema 10 (Invariancia de R bajo Procesamiento Interno)
    - Axioma A11 (Transformación de Estado en la Realidad)
    """
    c = Compuerta("Módulos y roles")
    
    if eng is None:
        c.pendiente("Engine no disponible")
        return c
    resumen = eng.registro.resumen()
    roles = resumen.get("roles", {})
    vacios = resumen.get("roles_vacios", [])
    rechazados = resumen.get("rechazados", [])
    c.datos["roles"] = roles
    c.datos["roles_vacios"] = vacios
    c.datos["rechazados"] = rechazados
    # Tabla de roles
    c.nota("+" + "-" * 76 + "+")
    c.nota(f"| {'ROL':<4} | {'ESTADO':<9} | {'MÓDULO ASOCIADO':<14} | {'DESCRIPCIÓN / FUNCIÓN':<37} |")
    c.nota("+" + "-" * 76 + "+")
    admitidos = _roles_del_engine()
    c.datos["roles_admitidos"] = list(admitidos)
    
    for rol in admitidos:
        cont = _contenedor_por_rol(eng, rol)
        if cont is not None:
            estado_str = "CARGADO"
            mod_str = cont.nombre
            meta = getattr(cont.modulo, "CONTENEDOR", None) or {}
            desc = str(meta.get("descripcion") or "(el módulo no se describe)")
            
            # Verificar que el módulo no modifique R (Axioma TA4)
            if hasattr(cont.modulo, "modifica_R"):
                c.fallo(f"Módulo {cont.nombre} (rol {rol}) modifica R (violación de Axioma TA4: R ⊥ observer)")
                return c
            
            # Verificar que el módulo no viole el Axioma A11 (Transformación de Estado en R)
            if hasattr(cont.modulo, "acciones"):
                for accion in cont.modulo.acciones:
                    if not hasattr(accion, "funcion_transicion") or not callable(accion.funcion_transicion):
                        c.fallo(f"Acción {accion.nombre} en módulo {cont.nombre} no tiene función de transición T_a: R → R (violación de Axioma A11)")
                        return c
        else:
            estado_str = "AUSENTE" if rol in OBLIGATORIOS else "vacío"
            mod_str = "-"
            desc = "(no montado)"
        
        c.nota(f"| {rol:<4} | {estado_str:<9} | {mod_str:<14} | {desc[:37]:<37} |")
    
    c.nota("+" + "-" * 76 + "+")
    for r in rechazados:
        c.nota(f"  RECHAZADO {r.get('ruta')}: {r.get('razon')}")
    # Verificar roles obligatorios
    faltan_obl = [r for r in OBLIGATORIOS if r not in roles]
    if faltan_obl:
        c.fallo(f"Roles obligatorios ausentes: {faltan_obl}")
        return c
    if vacios:
        c.nota(
            f"Roles opcionales vacíos: {vacios} "
            "-- sin CA no hay C, L, K y el camino de evaluación no puede correr"
        )
    
    c.ok()
    return c
# =============================================================================
# COMPUERTA 3 - BARRIDO AXIOMÁTICO CON DESGLOSE DE ORIGEN
# =============================================================================
def compuerta_axiomas(eng) -> Compuerta:
    """
    Verifica que no haya contradicciones axiomáticas y que todas las declaraciones
    cumplan con el Corolario Def-5.3.1 (Especificidad de Dominio).
    
    Axiomas y Teoremas Relacionados:
    - Corolario Def-5.3.1 (Especificidad de Dominio)
    - Teorema 9 (Imposibilidad de Verdad sin Evidencia)
    """
    c = Compuerta("Barrido axiomático")
    
    if eng is None:
        c.pendiente("Engine no disponible")
        return c
    informe = eng.informe_axiomas or {}
    total = informe.get("declaraciones", 0)
    choques = informe.get("choques", []) or []
    errores = informe.get("errores", []) or []
    c.datos["total"] = total
    c.datos["choques"] = len(choques)
    c.datos["errores"] = len(errores)
    c.nota(f"Total declaraciones que entraron al barrido: {total}")
    c.nota(f"Choques: {len(choques)}   errores de forma: {len(errores)}")
    # Desglose por origen
    ax_dir = REPO_ROOT / "modules" / "axiomas"
    por_archivo: Dict[str, int] = {}
    ids_archivo: List[str] = []
    cargador = None
    try:
        import modules.axiomas as _AX
        cargador = getattr(_AX, "_cargar_declaraciones_desde_archivo", None)
    except Exception as e:
        c.nota(f"  No se pudo importar modules.axiomas: {type(e).__name__}: {e}")
    if cargador is None:
        c.nota("  Sin cargador del repo: no se desglosa (no se inventa el conteo)")
        c.datos["desglose"] = None
    elif ax_dir.exists():
        for archivo in sorted(ax_dir.glob("*.py")):
            if archivo.name == "__init__.py" or archivo.name.startswith("_"):
                continue
            try:
                decls = cargador(archivo)
            except Exception as e:
                por_archivo[archivo.name] = -1
                c.nota(f"  Archivo {archivo.name}: RECHAZADO ({type(e).__name__}: {e})")
                continue
            
            # Verificar Corolario Def-5.3.1: K debe tener O_context
            for d in decls:
                if isinstance(d, dict) and "K" in d and "O_context" not in d:
                    c.fallo(f"Declaración axiomática {d.get('id')} tiene K sin O_context (violación de Corolario Def-5.3.1)")
                    return c
            
            por_archivo[archivo.name] = len(decls)
            ids_archivo.extend(str(d.get("id")) for d in decls if isinstance(d, dict))
            c.nota(f"  Archivo {archivo.name}: {len(decls)} declaraciones")
    total_archivos = sum(v for v in por_archivo.values() if v > 0)
    c.datos["por_archivo"] = por_archivo
    c.datos["total_archivos"] = total_archivos
    # Declaraciones externas
    externas: Dict[str, int] = {}
    ids_externas: List[str] = []
    for cont in eng.registro.contenedores.values():
        g = cont.fn("axiomas")
        if callable(g):
            try:
                lista = g()
            except Exception as e:
                externas[cont.nombre] = -1
                c.nota(f"  Externas de {cont.nombre}: ERROR {type(e).__name__}: {e}")
                continue
            if isinstance(lista, list):
                externas[cont.nombre] = len(lista)
                ids_externas.extend(str(d.get("id")) for d in lista if isinstance(d, dict))
                c.nota(f"  Externas de {cont.nombre}: {len(lista)} vía axiomas()")
    total_externas = sum(v for v in externas.values() if v > 0)
    c.datos["externas"] = externas
    c.datos["total_externas"] = total_externas
    suma = total_archivos + total_externas
    c.datos["suma_desglose"] = suma
    c.nota(f"Desglose: archivos {total_archivos} + externas {total_externas} = {suma}")
    if cargador is not None and suma != total:
        c.fallo(
            f"Descuadre: el barrido reporta {total} y el desglose suma {suma}. "
            "El reporte no puede afirmar de dónde salen las declaraciones."
        )
        return c
    # IDs duplicados
    todos = ids_archivo + ids_externas
    vistos: Dict[str, int] = {}
    for i in todos:
        vistos[i] = vistos.get(i, 0) + 1
    duplicados = {k: v for k, v in vistos.items() if v > 1}
    c.datos["ids_unicos"] = len(vistos)
    c.datos["duplicados"] = len(duplicados)
    if duplicados:
        muestra = ", ".join(sorted(duplicados)[:8])
        c.nota(
            f"IDs repetidos: {len(duplicados)} de {len(vistos)} únicos "
            f"(ej: {muestra})"
        )
        c.nota(
            "Una misma declaración entra por dos caminos de carga. "
            "Hoy no produce choque; si una copia se edita y la otra no, "
            "el choque será entre una declaración y su propia copia"
        )
    if errores:
        for e in errores[:10]:
            c.nota(f"  Error de forma: {e}")
    if choques:
        c.fallo(f"{len(choques)} contradicciones axiomáticas")
        for ch in choques[:10]:
            c.nota(f"  Choque: {ch}")
        return c
    if total == 0:
        c.fallo("0 declaraciones entraron al barrido: coherente por vacuidad, no por coherencia")
        return c
    c.ok()
    return c
# =============================================================================
# COMPUERTA 4 - FÓRMULAS: Tru_Ri y Tru_total
# =============================================================================
PUNTOS = [
    (Fraction(0), Fraction(0), Fraction(0), "colapso de los tres factores"),
    (Fraction(1), Fraction(1), Fraction(0), "K nula: forma impecable, ancla rota"),
    (Fraction(0), Fraction(1), Fraction(1), "C nula"),
    (Fraction(1), Fraction(0), Fraction(1), "L nula"),
    (Fraction(1), Fraction(1), Fraction(1), "sincronización total"),
]

def _declaracion(idn: str):
    """Lee una declaración del corpus. No la reescribe."""
    try:
        import modules.axiomas as _AX
        for d in _AX.axiomas():
            if str(d.get("id")) == idn:
                return d
    except Exception:
        pass
    return None

def compuerta_formulas(eng, ALPHA: Optional[Fraction], BETA: Optional[Fraction]) -> Compuerta:
    """
    Verifica que las fórmulas Tru_Ri y Tru_total operen correctamente y cumplan con:
    - Axioma TA5 (Multiplicatividad de la Verdad)
    - Teorema 17 (Imposibilidad de Colapso Total)
    - Teorema 16 (Techo Estructural α) para Tru_Ri (no para Tru_total en el caso (1,1,1))

    Axiomas y Teoremas Relacionados:
    - Axioma TA5 (Multiplicatividad de la Verdad)
    - Teorema 16 (Techo Estructural α)
    - Teorema 17 (Imposibilidad de Colapso Total)
    """
    c = Compuerta("Fórmulas Tru_Ri y Tru_total")

    if ALPHA is None or BETA is None:
        c.pendiente("Constantes no disponibles")
        return c

    try:
        from modules.formulas.truth import tru_ri, tru_total
    except Exception as e:
        c.pendiente(f"No se pudo importar modules.formulas.truth: {type(e).__name__}: {e}")
        return c

    c.nota("Tru_Ri    = C * L * K")
    c.nota("Tru_total = (Tru_Ri * ALPHA) + BETA")
    c.nota("Son dos objetos distintos y se reportan por separado.")
    c.nota("")
    c.nota("+" + "-" * 76 + "+")
    c.nota(f"| {'C':<5} | {'L':<5} | {'K':<5} | {'Tru_Ri':<12} | {'Tru_total':<14} | {'EST':<4} |")
    c.nota("+" + "-" * 76 + "+")

    fallos = 0
    filas = []

    for C, L, K, desc in PUNTOS:
        ri = tru_ri(C, L, K)
        tt = tru_total(C, L, K)

        problemas = []

        # Verificar Axioma TA5 (Multiplicatividad)
        if ri != C * L * K:
            problemas.append(f"Tru_Ri esperado {C*L*K}, recibido {ri}")

        # Verificar que Tru_total se derive de Tru_Ri
        if tt != (ri * ALPHA) + BETA:
            problemas.append(f"Tru_total no se deriva de Tru_Ri: {tt}")

        # Verificar tipos exactos (Fraction)
        if not isinstance(ri, Fraction) or not isinstance(tt, Fraction):
            problemas.append(
                f"Tipo no exacto: Tru_Ri={type(ri).__name__}, Tru_total={type(tt).__name__}"
            )

        # Verificar Teorema 17 (Piso Estructural β)
        if Fraction(0) in (C, L, K):
            if ri != Fraction(0):
                problemas.append(f"Factor nulo pero Tru_Ri = {ri}")
            if tt != BETA:
                problemas.append(f"Factor nulo pero Tru_total = {tt}, no BETA (violación de Teorema 17)")

        # Verificar Teorema 16 (Techo Estructural α) para Tru_Ri, no para Tru_total
        # Tru_Ri puede ser 1 en el caso (1,1,1), pero Tru_total(1,1,1) = 1 es válido
        if ri > ALPHA and (C, L, K) != (Fraction(1), Fraction(1), Fraction(1)):
            problemas.append(f"Tru_Ri(D) = {ri} > α = {ALPHA} (violación de Teorema 16)")

        # Verificar que Tru_total no exceda 1 (pero puede ser 1 en el caso (1,1,1))
        if tt > Fraction(1):
            problemas.append(f"Tru_total(D) = {tt} > 1 (violación de la fórmula canónica)")

        # Verificar que Tru_total no sea menor que β
        if tt < BETA:
            problemas.append(f"Tru_total(D) = {tt} < β = {BETA} (violación de Teorema 17)")

        estado = "OK" if not problemas else "FALL"
        if problemas:
            fallos += 1

        filas.append({
            "C": str(C), "L": str(L), "K": str(K),
            "tru_ri": str(ri), "tru_total": str(tt),
            "estado": estado, "punto": desc, "problemas": problemas,
        })

        c.nota(
            f"| {float(C):5.2f} | {float(L):5.2f} | {float(K):5.2f} | "
            f"{str(ri):<12} | {str(tt):<14} | {estado:<4} |"
        )
        for p in problemas:
            c.nota(f"        -> {p}")

    c.nota("+" + "-" * 76 + "+")
    c.datos["puntos"] = filas
    c.nota("")

    # Piso y techo
    piso_ri = tru_ri(Fraction(0), Fraction(0), Fraction(0))
    piso_tt = tru_total(Fraction(0), Fraction(0), Fraction(0))
    techo_ri = tru_ri(Fraction(1), Fraction(1), Fraction(1))
    techo_tt = tru_total(Fraction(1), Fraction(1), Fraction(1))

    c.datos.update({
        "piso_tru_ri": str(piso_ri), "piso_tru_total": str(piso_tt),
        "techo_tru_ri": str(techo_ri), "techo_tru_total": str(techo_tt),
    })

    c.nota(f"Piso    Tru_Ri = {frac(piso_ri)}     Tru_total = {frac(piso_tt)}")
    c.nota(f"Techo   Tru_Ri = {frac(techo_ri)}     Tru_total = {frac(techo_tt)}")

    # Verificar Teorema 17 (Piso Estructural β)
    if piso_tt != BETA:
        c.fallo(f"Piso incorrecto: Tru_total(0,0,0) = {piso_tt}, se exige BETA = {BETA} (violación de Teorema 17)")
        return c

    # Verificar que Tru_total(1,1,1) = 1 (caso válido de sincronización perfecta)
    if techo_tt != Fraction(1):
        c.fallo(f"Techo incorrecto: Tru_total(1,1,1) = {techo_tt}, se exige 1 (sincronización perfecta)")
        return c

    if fallos:
        c.fallo(f"{fallos} de {len(PUNTOS)} puntos no cumplen la fórmula")
        return c

    c.ok(f"{len(PUNTOS)} puntos ejecutados con aritmética exacta")
    return c
# =============================================================================
# COMPUERTA 5 - CAMINO DE EVALUACIÓN
# =============================================================================
SONDAS = [
    {
        "nombre": "sonda básica",
        "peticion": {
            "mensaje": "prueba de camino de evaluación",
            "contexto": "Octx declarado",
        },
    },
    {
        "nombre": "sonda con factores provistos (verdad completa)",
        "peticion": {
            "mensaje": "prueba con C, L, K inyectados",
            "contexto": "Octx declarado",
            "C": "1", "L": "1", "K": "1",  # K = 1 para Tru(D) = 1
        },
    },
    {
        "nombre": "sonda con factores provistos (colapso)",
        "peticion": {
            "mensaje": "prueba con C, L, K inyectados",
            "contexto": "Octx declarado",
            "C": "1", "L": "1", "K": "0",  # K = 0 para Tru_Ri(D) = 0
        },
    },
    {
        "nombre": "sonda con factores provistos (correlación parcial)",
        "peticion": {
            "mensaje": "prueba con C, L, K inyectados",
            "contexto": "Octx = 'dominio de prueba X'",  # O_context explícito
            "C": "1", "L": "1", "K": "9/10",  # K = 9/10 con O_context
        },
    },
]
def compuerta_evaluacion(eng) -> Compuerta:
    """
    Verifica que el camino de evaluación (engine.evaluar) funcione correctamente y cumpla con:
    - Axioma TA7 (Sin Acceso Directo)
    - Axioma F9 (Puntuación de Anclaje)
    - Teorema 12 (Conflación de R_i con R)
    - Teorema 14 (Propiedad de la Verdad)
    - Corolario 14.2 (Error Masivo no Refuta al Individuo)
    
    Axiomas y Teoremas Relacionados:
    - Axioma TA7 (Sin Acceso Directo)
    - Axioma F9 (Puntuación de Anclaje)
    - Teorema 2 (VPSI - Principio de Invariancia Estructural)
    - Teorema 12 (Conflación de R_i con R)
    - Teorema 14 (Propiedad de la Verdad)
    - Corolario 14.2 (Error Masivo no Refuta al Individuo)
    """
    c = Compuerta("Camino de evaluación (engine.evaluar)")
    
    if eng is None:
        c.pendiente("Engine no disponible")
        return c
    resultados = []
    hubo_excepcion = False
    hubo_undefined = False
    for sonda in SONDAS:
        c.nota(f"  {sonda['nombre']}: {json.dumps(sonda['peticion'], ensure_ascii=False)}")
        
        # Verificar Axioma F9 (Puntuación de Anclaje)
        peticion = sonda["peticion"]
        if "C" in peticion or "L" in peticion or "K" in peticion:
            if "contexto" not in peticion or not peticion["contexto"]:
                c.fallo(f"Sonda {sonda['nombre']} no tiene contexto (Octx) para anclar afirmaciones (violación de Axioma F9)")
                return c
        
        try:
            r = eng.evaluar(sonda["peticion"])
        except Exception as e:
            hubo_excepcion = True
            tb = traceback.extract_tb(sys.exc_info()[2])
            ultimo = tb[-1] if tb else None
            loc = f"{ultimo.filename}:{ultimo.lineno} en {ultimo.name}" if ultimo else "?"
            c.nota(f"    EXCEPCIÓN {type(e).__name__}: {e}")
            c.nota(f"    en {loc}")
            resultados.append({
                "sonda": sonda["nombre"],
                "excepcion": f"{type(e).__name__}: {e}",
                "ubicacion": loc,
            })
            continue
        factores = r.get("factores", {})
        tt = r.get("tru_total")
        c.nota(f"    Factores  : {factores}")
        c.nota(f"    Tru_Ri    : {r.get('tru_ri')}")
        c.nota(f"    Tru_total : {tt}")
        c.nota(f"    Estado    : {r.get('estado')}")
        c.nota(f"    Limitante : {r.get('limitante')}   Detenido en: {r.get('detenido_en')}")
        
        if r.get("fallos"):
            for f in r["fallos"]:
                c.nota(f"    Fallo interno: {f.get('rol')} {f.get('contenedor')}: {f.get('razon')}")
        
        if r.get("anotaciones"):
            c.nota(f"    Anotaciones taxonomía: {r['anotaciones']}")
        # Verificar Axioma TA7 (Sin Acceso Directo)
        if "R" in r.get("fuentes_usadas", []):
            c.fallo("El motor de evaluación accede directamente a R (violación de Axioma TA7)")
            return c
        
        if not r.get("markov_chain_validado", False):
            c.fallo("No se validó que R → X → Y sea una cadena de Markov (violación de Axioma TA7)")
            return c
        
        # Verificar Teorema 12 (Conflación de R_i con R)
        if r.get("R_i_equals_R", False):
            c.fallo("El motor de evaluación confunde R_i con R (violación de Teorema 12)")
            return c
        
        # Verificar Teorema 14 (Propiedad de la Verdad)
        if r.get("verdader_producida_por_R", False):
            c.fallo("El motor asigna la producción de verdad a R (violación de Teorema 14)")
            return c
        
        # Verificar Corolario 14.2 (Error Masivo no Refuta al Individuo)
        if r.get("consenso_sobre_individuo", False):
            c.fallo("El motor prioriza el consenso sobre la verdad individual (violación de Corolario 14.2)")
            return c
        
        # Verificar Corolario β-Gödel (Principio X)
        if not r.get("reconoce_beta_godel", False):
            c.fallo("El motor no reconoce el Corolario β-Gödel (violación del Principio X)")
            return c
        if tt == "UNDEFINED" or "UNDEFINED" in str(factores):
            hubo_undefined = True
        resultados.append({
            "sonda": sonda["nombre"],
            "factores": factores,
            "tru_ri": r.get("tru_ri"),
            "tru_total": tt,
            "estado": r.get("estado"),
            "limitante": r.get("limitante"),
            "detenido_en": r.get("detenido_en"),
            "fallos": r.get("fallos", []),
        })
    c.datos["sondas"] = resultados
    if hubo_excepcion:
        c.fallo(
            "evaluar() lanza excepción: el camino de evaluación no corre. "
            "Sin contenedor CA, C/L/K quedan UNDEFINED y el reporte Omega interno "
            "compara UNDEFINED con Fraction"
        )
        return c
    if hubo_undefined:
        c.fallo(
            "evaluar() devuelve UNDEFINED en factores o Tru_total: "
            "no hay contenedor que calcule C, L, K"
        )
        return c
    c.ok("evaluar() corrió y devolvió factores y Tru_total definidos")
    return c
# =============================================================================
# COMPUERTA 6 - TESTS
# =============================================================================
def compuerta_tests() -> Compuerta:
    """
    Verifica que los tests (pytest) pasen y cubran los módulos críticos, incluyendo:
    - Corolario β-Gödel
    - Teorema 16 (Techo Estructural α)
    
    Axiomas y Teoremas Relacionados:
    - Corolario β-Gödel
    - Teorema 16 (Techo Estructural α)
    """
    c = Compuerta("Tests (pytest / junit xml)")
    
    xml_path = DIAGNOSTICS_DIR / "test_results.xml"
    if not xml_path.exists():
        c.pendiente(f"No existe {xml_path.name}: corre pytest con --junit-xml antes de este paso")
        return c
    try:
        raiz = ET.parse(xml_path).getroot()
    except Exception as e:
        c.fallo(f"XML ilegible: {type(e).__name__}: {e}")
        return c
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    total = fallos = errores = omitidos = 0
    nombres: List[str] = []
    for s in suites:
        total += int(s.get("tests", 0))
        fallos += int(s.get("failures", 0))
        errores += int(s.get("errors", 0))
        omitidos += int(s.get("skipped", 0))
        for caso in s.iter("testcase"):
            nombres.append(f"{caso.get('classname','')}::{caso.get('name','')}")
    fallidos = fallos + errores
    pasados = total - fallidos - omitidos
    tasa = (pasados / total * 100) if total else 0.0
    c.datos.update({
        "total": total, "pasados": pasados, "fallidos": fallidos,
        "omitidos": omitidos, "tasa": tasa, "casos": nombres,
    })
    c.nota(f"Total {total}   pasados {pasados}   fallidos {fallidos}   omitidos {omitidos}   tasa {tasa:.2f}%")
    for n in nombres:
        c.nota(f"  {n}")
    tests_dir = REPO_ROOT / "tests"
    tocados = set()
    if tests_dir.exists():
        for f in tests_dir.glob("*.py"):
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for objetivo in ("core.engine", "modules.constante", "modules.formulas", "modules.axiomas"):
                if objetivo in txt:
                    tocados.add(objetivo)
    
    c.datos["modulos_cubiertos"] = sorted(tocados)
    c.nota(f"Módulos del paquete importados por los tests: {sorted(tocados) or 'ninguno'}")
    # Verificar Corolario β-Gödel
    if "beta_godel" not in [n.lower() for n in nombres]:
        c.fallo("Los tests no cubren el Corolario β-Gödel (incompletud formal como instancia de β)")
        return c
    
    # Verificar Teorema 16 (Techo Estructural α)
    if "structural_ceiling" not in [n.lower() for n in nombres]:
        c.fallo("Los tests no cubren el Teorema 16 (Techo Estructural α)")
        return c
    if fallidos:
        c.fallo(f"{fallidos} tests fallidos")
        return c
    
    if not tocados:
        c.fallo("Ningún test importa core.engine ni modules.*: la suite no cubre el paquete")
        return c
    c.ok()
    return c
# =============================================================================
# COMPUERTA 7 - GENERATIVIDAD ESTRUCTURAL (Teorema TR1)
# =============================================================================
def compuerta_generatividad(eng) -> Compuerta:
    """
    Verifica que el framework sea generativo (Teorema TR1).
    
    Axiomas y Teoremas Relacionados:
    - Teorema TR1 (Generatividad Estructural del Framework)
    """
    c = Compuerta("Generatividad Estructural (Teorema TR1)")
    
    if eng is None:
        c.pendiente("Engine no disponible")
        return c
    # Lista de teoremas (simplificación: usar los teoremas del framework VPSI)
    teoremas = [
        {"nombre": "T1", "dominios": {"ONT", "INF"}},
        {"nombre": "T2", "dominios": {"INF", "LOG"}},
        {"nombre": "T3", "dominios": {"INF", "TMP"}},
        {"nombre": "T4", "dominios": {"EPI", "TMP"}},
        {"nombre": "T5", "dominios": {"ONT", "EPI"}},
        {"nombre": "T6", "dominios": {"LOG", "SEM"}},
        {"nombre": "T7", "dominios": {"ONT", "MET"}},
        {"nombre": "T8", "dominios": {"INF", "MET"}},
        {"nombre": "T9", "dominios": {"EPI", "INF"}},
        {"nombre": "T10", "dominios": {"ONT", "INF"}},
        {"nombre": "T11", "dominios": {"ONT", "MET"}},
        {"nombre": "T12", "dominios": {"EPI", "ONT"}},
        {"nombre": "T13", "dominios": {"EPI", "SEM"}},
        {"nombre": "T14", "dominios": {"EPI", "MET"}},
        {"nombre": "T15", "dominios": {"ONT", "INF", "MET"}},
        {"nombre": "T16", "dominios": {"EPI", "MET"}},
        {"nombre": "T17", "dominios": {"ONT", "MET", "TMP"}},
        {"nombre": "U1", "dominios": {"EPI", "TMP", "MET"}},
        {"nombre": "M1", "dominios": {"MET", "LOG"}},
        {"nombre": "M.1", "dominios": {"MET", "ONT"}},
        {"nombre": "B-Canonical", "dominios": {"ONT", "LOG", "MET"}},
        {"nombre": "TT.6.1", "dominios": {"LOG", "SEM", "EPI"}},
        {"nombre": "U0", "dominios": {"ONT", "INF", "TMP"}},
        {"nombre": "TR1", "dominios": {"MET", "INF", "LOG"}},
    ]
    # Verificar recombinación
    nuevas_verdades = 0
    redundant_pairs = 0
    incompatible_pairs = 0
    
    for t1, t2 in combinations(teoremas, 2):
        if t1["dominios"] & t2["dominios"]:  # Dominios compatibles
            if t1["dominios"] == t2["dominios"]:
                redundant_pairs += 1
            else:
                nuevas_verdades += 1
        else:
            incompatible_pairs += 1
    c.datos["nuevas_verdades"] = nuevas_verdades
    c.datos["pares_redundantes"] = redundant_pairs
    c.datos["pares_incompatibles"] = incompatible_pairs
    c.nota(f"Total pares evaluados: {len(list(combinations(teoremas, 2)))}")
    c.nota(f"Pares con dominios compatibles: {nuevas_verdades + redundant_pairs}")
    c.nota(f"Pares que satisfacen el criterio de novedad: {nuevas_verdades}")
    c.nota(f"Pares redundantes: {redundant_pairs}")
    c.nota(f"Pares incompatibles: {incompatible_pairs}")
    if nuevas_verdades <= len(teoremas):
        c.fallo(
            f"El framework no es generativo: {nuevas_verdades} ≤ {len(teoremas)} "
            f"(violación de Teorema TR1)"
        )
        return c
    c.ok(f"Framework generativo: {nuevas_verdades} > {len(teoremas)}")
    return c
# =============================================================================
# COMPUERTA 8 - PRINCIPIO DE NO ESTANCAMIENTO (Teorema U1)
# =============================================================================
def compuerta_no_estancamiento(eng) -> Compuerta:
    """
    Verifica que el sistema cumpla con el Teorema U1 (Principio de No Estancamiento).
    
    Axiomas y Teoremas Relacionados:
    - Teorema U1 (Principio de No Estancamiento)
    """
    c = Compuerta("Principio de No Estancamiento (Teorema U1)")
    
    if eng is None:
        c.pendiente("Engine no disponible")
        return c
    # Verificar que β > 0
    if BETA <= 0:
        c.fallo(f"β ≤ 0 (violación de Teorema U1: β debe ser > 0)")
        return c
    # Verificar que el sistema no entre en estancamiento
    if hasattr(eng, "historial_K"):
        if len(eng.historial_K) > 1:
            K_t = eng.historial_K[-1]
            K_t_menos_1 = eng.historial_K[-2]
            if K_t == K_t_menos_1:
                c.fallo(
                    "K(t+1) = K(t): sistema en estancamiento "
                    "(violación de Teorema U1)"
                )
                return c
    c.ok("β > 0 y el sistema no está en estancamiento")
    return c
# =============================================================================
# ENSAMBLADO
# =============================================================================
def arrancar_engine() -> Tuple[Any, Optional[str]]:
    """Arranca el motor del framework."""
    try:
        from core.engine import Engine
    except Exception as e:
        return None, f"No se pudo importar core.engine: {type(e).__name__}: {e}"
    try:
        eng = Engine(
            raiz_modulos=str(REPO_ROOT / "modules"),
            invocador_id="core",
            verificar_axiomas=True,
        )
        return eng, None
    except Exception as e:
        return None, f"El Engine no arranca: {type(e).__name__}: {e}"
# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main() -> None:
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = os.getenv("GITHUB_SHA", "local")[:7]
    print("=" * 80)
    print("OMEGA REPORT - VPSI-TRUTH (Versión 9.4)")
    print(f"Generado: {ahora}    Commit: {sha}    Python: {sys.version.split()[0]}")
    print(f"Modo: {'STRICT (un FALLO pone el CI en rojo)' if STRICT else 'INFORMATIVO'}")
    print("=" * 80)
    print()
    eng, err_engine = arrancar_engine()
    if err_engine:
        print(f"[FALLO] Arranque del Engine")
        print(f"    {err_engine}")
        print()
    # Ejecutar compuertas
    c_const, ALPHA, BETA = compuerta_constantes()
    compuertas = [
        c_const,
        compuerta_modulos(eng),
        compuerta_axiomas(eng),
        compuerta_formulas(eng, ALPHA, BETA),
        compuerta_evaluacion(eng),
        compuerta_tests(),
        compuerta_generatividad(eng),
        compuerta_no_estancamiento(eng),
    ]
    for c in compuertas:
        print(bloque(c))
        print()
    # Resumen
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    ancho = max(len(c.nombre) for c in compuertas)
    for c in compuertas:
        marca = {OK: "OK       ", FALLO: "FALLO    ", PENDIENTE: "PENDIENTE"}[c.estado]
        print(f"  {marca}  {c.nombre.ljust(ancho)}")
    n_ok = sum(1 for c in compuertas if c.estado == OK)
    n_fallo = sum(1 for c in compuertas if c.estado == FALLO)
    n_pend = sum(1 for c in compuertas if c.estado == PENDIENTE)
    print()
    print(f"  {n_ok} OK   {n_fallo} FALLO   {n_pend} PENDIENTE")
    print("=" * 80)
    # Guardar datos en JSON
    datos = {
        "generado": datetime.now(timezone.utc).isoformat(),
        "commit": sha,
        "strict": STRICT,
        "compuertas": [
            {
                "nombre": c.nombre,
                "estado": c.estado,
                "detalle": [d for d in c.detalle if d],
                "datos": c.datos,
            }
            for c in compuertas
        ],
        "conteo": {"ok": n_ok, "fallo": n_fallo, "pendiente": n_pend},
    }
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    (DIAGNOSTICS_DIR / "omega_report_data.json").write_text(
        json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nJSON: {DIAGNOSTICS_DIR / 'omega_report_data.json'}")
    if STRICT and (n_fallo or err_engine):
        sys.exit(1)
if __name__ == "__main__":
    main()
