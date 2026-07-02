from django.contrib import admin
from .models import CommitteeDoctor, Patient, MedicalEvaluation, PersonalQuestionnaire

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'first_name', 'last_name', 'national_id', 'status', 'created_at')
    search_fields = ('tracking_number', 'national_id', 'military_number', 'first_name', 'last_name')
    list_filter = ('status', 'created_at')
    readonly_fields = ('tracking_number',)

@admin.register(MedicalEvaluation)
class MedicalEvaluationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'decision', 'created_at')
    list_filter = ('decision', 'created_at')
    search_fields = ('patient__tracking_number', 'doctor__username', 'committee_doctors__full_name')
    filter_horizontal = ('committee_doctors',)

@admin.register(PersonalQuestionnaire)
class PersonalQuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('patient', 'current_residence', 'created_at')
    search_fields = ('patient__tracking_number',)

@admin.register(CommitteeDoctor)
class CommitteeDoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'is_active', 'created_at')
    list_filter = ('is_active', 'specialty')
    search_fields = ('full_name', 'specialty')
