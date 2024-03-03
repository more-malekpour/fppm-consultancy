import pandas as pd
import numpy as np

# Read patients data
patients = pd.read_csv("materials/patients.csv")

# Read facilities data
facilities = pd.read_csv("materials/facilities.csv")

# Read initial visit data
initial_visit = pd.read_csv("materials/htn_initial_visits.csv")

# Read follow-up visit data
followup_visit = pd.read_csv("materials/htn_follow_up_visits.csv")

# Merge initial visit with follow-up visit data to get SBP and DBP at follow-up
initial_visit = initial_visit.merge(followup_visit[['patient_id', 'sbp', 'dbp','ckd_diagnosis','cvd_diagnosis','cvd_high_risk','diabetes']],
                                    on='patient_id', suffixes=('', '_followup'), how='left')

# Merge patient data with initial visit data to get additional patient details
initial_visit = initial_visit.merge(patients[['patient_id', 'gender', 'facility_id']],
                                    on='patient_id', how='left')

# Merge facility data with initial visit data to get additional facility details
initial_visit = initial_visit.merge(facilities[['facility_id', 'facility', 'district', 'province', 'country','metformin','sulfonylurea','insulin','statin']],
                                    on='facility_id', how='left')
# Criteria 1: Check if SBP < 140 and DBP < 90
initial_visit['bp_controlled_measurements'] = ((initial_visit['sbp_followup'] < 140) &
                                                (initial_visit['dbp_followup'] < 90))

# Criteria 2: Check if SBP < 130 for people with history of CVD
initial_visit['bp_controlled_cvd'] = ((initial_visit['sbp'] < 130) & (initial_visit['cvd_diagnosis'] == 'Yes'))

# Criteria 3: Check if SBP < 130 for high-risk people with hypertension
initial_visit['high_risk'] = ((initial_visit['cvd_high_risk'] == 'Yes') |
                               (initial_visit['diabetes'] == 'True') |
                               (initial_visit['ckd_diagnosis'] == 'Yes'))
initial_visit['bp_controlled_high_risk'] = ((initial_visit['sbp_followup'] < 130) & initial_visit['high_risk'])
# Combine all criteria to check if blood pressure is controlled
initial_visit['blood_pressure_controlled'] = (initial_visit['bp_controlled_measurements'] |
                                               initial_visit['bp_controlled_cvd'] |
                                               initial_visit['bp_controlled_high_risk'])
# Calculate the percentage of controlled blood pressure per district
district_percentage = initial_visit.groupby('district')['blood_pressure_controlled'].mean() * 100
district_percentage.to_csv("htn_bp_controll_all_criteria_by_district.csv",index=True)
# Calculate the percentage of controlled blood pressure per facility
facility_percentage = initial_visit.groupby('facility')['blood_pressure_controlled'].mean() * 100
facility_percentage.to_csv("htn_bp_controll_all_criteria_by_facility.csv",index=True)
# Calculate the percentage of controlled blood pressure per facility and sex
facility_sex_percentage = initial_visit.groupby(['district', 'facility', 'gender'])['blood_pressure_controlled']\
    .mean().reset_index().pivot(index=['district', 'facility'], columns='gender', values='blood_pressure_controlled')
facility_sex_percentage.to_csv("htn_bp_controll_all_criteria_by_sex_facility_level.csv",index=True)
# Calculate the percentage of controlled blood pressure per facility and high-risk status
facility_risk_percentage = initial_visit.groupby(['district', 'facility', 'cvd_high_risk'])['blood_pressure_controlled']\
    .mean().reset_index().pivot(index=['district', 'facility'], columns='cvd_high_risk', values='blood_pressure_controlled')
facility_risk_percentage.to_csv("htn_bp_controll_all_criteria_by_facility_risk_level.csv",index=True)
# Display or save the results as needed
print("Percentage of controlled blood pressure per district:")
print(district_percentage)
print("\nPercentage of controlled blood pressure per facility:")
print(facility_percentage)
print("\nPercentage of controlled blood pressure per facility and sex:")
print(facility_sex_percentage)
print("\nPercentage of controlled blood pressure per facility and high-risk status:")
print(facility_risk_percentage)
