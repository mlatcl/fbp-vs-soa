DROP TABLE IF EXISTS Claims;

CREATE TABLE Claims(
  claim_id INTEGER PRIMARY KEY,
  months_as_customer INTEGER NOT NULL,
  age INTEGER NOT NULL,
  policy_number INTEGER NOT NULL,
  policy_bind_date TIMESTAMP NOT NULL,
  policy_state TEXT NOT NULL,
  policy_csl TEXT NOT NULL,
  policy_deductable INTEGER NOT NULL,
  policy_annual_premium FLOAT NOT NULL,
  umbrella_limit INTEGER NOT NULL,
  insured_zip INTEGER NOT NULL,
  insured_sex TEXT NOT NULL,
  insured_education_level TEXT NOT NULL,
  insured_occupation TEXT NOT NULL,
  insured_hobbies TEXT NOT NULL,
  insured_relationship TEXT NOT NULL,
  capital_gains INTEGER NOT NULL,
  capital_loss INTEGER NOT NULL,
  incident_date TIMESTAMP NOT NULL,
  incident_type TEXT NOT NULL,
  collision_type TEXT NOT NULL,
  incident_severity TEXT NOT NULL,
  authorities_contacted TEXT NOT NULL,
  incident_state TEXT NOT NULL,
  incident_city TEXT NOT NULL,
  incident_location TEXT NOT NULL,
  incident_hour_of_the_day INTEGER NOT NULL,
  number_of_vehicles_involved INTEGER NOT NULL,
  property_damage TEXT NOT NULL,
  bodily_injuries INTEGER NOT NULL,
  witnesses INTEGER NOT NULL,
  police_report_available TEXT NOT NULL,
  total_claim_amount INTEGER NOT NULL,
  injury_claim INTEGER NOT NULL,
  property_claim INTEGER NOT NULL,
  vehicle_claim INTEGER NOT NULL,
  auto_make TEXT NOT NULL,
  auto_model TEXT NOT NULL,
  auto_year INTEGER NOT NULL,
  is_complex INTEGER NOT NULL,
  state INTEGER NOT NULL
);



