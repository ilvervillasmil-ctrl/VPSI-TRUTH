# Especificación de código — VPSI-TRUTH

## El principio

Un archivo debe poder recibir código **al final, literalmente al final**, sin
tocar una sola línea de lo anterior.

Tres días después, un mes después: se va al fondo, se pega, y funciona.

Todo lo demás en esta especificación existe para sostener eso.

---

## La regla que lo hace posible

**Nada de lo que está arriba nombra lo que está abajo.**

Si una línea del archivo contiene una lista con los nombres de lo que hay en
él, anexar obliga a volver arriba a editar esa lista. Y entonces ya no se pega
al final: se edita en dos sitios.

Eso descalifica tres cosas que parecen inofensivas:

| Patrón | Por qué rompe el anexo |
|---|---|
| `__all__ = ["a", "b", "c"]` | Lo nuevo no se exporta hasta editar la lista |
| `ARCHIVOS = ["x.py", "y.py"]` | Un archivo nuevo no entra hasta editar la lista |
| `TABLA = {"a": fn_a, "b": fn_b}` | Una entrada nueva no despacha hasta editar la tabla |

En los tres casos la sustitución es la misma: **que la colección se llene
sola.** Por descubrimiento, por decorador, o por la convención del guión bajo.

---

## Los tres mecanismos de auto-llenado

### 1. Sin `__all__`

Python ya exporta todo lo que no empiece por `_`. Un `__all__` escrito a mano
es exactamente la lista que la regla prohíbe.

```python
def _ayudante():        # privado, no se exporta
    ...

def funcion_publica():  # se exporta sola
    ...
```

Una función pública pegada al final queda exportada sin tocar nada.

### 2. Descubrimiento en vez de lista

El `__init__.py` de `axiomas` no nombra sus archivos: recorre el directorio.
Por eso `correlacion.py` entró sin editar una línea.

```python
for f in sorted(_DIR.glob("*.py")):
    if f.name.startswith("_"):
        continue
    ...
```

Aplica igual a roles, a fuentes, a formatos. Si el reporte hubiera leído los
roles de `core.engine.ROLES` desde el principio en vez de tener su propia lista,
no habría impreso roles que no existen.

### 3. Decorador de registro

Para lo que vive dentro del mismo archivo. La colección se declara vacía
arriba; el decorador la llena al pasar por cada definición.

```python
_REGLAS = []

def regla(fn):
    _REGLAS.append(fn)
    return fn
```

Una regla pegada al final se registra sola, porque Python ejecuta el archivo de
arriba abajo y el decorador corre en el momento de la definición.

---

## Orden de los segmentos

De lo más estable a lo más volátil. Lo que cambia poco arriba, lo que crece
abajo.

```
1  IDENTIDAD          CONTENEDOR
2  ERRORES            excepciones propias
3  CONSTANTES         estados, contratos, pisos
4  ESTADO             colecciones vacías que se llenan solas
5  GANCHOS DE ANEXO   los decoradores
6  LECTURA            helpers privados
7  API                barrer, inventario, axiomas
8  REGLAS             las comprobaciones
9  DECLARACIONES      los axiomas del contenedor
   ZONA DE ANEXO      aquí se pega
```

Los segmentos 8 y 9 van **después** de la API, aunque parezca al revés. La
razón es el principio: la API recorre las colecciones del segmento 4, así que
no necesita ver las reglas. Y si las reglas van al final, lo nuevo se pega
junto a lo que ya es del mismo tipo.

Cada segmento con su banda:

```python
# ===============================================================
# SEGMENTO 8 --- REGLAS
# ===============================================================
```

El número no es decoración: dice dónde pegar. Algo del mismo tipo va dentro de
su segmento; algo de un tipo nuevo abre un segmento propio en la zona de anexo.

---

## Cómo se anexa

**Una comprobación nueva:**

```python
@regla
def _que_no_haya_dos_iguales():
    faltas = []
    ...
    return faltas
```

