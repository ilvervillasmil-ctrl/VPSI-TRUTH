================================================================================
ℹ️  OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.6)
Generado: 2026-08-03 03:37:14 UTC    Commit: 194f839f11ff
Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · prioriza intervención
================================================================================

ESTADO GLOBAL
  ✅ Engine          : OPERATIVO
  ✅ Axiomas         : coherente
  📦 Contenedores    : 14
  ✅ Roles vacíos    : 0
  ✅ Rechazados      : 0
  ⚠️ Acciones abiertas: 1
  ✅ Salud           : OPERATIVO — listo para avanzar

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
⚠️  MAPA DE INTERVENCIÓN (ordenado por prioridad)
================================================================================

  ⚪ 1. [DATOS] resultados_evaluacion
     Detalle   : Sin diagnostics/evaluaciones.json o lista vacía (la auditoría aún no depositó evidencia)
     Impacto   : No se puede auditar el camino de evaluación desde Omega
     Acción    : Ejecutar auditoría de contratos antes de Omega; debe escribir diagnostics/evaluaciones.json

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

  ✅ Contratos (CI)
      coherente=True  validos=14  caps_ok=65  caps_fallo=0

  ⚪ Camino de evaluación — sin evidencia en evaluaciones.json

  ✅ Tests
      total=134  pasados=133  fallidos=0  tasa=99.25%

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
  estado=OPERATIVO  n_eval_en_este_proceso=0  (el n del camino viene del artefacto CI)

================================================================================
✅  CIERRE
================================================================================
  Versión Omega      : 9.6
  Salud              : ✅ OPERATIVO — listo para avanzar
  Acciones abiertas  : 1
  Bloqueantes        : 0
  Este reporte no recalculó nada.
  Este reporte no ejecutó humo ni evaluar().
  El orden de la lista = orden recomendado de trabajo.
================================================================================

JSON: /home/runner/work/VPSI-TRUTH/VPSI-TRUTH/diagnostics/omega_report_data.json
