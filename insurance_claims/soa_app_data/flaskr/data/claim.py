from .db import get_db
import os
from pandas import DataFrame

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


# Create a new claim
def create_claim(claim):
    db = get_db()

    sql = 'INSERT INTO Claims (months_as_customer,age,policy_number,policy_bind_date,policy_state,policy_csl,' \
          'policy_deductable,policy_annual_premium,umbrella_limit,insured_zip,insured_sex,insured_education_level,' \
          'insured_occupation,insured_hobbies,insured_relationship,capital_gains,capital_loss,incident_date,' \
          'incident_type,collision_type,incident_severity,authorities_contacted,incident_state,incident_city,' \
          'incident_location,incident_hour_of_the_day,number_of_vehicles_involved,property_damage,bodily_injuries,' \
          'witnesses,police_report_available,total_claim_amount,injury_claim,property_claim,vehicle_claim,auto_make,' \
          'auto_model,auto_year,claim_id,is_complex,state) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,' \
          '?,?,?,?,?,?,?,?,?,?,?,?,?,?,-1,0) ON CONFLICT(claim_id) DO UPDATE SET state = 0'
    values = []
    for key, value in claim.items():
        values.append(value)
    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid


# Calculate claims value
def calculate_claims_value():
    res = []
    db = get_db()
    sql = 'SELECT claim_id, total_claim_amount FROM Claims WHERE state = 0'
    cursor = db.execute(sql)
    for claim in cursor:
        value = (1.0+CLAIM_VALUE_PROCESSING_OVERHEAD_RATE) * claim['total_claim_amount']
        claim_values = {'claim_id': claim['claim_id'], 'value': value}
        res.append(claim_values)
    return res


# Classify claims by value
def classify_claims_value(claims):
    high_value_claims = []
    low_value_claims = []
    for claim in claims:
        if claim['value'] >= HIGH_VALUE_CLAIM_THRESHOLD:
            high_value_claims.append(claim)
        else:
            low_value_claims.append(claim)

    return {'high_value_claims': high_value_claims, 'low_value_claims': low_value_claims}


# Classify claims by complexity
def classify_claims_complexity(claims):
    db = get_db()
    simple_claims = []
    complex_claims = []
    low_value_claims = claims['low_value_claims']
    high_value_claims = claims['high_value_claims']
    for low_value_claim in low_value_claims:
        sql = 'SELECT claim_id, total_claim_amount, auto_year, witnesses, police_report_available FROM Claims ' \
              'WHERE claim_id = ?'
        values = [low_value_claim['claim_id']]
        cursor = db.execute(sql,values)
        for claim in cursor:
            c = {'claim_id':claim['claim_id'], 'total_claim_amount': claim['total_claim_amount']}
            if is_claim_complex(claim):
                complex_claims.append(c)
            else:
                simple_claims.append(c)

    for high_value_claim in high_value_claims:
        sql = 'SELECT claim_id, total_claim_amount, auto_year, witnesses FROM Claims WHERE claim_id = ?'
        values = [high_value_claim['claim_id']]
        cursor = db.execute(sql, values)
        for claim in cursor:
            c = {'claim_id': claim['claim_id'], 'total_claim_amount': claim['total_claim_amount']}
            complex_claims.append(c)

    for claim in simple_claims:
        sql = 'UPDATE Claims SET is_complex = 0 WHERE claim_id = ?'
        values = [claim['claim_id']]
        db.execute(sql, values)
        db.commit()
    for claim in complex_claims:
        sql = 'UPDATE Claims SET is_complex = 1 WHERE claim_id = ?'
        values = [claim['claim_id']]
        db.execute(sql, values)
        db.commit()
    return {'simple_claims': simple_claims, 'complex_claims': complex_claims}


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


# Calculate claims payments
def calculate_payments(claims):
    db = get_db()
    res = []
    simple_claims = claims['simple_claims']
    complex_claims = claims['complex_claims']
    for claim in simple_claims:
        payout = SIMPLE_CLAIMS_PAYOUT_RATE * claim["total_claim_amount"]
        r = {'claim_id': claim['claim_id'], 'payout': payout}
        res.append(r)

    for claim in complex_claims:
        payout = COMPLEX_CLAIMS_PAYOUT_RATE * claim["total_claim_amount"]
        r = {'claim_id': claim['claim_id'], 'payout': payout}
        res.append(r)

    for claim in res:
        sql = 'UPDATE Claims SET state = 1 WHERE claim_id = ?'
        values = [claim['claim_id']]
        db.execute(sql, values)
        db.commit()
    return res


# Save claims
def save_claims(claims):
    db = get_db()
    claim_ids = []
    for claim in claims:
        claim_ids.append(claim['claim_id'])
    sql = 'SELECT * FROM Claims WHERE claim_id IN (%s) ' % ("?," * len(claim_ids))[:-1]
    cursor = db.execute(sql, claim_ids)
    df = DataFrame(cursor.fetchall())
    columns = [column[0] for column in cursor.description]
    df.columns = columns
    _write_data_to_csv("claim_complexity.csv", df)


def _write_data_to_csv(filename, df):
    """
    Writes data from given pandas DataFrame to file
    Creates new file (with header) if it doesn't exist
    otherwise appends data to existing file

    Does not do anything if the dataset is empty
    """
    if df.empty:
        return

    if os.path.isfile(filename):
        df.to_csv(filename, mode="a", index=False, header=False)
    else:
        df.to_csv(filename, mode="w", index=False, header=True)
