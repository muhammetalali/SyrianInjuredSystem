from django import forms
from .models import CommitteeDoctor, Patient, MedicalEvaluation, PersonalQuestionnaire

class PatientIntakeForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['status', 'created_at', 'updated_at', 'tracking_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'injury_date': forms.DateInput(attrs={'type': 'date'}),
            'children_count': forms.NumberInput(attrs={'min': 0}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'health_condition': forms.Textarea(attrs={'rows': 3}),
            'previous_details': forms.Textarea(attrs={'rows': 3}),
            'other_documents': forms.Textarea(attrs={'rows': 3}),
            'reception_notes': forms.Textarea(attrs={'rows': 3}),
            'identity_card_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'military_card_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'medical_report_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'injury_document_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'children_count':
                field.required = False
            if name in ['phone', 'companion_phone']:
                field.widget.attrs.update({
                    'pattern': r'09[0-9]{8}',
                    'maxlength': '10',
                    'placeholder': '09XXXXXXXX',
                })
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('social_status') != 'married':
            cleaned_data['children_count'] = 0
        return cleaned_data

class MedicalEvaluationForm(forms.ModelForm):
    committee_doctors = forms.ModelMultipleChoiceField(
        queryset=CommitteeDoctor.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='الأطباء الحاضرون والمعتمدون',
        error_messages={'required': 'يجب اختيار طبيب واحد على الأقل من أطباء اللجنة.'},
    )

    class Meta:
        model = MedicalEvaluation
        # استبعاد الطبيب لأننا سنسنده برمجياً للمستخدم الحالي
        exclude = ['patient', 'doctor', 'committee_members', 'created_at']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 4}),
            'medical_notes': forms.Textarea(attrs={'rows': 3}),
            'decision_reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['committee_doctors'].queryset = CommitteeDoctor.objects.filter(is_active=True)
        self.fields['decision_reason'].required = False
        self.fields['decision_reason'].label = 'سبب القرار / سبب رفض الإحالة'
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'checkbox-list'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        decision_reason = cleaned_data.get('decision_reason')

        if decision == 'REJECTED' and not (decision_reason or '').strip():
            self.add_error('decision_reason', 'سبب رفض الإحالة مطلوب عند اختيار قرار الرفض.')
        elif decision != 'REJECTED':
            cleaned_data['decision_reason'] = ''

        return cleaned_data

class PersonalQuestionnaireForm(forms.ModelForm):
    class Meta:
        model = PersonalQuestionnaire
        exclude = ['patient', 'created_at']
        widgets = {
            'service_start_date': forms.DateInput(attrs={'type': 'date'}),
            'marital_details': forms.Textarea(attrs={'rows': 3}),
            'participated_battles': forms.Textarea(attrs={'rows': 4}),
            'injury_circumstances': forms.Textarea(attrs={'rows': 4}),
            'previous_injuries': forms.Textarea(attrs={'rows': 3}),
            'surgeries': forms.Textarea(attrs={'rows': 3}),
            'chronic_diseases': forms.Textarea(attrs={'rows': 3}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
            'psychological_condition': forms.Textarea(attrs={'rows': 3}),
            'rehabilitation_need': forms.Textarea(attrs={'rows': 3}),
            'family_support': forms.Textarea(attrs={'rows': 3}),
            'requested_support': forms.Textarea(attrs={'rows': 3}),
            'additional_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
