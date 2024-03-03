from django.contrib import admin
from .models import Facilities, Patients, HtnVisits,HTNIndicators

class FacilitiesAdmin(admin.ModelAdmin):
    list_display = ('id','county', 'province', 'district', 'facility_name', 'facility_id', 'month', 'metformin', 'sulfonylurea', 'insulin', 'statin')
    list_filter = ('county', 'province', 'district', 'facility_name', 'facility_id', 'month', 'metformin', 'sulfonylurea', 'insulin', 'statin')
    search_fields = ('county', 'province', 'district', 'facility_name', 'facility_id', 'month', 'metformin', 'sulfonylurea', 'insulin', 'statin')

class PatientsAdmin(admin.ModelAdmin):
    list_display = ('id','facility', 'patient_id', 'gender', 'birthdate')
    list_filter = ('facility', 'gender')
    search_fields = ('patient_id',)

class HtnVisitsAdmin(admin.ModelAdmin):
    list_display = ('visit_date', 'patient', 'sbp', 'dbp','ckd_diagnosis','cvd_diagnosis','cvd_high_risk','diabetes','visit_type')
    list_filter = ('visit_date','ckd_diagnosis','cvd_diagnosis','cvd_high_risk','diabetes','visit_type')
    search_fields = ('patient__patient_id','visit_date', 'patient', 'sbp', 'dbp','ckd_diagnosis','cvd_diagnosis','cvd_high_risk','diabetes','visit_type')

class HTNIndicatorsAdmin(admin.ModelAdmin):
    list_display = ('facility','indicator_name','high_risk','value','visit_date')
    list_filter = ('facility','patient__gender','indicator_name','value','high_risk')
    search_fields = ('indicator_name','high_risk','visit_date')
    readonly_fields = ('visit_date',)

admin.site.register(HTNIndicators, HTNIndicatorsAdmin)

admin.site.register(Facilities, FacilitiesAdmin)
admin.site.register(Patients, PatientsAdmin)
admin.site.register(HtnVisits, HtnVisitsAdmin)
