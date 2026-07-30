from dataclasses import dataclass
from typing import List, Literal

# -----------------------------
# Definición VPSI
# -----------------------------

ClaimType = Literal["deduction", "hypothesis", "invention"]

@dataclass
class Claim:
    name: str
    description: str
    type: ClaimType


# -----------------------------
# Auditor VPSI
# -----------------------------

class VPSIAuditor:

    def __init__(self, claims: List[Claim]):
        self.claims = claims

    def anchoring_score(self):
        total = len(self.claims)
        unsupported = sum(1 for c in self.claims if c.type == "invention")

        if total == 0:
            return 1.0

        return 1 - (unsupported / total)

    def report(self):
        report_lines = ["=== VPSI AUDIT REPORT ===\n"]

        for c in self.claims:
            report_lines.append(f"- {c.name}: {c.type.upper()} → {c.description}")

        A = self.anchoring_score()
        return A


# -----------------------------
# Test formal para Pytest
# -----------------------------

def test_vpsi_auditor_score():
    claims = [
        Claim("beta", "β = 1/27", "invention"),
        Claim("pi", "π appears in physics", "deduction"),
        Claim("phi", "golden ratio φ", "invention"),
        Claim("27pi", "structural exponent 27π", "invention"),
        Claim("exp_form", "exponential structure", "hypothesis"),
    ]

    auditor = VPSIAuditor(claims)
    score = auditor.anchoring_score()
    
    # Total claims = 5, inventions = 3 ("beta", "phi", "27pi")
    # Unsupported ratio = 3/5 = 0.6
    # Anchoring Score A = 1 - 0.6 = 0.4
    assert score == 0.4
