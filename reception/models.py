from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator


phone_validator = RegexValidator(
    regex=r'^09\d{8}$',
    message='يجب أن يبدأ رقم الهاتف بـ 09 وأن يتكون من 10 أرقام فقط.',
)

document_image_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
    message='يسمح برفع صور فقط بصيغ: jpg, jpeg, png, webp.',
)

class Patient(models.Model):
    STATUS_CHOICES = [
        ('UNDER_MEDICAL_REVIEW', 'قيد التقييم الطبي'),
        ('ACCEPTED', 'مقبول'),
        ('REJECTED', 'مرفوض'),
        ('SUSPENDED', 'معلّق'),
        ('QUESTIONNAIRE_COMPLETED', 'تمت تعبئة الاستمارة'),
    ]
    SOCIAL_STATUS_CHOICES = [('single', 'أعزب'), ('married', 'متزوج'), ('divorced', 'مطلق')]

    tracking_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='رقم التتبع التسلسلي')
    
    first_name = models.CharField(max_length=100, verbose_name='الاسم')
    last_name = models.CharField(max_length=100, verbose_name='الكنية')
    father_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم الأب')
    mother_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم الأم')
    national_id = models.CharField(max_length=50, unique=True, verbose_name='الرقم الذاتي')
    military_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='الرقم العسكري')
    rank = models.CharField(max_length=100, blank=True, null=True, verbose_name='الرتبة')
    military_unit = models.CharField(max_length=150, blank=True, null=True, verbose_name='الوحدة العسكرية')
    date_of_birth = models.DateField(verbose_name='تاريخ الميلاد')
    place_of_birth = models.CharField(max_length=150, blank=True, null=True, verbose_name='مكان الولادة')
    social_status = models.CharField(max_length=20, choices=SOCIAL_STATUS_CHOICES, verbose_name='الوضع الاجتماعي')
    children_count = models.PositiveIntegerField(default=0, verbose_name='عدد الأطفال')
    phone = models.CharField(max_length=10, blank=True, null=True, validators=[phone_validator], verbose_name='رقم الهاتف')
    address = models.TextField(blank=True, null=True, verbose_name='العنوان الحالي')
    health_condition = models.TextField(verbose_name='الحالة الصحية عند الاستقبال')
    previous_details = models.TextField(blank=True, null=True, verbose_name='التفاصيل السابقة')
    injury_date = models.DateField(blank=True, null=True, verbose_name='تاريخ الإصابة')
    injury_place = models.CharField(max_length=200, blank=True, null=True, verbose_name='مكان الإصابة')
    injury_type = models.CharField(max_length=200, blank=True, null=True, verbose_name='نوع الإصابة')
    has_identity_card = models.BooleanField(default=False, verbose_name='يوجد بطاقة شخصية')
    identity_card_image = models.FileField(upload_to='patient_documents/identity_cards/', blank=True, null=True, validators=[document_image_validator], verbose_name='صورة البطاقة الشخصية')
    has_military_card = models.BooleanField(default=False, verbose_name='يوجد بطاقة عسكرية')
    military_card_image = models.FileField(upload_to='patient_documents/military_cards/', blank=True, null=True, validators=[document_image_validator], verbose_name='صورة البطاقة العسكرية')
    has_medical_report = models.BooleanField(default=False, verbose_name='يوجد تقرير طبي')
    medical_report_image = models.FileField(upload_to='patient_documents/medical_reports/', blank=True, null=True, validators=[document_image_validator], verbose_name='صورة التقرير الطبي')
    has_injury_document = models.BooleanField(default=False, verbose_name='يوجد وثيقة إصابة')
    injury_document_image = models.FileField(upload_to='patient_documents/injury_documents/', blank=True, null=True, validators=[document_image_validator], verbose_name='صورة وثيقة الإصابة')
    has_photos = models.BooleanField(default=False, verbose_name='يوجد صور شخصية')
    other_documents = models.TextField(blank=True, null=True, verbose_name='وثائق أخرى')
    companion_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='اسم المرافق')
    companion_phone = models.CharField(max_length=10, blank=True, null=True, validators=[phone_validator], verbose_name='هاتف المرافق')
    emergency_contact = models.CharField(max_length=150, blank=True, null=True, verbose_name='شخص للتواصل عند الضرورة')
    reception_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات موظف الاستقبال')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='UNDER_MEDICAL_REVIEW', verbose_name='حالة الملف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإدخال')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تعديل')

    class Meta:
        verbose_name = 'مصاب'
        verbose_name_plural = 'المصابون'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.tracking_number:
            # توليد رقم تسلسلي معتمد على المعرف الفريد لقاعدة البيانات (مستحيل التكرار)
            self.tracking_number = f"INJ-{self.pk:06d}"
            super().save(update_fields=['tracking_number'])

    def __str__(self):
        return f'{self.tracking_number} - {self.first_name} {self.last_name}'


class CommitteeDoctor(models.Model):
    full_name = models.CharField(max_length=150, unique=True, verbose_name='اسم الطبيب')
    specialty = models.CharField(max_length=150, blank=True, null=True, verbose_name='الاختصاص')
    is_active = models.BooleanField(default=True, verbose_name='فعّال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')

    class Meta:
        verbose_name = 'طبيب لجنة'
        verbose_name_plural = 'أطباء اللجنة'
        ordering = ['full_name']

    def __str__(self):
        if self.specialty:
            return f'{self.full_name} - {self.specialty}'
        return self.full_name


