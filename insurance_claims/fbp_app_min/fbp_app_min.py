from typing import List, Dict, Callable, Tuple
from collections import namedtuple

from flowpipe import Graph, INode, Node, InputPlug, OutputPlug
from insurance_claims.record_types import *

# let's invent some kind of overhead that goes into processing the claim
CLAIM_VALUE_PROCESSING_OVERHEAD_RATE = 0.05

# threshold to decide if claim is high or low value
HIGH_VALUE_CLAIM_THRESHOLD = 60000

# claims below this value are considered simple
SIMPLE_CLAIM_VALUE_THRESHOLD = 5000

# in reality sometimes the claims will be paid in full, and sometimes partially or not at all
# to average this out let's just always pay out a certain partial amount
# we assume simple claims will be paid out more often
SIMPLE_CLAIMS_PAYOUT_RATE = 0.8
COMPLEX_CLAIMS_PAYOUT_RATE = 0.6


class Stream(INode):
    def __init__(self, **kwargs):
        super(Stream, self).__init__(**kwargs)
        self.data = []


    def add_data(self, new_data: List, key: Callable=None) -> None:
        if key is None:
            self.data.extend(new_data)
            return

        data_as_dict = {key(x):x for x in self.data}

        for record in new_data:
            # this may sometimes override existing records
            # but that's intentional as we only want one record per key
            data_as_dict[key(record)] = record

        self.data = list(data_as_dict.values())


    def get_data(self, drop=False):
        data_to_return = self.data[:]
        if drop:
            self.data = []
        return data_to_return


############ input streams ##############

class NewClaimsStream(Stream):
    def __init__(self, **kwargs):
        super(NewClaimsStream, self).__init__(**kwargs)
        OutputPlug('new_claims', self)

    def compute(self) -> Dict:
        return {'new_claims': self.data}

############ inner streams ##############

class ClaimValueStream(Stream):
    def __init__(self, **kwargs):
        super(ClaimValueStream, self).__init__(**kwargs)
        InputPlug('claim_values', self)
        OutputPlug('claim_values', self)

    def compute(self, claim_values: List[ClaimValue]) -> Dict:
        self.add_data(claim_values, lambda x: x.claim_id)
        return {'claim_values': self.data}


class HighValueClaimsStream(Stream):
    def __init__(self, **kwargs):
        super(HighValueClaimsStream, self).__init__(**kwargs)
        InputPlug('high_value_claims', self)
        OutputPlug('high_value_claims', self)

    def compute(self, high_value_claims: List[Dict]) -> Dict:
        self.add_data(high_value_claims, lambda x: x["claim_id"])
        return {'high_value_claims': self.data}

class LowValueClaimsStream(Stream):
    def __init__(self, **kwargs):
        super(LowValueClaimsStream, self).__init__(**kwargs)
        InputPlug('low_value_claims', self)
        OutputPlug('low_value_claims', self)

    def compute(self, low_value_claims: List[Dict]) -> Dict:
        self.add_data(low_value_claims, lambda x: x["claim_id"])
        return {'low_value_claims': self.data}


class SimpleClaimsStream(Stream):
    def __init__(self, **kwargs):
        super(SimpleClaimsStream, self).__init__(**kwargs)
        InputPlug('simple_claims', self)
        OutputPlug('simple_claims', self)

    def compute(self, simple_claims: List[Dict]) -> Dict:
        self.add_data(simple_claims, lambda x: x["claim_id"])
        return {'simple_claims': self.data}


class ComplexClaimsStream(Stream):
    def __init__(self, **kwargs):
        super(ComplexClaimsStream, self).__init__(**kwargs)
        InputPlug('high_value_claims', self)
        InputPlug('complex_claims', self)
        OutputPlug('complex_claims', self)

    def compute(self, high_value_claims: List[Dict], complex_claims: List[Dict]) -> Dict:
        self.add_data(high_value_claims, lambda x: x["claim_id"])
        self.add_data(complex_claims, lambda x: x["claim_id"])
        return {'complex_claims': self.data}

############ output streams ##############

