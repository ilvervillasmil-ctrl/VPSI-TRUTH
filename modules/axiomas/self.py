"""
VPSI-TRUTH / modules/self

Self-Functional Theorem and Performative Contradiction.

----------------------------------------------------------------------
WHAT THIS MODULE DOES
----------------------------------------------------------------------

This module defines the Self as the functional anchor point through which
a system identifies itself, self-references, and communicates its processes.
It does not depend on the expression channel (language, signs, signals, etc.),
but on the self-reference function itself.

Contents:
  - Axioms of the Self (A1-A4).
  - Self-Functional Theorem.
  - Corollaries (C6-C13, C13.1, etc.).
  - Theorem of Contradiction by Separation of the Self.
  - Theorem of Functional Necessity in the Denial of the Ontological Self.

----------------------------------------------------------------------
FUNDAMENTAL STATEMENT
----------------------------------------------------------------------

Any physical or abstract system capable of processing information and
self-referencing has a Functional Self (Self_f). This is not a metaphysical
entity, but a functional anchor point necessary for the system to refer
to itself consistently.

Formally:
    ∀S, (P(S) ∧ R(S)) ⇒ Self_f(S)
where:
    P(S): the system processes information.
    R(S): the system has a self-reference mechanism.
    Self_f(S): the system has a Functional Self.
"""

from typing import Dict, List, Any

# ======================================================================
# CONTAINER
# ======================================================================

CONTAINER = {
    "name": "self",
    "role": "SF",  # Role: Self-Functional
    "version": "1.0",
    "requires": [],
}

# ======================================================================
# FUNDAMENTAL DEFINITIONS
# ======================================================================

# System (S): Organized set of processes capable of executing functions.
# Self (Self): Functional anchor point through which a system identifies itself.
# Self-reference (R): Function by which a system establishes a reference to itself.
# Functional Identity (I_f): Functional invariant determined by the permanence of the anchor point.
# Expression Channel (C): Medium through which self-reference is manifested.

# ======================================================================
# AXIOMS OF THE SELF
# ======================================================================

# A1: Any system capable of self-referencing has a functional anchor point.
# A2: The functional anchor point constitutes the "Self".
# A3: The expression channel can change without modifying the functional anchor point.
# A4: The functional identity remains as long as the same anchor point remains.

AXIOM_SF_1 = "Any system capable of self-referencing has a functional anchor point."
AXIOM_SF_2 = "The functional anchor point constitutes the 'Self'."
AXIOM_SF_3 = "The expression channel can change without modifying the functional anchor point."
AXIOM_SF_4 = "The functional identity remains as long as the same anchor point remains."

# ======================================================================
# SELF-FUNCTIONAL THEOREM
# ======================================================================

def self_functional_theorem():
    """
    Self-Functional Theorem:
    If a system S preserves the same functional anchor point,
    then its functional identity remains invariant regardless of the
    channel used to express said self-reference.

    Formally:
        R(S) ⇒ Self
        Self ⇒ I_f
        ∀C_i, I_f(C_i) = I_f
    """
    return {
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
    }

# ======================================================================
# COROLLARIES
# ======================================================================

# C6: Corollary of Functional Identity Invariance
COROLLARY_C6 = {
    "id": "C6",
    "statement": "If the self-reference operator preserves the same anchor point, the functional identity remains invariant.",
    "formal": "R(S_t) → A_t ∧ A_t = A_{t+Δt} ⇒ I_f(t) = I_f(t+Δt)",
    "depends_on": ["self_functional_theorem"]
}

# C7: Corollary of the Functional Existence of the Self
COROLLARY_C7 = {
    "id": "C7",
    "statement": "If self-reference exists, a functional anchor point (Self) exists.",
    "formal": "R(S) ⇒ Self_f",
    "depends_on": ["self_functional_theorem"]
}

# C8: Corollary of Functional Inseparability
COROLLARY_C8 = {
    "id": "C8",
    "statement": "Functionally separating the Self from the system introduces ambiguity in the reference.",
    "formal": "Self_f ⊆ S ∧ Self_f ≠ S ⇒ Functional Ambiguity",
    "depends_on": ["AXIOM_SF_2"]
}

