from .models import *
import pandas as pd
from datetime import datetime

#data importer
class DataImporter:
    def __init__(self,filePath):
        self.filePath=filePath

    def convert_to_bool(self,value):
        return True if str(value).lower() == 'yes' else False

    def import_facilities(self):
        try:
            df = pd.read_csv(self.filePath)
            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                month = datetime.strptime(row['month'], '%Y-%m')
                facility, created = Facilities.objects.update_or_create(
                    facility_id=row['facility_id'],
                    month=month,
                    defaults={
                        'county': row['country'],
                        'province': row['province'],
                        'district': row['district'],
                        'facility_name': row['facility'],
                        'metformin': self.convert_to_bool(row['metformin']),
                        'sulfonylurea': self.convert_to_bool(row['sulfonylurea']),
                        'insulin': self.convert_to_bool(row['insulin']),
                        'statin': self.convert_to_bool(row['statin'])
                    }
                )
            return f"{len(df)} records uploaded!"
        except Exception as e:
               print(e)

    def import_patients(self):
        try:
            df = pd.read_csv(self.filePath)
            for index, row in df.iterrows():
                facility_id = row['facility_id']
                facility = Facilities.objects.filter(facility_id=facility_id).first()
                patient,created= Patients.objects.get_or_create(
                    patient_id=row['patient_id'],
                    defaults={
                    "facility":facility,
                    "gender":row['gender'],
                    "birthdate":datetime.strptime(row['birthdate'], '%Y-%m-%d'),
                    }
                )
            return f"{len(df)} records uploaded!"
        except Exception as e:
            print(e)

    def import_htn_visits_initial(self):
        try:
            df = pd.read_csv(self.filePath)
            for index, row in df.iterrows():
                patient_id = row['patient_id']
                patient = Patients.objects.get(patient_id=patient_id)
                visit,created= HtnVisits.objects.get_or_create(
                    patient=patient,
                    defaults={
                    "visit_date":datetime.strptime(row['visit_date'], '%Y-%m-%d'),
                    "ckd_diagnosis":False,
                    "cvd_diagnosis":False,
                    "cvd_high_risk":False, 
                    "diabetes":False,
                    "sbp":row['sbp'],
                    "dbp":row['dbp'],
                    "visit_type":'initial',
                    }
                )
            return f"{len(df)} records uploaded!"
        except Exception as e:
            print(e)
                
    def import_htn_visits_followup(self):
        try:
            df = pd.read_csv(self.filePath)
            for index, row in df.iterrows():
                patient_id = row['patient_id']
                patient = Patients.objects.get(patient_id=patient_id)
                visit,created= HtnVisits.objects.get_or_create(
                patient=patient,
                visit_type="followup",
                visit_date=datetime.strptime(row['visit_date'], '%Y-%m-%d'),
                defaults={
                "ckd_diagnosis":self.convert_to_bool(row['ckd_diagnosis']),  
                "cvd_diagnosis":self.convert_to_bool(row['cvd_diagnosis']),  
                "cvd_high_risk":self.convert_to_bool(row['cvd_high_risk']),  
                "diabetes":self.convert_to_bool(row['diabetes']),  
                "sbp":row['sbp'],
                "dbp":row['dbp'],
                }
                )
                print(f"Follow Up for {visit.visit_date} updated.")
            return f"{len(df)} records uploaded!"
        except Exception as e:
            print(e)