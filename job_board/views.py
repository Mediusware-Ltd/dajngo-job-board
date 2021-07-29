from django.contrib.admin import AdminSite
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from job_board.models import Assessment


class AssessmentPreview(LoginRequiredMixin, AccessMixin, AdminSite, TemplateView):
    template_name = 'admin/assessment/preview.html'

    def get_context_data(self, **kwargs):
        assessment = Assessment.objects.filter(**kwargs).first()
        # print(self.get_app_list())
        return {
            'assessment': assessment,
            'site_header': 'Mediusware Ltd',
            'opts': Assessment._meta,
            'is_nav_sidebar_enabled': False,
            'available_apps': [],
            'has_permission': True
        }

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_perm('preview_assessment'):
            return super(AssessmentPreview, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied("Permission denied")


class WebsiteView(TemplateView):
    template_name = 'website/index.html'
