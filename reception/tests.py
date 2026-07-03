from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .forms import MedicalEvaluationForm
from .models import phone_validator


class ValidationRulesTests(SimpleTestCase):
    def test_phone_must_start_with_09_and_have_10_digits(self):
        phone_validator('0912345678')

        with self.assertRaises(ValidationError):
            phone_validator('0812345678')

        with self.assertRaises(ValidationError):
            phone_validator('09123456789')

    def test_rejection_requires_decision_reason(self):
        form = MedicalEvaluationForm(data={
            'committee_members': 'committee',
            'diagnosis': 'diagnosis',
            'injury_degree': '5',
            'decision': 'REJECTED',
            'decision_reason': '',
        })
        form.fields['committee_doctors'].required = False

        self.assertFalse(form.is_valid())
        self.assertIn('decision_reason', form.errors)

    def test_acceptance_allows_empty_decision_reason(self):
        form = MedicalEvaluationForm(data={
            'committee_members': 'committee',
            'diagnosis': 'diagnosis',
            'injury_degree': '5',
            'decision': 'ACCEPTED',
            'decision_reason': '',
        })
        form.fields['committee_doctors'].required = False

        self.assertTrue(form.is_valid())
