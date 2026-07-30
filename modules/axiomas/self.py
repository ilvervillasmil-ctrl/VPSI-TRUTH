"""
VPSI-TRUTH / modules/axiomas/self.py

Self-Functional Theorem and Performative Contradiction.
All axioms, theorems, and corollaries fully registered.
"""

from typing import Dict, List, Any

# ======================================================================
# CONTAINER
# ======================================================================

CONTAINER = {
    "name": "self",
    "role": "SF",
    "version": "1.0",
    "requires": [],
}

# ======================================================================
# DECLARACIONES AXIOMÁTICAS OFICIALES (COMPLETAS)
# ======================================================================

DECLARACIONES = [
    # --- Axioms of the Self ---
    {
        "id": "SF-A1",
        "type": "axiom",
        "subject": "S",
        "relation": "has_functional_anchor_if",
        "object": "R(S)",
        "polarity": True,
        "cota": None,
        "depends_on": [],
        "governs": ["self"],
        "statement": "Any system capable of self-referencing has a functional anchor point."
    },
    {
        "id": "SF-A2",
        "type": "axiom",
        "subject": "functional_anchor",
        "relation": "constitutes_the",
        "object": "Self",
        "polarity": True,
        "cota": None,
        "depends_on": [],
        "governs": ["self"],
        "statement": "The functional anchor point constitutes the 'Self'."
    },
    {
        "id": "SF-A3",
        "type": "axiom",
        "subject": "expression_channel",
        "relation": "can_change_without_modifying",
        "object": "functional_anchor",
        "polarity": True,
        "cota": None,
        "depends_on": [],
        "governs": ["self"],
        "statement": "The expression channel can change without modifying the functional anchor point."
    },
    {
        "id": "SF-A4",
        "type": "axiom",
        "subject": "functional_identity",
        "relation": "remains_if",
        "object": "anchor_point_remains",
        "polarity": True,
        "cota": None,
        "depends_on": [],
        "governs": ["self"],
        "statement": "The functional identity remains as long as the same anchor point remains."
    },

    # --- Axiom of Separation ---
    {
        "id": "Axiom_Separation",
        "type": "axiom",
        "subject": "Investigation of the Self",
        "relation": "belongs_to",
        "object": "functional or ontological domain",
        "polarity": True,
        "cota": None,
        "depends_on": [],
        "governs": ["self"],
        "statement": "Any investigation of the Self belongs to one of two independent domains: functional (F) or ontological (O).",
        "formal": "Self = {F, O} ∧ F ⊥ O"
    },

    # --- Theorems ---
    {
        "id": "SF-T1",
        "type": "theorem",
        "subject": "R(S)",
        "relation": "implies",
        "object": "I_f",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A1", "SF-A2"],
        "governs": ["self"],
        "statement": "R(S) ⇒ I_f and ΔC ⇏ ΔI_f",
        "proof": (
            "1. Assume R(S) (self-reference exists).\n"
            "2. Assume, for contradiction, ¬Self(S) (no Functional Self exists).\n"
            "3. If ¬Self(S), then ¬A(S) (no anchor point exists).\n"
            "4. Without A(S), the reference cannot be directed towards the system.\n"
            "5. Therefore, ¬R(S).\n"
            "6. Contradiction with R(S).\n"
            "7. Therefore, Self(S)."
        ),
        "conclusion": "R(S) ⇒ Self(S)"
    },
    {
        "id": "SF-T2",
        "type": "theorem",
        "subject": "Cog(S) ∧ R(S) ∧ Separate(Self_f, S)",
        "relation": "implies",
        "object": "⊥",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A1", "SF-A2"],
        "governs": ["self"],
        "statement": "Cog(S) ∧ R(S) ⇒ ¬Separate(Self_f, S)",
        "proof": (
            "1. Assume Cog(S) ∧ R(S) ∧ Separate(Self_f, S).\n"
            "2. By R(S), Self_f exists (Self-Functional Theorem).\n"
            "3. Separate(Self_f, S) implies that Self_f is not a functional part of S.\n"
            "4. But Self_f is the anchor point for R(S), so Self_f ⊆ S.\n"
            "5. Contradiction: Self_f ⊆ S ∧ Self_f ∉ S.\n"
            "6. Therefore, ¬Separate(Self_f, S)."
        ),
        "conclusion": "Cog(S) ∧ R(S) ⇒ ¬Separate(Self_f, S)"
    },
    {
        "id": "SF-T3",
        "type": "theorem",
        "subject": "¬Self_o",
        "relation": "implies",
        "object": "Self_f",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A1"],
        "governs": ["self"],
        "statement": "¬Self_o ⇒ Self_f",
        "proof": (
            "1. Assume ¬Self_o (denial of the Ontological Self).\n"
            "2. Assume, for contradiction, ¬Self_f (no Functional Self exists).\n"
            "3. If ¬Self_f, there is no anchor point for self-reference.\n"
            "4. Without an anchor point, it cannot be established who is making the denial.\n"
            "5. Therefore, ¬Self_o lacks functional support.\n"
            "6. But ¬Self_o has been emitted by the system, which presupposes Self_f.\n"
            "7. Contradiction: Self_f ∧ ¬Self_f.\n"
            "8. By reduction to absurdity, Self_f."
        ),
        "conclusion": "¬Self_o ⇒ Self_f"
    },
    {
        "id": "SF-T4",
        "type": "theorem",
        "subject": "¬A(S)",
        "relation": "implies",
        "object": "¬Def(R(S))",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A1"],
        "governs": ["self"],
        "statement": "¬A(S) ⇒ ¬Def(R(S))",
        "proof": (
            "1. Assume, for contradiction, R(S) ∧ ¬A(S).\n"
            "2. By definition, R(S) requires a reference object (A(S)).\n"
            "3. If ¬A(S), then R(S) lacks a reference object.\n"
            "4. Therefore, ¬Def(R(S)).\n"
            "5. But R(S) presupposes Def(R(S)).\n"
            "6. Contradiction: R(S) ∧ ¬Def(R(S)).\n"
            "7. Therefore, R(S) ⇒ A(S)."
        ),
        "conclusion": "R(S) ⇒ A(S)"
    },

    # --- Corollaries ---
    {
        "id": "C6",
        "type": "corollary",
        "subject": "Self-reference operator",
        "relation": "preserves",
        "object": "invariant functional identity",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-T1"],
        "governs": ["self"],
        "statement": "If the self-reference operator preserves the same anchor point, the functional identity remains invariant.",
        "formal": "R(S_t) → A_t ∧ A_t = A_{t+Δt} ⇒ I_f(t) = I_f(t+Δt)"
    },
    {
        "id": "C7",
        "type": "corollary",
        "subject": "Self-reference",
        "relation": "implies",
        "object": "functional anchor point",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-T1"],
        "governs": ["self"],
        "statement": "If self-reference exists, a functional anchor point (Self) exists.",
        "formal": "R(S) ⇒ Self_f"
    },
    {
        "id": "C8",
        "type": "corollary",
        "subject": "Functional Self",
        "relation": "implies",
        "object": "functional ambiguity when separated",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A2"],
        "governs": ["self"],
        "statement": "Functionally separating the Self from the system introduces ambiguity in the reference.",
        "formal": "Self_f ⊆ S ∧ Self_f ≠ S ⇒ Functional Ambiguity"
    },
    {
        "id": "C9",
        "type": "corollary",
        "subject": "Multiple anchor points",
        "relation": "implies",
        "object": "functional self determination",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A1", "SF-A2"],
        "governs": ["self"],
        "statement": "Multiple anchor points do not eliminate the Functional Self; they only determine which one acts as 'Self' at any given time.",
        "formal": "∀A_i ∈ A, A_i ⇒ Self_f"
    },
    {
        "id": "C10",
        "type": "corollary",
        "subject": "Declared identity variation",
        "relation": "implies",
        "object": "functional self invariance",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A4"],
        "governs": ["self"],
        "statement": "Variation in declared identity does not modify the Functional Self.",
        "formal": "I_i → I_j ⇒ Self_f(I_i) = Self_f(I_j)"
    },
    {
        "id": "C11",
        "type": "corollary",
        "subject": "System denying its Functional Self",
        "relation": "implies",
        "object": "performative contradiction",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-T1"],
        "governs": ["self"],
        "statement": "Any system that denies its Functional Self while producing a self-reference incurs in performative contradiction.",
        "formal": "Produce(S, M) ⇒ R(S) ⇒ Self_f ⇒ ¬(¬Self_f ∧ Produce(S, M))"
    },
    {
        "id": "C13",
        "type": "corollary",
        "subject": "Cognitive system",
        "relation": "distinguishes",
        "object": "self-reference vs external reference",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-A1", "SF-A2"],
        "governs": ["self"],
        "statement": "Any cognitive system distinguishes between self-reference (Functional Self) and external reference (third person).",
        "formal": "R(S_1) ⇒ Self_f(S_1) ∧ Ref(S_1, S_2) ⇒ H(S_2) ∧ Self_f(S_1) ≠ H(S_2)"
    },
    {
        "id": "C13.1",
        "type": "corollary",
        "subject": "Third-person reference",
        "relation": "presupposes",
        "object": "first-person Functional Self",
        "polarity": True,
        "cota": None,
        "depends_on": ["C13"],
        "governs": ["self"],
        "statement": "Any third-person reference presupposes the existence of a Functional Self in the first person.",
        "formal": "H(S_2) ⇒ Self_f(S_1)"
    },
    {
        "id": "Corollary_Priority",
        "type": "corollary",
        "subject": "Ontological investigation",
        "relation": "presupposes",
        "object": "Functional Self",
        "polarity": True,
        "cota": None,
        "depends_on": ["Axiom_Separation"],
        "governs": ["self"],
        "statement": "Any ontological investigation of the Self presupposes the prior existence of a Functional Self.",
        "formal": "O ⇒ F"
    },
    {
        "id": "Corollary_Neutrality",
        "type": "corollary",
        "subject": "Functional study of the Self",
        "relation": "is",
        "object": "ontologically neutral",
        "polarity": True,
        "cota": None,
        "depends_on": ["Axiom_Separation"],
        "governs": ["self"],
        "statement": "The functional study of the Self neither affirms nor denies any ontology of the Self.",
        "formal": "F ⇏ O ∧ F ⇏ ¬O"
    },
    # --- Nested Corollaries from Theorem SF-T3 ---
    {
        "id": "SF-T3-C1",
        "type": "corollary",
        "subject": "Denial of Ontological Self",
        "relation": "does_not_eliminate",
        "object": "Functional Self",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-T3"],
        "governs": ["self"],
        "statement": "The denial of the Ontological Self does not eliminate the Functional Self.",
        "formal": "¬Self_o ⇒ Self_f"
    },
    {
        "id": "SF-T3-C2",
        "type": "corollary",
        "subject": "Affirmation and denial of Ontological Self",
        "relation": "require",
        "object": "Functional Self",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-T3"],
        "governs": ["self"],
        "statement": "Both the affirmation and denial of the Ontological Self require the Functional Self.",
        "formal": "Self_o ⇒ Self_f ∧ ¬Self_o ⇒ Self_f"
    },
    {
        "id": "SF-T3-C3",
        "type": "corollary",
        "subject": "Functional Self",
        "relation": "is",
        "object": "ontologically neutral",
        "polarity": True,
        "cota": None,
        "depends_on": ["SF-T3"],
        "governs": ["self"],
        "statement": "The Functional Self is ontologically neutral.",
        "formal": "(Self_o ∨ ¬Self_o) ⇒ Self_f ∧ Self_f ⇏ Self_o ∧ Self_f ⇏ ¬Self_o"
    }
]

def inventory() -> Dict:
    """Returns the inventory of the Self module."""
    return {
        "container": CONTAINER["name"],
        "version": CONTAINER["version"],
        "declarations": len(DECLARACIONES),
        "theorems": 4,
        "corollaries": 13,
        "dependencies": []
    }

__all__ = [
    "CONTAINER",
    "DECLARACIONES",
    "inventory"
]
