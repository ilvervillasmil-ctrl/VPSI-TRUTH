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
        print("=== VPSI AUDIT REPORT ===\n")

        for c in self.claims:
            print(f"- {c.name}: {c.type.upper()} → {c.description}")

        A = self.anchoring_score()

        print("\n-------------------------")
        print(f"Anchoring Score A = {A:.3f}")

        if A == 1:
            print("STATUS: Fully Anchored (VPSI PASS)")
        elif A > 0.5:
            print("STATUS: Partially Anchored")
        else:
            print("STATUS: Weak Anchoring (VPSI FAIL)")

        print("-------------------------\n")


# -----------------------------
# Test concreto (tu caso Λ)
# -----------------------------

claims = [
    Claim("beta", "β = 1/27", "invention"),
    Claim("pi", "π appears in physics", "deduction"),
    Claim("phi", "golden ratio φ", "invention"),
    Claim("27pi", "structural exponent 27π", "invention"),
    Claim("exp_form", "exponential structure", "hypothesis"),
]

auditor = VPSIAuditor(claims)
auditor.report()
