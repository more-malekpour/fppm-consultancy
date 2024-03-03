from django.db import models
from datetime import datetime

# Create your models here.
class Patients(models.Model):
    facility=models.ForeignKey("Facilities",on_delete=models.SET_NULL,null=True,related_name="patients")
    patient_id=models.CharField(max_length=100)
    gender=models.CharField(max_length=20,choices=[("Male","Male"),("Female","Female")])
    birthdate=models.DateField()

    def __str__(self) -> str:
        return self.patient_id
        
    class Meta:
        verbose_name_plural="Patients"
        db_table="patients"
        managed=True
    
class Facilities(models.Model):
    county=models.CharField(max_length=100)
    province=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    facility_name=models.CharField(max_length=100)
    facility_id=models.CharField(max_length=100)
    month=models.DateField()
    metformin=models.BooleanField(default=True)	
    sulfonylurea=models.BooleanField(default=True)		
    insulin=models.BooleanField(default=True)	
    statin=models.BooleanField(default=True)

    def get_medicine_percentage(self):
        total_medicines = 4  # Total number of medicine types
        available_medicines = sum([self.metformin, self.sulfonylurea, self.insulin, self.statin])
        percentage = (available_medicines / total_medicines) * 100
        return percentage

    def __str__(self) -> str:
        return self.facility_name
        
    class Meta:
        db_table="facilities"
        verbose_name_plural="Facilities"
        managed=True	

class HtnVisits(models.Model):
    visit_date=models.DateField()
    patient=models.ForeignKey(Patients,on_delete=models.CASCADE,related_name="visits")
    ckd_diagnosis=models.BooleanField(default=True)
    cvd_diagnosis=models.BooleanField(default=True)
    cvd_high_risk=models.BooleanField(default=False)
    diabetes=models.BooleanField(default=True)
    sbp=models.DecimalField(max_digits=10,decimal_places=2)
    dbp=models.DecimalField(max_digits=10,decimal_places=2)
    visit_type=models.CharField(max_length=10,choices=[("initial","Initial Visit"),("followup","Follow Up Visit")])

    def __str__(self) -> str:
        return self.patient.patient_id
        
    class Meta:
        verbose_name_plural="HTN Visits"
        db_table="htn_visits"
        managed=True

class HTNIndicators(models.Model):
    INDICATOR_CHOICES = [
        ('BP_CONTROL', 'Blood pressure control among people with hypertension'),
        ('DIABETES_MED_AVAILABILITY', 'Availability of diabetes core medicines'),
    ]
    facility = models.ForeignKey(Facilities, on_delete=models.CASCADE,related_name='htn_indicators')
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE,related_name='htn_indicators',null=True)
    indicator_name = models.CharField(max_length=100,choices=INDICATOR_CHOICES)
    high_risk=models.BooleanField(default=None)
    value=models.IntegerField(default=0)
    visit_date = models.DateField(default=datetime.now())

    def __str__(self):
        return f"{self.indicator_name} - {self.facility} ({self.visit_date})"
    
    class Meta:
        verbose_name_plural="HTN Indicators"
        db_table="htn_indicators"
        managed=True
