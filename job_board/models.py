import datetime
import random
from datetime import timedelta

from django.contrib.auth import hashers
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.exceptions import ValidationError
from django.db import models
# from gdstorage.storage import GoogleDriveStorage
from django.db.models import Sum
from django.utils import timezone
from tinymce.models import HTMLField
import uuid

# Create your models here.
from job_board.tasks import send_otp
from django_userforeignkey.models.fields import UserForeignKey

class AuthorMixin(models.Model):
    created_by = UserForeignKey(auto_user_add=True, verbose_name="Created By",
                                related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Assessment(AuthorMixin, TimeStampMixin):
    TYPE_CHOICE = (
        ('mcq', 'MCQ Examination'),
        ('written', 'Written Examination'),
        ('viva', 'Viva/Oral Examination'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    pass_percentage = models.FloatField()
    duration = models.FloatField(help_text='This duration will be in minutes')
    description = HTMLField()
    type = models.CharField(max_length=40, choices=TYPE_CHOICE, default='mcq')
    open_to_start = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        to_human = f'{self.duration} Minutes'
        if self.duration > 60:
            in_hour = str(round(self.duration / 60, 2)).split(".")
            to_human = f'{in_hour[0]} Hour {in_hour[1]} Minutes'
        return to_human

    @property
    def score(self):
        score = self.assessmentquestion_set.all().aggregate(Sum('score'))['score__sum']
        return score if score else 0

    @property
    def pass_score(self):
        return (float(self.score) * float(self.pass_percentage)) / 100

    class Meta:
        permissions = [
            ("preview_assessment", "Can preview assessment")
        ]


class AssessmentQuestion(AuthorMixin, TimeStampMixin):
    TYPE = (
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    title = HTMLField()
    score = models.FloatField()
    type = models.CharField(max_length=20, choices=TYPE)


class AssessmentAnswer(AuthorMixin, TimeStampMixin):
    title = HTMLField()
    score = models.FloatField()
    correct = models.BooleanField(default=False)
    assessment_question = models.ForeignKey(AssessmentQuestion, related_name='answers', on_delete=models.CASCADE)


class Job(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=155)
    slug = models.SlugField(max_length=255)
    job_context = HTMLField(max_length=500)
    job_description = HTMLField(null=True, blank=True)
    job_responsibility = HTMLField(null=True, blank=True)
    educational_requirement = HTMLField(null=True, blank=True)
    additional_requirement = HTMLField(null=True, blank=True)
    compensation = HTMLField(null=True, blank=True)
    assessments = models.ManyToManyField(Assessment)

    def __str__(self):
        return self.title


class JobSummery(AuthorMixin, TimeStampMixin):
    JOB_TYPE = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractual', 'Contractual')
    )
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='job_summery')
    application_deadline = models.DateField()
    experience = models.CharField(max_length=255)
    job_type = models.CharField(max_length=22, choices=JOB_TYPE)
    vacancy = models.IntegerField()
    salary_range = models.CharField(max_length=255)

    def __str__(self):
        return f'{naturalday(self.application_deadline)} | {self.vacancy} | {self.job_type}'


class JobAdditionalField(TimeStampMixin, AuthorMixin):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='additional_fields')
    title = models.CharField(max_length=255)
    required = models.BooleanField(default=True)
    validation_regx = models.CharField(max_length=255, null=True, blank=True)


# go_storage = GoogleDriveStorage()

def candidate_email_path(instance, filename):
    return 'hr/candidate/{0}/{1}'.format(instance.email, filename)


class Candidate(TimeStampMixin):
    STATUS_CHOICE = (
        ('active', 'Active'),
        ('banned', 'Banned')
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=40, unique=True)
    email_otp = models.CharField(max_length=10, null=True, blank=True)
    email_verified_at = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='candidate/avatar/', null=True, blank=True)
    cv = models.FileField(upload_to=candidate_email_path)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='active')

    def save(self, *args, **kwargs):
        self.password = hashers.make_password(self.password, salt='mediusware_hr')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class CandidateJob(TimeStampMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.RESTRICT)
    expected_salary = models.FloatField()
    additional_message = models.TextField(null=True, blank=True)

    def save(self, *ages, **kwargs):
        super(CandidateJob, self).save(*ages, **kwargs)
        for assessment in self.job.assessments.all():
            candidate_assessment = CandidateAssessment()
            candidate_assessment.candidate_job = self
            candidate_assessment.assessment = assessment
            candidate_assessment.save()
        # TODO : Schedule mail for assessment

    def __str__(self):
        return f'{self.candidate.full_name} | {self.job.title}'


class CandidateAssessment(TimeStampMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    candidate_job = models.ForeignKey(CandidateJob, on_delete=models.CASCADE, related_name='candidate_job')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    can_start_after = models.DateTimeField(null=True, blank=True)
    exam_started_at = models.DateTimeField(null=True, blank=True)
    exam_end_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    evaluation_url = models.CharField(null=True, blank=True, max_length=255)
    step = models.JSONField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    # TODO : send mail to candidate when can start after is present
    # It can be auto mated with cron job

    @property
    def time_spend(self):
        if self.exam_end_at is not None:
            now = timezone.now()
            if self.exam_end_at >= now:
                return now - self.exam_started_at
            return 'time_up'
        return 'not_started'

    @property
    def status(self):
        if self.step is None:
            return '-'
        if self.step['current_step'] == len(self.step['question_ids']):
            return 'complete'
        return 'processing'

    @property
    def result(self):
        if not self.step:
            return '-'
        if self.score >= self.assessment.pass_score:
            return 'pass'
        return 'fail'


class CandidateAssessmentAnswer(TimeStampMixin):
    candidate_job = models.ForeignKey(CandidateJob, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    total_score = models.FloatField()
    answers = models.JSONField()
    score_achieve = models.FloatField()


class ResetPassword(TimeStampMixin):
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    otp_expire_at = models.DateTimeField()
    otp_used_at = models.DateTimeField(null=True, blank=True)

    def clean_fields(self, exclude=None):
        super(ResetPassword, self).clean_fields(exclude=['otp', 'otp_expire_at'])
        if not Candidate.objects.filter(email__exact=self.email).first():
            raise ValidationError(
                {'email': 'Your given email is not found in candidate list, please insert a valid email address'})

    def save(self, *args, **kwargs):
        if self.otp_used_at is None:
            self.otp = random.randrange(100000, 999999, 6)
            self.otp_expire_at = timezone.now() + timedelta(minutes=15)
            send_otp(self.otp, self.email)
        super(ResetPassword, self).save(*args, **kwargs)
