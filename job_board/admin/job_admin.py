from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from job_board.models import JobSummery, Job, JobAdditionalField, Assessment


class JobSummeryInline(admin.StackedInline):
    model = JobSummery
    min_num = 1


class AdditionalFieldInline(admin.TabularInline):
    model = JobAdditionalField

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


class JobForm(forms.ModelForm):
    assessments = forms.ModelMultipleChoiceField(
        queryset=Assessment.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='assessments', is_stacked=False)
    )

    class Meta:
        model = Job
        fields = '__all__'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = (JobSummeryInline, AdditionalFieldInline)
    list_display = ('title', 'job_summery',)
    form = JobForm
