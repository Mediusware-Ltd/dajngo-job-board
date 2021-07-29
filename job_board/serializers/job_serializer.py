from rest_framework import serializers
from job_board.models import JobSummery, Job, JobAdditionalField


class JobSummerySerializer(serializers.ModelSerializer):
    application_deadline = serializers.DateField(format="%B %d %Y")
    job_type = serializers.CharField(source='get_job_type_display')

    class Meta:
        model = JobSummery
        fields = ['application_deadline', 'experience', 'job_type', 'vacancy', 'salary_range']


class AdditionalFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAdditionalField
        fields = ['title', 'required', 'validation_regx']


class JobSerializer(serializers.ModelSerializer):
    job_summery = JobSummerySerializer(many=False)
    additional_fields = AdditionalFieldsSerializer(many=True)
    updated_at = serializers.DateTimeField(format="%B %d %Y")

    # assessment = AssessmentSerializer(many=False)

    class Meta:
        model = Job
        fields = ['title', 'slug', 'job_context', 'job_description', 'job_responsibility',
                  'educational_requirement', 'additional_requirement', 'compensation', 'assessments',
                  'updated_at', 'job_summery', 'additional_fields']


class JobSerializerSimple(serializers.ModelSerializer):
    # assessment = AssessmentSerializer(many=False)

    class Meta:
        model = Job
        fields = ['title']
