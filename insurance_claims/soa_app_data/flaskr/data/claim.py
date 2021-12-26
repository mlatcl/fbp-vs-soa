from .db import get_db
import os
from datetime import datetime
from pandas import DataFrame

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
          '?,?,?,?,?,?,?,?,?,?,?,?,?,?,"NONE",0) ON CONFLICT(claim_id) DO UPDATE SET state = 0'
    values = []
    for key, value in claim.items():
        values.append(value)
    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid


# Calculate claims value
def get_claims_amount():
    res = []
    db = get_db()
    sql = 'SELECT claim_id, total_claim_amount FROM Claims WHERE state = 0'
    cursor = db.execute(sql)
    for claim in cursor:
        claim_values = {'claim_id': claim['claim_id'], 'value': claim['total_claim_amount']}
        res.append(claim_values)
    return res

def get_claim_classification_data(claim_id):
    db = get_db()
    sql = 'SELECT claim_id, total_claim_amount, auto_year, witnesses, police_report_available FROM Claims ' \
              'WHERE claim_id = ?'
    values = [claim_id]
    cursor = db.execute(sql, values)
    record = next(cursor)

    return {"claim_id": record["claim_id"],
            "total_claim_amount": record["total_claim_amount"],
            "auto_year": record["auto_year"],
            "witnesses": record["witnesses"],
            "police_report_available": record["police_report_available"]
            }

# Update claims by complexity
def update_claims_complexity(claims):
    db = get_db()
    simple_claims = claims['simple_claims']
    complex_claims = claims['complex_claims']
    for claim in simple_claims:
        sql = 'UPDATE Claims SET is_complex = "FALSE" WHERE claim_id = ?'
        values = [claim['claim_id']]
        db.execute(sql, values)
        db.commit()
    for claim in complex_claims:
        sql = 'UPDATE Claims SET is_complex = "TRUE" WHERE claim_id = ?'
        values = [claim['claim_id']]
        db.execute(sql, values)
        db.commit()

# Set claim state to 1
def mark_claim_processed(claim_id):
    db = get_db()
    sql = 'UPDATE Claims SET state = 1 WHERE claim_id = ?'
    values = [claim_id]
    db.execute(sql, values)
    db.commit()



# Save claims
def save_claims(claims):
    db = get_db()
    claim_ids = []
    for claim in claims:
        claim_ids.append(claim['claim_id'])
    sql = 'SELECT * FROM Claims WHERE claim_id IN (%s) ' % ("?," * len(claim_ids))[:-1]
    cursor = db.execute(sql, claim_ids)
    df = DataFrame(cursor.fetchall())
    cols = [column[0] for column in cursor.description]
    df.columns = cols
    df = df.drop(columns=['state'])
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
