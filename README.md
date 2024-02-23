# Facility-based Patient & Programme Monitoring
The objectives of this evaluation are to calculate the specified facility-based patient and programme monitoring indicators and create an online dashboard to present these indicators to non-technical stakeholders.

## Components
### Data Analysis
In the `materials` folder, you are provided with four CSV files containing data elements related to healthcare facilities and patients. In addition, the definition and related metadata for calculating the indicators are provided as a PDF file. The first task is to calculate following indicators:

1. Blood pressure control among people with hypertension (Hypertension and cardiovascular diseases C4)
2. Availability of diabetes core medicines (Diabetes C1)

The indicators should be calculated with the reporting date of 2022-12-31.

### Dashboard Creation
The second task is to create an online dashboard (using Django) to present the calculated indicators. Please ensure that the dashboard is user-friendly and provides meaningful insights into the facility-based patient and program monitoring indicators.

## Data Description
- The “facilities.csv” file contains 360 records for 30 facilities on the monthly availability of Metformin, Sulfonylurea, Insulin, and Statin in 2022.
- The “patients.csv” file is a reference table of all the registered patients. This file contains 47,759 rows on gender, birthdate, and the registered facility of patients.
- The “htn_initial_visits.csv” file contains hypertension data elements of hypertensive patients at their initial visits and has 18,062 records. This file includes the initial visit date, patient ID, systolic blood pressure, and diastolic blood pressure.
- The “htn_follow_up_visits.csv” file includes data elements of hypertensive patients at their follow-up visits and has 7,908  records. This file contains follow-up visit date, patient ID, systolic blood pressure, diastolic blood pressure, and whether a patient was diagnosed with diabetes mellitus, chronic kidney disease (CKD), and cardiovascular diseases (CVD). This file also includes a column named “cvd_high_risk” which indicates high CVD risk patients.

## Submission Requirements
1. Create a PR with your name as a branch that contains all necessary files required to calculate the indicators and to run the dashboard.
2. Host the online dashboard on a platform of your choice and provide a link to access it.

## Evaluation Criteria
Submissions will be evaluated based on the following criteria:
- Accuracy and correctness of the calculated indicators
- Effectiveness and meaningfulness of the dashboard in presenting the indicators


