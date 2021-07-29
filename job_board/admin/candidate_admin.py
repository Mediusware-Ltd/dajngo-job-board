from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from job_board.models import Candidate, CandidateJob, ResetPassword, CandidateAssessment


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/candidate/custom_candidate_form.html'

    list_display = ('full_name', 'email', 'phone', 'applied_job')

    def applied_job(self, obj: Candidate):
        return obj.candidatejob_set.count()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['candidate_jobs'] = CandidateJob.objects.filter(candidate_id=object_id).all()
        return super(CandidateAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(CandidateJob)
class CandidateJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'get_job', 'get_assessment', 'unique_id')
    list_display_links = ('get_job', 'candidate')

    @admin.display(description='Job', ordering='job')
    def get_job(self, obj):
        return obj.job.title

    @admin.display(description='Assessment', ordering='job__assessment')
    def get_assessment(self, obj: CandidateJob):
        # url = reverse(f'admin:{obj.job.assessment._meta.app_label}_{obj.job.assessment._meta.model_name}_change',
        #               args=[obj.job.assessment.id])
        # return format_html(
        #     f'<a href="{url}">{obj.job.assessment}</a>'
        # )
        return 'ok'


@admin.register(CandidateAssessment)
class CandidateAssessment(admin.ModelAdmin):
    list_display = ('candidate', 'exam_started_at', 'get_assessment', 'score', 'status', 'result',)
    search_fields = ('score', 'candidate_job__candidate__full_name', 'candidate_job__candidate__email')
    list_filter = ('assessment', 'assessment__type', 'candidate_job__job__title')
    readonly_fields = ['step']

    def candidate(self, obj):
        return format_html(
            f'{obj.candidate_job.candidate.full_name}'
        )

    def get_assessment(self, obj):
        return format_html(
            f'{obj.assessment.title} </br>'
            f'Total Score : {obj.assessment.score} </br>'
            f'Pass Score : {obj.assessment.pass_score} </br>'
            f'{obj.assessment.get_type_display()}'
        )

    def assessment_pass_score(self, obj):
        return obj.assessment.pass_score


@admin.register(ResetPassword)
class CandidateResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'otp_expire_at', 'otp_used_at')
    readonly_fields = ('otp', 'otp_expire_at', 'otp_used_at')
