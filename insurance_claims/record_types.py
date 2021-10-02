from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass
class ClaimValue:
    claim_id: int
    value: float


@dataclass_json
@dataclass
class ClaimPayout:
    claim_id: int
    payout: float