class ClaimPayoutStream(Stream):
    def __init__(self, **kwargs):
        super(ClaimPayoutStream, self).__init__(**kwargs)
        InputPlug('simple_claim_payouts', self)
        InputPlug('complex_claim_payouts', self)
        OutputPlug('claim_payouts', self)

    def compute(self, simple_claim_payouts: List[ClaimPayout], complex_claim_payouts: List[ClaimPayout]) -> Dict:
        self.add_data(simple_claim_payouts, lambda x: x.claim_id)
        self.add_data(complex_claim_payouts, lambda x: x.claim_id)
        return {'claim_payouts': self.data}


############ processing nodes ##############

class CalculateClaimValue(INode):
    def __init__(self, **kwargs):
        super(CalculateClaimValue, self).__init__(**kwargs)
        InputPlug('claims', self)
        OutputPlug('claim_values', self)
    
    def compute(self, claims: List[Dict]) -> Dict:
        # claim value itself plus processing overhead
        calc_total_claim_value = lambda v: (1.0 + CLAIM_VALUE_PROCESSING_OVERHEAD_RATE) * v
        claim_values = [ClaimValue(claim_id=c["claim_id"], value=calc_total_claim_value(c["total_claim_amount"])) for c in claims]
        return {'claim_values': claim_values}


class ClassifyClaimValue(INode):
    def __init__(self, **kwargs):
        super(ClassifyClaimValue, self).__init__(**kwargs)
        InputPlug('claims', self)
        InputPlug('claim_values', self)
        OutputPlug('high_value_claims', self)
        OutputPlug('low_value_claims', self)
    
    def compute(self, claims: List[Dict], claim_values: List[ClaimValue]) -> Dict:
        # these loops are twice as slow as they should be
        # because this filtering can be done in one iteration
        # but we won't be running crazy lots of data, so clarity first is ok

        # also this can be done with filter(), but i like generator syntax more

        high_value_claim_ids = [cv.claim_id for cv in claim_values if cv.value >= HIGH_VALUE_CLAIM_THRESHOLD]
        low_value_claim_ids = [cv.claim_id for cv in claim_values if cv.value < HIGH_VALUE_CLAIM_THRESHOLD]

        high_value_claims = [c for c in claims if c["claim_id"] in high_value_claim_ids]
        low_value_claims = [c for c in claims if c["claim_id"] in low_value_claim_ids]

        return {'high_value_claims': high_value_claims, 'low_value_claims': low_value_claims}


class ClassifyClaimComplexity(INode):
    def __init__(self, **kwargs):
        super(ClassifyClaimComplexity, self).__init__(**kwargs)
        InputPlug('claims', self)
        OutputPlug('simple_claims', self)
        OutputPlug('complex_claims', self)

    def compute(self, claims: List[Dict]) -> Dict:
        # just some almost random logic here
        def is_claim_complex(claim):
            if claim["total_claim_amount"] <= SIMPLE_CLAIM_VALUE_THRESHOLD:
                # small claims are never complex
                return False

            if claim["auto_year"] < 2000:
                # old cars yield complex cases
                return True
            
            if claim["witnesses"] == 0 and claim["police_report_available"] != "YES":
                # no objective evidence of incident cause
                return True

            return False

        simple_claims = [c for c in claims if not is_claim_complex(c)]
        complex_claims = [c for c in claims if is_claim_complex(c)]

        return {'simple_claims': simple_claims, 'complex_claims': complex_claims}


class CalculateSimpleClaimsPayout(INode):
    def __init__(self, **kwargs):
        super(CalculateSimpleClaimsPayout, self).__init__(**kwargs)
        InputPlug('simple_claims', self)
        OutputPlug('simple_claim_payouts', self)

    def compute(self, simple_claims: List[Dict]) -> Dict:
        simple_claim_payouts = [ClaimPayout(claim_id=c["claim_id"], payout=SIMPLE_CLAIMS_PAYOUT_RATE * c["total_claim_amount"])
                                for c in simple_claims]

        return {'simple_claim_payouts': simple_claim_payouts}