Devuelve la lista de faltas que encuentre; lista vacía si todo está bien.
`barrer()` la recoge sola.

**Una declaración nueva:**

```python
declarar({
    "id": "XX-2",
    "tipo": "axioma",
    "sujeto": "...",
    "relacion": "...",
    "objeto": "...",
    "polaridad": True,
    "cota": None,
    "depende_de": [],
    "gobierna": ["<nombre>"],
    "enunciado": "...",
})
```

Entra en `axiomas()` y en el barrido general sin tocar nada.

**Una función pública nueva:** se escribe sin prefijo y queda exportada.

---

## Contrato con el Engine

Toda carpeta bajo `modules/` expone:

| | Obligatorio | Qué es |
|---|---|---|
| `CONTENEDOR` | sí | `nombre`, `rol`, `version`, `requiere`, `descripcion` |
| `inventario()` | sí | describe el contenedor; **no toca red ni disco de más** |
| `barrer()` | si es filtro | informa, no lanza |
| `axiomas()` | si declara | declaraciones propias para el barrido general |

`descripcion` es lo que el reporte imprime en la tabla de roles. Sin ese campo,
sale `(el módulo no se describe)`.

---

## Reglas de higiene

**Los filtros informan, no lanzan.** `barrer()` devuelve
`{estado, coherente, faltas}`. Sólo el arranque del Engine aborta ante
contradicción.

**Coherente por vacuidad no es coherente.** Todo filtro lleva piso: si no cargó
nada, no hay nada que contradecir y el informe saldría verde sin haber
comprobado nada.

**Aritmética exacta.** `Fraction` siempre. `float` rechazado en frontera, no
convertido: `Fraction(str(0.1))` finge la precisión en vez de recuperarla.

**Nada se sustituye en silencio.** Una pieza indisponible se reporta.

**No reimplementar lo que ya existe.** Si otro módulo tiene el cargador, se
llama; no se copia. Una copia deriva, y entonces el archivo reporta números que
no están en el código.

---

## Lo que no va al final

Una sola cosa: `if __name__ == "__main__":`. Si un módulo necesita ejecutarse
suelto, ese bloque va en un script aparte, no en el `__init__.py`. Un bloque de
arranque al fondo convierte la zona de anexo en zona de "después del arranque",
y ahí lo pegado ya no se registra antes de que corra.

---

## Verificación

Que un archivo cumpla esta especificación se comprueba en un minuto:

1. `grep "__all__"` → no debe aparecer
2. Buscar listas de nombres de archivos, roles o funciones → no debe haber
3. Pegar una regla vacía al final e importar → debe aparecer en
   `barrer()["reglas"]` sin tocar nada más

