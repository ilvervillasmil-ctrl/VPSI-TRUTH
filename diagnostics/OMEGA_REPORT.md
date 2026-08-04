================================================================================
ℹ️  OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.9)
Generado: 2026-08-04 03:45:59 UTC    Commit: 2a59214fb131
Orden: (1) Auditoría VPSI  (2) Último test  (3) Mapa / capas
Contrato: Omega SOLO LEE lo que el ciclo depositó · no calcula · no rellena
================================================================================

══════════════════════════════════════════════════════════════════════════════
  AUDITORÍA DEL VPSI  ·  el repositorio como objeto
  Auto-auditoría del sistema (contexto O_VPSI_REPO) · valores LEÍDOS del ciclo
══════════════════════════════════════════════════════════════════════════════
  Estado     : ⚠️ PARCIAL
  Razón      : Faltan factores C/L/K (CA no los entregó o no vinieron en la petición)
  permite_k  : True

  📖  LECTURA DEL CICLO  (Omega no calcula; solo presenta)
  Factores leídos: 0/3  (C=⚪ L=⚪ K=⚪)
  ┌─────────────────────────────────────────────────────────┐
  │  ⚪ C (coherencia  ) =  no depositado                   │
  │  ⚪ L (lógica      ) =  no depositado                   │
  │  ⚪ K (correlación ) =  no depositado                   │
  │─────────────────────────────────────────────────────────│
  │  ⚪ Tru_Ri     =  no depositado                           │
  │  ⚪ Tru_total  =  no depositado                           │
  └─────────────────────────────────────────────────────────┘
  Nota: ✅ leído del ciclo · ⚠️ UNDEFINED (base nula) · ⚪ no depositado
        0 es valor real. Omega no rellena ni recalcula.

  Taxonomía  : none
  📎 Citas (teoremas / axiomas / normas):
       1. [citacion] CIT-CICLO
  CIT resumen: n_citas=1  n_anuncios=1
  Origen     : omega_report:PETICION_AUDITORIA_VPSI
  Secuencia  : 1
══════════════════════════════════════════════════════════════════════════════

══════════════════════════════════════════════════════════════════════════════
  ÚLTIMO TEST EVALUADO
  Último ciclo real depositado (tests / uso) · valores LEÍDOS del ciclo
══════════════════════════════════════════════════════════════════════════════
  Estado     : ⚠️ PARCIAL
  Razón      : Faltan factores C/L/K (CA no los entregó o no vinieron en la petición)
  permite_k  : True

  📖  LECTURA DEL CICLO  (Omega no calcula; solo presenta)
  Factores leídos: 2/3  (C=⚪ L=✅ K=✅)
  ┌─────────────────────────────────────────────────────────┐
  │  ⚪ C (coherencia  ) =  no depositado                   │
  │  ✅ L (lógica      ) =  1                               │
  │  ✅ K (correlación ) =  0                               │
  │─────────────────────────────────────────────────────────│
  │  ⚪ Tru_Ri     =  no depositado                           │
  │  ⚪ Tru_total  =  no depositado                           │
  └─────────────────────────────────────────────────────────┘
  Nota: ✅ leído del ciclo · ⚠️ UNDEFINED (base nula) · ⚪ no depositado
        0 es valor real. Omega no rellena ni recalcula.

  Taxonomía  : none
  📎 Citas      : — (sin ids/anuncios en el ciclo)
  Origen     : test_conversacion
  Secuencia  : 6
══════════════════════════════════════════════════════════════════════════════

