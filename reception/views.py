from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Patient, MedicalEvaluation
from .forms import PatientIntakeForm, MedicalEvaluationForm, PersonalQuestionnaireForm

@login_required
def dashboard(request):
    context = {
        'under_review_count': Patient.objects.filter(status='UNDER_MEDICAL_REVIEW').count(),
        'accepted_count': Patient.objects.filter(status='ACCEPTED').count(),
        'rejected_count': Patient.objects.filter(status='REJECTED').count(),
        'suspended_count': Patient.objects.filter(status='SUSPENDED').count(),
        'completed_count': Patient.objects.filter(status='QUESTIONNAIRE_COMPLETED').count(),
    }
    return render(request, 'reception/dashboard.html', context)

@login_required
def intake_create(request):
    if request.method == 'POST':
        form = PatientIntakeForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.status = 'UNDER_MEDICAL_REVIEW'
            patient.save()
            messages.success(request, f'تم حفظ بيانات الاستقبال برقم التتبع: {patient.tracking_number} وتحويل الملف إلى التقييم الطبي.')
            return redirect('reception:medical_queue')
    else:
        form = PatientIntakeForm()
    return render(request, 'reception/intake_form.html', {'form': form})

@login_required
def medical_queue(request):
    patients = Patient.objects.filter(status='UNDER_MEDICAL_REVIEW')
    return render(request, 'reception/medical_queue.html', {'patients': patients})

@login_required
def medical_evaluation_create(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    try:
        evaluation = patient.medical_evaluation
    except MedicalEvaluation.DoesNotExist:
        evaluation = None

    if request.method == 'POST':
        form = MedicalEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            medical_evaluation = form.save(commit=False)
            medical_evaluation.patient = patient
            # إسناد الطبيب تلقائياً للمستخدم مسجل الدخول
            medical_evaluation.doctor = request.user 
            selected_doctors = form.cleaned_data.get('committee_doctors')
            if selected_doctors:
                medical_evaluation.committee_members = '، '.join(str(doctor) for doctor in selected_doctors)
            medical_evaluation.save()
            form.save_m2m()
            
            messages.success(request, f'تم حفظ قرار اللجنة الطبية للملف رقم {patient.tracking_number}.')
            if medical_evaluation.decision == 'ACCEPTED':
                return redirect('reception:questionnaire_create', patient_id=patient.id)
            if medical_evaluation.decision == 'REJECTED':
                return redirect('reception:rejected_list')
            if medical_evaluation.decision == 'SUSPENDED':
                return redirect('reception:suspended_list')
    else:
        form = MedicalEvaluationForm(instance=evaluation)
        
    return render(request, 'reception/medical_evaluation_form.html', {'form': form, 'patient': patient})

@login_required
def questionnaire_create(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    try:
        questionnaire = patient.questionnaire
    except Exception:
        questionnaire = None

    if request.method == 'POST':
        form = PersonalQuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            questionnaire_obj = form.save(commit=False)
            questionnaire_obj.patient = patient
            questionnaire_obj.save()
            messages.success(request, 'تم حفظ استمارة البيانات الشخصية بنجاح.')
            return redirect('reception:accepted_list')
    else:
        initial_data = {
            'full_name_confirmation': f'{patient.first_name} {patient.last_name}',
            'military_number_confirmation': patient.military_number,
        }
        form = PersonalQuestionnaireForm(instance=questionnaire, initial=initial_data)
        
    return render(request, 'reception/questionnaire_form.html', {'form': form, 'patient': patient})

@login_required
def accepted_list(request):
    patients = Patient.objects.filter(status__in=['ACCEPTED', 'QUESTIONNAIRE_COMPLETED'])
    return render(request, 'reception/accepted_list.html', {'patients': patients})

@login_required
def rejected_list(request):
    patients = Patient.objects.filter(status='REJECTED')
    return render(request, 'reception/rejected_list.html', {'patients': patients})

@login_required
def suspended_list(request):
    patients = Patient.objects.filter(status='SUSPENDED')
    return render(request, 'reception/suspended_list.html', {'patients': patients})

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'reception/patient_detail.html', {'patient': patient})

@login_required
def patient_print_report(request, patient_id):
    patient = get_object_or_404(
        Patient.objects.select_related('medical_evaluation__doctor').prefetch_related('medical_evaluation__committee_doctors'),
        id=patient_id,
        status__in=['ACCEPTED', 'QUESTIONNAIRE_COMPLETED'],
    )
    return render(request, 'reception/patient_print_report.html', {'patient': patient})
