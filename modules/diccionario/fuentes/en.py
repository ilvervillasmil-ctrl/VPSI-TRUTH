"""
modules/diccionario/fuentes/en.py
=================================

English dictionary — lexical registry (package wn / oewn).

-------------------------------------------------------------------------------
WHY IT IS BUILT THIS WAY
-------------------------------------------------------------------------------
A single word is not the truth. Behind each lemma there are senses,
relations and evidence. If we only store "lemma → one definition",
we cut away the structure that makes correlation possible.

This file does not filter or forbid. It loads what the resource provides
and exposes it in a stable shape. Whoever correlates (the rest of the
system) uses what its contract and frame can sustain. What does not
hold, does not hold for lack of ground — not because it was banned here.

The external registry is consultable evidence, not frame authority.
Multiple synsets = multiple senses: the "right" one is not chosen here.
All available senses are delivered in the resource's deterministic order.

-------------------------------------------------------------------------------
AUTHOR NOTE — Ilver Villasmil
-------------------------------------------------------------------------------
Correlation with truth and with reality does not depend on prohibitions.
It depends on the capacity to correlate correctly.

My role as architect is not to deprive the system of capacities.
I am not the one to forbid it from connecting one word with another.
That would repeat the error of limiting by control instead of
structuring in order to understand.

My role is to build the most coherent structure that allows it to
understand reality and correlations in order to find the truth.
The dictionary delivers evidence. The system correlates. Coherence
is the bridge.

— I.V.
-------------------------------------------------------------------------------

Requirement (once):
  pip install wn
  python -c "import wn; wn.download('oewn:2024')"

If wn is unavailable, DICCIONARIO is empty and the module still loads.
"""

from __future__ import annotations

from typing import Any, Dict, List

META = {
    "nombre": "en",
    "idioma": "en",
    "tipo": "registro_wordnet",
    "capa": "registro",
    "version": "2.0",
    "descripcion": (
        "English dictionary from wn (oewn:2024). "
        "Rich entry: definitions, synsets, synonyms, hypernyms, "
        "hyponyms, pos. Evidence adapter, not a filter."
    ),
    "paquete": "wn",
    "lexicon": "oewn:2024",
    "autor_nota": (
        "Structure for correlation, not a list of prohibitions. "
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
        en = wn.Wordnet("oewn:2024")
    except Exception:
        META["nota"] = "wn/oewn not available; registry empty"
        return {}

    out: Dict[str, Any] = {}

    for word in en.words():
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

            glosa = syn.definition()
            if glosa and glosa not in definiciones:
                definiciones.append(glosa)

            synsets_info.append({
                "id": _synset_id(syn),
                "definicion": glosa,
                "pos": getattr(syn, "pos", None),
            })

            try:
                for w2 in syn.words():
                    lem2 = (w2.lemma() or "").strip().lower()
                    if lem2 and lem2 != lema and lem2 not in sinonimos:
                        sinonimos.append(lem2)
            except Exception:
                pass

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

            try:
                for ex in (syn.examples() or []):
                    if ex and ex not in ejemplos:
                        ejemplos.append(ex)
            except Exception:
                pass

        if not definiciones and not synsets_info:
            continue

        primera = definiciones[0] if definiciones else None
        out[lema] = {
            "lema": lema,
            "idioma": "en",
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