ESTADO GLOBAL
  ✅ Engine       : OPERATIVO
  ✅ Axiomas      : coherente
  📦 Contenedores : 15
  ✅ Roles vacíos : 0
  ✅ Rechazados   : 0
  ✅ Salud        : OPERATIVO — listo para avanzar

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
  | DI   | CARGADO   | 1   | diccionario                          |
  | FO   | CARGADO   | 1   | formulas                             |
  | MC   | CARGADO   | 1   | correlacion_mecanica                 |
  | RE   | CARGADO   | 1   | realidad                             |
  | SF   | CARGADO   | 1   | self                                 |
  | TX   | CARGADO   | 1   | taxonomia                            |
  | UI   | CARGADO   | 1   | interfaz                             |
  | VX   | CARGADO   | 1   | verificacion                         |
  +------+-----------+-----+--------------------------------------+

================================================================================
⚠️  MAPA DE INTERVENCIÓN
================================================================================

  ⚪ 1. [DATOS] auditoria_vpsi
     Detalle   : Ciclo de auto-auditoría sin factores depositados legibles
     Impacto   : La caja 1 no muestra C/L/K leídos
     Acción    : Engine.evaluar(PETICION_AUDITORIA_VPSI) debe depositar resultado

================================================================================
ℹ️  SALUD POR CAPA
================================================================================

  ✅ Constantes (CT)
      ALPHA = 26/27   BETA = 1/27

  ✅ Axiomas (AX)
      declaraciones = 487
      choques       = 0
      errores       = 0
      por_tipo      = {'axioma': 161, 'lema': 54, 'teorema': 121, 'corolario': 116, 'definicion': 35}

  ✅ Fórmulas (FO)
      coherente = True

  ✅ Mecánica (MC)
      coherente = True

  ✅ Calculator (CA)
      coherente = True

  ✅ Contratos (CI)
      coherente=True  validos=15  caps_ok=78  caps_fallo=0

  ✅ Tests (pytest — forma)
      total=134  pasados=133  fallidos=0  tasa=99.25%

================================================================================
ℹ️  GENERATIVIDAD (TR1 / U1)
================================================================================
  |Θ| (AX)           : 282
  pares totales      : 39621
  pares compatibles  : 10010
  pares novedosos    : 5959
  |Im(⊕)| ? |Θ|      : ✅ GENERATIVO
  dominios           : ['K', 'Tru_Ri', 'admisibilidad_medida', 'ancla_error', 'auditoria', 'axiomas', 'cache', 'calculator', 'citacion', 'composicion', 'condicion_funcionamiento', 'conocimiento_operativo', 'constantes', 'conteos', 'contexto', 'correccion_acumulativa', 'correlacion', 'criterio_error', 'engine', 'entendimiento_operativo', 'entrenamiento', 'epistemologia', 'evacion_ciclo', 'evaluacion', 'exactitud_memoria', 'formulas', 'frontera_disenador', 'indefinido', 'inferencia_causal', 'informacion', 'invarianza_significado', 'logica', 'maquina_sin_R', 'medicion', 'medicion_fiable', 'meta', 'ontologia', 'origen_distorsion', 'precision_mecanismo', 'prioridad_mapa', 'probabilidad_subordinada', 'realidad', 'reapertura_legitima', 'seleccion_correlacion', 'self', 'semantica', 'subordinacion_probabilidad', 'taxonomia', 'temporal', 'traza_resolucion', 'truth', 'verificacion']
  U1                 : NO_STAGNANT
  --- capa canónica ---
  |Θ|_can            : 24 / 24
  novedosos_can      : 102
  |Im| ? |Θ| can     : GENERATIVO

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
  ✅ DI: diccionario
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
✅  CIERRE
================================================================================
  Versión Omega      : 9.9
  Salud              : ✅ OPERATIVO — listo para avanzar
  Acciones abiertas  : 1
  Bloqueantes        : 0
  Caja 1             : Auditoría del VPSI (sistema) — LECTURA
  Caja 2             : Último test evaluado — LECTURA
  Omega no inventa C/L/K/Tru; lee lo que el ciclo depositó.
  0 = cero real · UNDEFINED = base nula · no depositado = no vino
================================================================================

JSON: /home/runner/work/VPSI-TRUTH/VPSI-TRUTH/diagnostics/omega_report_data.json
