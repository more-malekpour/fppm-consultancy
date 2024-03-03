from rest_framework import viewsets
from .serializers import *
from rest_framework.renderers import *
from rest_framework.response import Response
from rest_framework.permissions import *
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils import DataImporter
import time
from datetime import datetime,timedelta
from django.db.models import Q,Count,Sum, F, ExpressionWrapper, Value, FloatField,IntegerField,When,Case
from .models import *

class UploadData(APIView):
    permission_classes=[]#[IsAuthenticated]
    authentication_classes=()

    @csrf_exempt
    def post(self, request, format=None):
        # Check if the request contains a file
        fileType=request.data['fileType']
        #print(fileType)
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        file_obj = request.FILES['file']
        # Save the uploaded file
        file_name = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
        # Call the import_employee_data function
        try:
            path=default_storage.path(file_name)
            res=None
            if fileType =='facilities':
               res = DataImporter(path).import_facilities()
            if fileType =='patients':
               res = DataImporter(path).import_patients()
            if fileType =='htn_visits_initial':
               res = DataImporter(path).import_htn_visits_initial()
            if fileType == 'htn_visits_followup':
                res = DataImporter(path).import_htn_visits_followup()
            return Response({'message': res}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#upload files via form
def data_index(request):
    return render(request, 'core/data_index.html')

def home(request):
    return render(request, 'dashboard/index.html')

class FacilityFilterOptions(APIView):
    def get(self, request):
        # Query facilities along with their province, district, and county data
        facilities = Facilities.objects.values('facility_id', 'facility_name', 'province', 'district', 'county').order_by('facility_id').distinct()

        # Extract unique province, district, and county values
        provinces = set()
        districts = set()
        counties = set()
        for facility in facilities:
            provinces.add(facility['province'])
            districts.add(facility['district'])
            counties.add(facility['county'])

        # Convert sets to lists for JSON serialization
        provinces_list = list(provinces)
        districts_list = list(districts)
        counties_list = list(counties)

        # Prepare response data
        response_data = {
            'facilities': facilities.values('facility_id','facility_name'),
            'provinces': provinces_list,
            'districts': districts_list,
            'counties': counties_list
        }

        return Response(response_data)
    
class RunIndicatorAnalytics(APIView):
    authentication_classes=()
    permission_classes=()

    def post(self, request,*args,**kwargs):
        try:
            # Define date range for reporting period
            query_params = request.query_params
            start_date=query_params.get("from_date",datetime(2022, 1, 1))
            end_date = query_params.get("to_date",datetime(2022, 12, 31))
            reporting_period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            #print(reporting_period)
            three_months_ago = end_date-timedelta(days=90)

            #Get facilities
            facilities=Facilities.objects.filter(month__range=[start_date,end_date]).exclude(month__gt=three_months_ago)
            #create c1 indicator records
            for facility in facilities:
                indicator,created=HTNIndicators.objects.get_or_create(
                    facility=facility,
                    indicator_name='DIABETES_MED_AVAILABILITY',
                    patient = None,
                    value=facility.get_medicine_percentage(),
                    high_risk=False,
                    visit_date=facility.month,
                )
            # Query initial visits with necessary related fields
            initial_visits = HtnVisits.objects.filter(visit_date__range=[start_date,end_date]).exclude(visit_date__gte=three_months_ago).select_related('patient__facility')

            # Annotate blood pressure control criteria
            initial_visits = initial_visits.annotate(
                bp_controlled_measurements=Case(
                    When(sbp__lt=140, dbp__lt=90, then=Value(1)),
                    default=Value(0),
                    output_field=FloatField()
                ),
                bp_controlled_cvd=Case(
                    When(sbp__lt=130, cvd_diagnosis=True, then=Value(1)),
                    default=Value(0),
                    output_field=FloatField()
                ),
                bp_controlled_high_risk=Case(
                    When(sbp__lt=130, then=Value(1),
                        condition=Q(cvd_high_risk=True) | Q(diabetes=True) | Q(ckd_diagnosis=True)),
                    default=Value(0),
                    output_field=FloatField()
                ),
            )
            # Compute blood pressure control
            initial_visits = initial_visits.annotate(
                bp_controlled_proportion=ExpressionWrapper(
                    (F('bp_controlled_measurements') + F('bp_controlled_cvd') + F('bp_controlled_high_risk')),
                    output_field=FloatField()
                )
            ).values('visit_date','patient__facility','patient','cvd_high_risk','bp_controlled_proportion')

            # Create or update HTNIndicators objects
            for entry in initial_visits:
                facility_id = entry['patient__facility']
                patient=Patients.objects.get(id=entry['patient'])
                facility = Facilities.objects.get(id=facility_id)
                indicator, created = HTNIndicators.objects.get_or_create(
                    facility=facility,
                    indicator_name='BP_CONTROL',
                    patient = patient,
                    value=entry['bp_controlled_proportion'],
                    high_risk=entry['cvd_high_risk'],
                    visit_date=entry['visit_date']
                )            
            return Response({"detail":"Data analytics completed successfully!"})
        except Exception as e:
             print(e)
             return Response({"detail":str(e)})

class BPControlAnalytics(APIView):
    def get(self, request):
        # Retrieve filter parameters from request
        facility_id = request.query_params.get('facility_id')
        county = request.query_params.get('county')
        province = request.query_params.get('province')
        district = request.query_params.get('district')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by')

        # Query HTNIndicators to get relevant data
        indicators = HTNIndicators.objects.all()
        # Apply filters if provided
        if facility_id:
            indicators = indicators.filter(facility__facility_id=facility_id)
        elif district:
            indicators = indicators.filter(facility__district=district)
        elif county:
            indicators = indicators.filter(facility__county=county)
        elif province:
            indicators = indicators.filter(facility__province=province)

        if start_date and end_date:
            indicators = indicators.filter(visit_date__range=[start_date, end_date])
        #get total facilities
        total_facilities = Count('facility')
        core_medicines_available = Sum('value')
        # Define annotation for controlled patients
        controlled_annotation = Sum(Case(When(value__gte=1, then=1), default=0, output_field=models.IntegerField()))

        # Define grouping criteria based on filters
        bp_control_data=indicators.filter(indicator_name='BP_CONTROL').exclude(patient__gender='').exclude(patient__gender=None)
        diabetes_med_data = indicators.filter(indicator_name='DIABETES_MED_AVAILABILITY')
        #print(diabetes_med_data)
        if group_by == 'risk_level':
            # Group by risk level and facility
            bp_control_data = bp_control_data.values('high_risk', 'facility__facility_name') \
                .annotate(total_patients=Count('patient'),
                          controlled_patients=controlled_annotation) \
                .order_by('high_risk', 'facility__facility_name')
        elif facility_id or district or county or province:
            # Group by gender and facility
            bp_control_data = bp_control_data.values('patient__gender', 'facility__facility_name') \
                .annotate(total_patients=Count('patient'),
                          controlled_patients=controlled_annotation) \
                .order_by('patient__gender', 'facility__facility_name')
        else:
            # Default to group by gender and facility
            bp_control_data = bp_control_data.values('patient__gender', 'facility__facility_name') \
                .annotate(total_patients=Count('patient'),
                          controlled_patients=controlled_annotation) \
                .order_by('patient__gender', 'facility__facility_name')

        # Prepare response data
        indicator_data = {}
        response_data={}
        for data in bp_control_data:
            gender_or_risk = data.get('patient__gender') if 'patient__gender' in data else data.get('high_risk')
            facility = data['facility__facility_name']
            total_patients = data['total_patients']
            controlled_patients = data['controlled_patients']
            percentage_controlled = round((controlled_patients / total_patients) * 100, 2) if total_patients > 0 else 0

            if gender_or_risk not in response_data:
                response_data[gender_or_risk] = {}
            response_data[gender_or_risk][facility] = percentage_controlled
        indicator_data['bp_control']=response_data

        #get analytics for c1 indicator
        # Annotate data for diabetes core medicines availability indicator
        diabetes_med_data = diabetes_med_data.values(
            'facility__facility_name'
        ).annotate(
            total_facilities=total_facilities,
            core_medicines_available=core_medicines_available
        )
        # Format response data for diabetes core medicines availability indicator
        meds_data={}
        for data in diabetes_med_data:
            #print(data)
            facility = data['facility__facility_name']
            total_facilities = data['total_facilities']
            core_medicines_available = data['core_medicines_available']
            percentage_available = round((core_medicines_available / (total_facilities*100)) * 100, 2) if total_facilities > 0 else 0
            meds_data[facility]=percentage_available
        indicator_data['bp_meds']=meds_data
        # Return the result as JSON response
        return Response(indicator_data)

class AnalyticsOverview(APIView):
    def get(self, request):
        # Retrieve filter parameters from request
        facility_id = request.query_params.get('facility_id')
        county = request.query_params.get('county')
        province = request.query_params.get('province')
        district = request.query_params.get('district')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Apply filters to querysets
        patients_qs = Patients.objects.all()
        facilities_qs = Facilities.objects.all().order_by('facility_id').distinct()
        initial_visits_qs = HtnVisits.objects.filter(visit_type='initial')
        followup_visits_qs = HtnVisits.objects.filter(visit_type='followup')

        if facility_id:
            patients_qs = patients_qs.filter(facility__facility_id=facility_id)
            facilities_qs = facilities_qs.filter(facility_id=facility_id)
            initial_visits_qs = initial_visits_qs.filter(patient__facility__facility_id=facility_id)
            followup_visits_qs = followup_visits_qs.filter(patient__facility__facility_id=facility_id)
        elif district:
            patients_qs = patients_qs.filter(facility__district=district)
            facilities_qs = facilities_qs.filter(district=district)
            initial_visits_qs = initial_visits_qs.filter(patient__facility__district=district)
            followup_visits_qs = followup_visits_qs.filter(patient__facility__district=district)
        elif county:
            patients_qs = patients_qs.filter(facility__county=county)
            facilities_qs = facilities_qs.filter(county=county)
            initial_visits_qs = initial_visits_qs.filter(patient__facility__county=county)
            followup_visits_qs = followup_visits_qs.filter(patient__facility__county=county)
        elif province:
            patients_qs = patients_qs.filter(facility__province=province)
            facilities_qs = facilities_qs.filter(province=province)
            initial_visits_qs = initial_visits_qs.filter(patient__facility__province=province)
            followup_visits_qs = followup_visits_qs.filter(patient__facility__province=province)

        if start_date and end_date:
            initial_visits_qs = initial_visits_qs.filter(visit_date__range=(start_date, end_date))
            followup_visits_qs = followup_visits_qs.filter(visit_date__range=(start_date, end_date))

        # Get total number of patients, facilities, initial visits, and follow-up visits
        total_patients = patients_qs.count()
        total_facilities = facilities_qs.count()
        total_initial_visits = initial_visits_qs.count()
        total_followup_visits = followup_visits_qs.count()

        # Prepare response data
        response_data = {
            'total_patients': total_patients,
            'total_facilities': total_facilities,
            'total_initial_visits': total_initial_visits,
            'total_followup_visits': total_followup_visits,
        }

        # Return the result as JSON response
        return Response(response_data)
