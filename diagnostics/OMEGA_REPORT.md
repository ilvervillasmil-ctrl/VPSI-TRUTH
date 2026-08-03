================================================================================
ℹ️  OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.7.1)
Generado: 2026-08-03 03:59:13 UTC    Commit: 0e418e2d21bc
Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · C/L/K solo si el ciclo los trajo
================================================================================

ESTADO GLOBAL
  ✅ Engine          : OPERATIVO
  ✅ Axiomas         : coherente
  📦 Contenedores    : 14
  ✅ Roles vacíos    : 0
  ✅ Rechazados      : 0
  ⚠️ Acciones abiertas: 1
  ✅ Salud           : OPERATIVO — listo para avanzar

================================================================================
📐  VALUACIÓN (C · L · K → Tru) — solo evidencia depositada
================================================================================
  origen evidencia : ci_auditoria_contratos   n_ciclos=0
  Omega no calcula. Si C/L/K/Tru aparecen, salieron del ciclo (CA/FO).
  ⚪ Citación: ningún ciclo trajo bloque citacion

  ⚪ Sin ciclos en evaluaciones.json — nada que cuantificar aquí.
  pytest mide forma; la valuación de contenido aparece cuando un ciclo real deposita resultado.

📦  MÓDULOS Y ROLES
  +------+-----------+-----+--------------------------------------+
  | ROL  | ESTADO    | N   | MÓDULOS                              |
  +------+-----------+-----+--------------------------------------+
  | AX   | CARGADO   | 1   | axiomas                              |
  | CA   | CARGADO   | 1   | calculator                           |
  | CH   | CARGADO   | 1   | cache                                |
  | CIT  | CARGADO   | 1   | citacion                             |
  | CT   | CARGADO   | 1   | constante                            |
  | CX   | CARGADO   | 1   | contexto                             |
  | DG   | CARGADO   | 1   | diagnostico                          |
  | FO   | CARGADO   | 1   | formulas                             |
  | MC   | CARGADO   | 1   | correlacion_mecanica                 |
  | RE   | CARGADO   | 1   | realidad                             |
  | SF   | CARGADO   | 1   | self                                 |
  | TX   | CARGADO   | 1   | taxonomia                            |
  | UI   | CARGADO   | 1   | interfaz                             |
  | VX   | CARGADO   | 1   | verificacion                         |
  +------+-----------+-----+--------------------------------------+

================================================================================
⚠️  MAPA DE INTERVENCIÓN (por prioridad)
================================================================================

  ⚪ 1. [DATOS] resultados_evaluacion
     Detalle   : Sin ciclos en evaluaciones.json (normal si CI va sin humo y los tests no depositaron en ese artefacto)
     Impacto   : Omega no puede mostrar C/L/K/Tru de ciclos
     Acción    : Que los tests reales escriban evidencia o que un proceso legítimo deposite evaluaciones.json tras evaluar()

================================================================================
ℹ️  SALUD POR CAPA
================================================================================

  ✅ Constantes (CT)
      ALPHA = 26/27   BETA = 1/27

  ✅ Axiomas (AX)
      declaraciones = 418
      choques       = 0
      errores       = 0
      por_tipo      = {'axioma': 159, 'lema': 39, 'teorema': 115, 'corolario': 91, 'definicion': 14}

  ✅ Fórmulas (FO)
      coherente = True   faltas = []

  ✅ Mecánica (MC)
      coherente = True

  ✅ Calculator (CA)
      coherente = True  detalle = ['C', 'K', 'L']

  ✅ Contratos (CI)
      coherente=True  validos=14  caps_ok=65  caps_fallo=0

  ✅ Tests (pytest — forma)
      total=134  pasados=133  fallidos=0  tasa=99.25%
      nota: pytest no es Tru; cuantificación de contenido = tabla de ciclos

================================================================================
ℹ️  GENERATIVIDAD (TR1 / U1)
================================================================================
  |Θ| (AX)           : 274
  pares totales      : 37401
  pares compatibles  : 10388
  pares novedosos    : 4972
  |Im(⊕)| ? |Θ|      : ✅ GENERATIVO
  dominios           : ['auditoria', 'axiomas', 'cache', 'citacion', 'constantes', 'contexto', 'engine', 'epistemologia', 'evaluacion', 'formulas', 'inferencia_causal', 'informacion', 'logica', 'meta', 'ontologia', 'realidad', 'self', 'semantica', 'taxonomia', 'temporal', 'verificacion']
  roles vacíos       : []
  U1                 : NO_STAGNANT
  por_tipo_theta     : {'axioma': 159, 'teorema': 115}
  --- capa canónica (paper TR1) ---
  |Θ|_can           : 24 / 24
  novedosos_can     : 102  (paper: 153)
  |Im| ? |Θ| can    : GENERATIVO
  ids_faltantes     : []
  ids_sin_dominio   : []
  dominios_can      : ['EPI', 'INF', 'LOG', 'MET', 'ONT', 'SEM', 'TMP']
  nota               : Capa operativa = grafo del repo. Capa canonica = solo ids TR1 del paper. Dominio O/K: ver ids_dominio_k_o y cuerpos (no se clasifica entrada aquí).

================================================================================
📦  INVENTARIO RÁPIDO
================================================================================
Presente:
  ✅ AX: axiomas
  ✅ CA: calculator
  ✅ CH: cache
  ✅ CIT: citacion
  ✅ CT: constante
  ✅ CX: contexto
  ✅ DG: diagnostico
  ✅ FO: formulas
  ✅ MC: correlacion_mecanica
  ✅ RE: realidad
  ✅ SF: self
  ✅ TX: taxonomia
  ✅ UI: interfaz
  ✅ VX: verificacion
Ausente:
  ✅ (ninguno)
Rechazado:
  ✅ (ninguno)

================================================================================
ℹ️  INVENTARIO ENGINE (solo lectura)
================================================================================
  estado=OPERATIVO  n_eval_proceso_omega=0  (valuación mostrada = artefacto CI/tests, no este proceso)

================================================================================
✅  CIERRE
================================================================================
  Versión Omega      : 9.7.1
  Salud              : ✅ OPERATIVO — listo para avanzar
  Acciones abiertas  : 1
  Bloqueantes        : 0
  Ciclos valuados    : 0
  Este reporte no recalculó C, L, K ni Tru.
  Este reporte no ejecutó humo ni evaluar().
  Los números salen del sistema (CA/FO) vía evidencia depositada.
================================================================================

JSON: /home/runner/work/VPSI-TRUTH/VPSI-TRUTH/diagnostics/omega_report_data.json
