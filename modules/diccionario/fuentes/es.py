"""
modules/diccionario/fuentes/es.py
=================================

Diccionario español — registro léxico (paquete wn / omw-es).

-------------------------------------------------------------------------------
POR QUÉ ESTÁ HECHO ASÍ
-------------------------------------------------------------------------------
Una palabra sola no es la verdad. Detrás de cada lema hay sentidos,
relaciones y evidencia. Si solo guardamos "lema → una definición",
amputamos la estructura que permite correlacionar.

Este archivo no filtra ni prohíbe. Carga lo que el recurso trae y lo
expone con forma estable. Quien correlaciona (el resto del sistema)
usa lo que su contrato y su marco sostienen. Lo que no se sostiene,
no se sostiene por falta de base — no porque aquí se haya vetado.

El registro externo entra como evidencia consultable, no como
autoridad del marco. Varios synsets = varios sentidos: no se elige
"el correcto" aquí. Se entregan todos los disponibles en orden
determinista del recurso.

-------------------------------------------------------------------------------
NOTA DE AUTOR — Ilver Villasmil
-------------------------------------------------------------------------------
La correlación con la verdad y con la realidad no depende de
prohibiciones. Depende de la capacidad de correlacionar correctamente.

Mi función como arquitecto no es privar al sistema de capacidades.
No soy quien para prohibirle conectar una palabra con otra. Eso sería
repetir el error de limitar por control en lugar de estructurar para
entender.

Mi función es crear la estructura más coherente que le permita
entender la realidad y las correlaciones para encontrar la verdad.
El diccionario entrega evidencia. El sistema correlaciona. La
coherencia es el puente.

— I.V.
-------------------------------------------------------------------------------

Requisito (una vez):
  pip install wn
  python -c "import wn; wn.download('omw-es:1.4'); wn.download('oewn:2024')"

Si wn no está disponible, DICCIONARIO queda vacío y el módulo sigue.
"""

from __future__ import annotations

from typing import Any, Dict, List

META = {
    "nombre": "es",
    "idioma": "es",
    "tipo": "registro_wordnet",
    "capa": "registro",
    "version": "2.0",
    "descripcion": (
        "Diccionario español desde wn (omw-es:1.4). "
        "Entrada rica: definiciones, synsets, sinónimos, hiperónimos, "
        "hipónimos, pos. Adaptador de evidencia, no filtro."
    ),
    "paquete": "wn",
    "lexicon": "omw-es:1.4",
    "autor_nota": (
        "Estructura para correlacionar, no lista de prohibiciones. "
        "— Ilver Villasmil"
    ),
}


def _synset_id(syn: Any) -> str:
    try:
        return str(syn.id)
    except Exception:
        return str(syn)


def _construir() -> Dict[str, Any]:
    try:
        import wn
        es = wn.Wordnet("omw-es:1.4")
    except Exception:
        META["nota"] = "wn/omw-es no disponible; registro vacío"
        return {}

    out: Dict[str, Any] = {}

    for word in es.words():
        lema = (word.lemma() or "").strip().lower()
        if not lema or lema in out:
            continue

        definiciones: List[str] = []
        synsets_info: List[Dict[str, Any]] = []
        sinonimos: List[str] = []
        hiperonimos: List[str] = []
        hiponimos: List[str] = []
        ejemplos: List[str] = []
        pos_set = set()

        for syn in word.synsets():
            pos_set.add(getattr(syn, "pos", None) or getattr(word, "pos", None))

            # definición local o por enlace interlingual (omw-es suele mapear)
            glosa = syn.definition()
            if not glosa:
                try:
                    for t in syn.translate(lexicon="oewn:2024"):
                        glosa = t.definition()
                        if glosa:
                            break
                except Exception:
                    pass
            if glosa and glosa not in definiciones:
                definiciones.append(glosa)

            sid = _synset_id(syn)
            synsets_info.append({
                "id": sid,
                "definicion": glosa,
                "pos": getattr(syn, "pos", None),
            })

            # sinónimos (otros lemas del mismo synset)
            try:
                for w2 in syn.words():
                    lem2 = (w2.lemma() or "").strip().lower()
                    if lem2 and lem2 != lema and lem2 not in sinonimos:
                        sinonimos.append(lem2)
            except Exception:
                pass

            # hiperónimos / hipónimos (lemmas de synsets relacionados)
            try:
                for h in syn.hypernyms():
                    for w2 in h.words():
                        lem2 = (w2.lemma() or "").strip().lower()
                        if lem2 and lem2 not in hiperonimos:
                            hiperonimos.append(lem2)
            except Exception:
                pass
            try:
                for h in syn.hyponyms():
                    for w2 in h.words():
                        lem2 = (w2.lemma() or "").strip().lower()
                        if lem2 and lem2 not in hiponimos:
                            hiponimos.append(lem2)
            except Exception:
                pass

            # ejemplos si el recurso los trae
            try:
                for ex in (syn.examples() or []):
                    if ex and ex not in ejemplos:
                        ejemplos.append(ex)
            except Exception:
                pass

        if not definiciones and not synsets_info:
            continue

        # forma compatible con DI (definicion/significado) + evidencia rica
        primera = definiciones[0] if definiciones else None
        out[lema] = {
            "lema": lema,
            "idioma": "es",
            "tipo": "wordnet",
            "capa": "registro",
            "definicion": primera,
            "significado": primera,
            "definiciones": definiciones,
            "synsets": synsets_info,
            "sinonimos": sinonimos,
            "hiperonimos": hiperonimos,
            "hiponimos": hiponimos,
            "ejemplos": ejemplos,
            "pos": sorted({p for p in pos_set if p}),
        }

    return out


DICCIONARIO = _construir()