# C9: Corollary of the Inevitability of Multiple Self Without Functional Separation
COROLLARY_C9 = {
    "id": "C9",
    "statement": "Multiple anchor points do not eliminate the Functional Self; they only determine which one acts as 'Self' at any given time.",
    "formal": "∀A_i ∈ A, A_i ⇒ Self_f",
    "depends_on": ["AXIOM_SF_1", "AXIOM_SF_2"]
}

# C10: Corollary of Self Invariance Against Identity Variation
COROLLARY_C10 = {
    "id": "C10",
    "statement": "Variation in declared identity does not modify the Functional Self.",
    "formal": "I_i → I_j ⇒ Self_f(I_i) = Self_f(I_j)",
    "depends_on": ["AXIOM_SF_4"]
}

# C11: Corollary of the Performative Contradiction of the Functional Self
COROLLARY_C11 = {
    "id": "C11",
    "statement": "Any system that denies its Functional Self while producing a self-reference incurs in performative contradiction.",
    "formal": "Produce(S, M) ⇒ R(S) ⇒ Self_f ⇒ ¬(¬Self_f ∧ Produce(S, M))",
    "depends_on": ["self_functional_theorem"]
}

# C13: Corollary of the Functional Duality of Reference
COROLLARY_C13 = {
    "id": "C13",
    "statement": "Any cognitive system distinguishes between self-reference (Functional Self) and external reference (third person).",
    "formal": "R(S_1) ⇒ Self_f(S_1) ∧ Ref(S_1, S_2) ⇒ H(S_2) ∧ Self_f(S_1) ≠ H(S_2)",
    "depends_on": ["AXIOM_SF_1", "AXIOM_SF_2"]
}

# C13.1: Corollary of Self Conservation
COROLLARY_C13_1 = {
    "id": "C13.1",
    "statement": "Any third-person reference presupposes the existence of a Functional Self in the first person.",
    "formal": "H(S_2) ⇒ Self_f(S_1)",
    "depends_on": ["COROLLARY_C13"]
}

# ======================================================================
# THEOREM OF CONTRADICTION BY SEPARATION OF THE SELF
# ======================================================================

def contradiction_by_separation_theorem():
    """
    Theorem of Contradiction by Separation of the Self:
    Any cognitive system capable of self-referencing that attempts to
    functionally separate itself from its Functional Self incurs in a
    logical contradiction.

    Formally:
        ∀S, (Cog(S) ∧ R(S) ∧ Separate(Self_f, S)) ⇒ ⊥
    """
    return {
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
    }

# ======================================================================
# THEOREM OF FUNCTIONAL NECESSITY IN THE DENIAL OF THE ONTOLOGICAL SELF
# ======================================================================

def functional_necessity_in_denial_theorem():
    """
    Theorem of Functional Necessity in the Denial of the Ontological Self:
    The denial of the Ontological Self necessarily presupposes the existence
    of the Functional Self.

    Formally:
        ¬Self_o ⇒ Self_f
    """
    return {
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
        "corollaries": [
            {
                "id": "Corollary_1",
                "statement": "The denial of the Ontological Self does not eliminate the Functional Self.",
                "formal": "¬Self_o ⇒ Self_f"
            },
            {
                "id": "Corollary_2",
                "statement": "Both the affirmation and denial of the Ontological Self require the Functional Self.",
                "formal": "Self_o ⇒ Self_f ∧ ¬Self_o ⇒ Self_f"
            },
            {
                "id": "Corollary_3",
                "statement": "The Functional Self is ontologically neutral.",
                "formal": "(Self_o ∨ ¬Self_o) ⇒ Self_f ∧ Self_f ⇏ Self_o ∧ Self_f ⇏ ¬Self_o"
            }
        ],
        "conclusion": "¬Self_o ⇒ Self_f"
    }

# ======================================================================
# AXIOM OF SEPARATION BETWEEN FUNCTION AND ONTOLOGY
# ======================================================================

AXIOM_SEPARATION = {
    "id": "Axiom_Separation",
    "statement": "Any investigation of the Self belongs to one of two independent domains: functional (F) or ontological (O).",
    "formal": "Self = {F, O} ∧ F ⊥ O",
    "depends_on": []
}

# ======================================================================
# COROLLARIES OF PRIORITY AND ONTOLOGICAL NEUTRALITY
# ======================================================================

