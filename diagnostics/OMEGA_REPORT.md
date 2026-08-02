================================================================================
ℹ️  OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.6)
Generado: 2026-08-02 23:47:24 UTC    Commit: 2e3550f3818b
Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · prioriza intervención
================================================================================

ESTADO GLOBAL
  ✅ Engine          : OPERATIVO
  ✅ Axiomas         : coherente
  📦 Contenedores    : 14
  ✅ Roles vacíos    : 0
  ✅ Rechazados      : 0
  ✅ Acciones abiertas: 0
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

  ✅ No hay acciones pendientes. Sistema limpio.

================================================================================
ℹ️  SALUD POR CAPA
================================================================================

  ✅ Constantes (CT)
      ALPHA = 26/27   BETA = 1/27

  ✅ Axiomas (AX)
      declaraciones = 397
      choques       = 0
      errores       = 0
      por_tipo      = {'axioma': 154, 'lema': 35, 'teorema': 114, 'corolario': 85, 'definicion': 9}

  ✅ Fórmulas (FO)
      coherente = True   faltas = []

  ✅ Mecánica (MC)
      coherente = True

  ✅ Contratos (CI)
      coherente=True  validos=14  caps_ok=63  caps_fallo=0

  ✅ Camino de evaluación
      n = 3   origen = ci_auditoria_contratos
    · seq 1/3  estado=UNDEFINED  Tru_Ri=UNDEFINED  Tru_total=UNDEFINED
    ✅ seq 2/3  estado=OK  Tru_Ri=1  Tru_total=1
    ✅ seq 3/3  estado=OK  Tru_Ri=1  Tru_total=1

  ✅ Tests
      total=134  pasados=133  fallidos=0  tasa=99.25%

================================================================================
ℹ️  GENERATIVIDAD (TR1 / U1)
================================================================================
  |Θ| (AX)           : 268
  pares totales      : 35778
  pares compatibles  : 9819
  pares novedosos    : 4535
  |Im(⊕)| ? |Θ|      : ✅ GENERATIVO
  dominios           : ['auditoria', 'axiomas', 'cache', 'citacion', 'constantes', 'contexto', 'engine', 'epistemologia', 'evaluacion', 'formulas', 'inferencia_causal', 'informacion', 'logica', 'meta', 'ontologia', 'realidad', 'self', 'semantica', 'taxonomia', 'temporal']
  roles vacíos       : []
  U1                 : NO_STAGNANT
  por_tipo_theta     : {'axioma': 154, 'teorema': 114}
  --- capa canónica (paper TR1) ---
  |Θ|_can           : 24 / 24
  novedosos_can     : 102  (paper: 153)
  |Im| ? |Θ| can    : GENERATIVO
  ids_faltantes     : []
  ids_sin_dominio   : []
  dominios_can      : ['EPI', 'INF', 'LOG', 'MET', 'ONT', 'SEM', 'TMP']
  nota               : Capa operativa = grafo del repo. Capa canonica = solo ids TR1 del paper. Saber ≠ creer: comparar canonica con 24/153.

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
  Acciones abiertas  : 0
  Bloqueantes        : 0
  Este reporte no recalculó nada.
  Este reporte no ejecutó humo ni evaluar().
  El orden de la lista = orden recomendado de trabajo.
================================================================================

JSON: /home/runner/work/VPSI-TRUTH/VPSI-TRUTH/diagnostics/omega_report_data.json
