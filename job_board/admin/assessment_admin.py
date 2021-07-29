from django.contrib import admin
from django.template.defaultfilters import truncatechars_html
from django.urls import reverse
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe

from job_board.models import AssessmentAnswer, AssessmentQuestion, Assessment


class AssessmentAnswerInline(admin.TabularInline):
    model = AssessmentAnswer
    fk_name = 'assessment_question'

    # readonly_fields = ['score']
    # min_num = 2

    def get_extra(self, request, obj=None, **kwargs):
        return 2 if not obj else 0


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'score', 'duration_display', 'get_description', 'type', 'open_to_start', 'show_action')

    @admin.display(description='description')
    def get_description(self, obj):
        return strip_tags(obj.description)

    @admin.display(description='Actions')
    def show_action(self, obj):
        return format_html(
            f'<a href="{reverse("preview_assessment", kwargs={"pk": obj.pk})}">Preview</a>'
        )


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'get_title', 'score', 'type')
    list_filter = ('assessment',)
    inlines = (AssessmentAnswerInline,)

    ordering = ['assessment']

    change_form_template = 'admin/assessment_question/form.html'

    @admin.display(description='Title')
    def get_title(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.title, 200))
        return mark_safe("&nbsp;".join(safe_value.split(' ')))

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        correct_answer = self._correct_answer(formset)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if request.POST['type'] == 'single_choice':
                instance.score = 0
                if instance.correct:
                    instance.score = float(request.POST['score']) / correct_answer
            else:
                instance.score = - (float(request.POST['score']) / correct_answer)
                if instance.correct:
                    instance.score = float(request.POST['score']) / correct_answer
            instance.save()
        formset.save_m2m()

    def _correct_answer(self, formset):
        correct_answer = 0
        for form in formset:
            if form.cleaned_data['DELETE'] is False and form.cleaned_data['correct'] is True:
                correct_answer += 1
        return correct_answer
