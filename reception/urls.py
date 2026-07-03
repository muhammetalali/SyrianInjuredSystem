from django.urls import path
from . import views

app_name = 'reception'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('intake/', views.intake_create, name='intake_create'),
    path('medical/queue/', views.medical_queue, name='medical_queue'),
    path('medical/evaluation/<int:patient_id>/', views.medical_evaluation_create, name='medical_evaluation_create'),
    path('questionnaire/<int:patient_id>/', views.questionnaire_create, name='questionnaire_create'),
    path('accepted/', views.accepted_list, name='accepted_list'),
    path('rejected/', views.rejected_list, name='rejected_list'),
    path('suspended/', views.suspended_list, name='suspended_list'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # مسار زر الطباعة الجديد
    path('patient/<int:patient_id>/print/', views.patient_print_report, name='patient_print_report'),
]