class CalculateComplexClaimsPayout(INode):
    def __init__(self, **kwargs):
        super(CalculateComplexClaimsPayout, self).__init__(**kwargs)
        InputPlug('complex_claims', self)
        OutputPlug('complex_claim_payouts', self)

    def compute(self, complex_claims: List[Dict]) -> Dict:
        complex_claim_payouts = [ClaimPayout(claim_id=c["claim_id"], payout=COMPLEX_CLAIMS_PAYOUT_RATE * c["total_claim_amount"])
                                for c in complex_claims]

        return {'complex_claim_payouts': complex_claim_payouts}


class App():
    def __init__(self):
        self._build()

    def evaluate(self):
        self.graph.evaluate()
        return self.get_outputs()

    def add_data(self, new_claims):
        self.new_claims_stream.add_data(new_claims, key=lambda x: x["claim_id"])

    def get_outputs(self):
        return self.claim_payouts_stream.get_data()

    def _build(self) -> Graph:
        graph = Graph(name='InsuraceClaims')

        # input streams
        self.new_claims_stream = NewClaimsStream(graph=graph)

        # inner streams
        claim_values_stream = ClaimValueStream(graph=graph)
        high_value_claims_stream = HighValueClaimsStream(graph=graph)
        low_value_claims_stream = LowValueClaimsStream(graph=graph)
        simple_claims_stream = SimpleClaimsStream(graph=graph)
        complex_claims_stream = ComplexClaimsStream(graph=graph)

        # output streams
        self.claim_payouts_stream = ClaimPayoutStream(graph=graph)

        self._all_streams = [self.new_claims_stream, claim_values_stream,
                             high_value_claims_stream, low_value_claims_stream,
                             simple_claims_stream, complex_claims_stream,
                             self.claim_payouts_stream]

        # processing nodes
        calculate_claim_value = CalculateClaimValue(graph=graph)
        classify_claim_value = ClassifyClaimValue(graph=graph)
        classify_claim_complexity = ClassifyClaimComplexity(graph=graph)
        calculate_simple_claim_payout = CalculateSimpleClaimsPayout(graph=graph)
        calculate_complex_claim_payout = CalculateComplexClaimsPayout(graph=graph)

        # wiring graph components
        self.new_claims_stream.outputs["new_claims"] >> calculate_claim_value.inputs["claims"]
        calculate_claim_value.outputs["claim_values"] >> claim_values_stream.inputs["claim_values"]

        self.new_claims_stream.outputs["new_claims"] >> classify_claim_value.inputs["claims"]
        claim_values_stream.outputs["claim_values"] >> classify_claim_value.inputs["claim_values"]
        classify_claim_value.outputs["low_value_claims"] >> low_value_claims_stream.inputs["low_value_claims"]
        classify_claim_value.outputs["high_value_claims"] >> high_value_claims_stream.inputs["high_value_claims"]

        high_value_claims_stream.outputs["high_value_claims"] >> complex_claims_stream.inputs["high_value_claims"]
        low_value_claims_stream.outputs["low_value_claims"] >> classify_claim_complexity.inputs["claims"]
        classify_claim_complexity.outputs["simple_claims"] >> simple_claims_stream.inputs["simple_claims"]
        classify_claim_complexity.outputs["complex_claims"] >> complex_claims_stream.inputs["complex_claims"]

        simple_claims_stream.outputs["simple_claims"] >> calculate_simple_claim_payout.inputs["simple_claims"]
        complex_claims_stream.outputs["complex_claims"] >> calculate_complex_claim_payout.inputs["complex_claims"]

        calculate_simple_claim_payout.outputs["simple_claim_payouts"] >> self.claim_payouts_stream.inputs["simple_claim_payouts"]
        calculate_complex_claim_payout.outputs["complex_claim_payouts"] >> self.claim_payouts_stream.inputs["complex_claim_payouts"]

        self.graph = graph


if __name__ == "__main__":
    app = App()
    graph = app.graph

    print(graph.name)
    print(graph)
    print(graph.list_repr())