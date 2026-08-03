================================================================================
ℹ️  OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.8)
Generado: 2026-08-03 21:56:08 UTC    Commit: b590cb47d893
Orden: (1) Auditoría VPSI  (2) Último test  (3) Mapa / capas
Cálculo: sistema (CA/FO/Engine) · Omega solo presenta
================================================================================

══════════════════════════════════════════════════════════════════════════════
  AUDITORÍA DEL VPSI  ·  el repositorio como objeto
  Auto-auditoría del sistema (contexto O_VPSI_REPO) · valores del ciclo
══════════════════════════════════════════════════════════════════════════════
  Estado     : ✅ OK
  permite_k  : True

  📐  CÁLCULO  (fórmula canónica VPSI)
  ┌─────────────────────────────────────────────────────────┐
  │  C          =  1                                       │
  │  L          =  1                                       │
  │  K          =  1                                       │
  │─────────────────────────────────────────────────────────│
  │  Tru_Ri     =  C · L · K                              │
  │             =  1                                       │
  │─────────────────────────────────────────────────────────│
  │  Tru_total  =  (Tru_Ri · α) + β                       │
  │             =  1                                       │
  │  ancla      α=26/27  β=1/27                           │
  └─────────────────────────────────────────────────────────┘

  Taxonomía  : none
  📎 Citas (teoremas / axiomas / normas):
       1. CX-A14
       2. CX-A1
       3. CX-C4
       4. PA-A1
       5. PA-A2
       6. PA-T1
       7. PA-C2
       8. [citacion] CIT-CICLO
  CIT resumen: n_citas=1  n_anuncios=1
  Origen     : omega_report:PETICION_AUDITORIA_VPSI
  Secuencia  : 1
══════════════════════════════════════════════════════════════════════════════

══════════════════════════════════════════════════════════════════════════════
  ÚLTIMO TEST EVALUADO
  Último ciclo real depositado (tests / uso) · mismos campos
══════════════════════════════════════════════════════════════════════════════
  Estado     : ✅ OK
  permite_k  : True

  📐  CÁLCULO  (fórmula canónica VPSI)
  ┌─────────────────────────────────────────────────────────┐
  │  C          =  1                                       │
  │  L          =  1                                       │
  │  K          =  0                                       │
  │─────────────────────────────────────────────────────────│
  │  Tru_Ri     =  C · L · K                              │
  │             =  0                                       │
  │─────────────────────────────────────────────────────────│
  │  Tru_total  =  (Tru_Ri · α) + β                       │
  │             =  1/27                                    │
  │  ancla      α=26/27  β=1/27                           │
  └─────────────────────────────────────────────────────────┘

  Taxonomía  : none
  📎 Citas (teoremas / axiomas / normas):
       1. CX-A14
       2. CX-A1
       3. CX-C4
  Origen     : test_conversacion
  Secuencia  : 6
══════════════════════════════════════════════════════════════════════════════

ESTADO GLOBAL
  ✅ Engine       : OPERATIVO
  ✅ Axiomas      : coherente
  📦 Contenedores : 14
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

  ✅ Sin acciones pendientes.

================================================================================
ℹ️  SALUD POR CAPA
================================================================================

  ✅ Constantes (CT)
      ALPHA = 26/27   BETA = 1/27

  ✅ Axiomas (AX)
      declaraciones = 411
      choques       = 0
      errores       = 0
      por_tipo      = {'axioma': 144, 'lema': 44, 'teorema': 107, 'corolario': 99, 'definicion': 17}

  ✅ Fórmulas (FO)
      coherente = True

  ✅ Mecánica (MC)
      coherente = True

  ✅ Calculator (CA)
      coherente = True

  ✅ Contratos (CI)
      coherente=True  validos=14  caps_ok=67  caps_fallo=0

  ✅ Tests (pytest — forma)
      total=134  pasados=133  fallidos=0  tasa=99.25%

================================================================================
ℹ️  GENERATIVIDAD (TR1 / U1)
================================================================================
  |Θ| (AX)           : 251
  pares totales      : 31375
  pares compatibles  : 9159
  pares novedosos    : 5277
  |Im(⊕)| ? |Θ|      : ✅ GENERATIVO
  dominios           : ['K', 'Tru_Ri', 'admisibilidad_medida', 'ancla_error', 'auditoria', 'axiomas', 'cache', 'citacion', 'composicion', 'constantes', 'contexto', 'correlacion', 'criterio_error', 'engine', 'entendimiento_operativo', 'entrenamiento', 'epistemologia', 'evaluacion', 'formulas', 'inferencia_causal', 'informacion', 'invarianza_significado', 'logica', 'maquina_sin_R', 'meta', 'ontologia', 'prioridad_mapa', 'probabilidad_subordinada', 'realidad', 'seleccion_correlacion', 'self', 'semantica', 'taxonomia', 'temporal', 'verificacion']
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
  Versión Omega      : 9.8
  Salud              : ✅ OPERATIVO — listo para avanzar
  Acciones abiertas  : 0
  Bloqueantes        : 0
  Caja 1             : Auditoría del VPSI (sistema)
  Caja 2             : Último test evaluado
  Omega no inventa C/L/K/Tru; los lanza el ciclo del sistema.
================================================================================

JSON: /home/runner/work/VPSI-TRUTH/VPSI-TRUTH/diagnostics/omega_report_data.json
