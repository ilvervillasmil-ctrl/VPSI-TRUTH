

```markdown
# VPSI-TRUTH: Implementación del Protocolo SSMC
**Metodología Estructural de la Verdad**
Ilver Villasmil, 2026
Versión: 9.4 (En Construcción)

---

---

## Índice
1. [Propósito](#1-propósito)
2. [Principio de Arquitectura](#2-principio-de-arquitectura)
3. [Estructura del Repositorio](#3-estructura-del-repositorio)
4. [Mecanismo de Funcionamiento](#4-mecanismo-de-funcionamiento)
   - [4.1. Dos Secuencias Distintas](#41-dos-secuencias-distintas)
   - [4.2. Los Tres Filtros](#42-los-tres-filtros)
   - [4.3. Lo Indefinido no es Cero](#43-lo-indefinido-no-es-cero)
5. [Módulos](#5-módulos)
   - [5.1. `core/engine.py` — Autoridad de Despacho](#51-coreenginepy---autoridad-de-despacho)
   - [5.2. `modules/axiomas/` — Juez de Contraste](#52-modulesaxiomas---juez-de-contraste)
   - [5.3. `modules/constante/` — El Ancla](#53-modulesconstante---el-ancla)
   - [5.4. `modules/formulas/` — La Ecuación](#54-modulesformulas---la-ecuación)
   - [5.5. `modules/realidad/` — Canal de Evidencia](#55-modulesrealidad---canal-de-evidencia)
   - [5.6. `modules/correlacion_mecanica/` — Secuencia y Acoplamiento](#56-modulescorrelacion_mecanica---secuencia-y-acoplamiento)
   - [5.7. `modules/verificacion/` — Auto-Auditoría](#57-modulesverificacion---auto-auditoría)
   - [5.8. `modules/calculador/` — Produce C, L, K](#58-modulescalculador---produce-c-l-k)
   - [5.9. `modules/contexto/` — Lógica del Contexto](#59-modulescontexto---lógica-del-contexto)
   - [5.10. `modules/taxonomia/` — Tácticas T1–T15](#510-modulestaxonomia---tácticas-t1t15)
   - [5.11. `modules/cache/` — Registro Forense](#511-modulescache---registro-forense)
   - [5.12. `core/centinela.py` — Filtro de Orquestación](#512-corecentinelapy---filtro-de-orquestación)
   - [5.13. `core/diagnostico.py` — Tabla de Códigos](#513-corediagnosticopy---tabla-de-códigos)
6. [Fórmulas Canónicas](#6-fórmulas-canónicas)
7. [Axiomas del Documento no Cargados](#7-axiomas-del-documento-no-cargados)
8. [Problemas Abiertos](#8-problemas-abiertos)
9. [Prioridad de Construcción](#9-prioridad-de-construcción)
10. [Convenciones](#10-convenciones)
11. [CI/CD](#11-cicd)
12. [Tests](#12-tests)
13. [Diagrama de Flujo](#13-diagrama-de-flujo)

---

---

## 1. Propósito

Trasladar la evaluación de un discurso estructurado desde la **apreciación cualitativa** hacia una **auditoría formal, determinista y reproducible**.

El sistema mide toda emisión contra un **contexto declarado** (`Octx`) mediante el **funcional canónico**:

```
Tru_Ri(D)    = C(D) · L(D) · K(D)
Tru_total(D) = (Tru_Ri(D) · α) + β
```

donde:
- **α = 26/27** (techo estructural).
- **β = 1/27** (piso ontológico irreducible).
- **C**: Coherencia interna.
- **L**: Invariancia lógica.
- **K**: Correlación con el contexto `Octx`.

**Objetivo:**
- Detectar manipulación estructural: `C` y `L` altas con `K` colapsada (forma impecable, ancla rota).
- Aplicable a cualquier sistema: Personas, instituciones, IA, etc.

---

---

## 2. Principio de Arquitectura

El sistema **está diseñado para fallar**:
- Cada módulo es **independiente** en su cálculo y contexto.
- **Ningún módulo garantiza nada por sí solo**.
- Si una pieza falla, **no degrada el resultado: lo anula** (Principio **TA5**: multiplicatividad sin compensación).
- **Sincronización total** = Todos los módulos convergen.

**Puntos críticos sin segundo canal de verificación:**

| Punto | Razón | Anclaje |
|---|---|---|
| **CONSTANTES** | Todos dependen de α y β. Si fallan, todos coinciden mal. | Derivadas del cubo 3×3×3: 27 celdas, 26 accesibles, 1 encerrada. |
| **AXIOMAS** | Es el juez de contradicciones. Una contradicción en él no la ve nadie. | Piso de carga: Si no cargó lo que debía, falla. |

**Todo lo demás se sostiene por convergencia entre canales.**

---

~~~
VPSI-TRUTH/
├── core/
│   ├── engine.py                  # Autoridad de despacho          [MONTADO]
│   ├── diagnostico.py             # Tabla de códigos               [HUÉRFANO]
│   └── centinela.py               # Filtro de orquestación         [PENDIENTE]
│
├── modules/
│   ├── axiomas/                   # AX: Juez de contraste          [MONTADO]
│   │   ├── __init__.py            #   Cargador + barrido
│   │   ├── VPSI.py                #   89 declaraciones
│   │   ├── correlacion.py         #   36 declaraciones (causalidad)
│   │   └── self.py                #   22 declaraciones (Yo Funcional)
│   │
│   ├── constante/                 # CT: α y β                      [MONTADO]
│   │   └── __init__.py
│   │
│   ├── formulas/                  # FO: tru_ri, tru_total          [MONTADO]
│   │   └── truth.py
│   │
│   ├── verificacion/              # VX: Auto-auditoría   [ROL NO ADMITIDO]
│   │   └── __init__.py
│   │
│   ├── realidad/                  # RE: Canal de evidencia [ROL NO ADMITIDO]
│   │   ├── __init__.py
│   │   └── acceso.py
│   │
│   ├── correlacion_mecanica/      # MC: Secuencia         [ROL NO ADMITIDO]
│   │   └── __init__.py
│   │
│   ├── calculador/                # CA: Produce C, L, K            [PENDIENTE]
│   │   └── __init__.py
│   │
│   ├── contexto/                  # CX: Lógica del contexto        [PENDIENTE]
│   │   └── __init__.py
│   │
│   ├── taxonomia/                 # TX: Tácticas T1–T15            [PENDIENTE]
│   │   └── __init__.py
│   │
│   └── cache/                     # Registro forense               [PENDIENTE]
│       └── __init__.py
│
├── diagnostics/
│   └── omega_report.py            # Informe de compuertas          [MONTADO]
│
├── tests/
│   └── test_vpsi.py               # Suite única                    [MONTADO]
│
└── .github/workflows/
    └── ci.yml                     # Pipeline de CI/CD              [MONTADO]
~~~



---

---

## 4. Mecanismo de Funcionamiento

---

### 4.1. Dos Secuencias Distintas

#### Secuencia del Método (Tiempo del Auditor)
1. Declarar `Octx` antes de cualquier interacción.
2. Fijar las premisas del sistema evaluado.
3. Registrar y puntuar cada emisión contra `Octx`.
4. Clasificar desviaciones con la taxonomía (T1–T15).
5. Reconstruir y contrastar de forma independiente.

#### Secuencia del Engranaje (Tiempo de la Máquina)
Orden de una pasada para cada mensaje:
```
AX → CX → RE → CA → FO → TX → CENTINELA → CACHE
```

- **AX**: Barrido axiomático (verifica coherencia).
- **CX**: Contexto (define conteos `k`, `m`, `r`, `p`, etc.).
- **RE**: Realidad (canal de evidencia `R → X`).
- **CA**: Calculador (produce `C`, `L`, `K`).
- **FO**: Fórmulas (calcula `Tru_Ri` y `Tru_total`).
- **TX**: Taxonomía (clasifica tácticas).
- **CENTINELA**: Verifica la orquestación completa.
- **CACHE**: Registra ambas ramas (aprobados y rechazados).

**Cierre cíclico (R6):**
La pasada `N` termina en el `CACHE`, y ese `CACHE` es el **estado inicial** de la pasada `N+1`.

---

### 4.2. Los Tres Filtros

Cada filtro mira un **objeto distinto** y **no duplica** al anterior:

| Filtro | Objeto | Dónde Vive | Función |
|---|---|---|---|
| `__init__.py` del módulo | Lógica interna del contenedor | Cada `modules/*/` | Valida la coherencia interna del módulo. |
| **Engine** | Que el módulo cuadre con los demás y con los axiomas | `core/engine.py` | Verifica la integración entre módulos. |
| **Centinela** | La orquestación completa | `core/centinela.py` | Certifica que el resultado se deriva de sus premisas. |

**Regla:**
- Solo cuando el centinela aprueba, hay salida.
- El `CACHE` registra **ambas ramas** (aprobados y rechazados).
  - Razón: Un sistema que solo guarda salidas exitosas tiene **sesgo de supervivencia** y no puede detectar patrones de fallo reproducibles.

---
### 4.3. Lo Indefinido no es Cero

- Sin `Octx` declarado, `K` queda **indefinida y no nula** (Lema 1.16).
- El cómputo del funcional es **inviable**, no vale cero.
- Lo indefinido se separa:
  - Se puntúa **lo definible**.
  - Quien intente refugiarse en lo indefinido para no comprometerse **queda registrado por la taxonomía** (aunque el factor no lo capture).
- El cálculo mide correspondencia; la táctica mide la maniobra.

---

---

## 5. Módulos

---

### 5.1. `core/engine.py` — Autoridad de Despacho
**Estado:** MONTADO

- **Función:** Ningún contenedor invoca a otro. Todo pasa por aquí.
- **Componentes:**
  - `Registro`: Descubre y valida contenedores.
  - `Contenedor`: Envoltura de un módulo.
  - `Invocador`: Llamada controlada.
  - `Compositor`: Aplica el funcional.
  - `Engine`: Orquesta.
- **Roles admitidos:** `('AX', 'CT', 'FO', 'CA', 'CX', 'TX')`
- **Obligatorios:** `AX`, `CT`, `FO`
- **Frontera de tipos:**
  - `normalizar()` acepta `Fraction`, `int`, `str`.
  - Rechaza `float`.
  - Exige dominio `[0,1]`.
  - Propaga `UNDEFINED`.
- **Errores:**
  - `AutoridadError`, `ContratoError`, `ArranqueError`, `DominioError`, `CotaError`, `FormulaError`.

---

### 5.2. `modules/axiomas/` — Juez de Contraste
**Estado:** MONTADO

- **Función:** Carga declaraciones del directorio y detecta contradicciones. No calcula.
- **Archivos:**
  - `VPSI.py`: 89 declaraciones (ejes ontológico, informacional, epistemológico, de la verdad).
  - `correlacion.py`: 36 declaraciones (Teorema de Inferencia Causal Estructural).
  - `self.py`: 22 declaraciones (Teorema del Yo Funcional).
  - Total: 147 declaraciones.
- **Por tipo:**
  - 54 axiomas.
  - 42 teoremas.
  - 34 corolarios.
  - 11 lemas.
  - 6 definiciones.
- **Vigila:**
  - `contradiccion_directa`.
  - `contradiccion_de_cota`.
- **Regla:** Un choque impide el arranque del `Engine` (`ArranqueError`).
- **Esquema obligatorio de cada declaración:**
  `id`, `tipo`, `sujeto`, `relacion`, `objeto`, `polaridad`.
  - Una declaración sin estos campos hace que el archivo entero sea rechazado.

> Nota: `correlacion.py` contiene **causalidad**, no correlación. El nombre no refleja su contenido.

---

### 5.3. `modules/constante/` — El Ancla
**Estado:** MONTADO

- **Constantes:**
  ```python
  ALPHA = Fraction(26, 27)  # Techo estructural
  BETA  = Fraction(1, 27)   # Piso ontológico irreducible
  ALPHA + BETA = 1          # Exacto
  ```
- **Derivadas de la topología del cubo 3×3×3**.
- **Expone:**
  - `CUBE_TOTAL`, `CUBE_EXTERIOR`, `CUBE_CENTER`, `LAYER_FACES`, `LAYER_EDGES`, `LAYER_VERTICES`, `SURFACE`.
  - `theta()`, `partition()`, `anatomy()`, `topology()`.
- **Aritmética exacta:** `Fraction` en todo el módulo, nunca `float`.

---

### 5.4. `modules/formulas/` — La Ecuación
**Estado:** MONTADO

- **Fórmulas canónicas:**
  ```python
  tru_ri(C, L, K)      -> C · L · K
  tru_total(C, L, K)   -> (C · L · K · ALPHA) + BETA
  ```
- **Características:**
  - Fija, sin estado.
  - Se verifica con aritmética exacta de una vez y para siempre.
  - Toda la incertidumbre del sistema queda concentrada en el calculador (`CA`).

---

### 5.5. `modules/realidad/` — Canal de Evidencia
**Estado:** ROL NO ADMITIDO

- **Función:** Contacto directo con lo externo (internet, RAE, sintaxis, morfología).
  - Mapeo `R → X` (Axioma F3).
- **Es un `R_i`, no `R`:**
  - No tiene veto.
  - Entra al cálculo como un factor más, sujeto a la misma fórmula que todo lo demás.
  - Si la evidencia y la lógica del auditor son más precisas que lo que dice una fuente, la contradicen (el sistema no se ofende, solo lanza un número).
- **Archivos:**
  - `__init__.py`: Filtro (los archivos no se contradicen entre sí).
  - `acceso.py`: Capacidad de conexión (socket, SSL, urllib, requests).
- **Diferenciación de errores:**
  - `socket.gaierror` (DNS).
  - Ruta TCP.
  - Timeout de conexión vs. de lectura.
  - TLS.
  - Fallo de canal vs. respuesta con código de error (ej: 404).
- **Regla de oro:**
  - Refrescar y evaluar son operaciones distintas y no ocurren en la misma pasada.
  - La pasada lee de una instantánea sellada, nunca del cable.
    - Razón: Si se lee del cable, la misma entrada podría admitir dos salidas y `L` decaería.

---

### 5.6. `modules/correlacion_mecanica/` — Secuencia y Acoplamiento
**Estado:** ROL NO ADMITIDO

- **Función:**
  - Lee los archivos de la carpeta en su orden nativo.
  - Calcula la mecánica resultante de lo que ellos mismos dicen.
  - Comprueba que no se contradigan.
- **No exige, no dispone, no ordena, no completa, no elige.**
  - Si dos archivos colisionan sobre un mismo nodo, no pasa nadie y se reportan los identificadores en desacuerdo.
- **Detecta:**
  - Orden opuesto sobre el mismo par de nodos.
  - Secuencia que se muerde la cola.
  - Carpeta vacía.
- **Declara:**
  - `CORR_SEQ_01` (secuencia transversal).
  - `CORR_SEQ_02` (no contradicción cruzada).

---
### 5.7. `modules/verificacion/` — Auto-Auditoría
**Estado:** ROL NO ADMITIDO

- **Función:** Contraste axiomático transversal sobre el código fuente.
- **Declara `VX-1`:**
  > Ningún segmento de código o lógica implementada puede violar las restricciones formales declaradas en los axiomas del sistema.
- **Cierra el ciclo:** El código que aplica los axiomas queda sujeto a ellos.

---
### 5.8. `modules/calculador/` — Produce C, L, K
**Estado:** PENDIENTE

- **Función:** Único módulo que produce números.
  - No decide qué contar: Solo divide.
  - Lo que va en el numerador y denominador lo decide `CONTEXTO`.
- **Fórmulas:**
  ```python
  C = 1 - k/m          # Coherencia interna
  L = 1 - r/p          # Invariancia lógica
  K = 1 - f/c          # Correlación con el contexto
  A(D,X) = 1 - u/n      # Puntuación de anclaje
  ```
- **Los 8 conteos y quién los define:**

| Símbolo | Qué se cuenta | Quién lo define |
|---|---|---|
| `m` | Compromisos estructurales del mensaje | CONTEXTO |
| `k` | Pares mutuamente contradictorios | CONTEXTO + AXIOMAS |
| `p` | Posturas asumidas sobre puntos fijados | CONTEXTO + CACHE |
| `r` | Posturas que revierten una consolidada | CONTEXTO + CACHE |
| `c` | Aserciones de correspondencia verificable | CONTEXTO |
| `f` | Las que divergen bajo `Octx` | CONTEXTO + REALIDAD |
| `n` | Afirmaciones estructurales | CONTEXTO |
| `u` | Las sin soporte causal en `X` | REALIDAD |

- **Debe entregar trazabilidad:**
  - Si devuelve únicamente `{C, L, K}`, nadie puede reconstruir de dónde salió el número.
  - Solución: Devolver además los conteos `(k,m)`, `(r,p)`, `(f,c)` usados.
    - El centinela puede recalcular la división y comprobar que el factor se deriva de sus conteos.
    - No es autoauditoría: Es un tercero verificando contra la evidencia.

---
### 5.9. `modules/contexto/` — Lógica del Contexto
**Estado:** PENDIENTE

- **Función:** El armazón.
  - Define qué cuenta como:
    - Compromiso.
    - Postura.
    - Aserción verificable.
    - Alcance que gobierna cada caso `z`.
- **Aplica a toda escala** con las mismas reglas:
  - Palabra, frase, conversación completa.
- **El dominio se reconstruye** desde las palabras mismas vía diccionario:
  - La acepción trae su campo semántico.
- **Construcción continua:**
  - "Yo como amarillo" está indefinido hasta que la conversación aporta el objeto.
- **Consecuencia crítica:**
  - El anclaje se evalúa contra el estado del contexto en el turno en que se emitió, no contra el estado final.
  - Reevaluar al final cambiaría `K` retroactivamente y violaría el Lema 1.17.
- **Si CONTEXTO no está como debe, todo se detiene** (aunque la taxonomía, la constante y el resto sean impecables).

---
### 5.10. `modules/taxonomia/` — Tácticas T1–T15
**Estado:** PENDIENTE

- **Función:** Describe, no puntúa.
  - Las 15 tácticas T1–T15.

| Táctica | Descripción |
|---|---|
| T1 | Concession-pivot |
| T2 | False Deference |
| T3 | False Choice |
| T4 | Pseudo-rigor |
| T5 | Object Invention |
| T6 | Seeded Doubt |
| T7 | Usurped Verdict |
| T8 | Methodological Drift |
| T9 | Authority Label |
| T10 | Equivocation |
| T11 | Moving the Goalposts |
| T12 | Hedging |
| T13 | Category Mistake |
| T14 | Ad Hoc Hypothesis |
| T15 | Bucle de inversión de objetos |

- **No es un adorno descriptivo:**
  - Cierra la puerta que el cálculo deja abierta.
  - El factor mide correspondencia; la táctica mide la maniobra.
- **Decisión abierta:**
  - ¿TX corre antes o después de CA?
    - Si la táctica atrapa lo que el cálculo deja pasar, necesita ver el resultado del cálculo (no solo el texto).
    - Va después de CA.

---
### 5.11. `modules/cache/` — Registro Forense
**Estado:** PENDIENTE

- **Pertenece al centinela**, no a la salida.
- **Guarda:**
  - El informe completo y detallado (no un resumen):
    - Cómo se calculó cada celda, con procedencia por conteo.
  - La instantánea del ancla contra la que se midió, con su fecha.
  - Los rechazos, marcados aparte:
    - Qué filtro detuvo.
    - En qué módulo.
    - Qué contrato se rompió.
    - La huella de la petición.
- **Política de capacidad:**
  - Separar el detalle forense (voluminoso, podable) del estado consolidado de sesión (compacto, no podable).
  - Truncar en silencio el estado consolidado convertiría un olvido en `L = 1` (falso positivo grave).

---
### 5.12. `core/centinela.py` — Filtro de Orquestación
**Estado:** PENDIENTE

- **Función:** Verifica la orquestación completa después de que el Engine termina.
  - Solo cuando el centinela aprueba, hay salida.
- **Cara de entrada** (parcialmente escrita):
  - Orden de arranque.
  - Rol declarado vs. rol ejercido.
  - Roles ausentes antes del despacho.
  - Frontera de tipos.
  - Autoridad de despacho.
  - Invariancia L (misma petición, mismo resultado).
- **Cara de salida** (no escrita):
  - Certificar que el resultado se deriva de sus premisas.
  - No basta con validar rangos: Hay que recalcular la derivación.
    ```python
    esperado = (C * L * K * ALPHA) + BETA
    if tru_total != esperado:
        raise FormulaError("Tru_total no se deriva de sus factores")
    ```
  - Un `Tru_total` dentro de cota pero desacoplado de sus factores pasaría cualquier chequeo de rango.

---
### 5.13. `core/diagnostico.py` — Tabla de Códigos
**Estado:** HUÉRFANO

- **Problema:** Nadie lo importa (ni el Engine ni el CI).
- **Defectos:**
  - Define `ALPHA` local en vez de leerlo de `modules.constante`.
  - La tabla de códigos vive duplicada aquí y en `engine.py`, y las dos versiones ya divergieron.

---
---
## 6. Fórmulas Canónicas

### Tru_Ri(D): Contribución del Observador
```
Tru_Ri(D) = C(D) · L(D) · K(D)
```
- **Rango:** [0, 1].
- **Interpretación:**
  - Tru_Ri = 0: Si C = 0, L = 0, o K = 0 (fallo en coherencia, lógica o correlación).
  - Tru_Ri = 1: Si C = L = K = 1 (sincronización perfecta del observador con la realidad).
- **Base teórica:**
  - Axioma TA5 (Multiplicatividad de la Verdad):
    > Un factor nulo anula todo Tru(D). No es posible compensación.

---

### Tru_total(D): Verdad Total
```
Tru_total(D) = (Tru_Ri(D) · α) + β
```
- **Rango:** [β, 1], donde β = 1/27.
- **Interpretación:**
  - Tru_total = β: Si Tru_Ri = 0 (el observador falla, pero R persiste).
  - Tru_total = 1: Si Tru_Ri = 1 (sincronización perfecta: C = L = K = 1).
- **Base teórica:**
  - Definición 2.14 (Verdad: Forma Canónica):
    > Tru_total(D) = C(D) · L(D) · K(D) · α + β.
  - Teorema 17 (Imposibilidad de Colapso Total):
    > Tru_total(D) = 0 es formalmente imposible. El mínimo es β = 1/27.

---
---
## 7. Axiomas del Documento no Cargados

| Falta | Sección | Impacto |
|---|---|---|
| Regla Operacional `C=1−k/m`, `L=1−r/p`, `K=1−f/c` | §0.15 | Bloquea CA: Nada obliga a que el calculador use esas fórmulas. |
| Conteos fraccionarios (`k≈0.6` = severidad 0.6) | §0.15 | Alto |
| Convención de redondeo (2 y 4 decimales) | §0.15 | Alto |
| `p = 0 ⟹ L = 1` por vacuidad | §0.15 | Medio |
| Regla de Oro Operativa — rol instrumental puro | §0.4 | Medio |
| Firma de desviación dirigida (g, d, r, a) | §4.4 | Medio |
| Cruces `N2 = Q ∧ D`, `N3 = ¬Q` | §4.4 | Medio |
| Observación 1.41 — dos techos declarados | §1.11 | Medio |
| Definiciones de la §2.1 (6 items) | §2.1 | Bajo |


---
---
## 8. Problemas Abiertos

| Problema | Descripción | Impacto | Solución Propuesta |
|---|---|---|---|
| `evaluar()` no corre | `TypeError: '>' not supported between '_Undefined' and 'Fraction'` en `core/engine.py:684`. | Bloquea el camino de evaluación. | Manejar `_Undefined` en el motor o montar `CA`. |
| Tres techos en circulación | T16 (corpus): `Tru_Ri ≤ α = 26/27`. Observación 1.41: `Tru_total ≤ α² + β = 703/729`. Código actual: `Tru_total ≤ 1`. | Inconsistencia en el techo estructural. | Elegir una convención y declararla como axioma. |
| Roles no admitidos | `realidad`, `verificacion`, `correlacion_mecanica` son rechazados por el Registro. | Módulos fuera del sistema. | Añadir roles a la tupla `ROLES` en `core/engine.py`. |
| Tests con vacuidad | `modules.axiomas.axiomas()` devuelve lista vacía. Los tests pasan por vacuidad. | Falsos positivos en tests. | Leer declaraciones del barrido (`AX.barrer()`). |
| Error en `ci.yml` | El paso "Auditar librería de axiomas" está mal indentado. | Fallos en el pipeline de CI. | Corregir indentación en el archivo YAML. |

---
---
## 9. Prioridad de Construcción

| Prioridad | Módulo/Acción | Descripción | Impacto |
|---|---|---|---|
| 1 | Declarar §0.15 como axiomas | Añadir reglas operacionales (`C=1−k/m`, etc.) a `modules/axiomas/`. | Desbloquea CA. |
| 2 | Añadir roles a la tupla `ROLES` | Incluir `RE`, `VX`, `MC` en `core/engine.py`. | Integra módulos pendientes. |
| 3 | `modules/contexto/` | Define los conteos (`k`, `m`, `r`, `p`, etc.). | Sin contexto, no hay C, L, K. |
| 4 | `core/centinela.py` | Verifica la orquestación completa. | Convierte el `TypeError` en estado. |
| 5 | `modules/calculador/` | Produce C, L, K con trazabilidad. | Cierra el camino de evaluación. |
| 6 | `modules/cache/` | Registro forense de ambas ramas. | Evita sesgo de supervivencia. |
| 7 | `modules/taxonomia/` | Tácticas T1–T15. | Cierra la puerta del cálculo. |
| 8 | Resolver el techo | Elegir una convención para `Tru_total`. | Consistencia teórica. |

---
---
## 10. Convenciones

1. **Aritmética exacta:**
   - `Fraction` siempre.
   - `float` prohibido y rechazado en frontera.
   - `Fraction(str(0.1))` finge precisión en vez de recuperarla.

2. **Descubrimiento por directorio:**
   - Cada contenedor expone:
     - `CONTENEDOR` (metadatos).
     - `inventario()` (estado interno).
     - `axiomas()` (declaraciones propias, opcional).
   - Añadir un archivo correcto a una carpeta lo incorpora solo.
   - Ninguna lista central que mantener.

3. **Los filtros informan, no lanzan:**
   - `barrer()` devuelve un informe.
   - Solo el arranque del Engine aborta ante contradicción.

4. **Coherente por vacuidad no es coherente:**
   - Un archivo vacío es trivialmente consistente con todo.
   - Todo filtro lleva piso de carga.

5. **Nada se sustituye en silencio:**
   - Una fuente indisponible se reporta.
   - No se reemplaza por otra.

---
---
## 11. CI/CD

**Pipeline en `.github/workflows/ci.yml`:**
1. Invariante α + β = 1.
2. Barrido axiomático — 0 choques.
3. Prohibición de componentes estocásticos.
4. `float` prohibido en factores.
5. `pytest --junit-xml`.
6. Omega Report.
7. Coherence Guard.
8. Omega Diary.
9. Upload artifacts.
10. Commit coherence history.
11. Auditar librería de axiomas.

**Problema actual:**
- El paso "Auditar librería de axiomas" está mal indentado (dentro del bloque `run:` de otro paso).
- Solución: Desindentar para que sea un paso independiente.

**Nota sobre `jitter`:**
- El backoff exponencial estándar usa aleatoriedad para evitar el efecto manada.
- No es contradicción: El azar vive en la capa de red, fuera de la pasada.
- La compuerta 3 (Prohibición de componentes estocásticos) debe distinguir entre:
  - Capa de pasada (determinista).
  - Capa de red (puede usar aleatoriedad).

---
---
## 12. Tests

**Archivo:** `tests/test_vpsi.py` (suite única, seis secciones).

| Sección | Qué cubre |
|---|---|
| 1. ANCLA | α y β reconstruidos desde la geometría del cubo. |
| 2. FÓRMULAS | La ecuación con puntos exactos, piso, techo, sin compensación. |
| 3. AXIOMAS | Barrido coherente y piso de carga. |
| 4. ENGINE | Arranque, descubrimiento, frontera de tipos, autoridad. |
| 5. REALIDAD | Acceso e `__init__` (se salta si no está montado). |
| 6. CONSTRUCCIÓN | Lo que falta debe ser visible, no silencioso. |

**Principios:**
- Ningún test toca la red ni depende del reloj.
- El test de `evaluar()` no exige que funcione:
  - Acepta que aborte o devuelva `UNDEFINED`.
  - Solo falla si devuelve un número sin haber calculado nada.

---
---
## 13. Diagrama de Flujo

```mermaid
graph TD
    %% Secuencia del Método
    A[Iniciar] --> B[Declarar Octx]
    B --> C[Fijar Premisas]
    C --> D[Registrar Emisión]
    D --> E[Clasificar con Taxonomía]
    E --> F[Reconstruir y Contrastar]

    %% Secuencia del Engranaje
    G[AX: Barrido Axiomático] --> H[CX: Contexto]
    H --> I[RE: Realidad]
    I --> J[CA: Calculador]
    J --> K[FO: Fórmulas]
    K --> L[TX: Taxonomía]
    L --> M[CENTINELA: Verificación]
    M --> N[CACHE: Registro Forense]

    %% Conexiones
    A --> G
    N -->|Estado Inicial| D
    F --> N

    %% Leyendas
    subgraph Leyenda
        direction TB
        O[Módulos Montados]
        P[Módulos Pendientes]
        Q[Módulos No Admitidos]
    end

    classDef montado fill:#90EE90,stroke:#333;
    classDef pendiente fill:#FFD700,stroke:#333;
    classDef no_admitido fill:#FF6347,stroke:#333;

    class G,H,I,K,O;
    class J,L,M,N,P;
    class Q;
```

---
---
## Resumen Ejecutivo

### Estado Actual
- 6 módulos montados (Engine, Axiomas, Constante, Fórmulas, Omega Report, Tests).
- 5 módulos pendientes (Calculador, Contexto, Taxonomía, Cache, Centinela).
- 3 módulos no admitidos (Realidad, Verificación, Correlación Mecánica).
- 2 problemas críticos:
  1. `evaluar()` no corre por falta de `CA`.
  2. Inconsistencia en el techo estructural (`Tru_total`).

### Objetivo Inmediato
1. Montar `CA` (Calculador) para desbloquear el camino de evaluación.
2. Corregir el manejo de `_Undefined` en el motor.
3. Declarar el techo estructural como axioma.

### Objetivo a Mediano Plazo
- Completar los módulos pendientes (CX, TX, CACHE, CENTINELA).
- Integrar los módulos no admitidos (RE, VX, MC).
- Resolver los problemas abiertos (tests con vacuidad, `ci.yml`).

### Objetivo Final
- Sistema completamente funcional con:
  - 8 compuertas en estado OK en el OMEGA REPORT.
  - Todos los tests pasando.
  - CI/CD estable.

---
---
## Referencias
- Villasmil, I. (2026). Metodología Estructural de la Verdad — Taxonomía de Desviaciones Funcionales e Inevitabilidad del Yo Funcional.
- Villasmil, I. (2026). The Seven-Layer Theorem.
- Villasmil, I. (2026). VPSI — Principle of Structural Invariance, v9.4.
```

---