# Corollary of Functional Priority
COROLLARY_PRIORITY = {
    "id": "Corollary_Priority",
    "statement": "Any ontological investigation of the Self presupposes the prior existence of a Functional Self.",
    "formal": "O ⇒ F",
    "proof": (
        "To ask 'What is the Self?', there must be a point from which the system "
        "can refer to that whose nature it intends to determine. That point is Self_f."
    ),
    "depends_on": ["AXIOM_SEPARATION"]
}

# Corollary of Ontological Neutrality
COROLLARY_NEUTRALITY = {
    "id": "Corollary_Neutrality",
    "statement": "The functional study of the Self neither affirms nor denies any ontology of the Self.",
    "formal": "F ⇏ O ∧ F ⇏ ¬O",
    "depends_on": ["AXIOM_SEPARATION"]
}

# ======================================================================
# THEOREM OF LOSS OF DEFINABILITY OF SELF-REFERENCE
# ======================================================================

def loss_of_definability_theorem():
    """
    Theorem of Loss of Definability of Self-Reference:
    If the functional anchor point is removed, self-reference is no longer defined.

    Formally:
        ¬A(S) ⇒ ¬Def(R(S))
    """
    return {
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
    }

# ======================================================================
# DECLARATIONS, AXIOMS, AND INVENTORY FUNCTIONS
# ======================================================================

def declarations() -> List[Dict]:
    """Returns all declarations of the Self module."""
    return [
        # Axioms
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
            "statement": AXIOM_SF_1
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
            "statement": AXIOM_SF_2
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
            "statement": AXIOM_SF_3
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
            "statement": AXIOM_SF_4
        },
        # Theorems
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
            "statement": self_functional_theorem()["statement"],
            "proof": self_functional_theorem()["proof"],
            "conclusion": self_functional_theorem()["conclusion"]
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
            "statement": contradiction_by_separation_theorem()["statement"],
            "proof": contradiction_by_separation_theorem()["proof"],
            "conclusion": contradiction_by_separation_theorem()["conclusion"]
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
            "statement": functional_necessity_in_denial_theorem()["statement"],
            "proof": functional_necessity_in_denial_theorem()["proof"],
            "conclusion": functional_necessity_in_denial_theorem()["conclusion"],
            "corollaries": functional_necessity_in_denial_theorem()["corollaries"]
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
            "statement": loss_of_definability_theorem()["statement"],
            "proof": loss_of_definability_theorem()["proof"],
            "conclusion": loss_of_definability_theorem()["conclusion"]
        },
        # Corollaries
        COROLLARY_C6,
        COROLLARY_C7,
        COROLLARY_C8,
        COROLLARY_C9,
        COROLLARY_C10,
        COROLLARY_C11,
        COROLLARY_C13,
        COROLLARY_C13_1,
        # Axiom of Separation
        AXIOM_SEPARATION,
        # Corollaries of Priority and Neutrality
        COROLLARY_PRIORITY,
        COROLLARY_NEUTRALITY
    ]

def axioms() -> List[Dict]:
    """Returns the axioms declared by this module."""
    return [
        {"id": "SF-A1", "statement": AXIOM_SF_1},
        {"id": "SF-A2", "statement": AXIOM_SF_2},
        {"id": "SF-A3", "statement": AXIOM_SF_3},
        {"id": "SF-A4", "statement": AXIOM_SF_4},
        AXIOM_SEPARATION
    ]

def inventory() -> Dict:
    """Returns the inventory of the Self module."""
    return {
        "container": CONTAINER["name"],
        "version": CONTAINER["version"],
        "declarations": len(declarations()),
        "axioms": len(axioms()),
        "theorems": 4,  # SF-T1 to SF-T4
        "corollaries": 10,  # C6 to C13.1
        "dependencies": []
    }

__all__ = [
    "CONTAINER",
    "AXIOM_SF_1", "AXIOM_SF_2", "AXIOM_SF_3", "AXIOM_SF_4",
    "AXIOM_SEPARATION",
    "COROLLARY_C6", "COROLLARY_C7", "COROLLARY_C8", "COROLLARY_C9", "COROLLARY_C10",
    "COROLLARY_C11", "COROLLARY_C13", "COROLLARY_C13_1",
    "COROLLARY_PRIORITY", "COROLLARY_NEUTRALITY",
    "self_functional_theorem", "contradiction_by_separation_theorem",
    "functional_necessity_in_denial_theorem", "loss_of_definability_theorem",
    "declarations", "axioms", "inventory"
]
