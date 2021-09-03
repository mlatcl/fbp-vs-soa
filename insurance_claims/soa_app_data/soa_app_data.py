import requests

from insurance_claims.record_types import *

base_url = 'http://127.0.0.1:5000/'


class App():

    def evaluate(self, save_dataset=False):
        calculated_claims_value = self._calculate_claims_value()
        classified_claims_value = self._classify_claims_value(calculated_claims_value)
        classified_claims_complexity = self._classify_claims_complexity(classified_claims_value)
        self._update_claims_complexity(classified_claims_complexity)
        claim_payouts = self._calculate_payments(classified_claims_complexity)
        if save_dataset:
            self._save_claims(claim_payouts)
        return self.get_outputs(claim_payouts)

    # Client to calculate claims value
    def _calculate_claims_value(self):
        url = base_url + 'claim-request/calculate_claims_value'
        response = requests.post(url, json={})
        calculated_claims_value = response.json()
        return calculated_claims_value

    # Client to classify claims by value
    def _classify_claims_value(self, claims):
        url = base_url + 'claim-request/classify_claims_value'
        response = requests.post(url, json=claims)
        classified_claims_value = response.json()
        return classified_claims_value

    # Client to classify claims by complexity
    def _classify_claims_complexity(self, classified_claims_value):
        url = base_url + 'claim-request/classify_claims_complexity'
        response = requests.post(url, json=classified_claims_value)
        classified_claims_complexity = response.json()
        return classified_claims_complexity

    # Client to update claims by complexity
    def _update_claims_complexity(self, classified_claims_complexity):
        url = base_url + 'claim-request/update_claims_complexity'
        requests.post(url, json=classified_claims_complexity)

    # Client to calculate payments
    def _calculate_payments(self, classified_claims_complexity):
        url = base_url + 'claim-request/calculate_payments'
        response = requests.post(url, json=classified_claims_complexity)
        claim_payouts = response.json()
        return claim_payouts

    # Client to save claims
    def _save_claims(self, claim_payouts):
        url = base_url + 'claim-request/save_claims'
        response = requests.post(url, json=claim_payouts)
        claim_payouts = response.json()
        return claim_payouts

    def add_data(self, input_records):
        self._add_claims_requests(input_records)

    # Client to add claims data
    def _add_claims_requests(self, input_records):
        if len(input_records) > 0:
            claims = []
            for record in input_records:
                claims.append(record)
            url = base_url + 'claim-request/add_claims'
            response = requests.post(url, json=claims)
            # print(response.json())

    # Parsing data for main program
    def get_outputs(self, claim_payouts):
        claim_payouts = self._parse_claim_payouts(claim_payouts)
        return claim_payouts

    # Parses payouts
    def _parse_claim_payouts(self, claim_payouts):
        claims = []
        for claim in claim_payouts:
            c = ClaimPayout.from_dict(claim)
            claims.append(c)
        return claims


if __name__ == "__main__":
    app = App()
