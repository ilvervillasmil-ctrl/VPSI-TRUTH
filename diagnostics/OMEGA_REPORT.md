================================================================================
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.5)
Generado: 2026-08-02 05:31:44 UTC    Commit: 28ebae5915e2
Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · prioriza intervención
================================================================================

ESTADO GLOBAL
  Engine          : OPERATIVO
  Axiomas         : coherente
  Contenedores    : 13
  Roles vacíos    : 0
  Rechazados      : 0
  Acciones abiertas: 1
  Salud           : OPERATIVO — listo para avanzar

MÓDULOS Y ROLES
  +------+-----------+-----+--------------------------------------+
  | ROL  | ESTADO    | N   | MÓDULOS                              |
  +------+-----------+-----+--------------------------------------+
  | AX   | CARGADO   | 1   | axiomas                              |
  | CA   | CARGADO   | 1   | calculator                           |
  | CH   | CARGADO   | 1   | cache                                |
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
MAPA DE INTERVENCIÓN (ordenado por prioridad)
================================================================================

  1. [DATOS] resultados_evaluacion
     Detalle   : Lista vacía en el paquete (Engine no entregó evaluaciones acumuladas en esta sesión de carga)
     Impacto   : No se puede auditar el camino de evaluación desde Omega
     Acción    : Quien invoque evaluar() debe dejar la lista en Engine; Omega solo la lee (get_resultados_evaluacion / inventario)

================================================================================
SALUD POR CAPA
================================================================================

  [OK] Constantes (CT)
      ALPHA = 26/27   BETA = 1/27

  [OK] Axiomas (AX)
      declaraciones = 315
      choques       = 0
      errores       = 0
      por_tipo      = {'axioma': 123, 'lema': 27, 'teorema': 90, 'corolario': 69, 'definicion': 6}

  [OK] Fórmulas (FO)
      coherente = True   faltas = []

  [OK] Mecánica (MC)
      coherente = True

  [OK] Contratos (CI)
      coherente=True  validos=13  caps_ok=53  caps_fallo=0

  [PENDIENTE] Camino de evaluación — sin resultados en el paquete

  [OK] Tests
      total=120  pasados=119  fallidos=0  tasa=99.17%

================================================================================
GENERATIVIDAD (TR1 / U1)
================================================================================
  |Θ| (AX)           : 213
  pares totales      : 22578
  pares compatibles  : 6106
  pares novedosos    : 1978
  |Im(⊕)| ? |Θ|      : GENERATIVO
  dominios           : ['constantes', 'contexto', 'epistemologia', 'evaluacion', 'inferencia_causal', 'informacion', 'logica', 'meta', 'ontologia', 'self', 'semantica', 'temporal']
  roles vacíos       : []
  U1                 : NO_STAGNANT
  por_tipo_theta     : {'axioma': 123, 'teorema': 90}
  --- capa canónica (paper TR1) ---
  |Θ|_can           : 24 / 24
  novedosos_can     : 102  (paper: 153)
  |Im| ? |Θ| can    : GENERATIVO
  ids_faltantes     : []
  ids_sin_dominio   : []
  dominios_can      : ['EPI', 'INF', 'LOG', 'MET', 'ONT', 'SEM', 'TMP']
  nota               : Capa operativa = grafo del repo. Capa canonica = solo ids TR1 del paper. Saber ≠ creer: comparar canonica con 24/153.

================================================================================
INVENTARIO RÁPIDO
================================================================================
Presente:
  ✓ AX: axiomas
  ✓ CA: calculator
  ✓ CH: cache
  ✓ CT: constante
  ✓ CX: contexto
  ✓ DG: diagnostico
  ✓ FO: formulas
  ✓ MC: correlacion_mecanica
  ✓ RE: realidad
  ✓ SF: self
  ✓ TX: taxonomia
  ✓ UI: interfaz
  ✓ VX: verificacion
Ausente:
Rechazado:
  (ninguno)

================================================================================
INVENTARIO ENGINE (solo lectura)
================================================================================
  estado=OPERATIVO  n_eval=0

================================================================================
CIERRE
================================================================================
  Versión Omega      : 9.5
  Salud              : OPERATIVO — listo para avanzar
  Acciones abiertas  : 1
  Bloqueantes        : 0
  Este reporte no recalculó nada.
  Este reporte no ejecutó humo ni evaluar().
  El orden de la lista = orden recomendado de trabajo.
================================================================================

JSON: /home/runner/work/VPSI-TRUTH/VPSI-TRUTH/diagnostics/omega_report_data.json
