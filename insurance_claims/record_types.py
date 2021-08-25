from dataclasses import dataclass

@dataclass
class ClaimValue:
    claim_id: int
    value: float

@dataclass
class ClaimPayout:
    claim_id: int
    payout: float