Si el paso 3 obliga a subir a editar algo, el archivo no cumple.
"""
VPSI-TRUTH  ---  modules/<nombre>/__init__.py

<Que hace este contenedor. Una frase.>
<Que NO hace. Una frase.>

======================================================================
FORMATO DE ANEXO

Este archivo se lee de arriba abajo y nada de lo de arriba nombra lo
de abajo. Por eso se le puede pegar codigo al final, literalmente al
final, sin tocar una sola linea de lo anterior.

Para anexar: ir al fondo del archivo y pegar. Nada mas.
======================================================================
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================

CONTENEDOR = {
    "nombre": "<nombre>",
    "rol": "<XX>",
    "version": "1.0",
    "requiere": [],
    "descripcion": "<que hace, en una linea>",
}

# ===============================================================
# SEGMENTO 2 --- ERRORES
# ===============================================================

class FiltroRoto(Exception):
    """Algo declarado no cumple lo que declara."""
    def __init__(self, quien: str, exigido: str, recibido: str):
        self.quien = quien
        super().__init__(f"[{quien}] se exige {exigido}; se recibio {recibido}")

# ===============================================================
# SEGMENTO 3 --- CONSTANTES Y CONTRATOS
# ===============================================================

APROBADO = "APROBADO"
RECHAZADO = "RECHAZADO"

PISO = 1   # un contenedor vacio es coherente con todo: no vale

# ===============================================================
# SEGMENTO 4 --- ESTADO
# ===============================================================
#
# Las colecciones se declaran vacias aqui y se llenan solas. Nunca se
# escribe a mano lo que contienen: si hubiera una lista con nombres,
# anexar obligaria a volver arriba a editarla.

DECLARACIONES: List[Dict[str, Any]] = []
_REGLAS: List[Callable[[], List[str]]] = []

# ===============================================================
# SEGMENTO 5 --- GANCHOS DE ANEXO
# ===============================================================
#
# Estos dos decoradores son lo que hace posible pegar al final.
# Una regla o una declaracion escritas abajo se registran solas al
# importarse el modulo, porque Python ejecuta el archivo de arriba
# abajo y el decorador corre en el momento de la definicion.

def regla(fn: Callable[[], List[str]]) -> Callable[[], List[str]]:
    """Registra una comprobacion. Devuelve la lista de faltas que halle."""
    _REGLAS.append(fn)
    return fn


def declarar(d: Dict[str, Any]) -> Dict[str, Any]:
    """Registra una declaracion axiomatica del contenedor."""
    DECLARACIONES.append(d)
    return d

# ===============================================================
# SEGMENTO 6 --- LECTURA
# ===============================================================
#
# Privado: prefijo de guion bajo. No se exporta y no forma parte del
# contrato del contenedor.

def _leer() -> Dict[str, Any]:
    """Descubre lo que hay. Nunca una lista escrita a mano."""
    hallado: Dict[str, Any] = {}
    # ... descubrimiento por directorio, por atributo, etc.
    return hallado

# ===============================================================
# SEGMENTO 7 --- API DEL CONTENEDOR
# ===============================================================
#
# Estas tres funciones son el contrato con el Engine. Recorren las
# colecciones del Segmento 4, asi que todo lo anexado abajo entra
# solo, sin tocar nada de aqui.

def barrer() -> Dict[str, Any]:
    """Filtro de paso al Engine. No lanza: informa."""
    faltas: List[str] = []
    for r in _REGLAS:
        try:
            faltas.extend(r() or [])
        except Exception as e:
            faltas.append(f"regla '{r.__name__}': {type(e).__name__}: {e}")

    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": APROBADO if not faltas else RECHAZADO,
        "coherente": not faltas,
        "faltas": faltas,
        "reglas": [r.__name__ for r in _REGLAS],
    }


def inventario() -> Dict[str, Any]:
    """Describe el contenedor. No abre red ni toca disco de mas."""
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "reglas": len(_REGLAS),
        "declaraciones": len(DECLARACIONES),
    }


def axiomas() -> List[Dict[str, Any]]:
    """Declaraciones propias del contenedor, para el barrido general."""
    return DECLARACIONES

# ===============================================================
# SEGMENTO 8 --- REGLAS
# ===============================================================

@regla
def _hay_contenido() -> List[str]:
    if len(_leer()) < PISO:
        return ["nada declarado: coherente por vacuidad, no por coherencia"]
    return []

# ===============================================================
# SEGMENTO 9 --- DECLARACIONES
# ===============================================================

declarar({
    "id": "<XX>-1",
    "tipo": "axioma",
    "sujeto": "<sujeto>",
    "relacion": "<relacion>",
    "objeto": "<objeto>",
    "polaridad": True,
    "cota": None,
    "depende_de": [],
    "gobierna": ["<nombre>"],
    "enunciado": "<enunciado>",
})

# ===============================================================
# ZONA DE ANEXO
# ===============================================================
#
# A partir de aqui se pega. Reglas nuevas con @regla, declaraciones
# nuevas con declarar(), funciones publicas sin prefijo de guion bajo.
#
# NO hay __all__ al final. Un __all__ escrito a mano es una lista que
# nombra lo de arriba, y anexar obligaria a volver a editarla. Python
# ya exporta todo lo que no empiece por guion bajo.
