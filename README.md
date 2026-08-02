# VPSI-TRUTH

**Sistema determinista de evaluación de verdad estructural**  
Framework Villasmil–Omega / Universal Coherence Framework (UCF) · VPSI v9.x

> No es un chatbot. No es un modelo de lenguaje. No es un filtro de opiniones.  
> Es un **mecanismo contractual** que calcula, registra y audita la coherencia de descripciones
> bajo reglas explícitas. Funciona *como* un organismo (partes interdependientes, fallar cerrado,
> centinelas por capa); **es** mecánica reproducible con contratos.

Autor: Ilver Villasmil · ORCID: [0009-0009-3413-4270](https://orcid.org/0009-0009-3413-4270)

---

## 1. Qué es (y qué no es)

### Qué es

**VPSI-TRUTH** es un repositorio de software cuya función central es:

1. Recibir una **petición** (descripción, fragmento de conversación, criterios de contexto).
2. Clasificar el **contexto observable** \(O\) bajo reglas deterministas.
3. Calcular factores **C** (coherencia), **L** (lógica), **K** (correlación con el dominio).
4. Aplicar la **Fórmula de la Verdad**:

\[
\begin{aligned}
\mathrm{Tru}_{Ri}(D) &= C(D)\cdot L(D)\cdot K(D) \\
\mathrm{Tru}_{total}(D) &= \bigl(\mathrm{Tru}_{Ri}(D)\cdot\alpha\bigr)+\beta
\end{aligned}
\]

con \(\alpha = 26/27\), \(\beta = 1/27\) (dominio estricto `fractions.Fraction`; sin floats en la ruta de decisión).

5. Dejar **evidencia** inspectable (JSON, reportes, CI) para que cualquiera contraste el informe con los datos.

Principio operativo: **saber ≠ creer**. El sistema no “opina”; ejecuta contratos. Si el grafo axiomático se contradice o un módulo declara una capacidad que no puede resolver, el sistema **se detiene o se delata** (arranque rechazado, contrato incoherente, choque axiomático).

### Qué no es

| No es | Por qué importa |
|--------|-----------------|
| Chatbot / asistente conversacional | No genera prosa libre como producto principal |
| LLM embebido en la ruta de verdad | Prohibidos componentes estocásticos en `core/` y `modules/` |
| Censor ideológico | No clasifica “aceptable”; calcula estructura bajo reglas |
| Caja negra | Artefactos CI y Omega son legibles sin reejecutar el cálculo |
| Yo consciente | El módulo `self` es **yo funcional en fase**, no persona |

---

## 2. Para qué sirve

- **Auditar** afirmaciones, diálogos o documentos: contradicción, deriva de contexto, K sin ancla en \(O\).
- **Exponer** el piso estructural \(\beta\): incluso con C=L=K=0, \(\mathrm{Tru}_{total}=\beta\); el techo observable involucra \(\alpha\).
- **Sostener** interfaces, guías o sistemas posteriores que necesiten un **cálculo de verdad reproducible**, no una respuesta persuasiva.
- **Permitir auditoría externa**: un tercero puede abrir `diagnostics/*.json` y verificar que el mapa Omega refleja la evidencia, no la inventa.

Implementación típica: biblioteca + orquestador (`Engine`) + pipeline CI como **juez externo**; la interfaz de usuario es un módulo (`UI`) de composición, no de autoridad sobre el cálculo.

---

## 3. Cómo se usa (visión)

```text
Humano / sistema externo
        │
        │  petición (dict: contexto, factores o material a clasificar)
        ▼
   Engine.evaluar(peticion)
        │
        │  orquesta solo lo declarado en cada CONTENEDOR
        ▼
   módulos (CX → CA → FO · AX · MC · …)
        │
        ▼
   resultado estructurado + acumulación en resultados_evaluacion
        │
        ├──► CACHE (evidencia de secuencia, si está montado)
        ├──► CI escribe evaluaciones.json + contratos_report.json
        └──► Omega Report lee artefactos y presenta el mapa
Entrada mínima conceptual: descripción (D) y, cuando aplique, enunciado de (O) / modo de entrada. Salida: estado, factores, Tru (cuando el camino está completo), errores y notas de contrato. Lo que el humano lee en CI: OMEGA_REPORT.md + JSON de evidencia.

4. Arquitectura — diagrama de información
flowchart TB
  subgraph entrada [Entrada]
    P[Petición / descripción D]
  end

  subgraph orquestacion [Orquestación]
    E[Engine]
  end

  subgraph anclas [Anclas]
    CT[CT constante α β]
    AX[AX cuerpo axiomático]
  end

  subgraph calculo [Cálculo]
    CX[CX contexto / O]
    CA[CA C L K]
    FO[FO Tru_Ri Tru_total]
    MC[MC correlación mecánica]
  end

  subgraph apoyo [Apoyo]
    RE[RE realidad]
    TX[TX taxonomía]
    VX[VX verificación]
    CH[CH cache]
    SF[SF self fase]
    UI[UI interfaz]
    DG[DG diagnóstico enlace]
  end

  subgraph evidencia [Evidencia y presentación]
    CI[CI juez externo]
    EV[evaluaciones.json]
    CR[contratos_report.json]
    OM[Omega Report]
  end

  P --> E
  E --> CT
  E --> AX
  E --> CX
  E --> CA
  E --> FO
  E --> MC
  E --> RE
  E --> TX
  E --> VX
  E --> CH
  E --> SF
  E --> UI
  E --> DG
  E --> CI
  CI --> EV
  CI --> CR
  EV --> OM
  CR --> OM
Cadena causal (orden lógico, no “opinión del Engine”)
CT ancla constantes
AX mantiene el grafo y detecta choques
CX clasifica O, estado, permite_k
CA calcula C, L, K (None/UNDEFINED si falta dato legítimo)
FO aplica la fórmula de la verdad
MC define el orden mecánico causa-efecto entre pasos
Engine solo invoca capacidades listadas en cada CONTENEDOR
CI verifica contratos y deposita evidencia
Omega solo presenta
Fatalidad estructural: si AX es incoherente, si falta un rol obligatorio, o si una capacidad declarada no es callable, el sistema no “sigue igual”: falla cerrado o el juez CI marca coherente: false.

5. El Engine
Ubicación: core/engine.py
Responsabilidad
Detalle
Descubrir módulos
Lee modules/*/__init__.py y el dict CONTENEDOR
Resolver dependencias
Roles, requiere, orden de carga
Ejecutar contratos
Contenedor.fn(clave) — sin inventar nombres
Evaluar
evaluar(peticion) acumula en resultados_evaluacion
Fallar cerrado
ArranqueError si strict y hay errores de arranque
Engine no es el experto de cada dominio. Cada módulo es autoridad de su función; Engine es el director que solo puede pedir lo que el contrato permite.
modules/
  /
    __init__.py     ← contrato CONTENEDOR + centinela (barrer/verificar/…)
    *.py            ← lógica de dominio (el init audita coherencia interna)
core/
  engine.py         ← orquestación
diagnostics/
  omega_report.py   ← solo presentación
  *.json            ← evidencia CI

6. Módulos — catálogo
Cada módulo expone un CONTENEDOR con al menos: nombre, rol, version, requiere, capacidades (mapa clave → función real).
El __init__.py es el centinela de su carpeta: si los archivos internos se contradicen o no cumplen la API esperada, el barrido del módulo debe reportarlo; el Engine no “arregla” el contenido.
6.1 Tabla de roles
Rol
Carpeta
Función en una frase
Capacidades típicas
CT
constante
Ancla (\alpha,\beta) del repo
alpha, beta, inventario
AX
axiomas
Cuerpo axiomático, choques, generatividad
verificar/barrer, inventario, axiomas, generatividad
FO
formulas
Fórmula de la verdad (Fraction)
verificar, evaluar, axiomas, inventario
MC
correlacion_mecanica
Manual causa-efecto del mecanismo
verificar, evaluar, inventario, axiomas
CX
contexto
Reglas de O, clasificación, permite_k
verificar/resolver, evaluar, inventario, axiomas
CA
calculator
Calcula C, L, K
calcular, verificar/barrer, inventario
RE
realidad
Ancla / filtro de representaciones de realidad
verificar, inventario
TX
taxonomia
Taxonomías deterministas (p. ej. manipulación)
verificar, aplicar, inventario, axiomas
VX
verificacion
Auditoría de verificación de sistema
verificar, axiomas
CH
cache
Registro inmutable de secuencias / evidencia
verificar, depositar, leer, secuencia, inventario
SF
self
Yo funcional en fase (capas L0–L7)
verificar, barrer, yo_funcional, oscilar
UI
interfaz
Composición de interfaces; sin autoridad de cálculo
componer, barrer, inventario, observar, …
DG
diagnostico
Enlace / censo de diagnóstico (sin poder de alterar verdad)
censo, verificar, presentar, reportar, inventario
6.2 Conexión entre carpetas (vista repo)
modules/
├── constante/              CT   anclas α, β
├── axiomas/                AX   grafo · choques · TR1
│   └── (cuerpos: VPSI, contexto_AX, correlacion, self, …)
├── formulas/               FO   truth.py → tru_ri, tru_total
├── correlacion_mecanica/   MC   orden mecánico · archivos MC
├── contexto/               CX   reglas de O · clasificadores
├── calculator/             CA   coherencia.py · logica.py · correlacion_k.py
├── realidad/               RE   filtro / ancla de R
├── taxonomia/              TX   p.ej. manipulation_TX.py
├── verificacion/           VX   auditar_sistema
├── cache/                  CH   depósito de evidencia
├── self/                   SF   capas L0…L7 (fase)
├── interfaz/               UI   composición UI
└── diagnostico/            DG   puente de diagnóstico

core/
└── engine.py               orquestador + Contenedor + Registro

diagnostics/
├── omega_report.py         presentador 9.6
├── evaluaciones.json       evidencia de evaluar() (CI)
├── contratos_report.json   juez de contratos (CI)
├── axioms_report.json
├── test_results.xml
└── OMEGA_REPORT.md
6.3 Qué hace / qué no hace (resumen por capa crítica)
Módulo
Hace
No hace
CX
Define reglas para armar y clasificar contexto; permite_k
No calcula Tru_total
CA
Calcula C, L, K según petición
No aplica α/β (eso es FO)
FO
Aplica la fórmula canónica en Fraction
No inventa C/L/K
AX
Juzga coherencia del grafo; generatividad
No orquesta el pipeline completo
MC
Especifica el orden mecánico
No sustituye el juicio axiomático
Omega
Presenta
No evalúa, no hace humo, no rellena huecos

7. Cuerpo axiomático
Las declaraciones viven bajo AX (y cuerpos satélite). Tipos habituales: axioma, lema, teorema, corolario, definición.
Campos conceptuales de una declaración:
	•	identidad (id)
	•	sujeto / relacion / objeto
	•	polaridad
	•	depende_de / gobierna
	•	enunciado
Choques: contradicción directa o de cota → barrer() marca incoherente → el sistema no debe “seguir como si el grafo fuera sano”.
Generatividad (TR1 / U1): mide si el grafo recombina y produce pares novedosos en dominios (|Im(⊕)| vs (|\Theta|)). “GENERATIVO” describe expansión del grafo, no omnisciencia ni verdad absoluta del marco.

8. Fractalidad y escalas de contexto
El mismo aparato se aplica a:
	•	una palabra o morfología,
	•	una frase,
	•	un turno de diálogo,
	•	una conversación con cambios de O,
	•	un dominio formal (p. ej. propulsión) donde las expansiones deben seguir reglas de estabilidad de O.
Contexto indefinido o con ligaduras contradictorias no se “suaviza”: se clasifica y, si corresponde, se niega K completo o se degrada coherencia/lógica en la ruta de evaluación.
Eso es fractal en el sentido operativo: misma familia de reglas a varias escalas, no metáfora decorativa.

9. Integridad y auditoría (credibilidad)
La credibilidad no se pide: se estructura.
9.1 Filtros internos
Filtro
Dónde
Efecto
Centinela de módulo
cada __init__.py
API y coherencia de archivos del módulo
Grafo AX
barrer()
choques → incoherente
Dominio Fraction
FO + compuerta CI
float rechazado en ruta de verdad
Prohibición estocástica
AST sobre core/ y modules/
sin random/ML en decisión
Contratos
Contenedor.fn
clave declarada debe ser callable real
9.2 Filtro externo (CI)
Pipeline típico:
	1	Invariante (\alpha+\beta=1)
	2	Barrido axiomático (detalle de choques)
	3	Sin imports estocásticos
	4	Fórmulas y dominio Fraction
	5	Engine operativo + evaluar mínimo
	6	Pytest
	7	Auditoría estructural de contratos (determinismo, idempotencia, cobertura)
	8	Escritura de evaluaciones.json (evidencia de las evaluaciones de esa auditoría)
	9	Omega Report (solo lectura de artefactos)
	10	Coherence guard (regresión de tests)
	11	Upload + commit de historia de diagnósticos
Cualquiera puede descargar los artefactos y contrastar:
evaluaciones.json     → qué devolvió evaluar en la auditoría
contratos_report.json → si los contratos cuadran
OMEGA_REPORT.md       → si el mapa refleja esos datos
Omega no es el juez: es el visor. El juez es el CI + los contratos + AX.

10. Artefactos `diagnostics/`
Archivo
Significado
evaluaciones.json
Evidencia persistente de evaluar() generada por la auditoría CI
contratos_report.json
Informe del juez de contratos (roles, capacidades, coherente)
axioms_report.json
Salida de barrer() AX
test_results.xml
Pytest JUnit
coherence_history.json
Serie temporal de passed/failed
OMEGA_REPORT.md
Mapa de trabajo legible
omega_report_data.json
Paquete estructurado que Omega serializó
omega_report.py
Código del presentador (v9.6)

11. Cómo correr
Requisitos
	•	Python 3.11+
	•	Dependencias: requirements.txt
	•	Estructura core/, modules/, diagnostics/, tests/
Local (idea)
python -m pip install -r requirements.txt
pytest tests/ -v --tb=short --junit-xml=diagnostics/test_results.xml
# Arranque manual del Engine y, si existen artefactos, Omega:
python diagnostics/omega_report.py
El orden correcto cuando se quiere el camino de evaluación en Omega es el del CI: auditoría de contratos (escribe evaluaciones.json) → luego Omega.
Variables útiles
	•	OMEGA_STRICT=1 — Omega sale con código ≠ 0 si la entrada está incompleta o el Engine no está operativo.

12. Madurez (honesto)
Capa
Estado aproximado
CT, AX, FO, dominio Fraction
Núcleo estable
Engine + contratos + CI juez
Operativo
CX, CA, MC
En uso; extensibles por archivos bajo el init
CH, SF, UI
En fase / parcial
Omega 9.6
Presentación pura + puente de evidencia
“Organismo” pleno
No reivindicado: mecánica con interdependencia y fail-closed
El repositorio genera estructura (TR1) cuando el grafo y los contratos lo permiten; no fuerza narrativa de completitud.

13. Autor
Ilver Villasmil Investigador independiente ORCID: 0009-0009-3413-4270
Marco: Universal Integration System (UIS) / Villasmil–Omega / UCF / VPSI-TRUTH.

Este documento describe el sistema tal como está diseñado para ser auditado: contratos, evidencia y presentación separados. Si el mapa y los JSON no coinciden, prevalece la evidencia.

