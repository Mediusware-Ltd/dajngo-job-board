from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from job_board.models import Candidate, CandidateJob
from job_board.serializers.job_serializer import JobSerializerSimple


class CandidateSerializer(ModelSerializer):
    """
    Candidate serializer has been used in registration and fetch candidate
    this serializer is based on Candidate Model
    """

    class Meta:
        model = Candidate
        fields = ('id', 'full_name', 'email', 'password', 'phone', 'avatar', 'cv')
        extra_kwargs = {'password': {"write_only": True}}

    def get_cv_url(self, candidate):
        request = self.context.get('request')
        cv_url = candidate.cv.url
        return request.build_absolute_uri(cv_url)


class CandidateUpdateSerializer(serializers.ModelSerializer):
    """
    Candidate profile update serializer, this serializer has been used in candidate profile update
    """
    current_password = serializers.CharField()

    class Meta:
        model = Candidate
        fields = ('full_name', 'cv', 'avatar', 'current_password')
        extra_kwargs = {'cv': {'required': False}}


class CandidateJobApplySerializer(serializers.Serializer):
    job_slug = serializers.CharField()
    expected_salary = serializers.FloatField()
    additional_message = serializers.CharField(allow_null=True)

    def create(self, validated_data):
        validated_data.pop('job_slug')
        candidate_job = CandidateJob(**validated_data)
        candidate_job.save()
        return candidate_job

    def update(self, instance, validated_data):
        pass


class CandidateJobSerializer(serializers.ModelSerializer):
    job = JobSerializerSimple(many=False)
    created_at = serializers.DateTimeField(format='%d %B, %Y', read_only=True, required=False)

    class Meta:
        model = CandidateJob
        fields = ('unique_id', 'job', 'expected_salary', 'additional_message', 'created_at')
