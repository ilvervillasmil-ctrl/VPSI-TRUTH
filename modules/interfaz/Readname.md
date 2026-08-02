Documento listo para colocar en la carpeta de interfaz:
modules/interfaz/README.md (o docs/interfaz.md si aún no existe el módulo).

# interfaz (UI)

Módulo de **composición de interfaz**.  
No calcula verdad. No clasifica O. No aprueba material de realidad.  
Conoce el mecanismo solo para **presentar** y **recoger** lo que el usuario y el Engine ya definen por contrato.

Cuando se implemente este módulo, este documento es la lógica a seguir.

---

## Qué es (y qué no es)

| Es | No es |
|----|--------|
| Capa de entrada/salida para humanos | Autoridad sobre C, L, K o Tru |
| Composición de pantallas, casillas, reportes visibles | Sustituto de CX, CA, FO, RE o Engine |
| Comodidad: idiomas, layout, empaquetado visual | Filtro axiomático ni centinela de grafo |
| Observador de contratos y de artefactos (Omega, cache) | Quien decide si un material de Internet “es R” |

Principio: **la UI no tiene agencia sobre el cálculo**.  
Pide, muestra, traduce mensajes del programa; el núcleo evalúa bajo contratos.

---

## Separación de capas

```text
Usuario (cualquier idioma)
        │
        ▼
┌───────────────────────────┐
│  interfaz (UI)            │  ← comodidad, i18n, layout
│  - casillas de entrada    │
│  - mensajes del programa  │
│  - vistas de reporte      │
└─────────────┬─────────────┘
              │  petición estructurada (texto, modo, O si el usuario lo dio)
              ▼
┌───────────────────────────┐
│  Engine + módulos        │  ← ruta determinista
│  CX → CA → FO · AX · RE…  │
└─────────────┬─────────────┘
              │  resultado estructural + evidencia
              ▼
┌───────────────────────────┐
│  interfaz (UI)            │  ← solo presenta
│  - Tru, notas, errores    │
│  - enlaces a diagnostics  │
└───────────────────────────┘
La UI entrega lo que el usuario escribió y el modo/contexto que la casilla permita. La UI no inventa O técnico si el usuario no lo dio: eso lo arma CX a partir de entrada natural (ver módulo contexto).

Idiomas (comodidad del usuario)
Objetivo
El usuario puede escribir en árabe, chino, español, etc. Los textos del programa (botones, etiquetas, ayuda) pueden mostrarse en su lengua.
Qué implica
Pieza
Dónde
Notas
Entrada de texto en cualquier script
UI
Aceptar Unicode; no filtrar por idioma
Mensajes de la UI (i18n)
UI
Catálogo de cadenas del programa, no del contenido evaluado
Traducción automática del contenido del usuario
Opcional, fuera del núcleo
Solo ayuda de presentación; nunca input oculto de Tru
Norma léxica / diccionario
RE (lexico, futuro idiomas de referencia)
Contraste etiquetado; no es el traductor de la UI
Regla dura
	•	Traducir para que el humano lea mejor → UI / extra opcional.
	•	Traducir para que el motor “entienda” y calcule K → prohibido en la ruta de decisión.
	•	El núcleo recibe el texto tal cual (o la forma que CX normalice) + O.
	•	Un paquete de traducción, si existe, vive en dependencias de UI (requirements-ui.txt), no en el requirements.txt del motor.
Empaquetado previsto
requirements.txt        → núcleo (stdlib + pytest; requests opcional en acceso)
requirements-ui.txt     → extras de interfaz (i18n, posible cliente de traducción, toolkit UI)
Quien instale solo el motor no arrastra traductores. Quien monte la interfaz completa puede instalar el extra.

Qué debe conocer la UI del mecanismo
La UI conoce por observación / contratos, no por reimplementar:
	1	Casilla de contexto — texto libre, lista de criterios, conversación (entrada natural de CX).
	2	Casilla de descripción / material — lo que se evalúa.
	3	Modo de entrada — si el usuario lo elige (auditoría, conversación, …); si no, CX puede inferir.
	4	Salida de Engine — estado, factores, Tru, errores, notas; sin reescribir la fórmula.
	5	Artefactos — enlaces o vistas a diagnostics/ (Omega, evaluaciones.json, etc.).
	6	Centinela / rechazo — si el sistema no aprueba, la UI muestra el rechazo; no lo suaviza.
No calcula Tru_total. No llama a CA/FO por su cuenta saltándose Engine. No declara “esto es verdadero” en nombre del marco.

Contrato del módulo (cuando exista `__init__.py`)
Alineado al resto del repo:
CONTENEDOR:
  nombre: interfaz
  rol: UI
  requiere: [] o los que el diseño fije sin crear agencia de cálculo
  capacidades típicas:
    - componer      → armar vistas / layouts según petición de diseño
    - presentar     → mostrar resultado de Engine / reportes
    - inventario    → qué piezas de UI hay
    - barrer        → coherencia interna de archivos de interfaz (no Tru)
El Engine solo invoca lo declarado. La UI no gana poder de cálculo por tener muchos idiomas.

Entrada típica que la UI debe poder armar
Sin exigir jerga técnica al usuario:
Casilla contexto (ejemplo):
  1. evaluar si es razonable
  2. si Carlos dijo la verdad
  3. leyes sobre su actitud

Casilla contenido:
  [texto del usuario en su idioma]

Opcional:
  idioma_ui = "ar" | "es" | "en" | …
  modo_entrada = si el usuario lo elige
CX convierte eso en registro O cuando corresponda. Engine evalúa. UI pinta el resultado en el idioma de la interfaz.

Idioma de la UI vs idioma del contenido
Concepto
Significado
idioma_ui
Lengua de menús, botones, mensajes de error del programa
Contenido del usuario
Puede ser otra lengua; se evalúa como D bajo O, no se “corrige” por traducción oculta
RE / lexico
Fuentes de norma; no sustituyen i18n de la UI
Si en el futuro se muestra una traducción del contenido al lado del original, debe etiquetarse como ayuda de lectura, no como texto que reemplazó a D en el cálculo.

Diseño y empaquetado (recordatorio)
	•	La UI puede empaquetarse para web, escritorio o móvil; el núcleo es el mismo.
	•	Actualización de toolkits de diseño = capacidad del contrato de UI, no cambio de la fórmula.
	•	Centinela de la carpeta interfaz/: coherencia de sus archivos de composición; no juicio de Tru.
	•	Engine puede conocer el contrato UI; Centinela del sistema puede verificar integridad de salida según reglas ya definidas en el núcleo.

Orden de implementación (cuando toque)
	1	Contrato CONTENEDOR + inventario / barrer mínimo.
	2	Casillas de entrada alineadas a CX (contexto + contenido).
	3	Presentación de salida de Engine (sin humo: solo lo que venga en el resultado).
	4	i18n de cadenas del programa (catálogo de lenguas de UI).
	5	Extras opcionales: traducción de ayuda, temas, empaquetado multiplataforma.
	6	Nunca: meter motor estocástico en la ruta que alimenta C, L, K, Tru.

Principio en una frase
La interfaz habla el idioma del usuario; el motor habla el idioma de los contratos. La comodidad no sustituye a O, ni a Fraction, ni a la aprobación de dominio.
Este archivo permanece en la carpeta de interfaz para no reconstruir la lógica de memoria cuando se implemente el módulo.
---

Con esto, cuando llegues a interfaz, el MD ya fija: idiomas = UI, no Tru; dependencias opcionales; qué casillas; qué no puede hacer el módulo.
