from collections import OrderedDict

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from job_board.models import Assessment, AssessmentAnswer, AssessmentQuestion, CandidateJob, CandidateAssessmentAnswer, \
    CandidateAssessment
from job_board.serializers.candidate_serializer import CandidateJobSerializer


class AssessmentSerializer(ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['title', 'slug', 'description', 'score', 'pass_score', 'duration', 'type']


class AssessmentAnswerSerializer(ModelSerializer):
    class Meta:
        model = AssessmentAnswer
        fields = ('id', 'title')


class AssessmentQuestionSerializer(ModelSerializer):
    answers = AssessmentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'title', 'type', 'answers')


class CandidateAssessmentSerializer(serializers.ModelSerializer):
    assessment = AssessmentSerializer(many=False)
    created_at = serializers.DateTimeField(format='%B %d, %Y')
    updated_at = serializers.DateTimeField(format='%B %d, %Y')
    candidate_job = CandidateJobSerializer(many=False)
    time_spend = serializers.CharField()

    class Meta:
        model = CandidateAssessment
        fields = ('unique_id', 'created_at', 'updated_at', 'exam_started_at', 'exam_end_at', 'score', 'time_spend',
                  'evaluation_url', 'step', 'candidate_job', 'assessment')


def valid_uuid(value):
    candidate_assessment = CandidateAssessment.objects.filter(unique_id=value).first()
    if not candidate_assessment:
        raise serializers.ValidationError('We could not found any assessment in your given uuid')
    # TODO : this section should uncommented in production
    # if candidate_assessment.time_spend == 'time_up':
    #     raise serializers.ValidationError(f'{candidate_assessment.assessment} has been expired')


class GivenAssessmentAnswerSerializer(serializers.Serializer):
    """
    Most complicated part, Handle with care
    TODO : i need to modify the comment and it should be elaborate
    """
    uuid = serializers.UUIDField(validators=[valid_uuid])
    question_id = serializers.IntegerField(min_value=1)
    answers = serializers.ListField(child=serializers.IntegerField(min_value=1), min_length=1)

    candidate_assessment = CandidateAssessment
    candidate_job = CandidateJob
    question = AssessmentQuestion
    candidate_answer = CandidateAssessmentAnswer

    def validate(self, data: OrderedDict):
        self.candidate_assessment = CandidateAssessment.objects.filter(unique_id__exact=data['uuid']).first()
        self.candidate_job = self.candidate_assessment.candidate_job
        self.question = AssessmentQuestion.objects.get(pk=data['question_id'])
        if self.question.type == 'single_choice' and len(data['answers']) > 1:
            raise serializers.ValidationError(
                {
                    'answers':
                        f'{self.question.get_type_display()} allow single answer, your answer {len(data["answers"])}'
                }
            )
        return data

    def create(self, validated_data):
        assessment_answer = AssessmentAnswer.objects.filter(pk__in=validated_data['answers'],
                                                            assessment_question_id__exact=validated_data[
                                                                'question_id']
                                                            ).all()
        candidate_answer = CandidateAssessmentAnswer.objects.filter(question=self.question,
                                                                    candidate_job=self.candidate_job).first()
        if not candidate_answer:
            self._create_answer(assessment_answer=assessment_answer)
            return validated_data
        raise serializers.ValidationError({'message': 'This answer has been taken already'})

    def _create_answer(self, assessment_answer):
        candidate_answer = CandidateAssessmentAnswer()
        candidate_answer.candidate_job = self.candidate_job
        candidate_answer.question = self.question
        candidate_answer.answers = AssessmentAnswerSerializer(assessment_answer, many=True).data
        candidate_answer.total_score = self.question.score
        candidate_answer.score_achieve = assessment_answer.aggregate(score_achieve=Sum('score'))['score_achieve']
        candidate_answer.save()
        self._step_increment()
        self._add_mcq_mark(candidate_answer.score_achieve)

    def _step_increment(self):
        self.candidate_assessment.step['current_step'] += 1
        self.candidate_assessment.save()

    def _add_mcq_mark(self, score):
        self.candidate_assessment.score += score
        self.candidate_assessment.save()
