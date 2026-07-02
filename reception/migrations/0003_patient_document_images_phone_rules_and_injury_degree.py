# Generated manually on 2026-07-02

import django.core.validators
from django.db import migrations, models


IMAGE_VALIDATOR = django.core.validators.FileExtensionValidator(
    allowed_extensions=["jpg", "jpeg", "png", "webp"],
    message="يسمح برفع صور فقط بصيغ: jpg, jpeg, png, webp.",
)

PHONE_VALIDATOR = django.core.validators.RegexValidator(
    regex="^09\\d{8}$",
    message="يجب أن يبدأ رقم الهاتف بـ 09 وأن يتكون من 10 أرقام فقط.",
)


def _existing_column_names(schema_editor, table_name):
    with schema_editor.connection.cursor() as cursor:
        columns = schema_editor.connection.introspection.get_table_description(cursor, table_name)
    return {column.name for column in columns}


def _build_file_field(name, upload_to, verbose_name):
    field = models.FileField(
        blank=True,
        null=True,
        upload_to=upload_to,
        validators=[IMAGE_VALIDATOR],
        verbose_name=verbose_name,
    )
    field.set_attributes_from_name(name)
    return field


def _add_field_if_missing(apps, schema_editor, model_name, field):
    model = apps.get_model("reception", model_name)
    field.model = model
    if field.column not in _existing_column_names(schema_editor, model._meta.db_table):
        schema_editor.add_field(model, field)


def sync_existing_database_schema(apps, schema_editor):
    image_fields = [
        _build_file_field(
            "identity_card_image",
            "patient_documents/identity_cards/",
            "صورة البطاقة الشخصية",
        ),
        _build_file_field(
            "military_card_image",
            "patient_documents/military_cards/",
            "صورة البطاقة العسكرية",
        ),
        _build_file_field(
            "medical_report_image",
            "patient_documents/medical_reports/",
            "صورة التقرير الطبي",
        ),
        _build_file_field(
            "injury_document_image",
            "patient_documents/injury_documents/",
            "صورة وثيقة الإصابة",
        ),
    ]

    for field in image_fields:
        _add_field_if_missing(apps, schema_editor, "Patient", field)

    evaluation_model = apps.get_model("reception", "MedicalEvaluation")
    old_reason_field = evaluation_model._meta.get_field("decision_reason")
    new_reason_field = models.TextField(blank=True, null=True, verbose_name="سبب القرار")
    new_reason_field.set_attributes_from_name("decision_reason")
    new_reason_field.model = evaluation_model
    schema_editor.alter_field(evaluation_model, old_reason_field, new_reason_field, strict=False)


class Migration(migrations.Migration):

    dependencies = [
        ("reception", "0002_remove_medicalevaluation_main_doctor_name_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(sync_existing_database_schema, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="patient",
                    name="identity_card_image",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to="patient_documents/identity_cards/",
                        validators=[IMAGE_VALIDATOR],
                        verbose_name="صورة البطاقة الشخصية",
                    ),
                ),
                migrations.AddField(
                    model_name="patient",
                    name="military_card_image",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to="patient_documents/military_cards/",
                        validators=[IMAGE_VALIDATOR],
                        verbose_name="صورة البطاقة العسكرية",
                    ),
                ),
                migrations.AddField(
                    model_name="patient",
                    name="medical_report_image",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to="patient_documents/medical_reports/",
                        validators=[IMAGE_VALIDATOR],
                        verbose_name="صورة التقرير الطبي",
                    ),
                ),
                migrations.AddField(
                    model_name="patient",
                    name="injury_document_image",
                    field=models.FileField(
                        blank=True,
                        null=True,
                        upload_to="patient_documents/injury_documents/",
                        validators=[IMAGE_VALIDATOR],
                        verbose_name="صورة وثيقة الإصابة",
                    ),
                ),
                migrations.AlterField(
                    model_name="patient",
                    name="phone",
                    field=models.CharField(
                        blank=True,
                        max_length=10,
                        null=True,
                        validators=[PHONE_VALIDATOR],
                        verbose_name="رقم الهاتف",
                    ),
                ),
                migrations.AlterField(
                    model_name="patient",
                    name="companion_phone",
                    field=models.CharField(
                        blank=True,
                        max_length=10,
                        null=True,
                        validators=[PHONE_VALIDATOR],
                        verbose_name="هاتف المرافق",
                    ),
                ),
                migrations.AlterField(
                    model_name="medicalevaluation",
                    name="injury_degree",
                    field=models.CharField(
                        choices=[(str(i), f"{i}%") for i in range(1, 19)],
                        max_length=3,
                        verbose_name="درجة الإصابة",
                    ),
                ),
                migrations.AlterField(
                    model_name="medicalevaluation",
                    name="decision_reason",
                    field=models.TextField(blank=True, null=True, verbose_name="سبب القرار"),
                ),
            ],
        ),
    ]