class MedicalEvaluation(models.Model):
    DECISION_CHOICES = [('ACCEPTED', 'قبول'), ('REJECTED', 'رفض'), ('SUSPENDED', 'تعليق')]
    INJURY_DEGREE_CHOICES = [(str(i), f'{i}%') for i in range(1, 19)]
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='medical_evaluation', verbose_name='المصاب')
    doctor = models.ForeignKey(User, on_delete=models.PROTECT,null=True, blank=True, verbose_name='الطبيب المسؤول')
    committee_doctors = models.ManyToManyField(CommitteeDoctor, blank=True, verbose_name='الأطباء الحاضرون والمعتمدون')
    committee_members = models.TextField(blank=True, null=True, verbose_name='أسماء الأطباء الحاضرين والمعتمدين')
    diagnosis = models.TextField(verbose_name='التشخيص الطبي')
    injury_degree = models.CharField(max_length=3, choices=INJURY_DEGREE_CHOICES, verbose_name='درجة الإصابة')
    medical_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات طبية')
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, verbose_name='قرار اللجنة')
    decision_reason = models.TextField(blank=True, null=True, verbose_name='سبب القرار')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التقييم')

    class Meta:
        verbose_name = 'تقييم طبي'
        verbose_name_plural = 'التقييمات الطبية'
        ordering = ['-created_at']

    def clean(self):
        if self.decision == 'REJECTED' and not (self.decision_reason or '').strip():
            raise ValidationError({'decision_reason': 'سبب رفض الإحالة مطلوب عند اختيار قرار الرفض.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.patient.status = self.decision
        self.patient.save()

    def decision_report(self):
        reason = self.decision_reason or 'غير محدد'
        return (f'تقرر {self.get_decision_display()} إصابة الأخ {self.patient.first_name} {self.patient.last_name}، '
                f'صاحب الرقم الذاتي {self.patient.national_id}، للأسباب: {reason}')

    def __str__(self):
        return f'تقييم {self.patient.tracking_number}'


class PersonalQuestionnaire(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='questionnaire', verbose_name='المصاب')
    full_name_confirmation = models.CharField(max_length=200, verbose_name='تأكيد الاسم الكامل')
    military_number_confirmation = models.CharField(max_length=100, verbose_name='تأكيد الرقم العسكري')
    current_residence = models.CharField(max_length=200, verbose_name='مكان الإقامة الحالي')
    original_residence = models.CharField(max_length=200, verbose_name='مكان الإقامة الأصلي')
    education_level = models.CharField(max_length=150, verbose_name='المستوى التعليمي')
    previous_job = models.CharField(max_length=150, blank=True, null=True, verbose_name='المهنة قبل الإصابة')
    marital_details = models.TextField(blank=True, null=True, verbose_name='تفاصيل الوضع العائلي')
    number_of_children = models.PositiveIntegerField(default=0, verbose_name='عدد الأولاد')
    service_start_date = models.DateField(blank=True, null=True, verbose_name='تاريخ بدء الخدمة')
    last_military_unit = models.CharField(max_length=200, blank=True, null=True, verbose_name='آخر وحدة خدم بها')
    participated_battles = models.TextField(verbose_name='المعارك أو المهام التي شارك بها')
    most_important_battle = models.CharField(max_length=200, blank=True, null=True, verbose_name='أهم معركة أو مهمة شارك بها')
    injury_circumstances = models.TextField(verbose_name='ظروف حدوث الإصابة')
    previous_injuries = models.TextField(blank=True, null=True, verbose_name='إصابات سابقة إن وجدت')
    surgeries = models.TextField(blank=True, null=True, verbose_name='عمليات جراحية سابقة')
    chronic_diseases = models.TextField(blank=True, null=True, verbose_name='أمراض مزمنة')
    current_medications = models.TextField(blank=True, null=True, verbose_name='الأدوية الحالية')
    disability_level = models.CharField(max_length=150, blank=True, null=True, verbose_name='درجة العجز أو الإعاقة')
    psychological_condition = models.TextField(blank=True, null=True, verbose_name='الحالة النفسية الحالية')
    rehabilitation_need = models.TextField(blank=True, null=True, verbose_name='الحاجة إلى علاج أو تأهيل')
    housing_status = models.CharField(max_length=200, blank=True, null=True, verbose_name='وضع السكن')
    family_support = models.TextField(blank=True, null=True, verbose_name='الدعم العائلي المتوفر')
    financial_condition = models.CharField(max_length=200, blank=True, null=True, verbose_name='الوضع المادي')
    requested_support = models.TextField(blank=True, null=True, verbose_name='نوع الدعم المطلوب')
    additional_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات إضافية')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ تعبئة الاستمارة')

    class Meta:
        verbose_name = 'استمارة بيانات شخصية'
        verbose_name_plural = 'استمارات البيانات الشخصية'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.patient.status = 'QUESTIONNAIRE_COMPLETED'
        self.patient.save()
