from urllib import request
from pytimeparse.timeparse import timeparse

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse

from accounts.models import Organization
from results.models import Result

from .forms import CreateAssessmentForm
from .models import Assessment


# Create your views here.


# class CreateAssessmentView(LoginRequiredMixin, CreateView):
#     model = Assessment
#     template_name_suffix = '_create'
#     fields = (
#         'name',
#         'description',
#         'duration',
#         'pass_mark'
#     )

#     def form_valid(self, form):
#         organization = Organization.objects.filter(
#             email=self.request.user.email
#         ).first()
#         form.instance.created_by = organization
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('assessments:detail', args=[self.object.id])


class CreateAssessmentView(View):

    def post(self, request, **kwargs):
        form = CreateAssessmentForm(request.POST)
        if form.is_valid():
            organization = Organization.objects.filter(
                email=self.request.user.email
            ).first()
            form.instance.created_by = organization
            assessment = form.save()
            return HttpResponseRedirect(
                reverse('assessments:questions:create', args=[assessment.id])
            )
        


class EditAssessmentView(LoginRequiredMixin, UpdateView):
    model = Assessment
    template_name_suffix = '_update'
    fields = (
        'name',
        'duration',
        'pass_mark',
        'is_published',
    )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(id=self.request.user.id)
        context['organization'] = organization
        return context

    def get_success_url(self):
        return reverse('assessments:detail', args=[self.object.id])


class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    
    def get_queryset(self):
        return Assessment.objects.filter(created_by_id=self.request.user.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(id=self.request.user.id)
        context['organization'] = organization
        context['organization_email'] = organization.email
        return context


class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    queryset = Assessment.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(id=self.request.user.id)
        assessment = self.get_object()
        total_assessment_result = Result.objects.filter(assessment=assessment).count()
        complete_assessment_result = Result.objects.filter(assessment=assessment).exclude(percentage_score__isnull=True)
        total_complete_assessment_result = complete_assessment_result.count()
        context['duration_in_time'] = assessment.duration.total_seconds()/60
        context['total_assessment_result'] = total_assessment_result
        context['total_complete_assessment_result'] = total_complete_assessment_result
        context['complete_assessment_result'] = complete_assessment_result
        context['total_incomplete_result'] = total_assessment_result - total_complete_assessment_result
        context['created_by'] = assessment.created_by
        context['organization_email'] = assessment.created_by.email
        context['organization'] = organization
        return context
        


class ToggleAssessmentVisibilityView(LoginRequiredMixin, View):

    def get(self, request, pk, **kwargs):
        assessment = Assessment.objects.filter(id=pk).first()
        assessment.is_published = not assessment.is_published
        assessment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
class ToggleAssessmentDeleteView(LoginRequiredMixin, View):

    def get(self, request, pk, **kwargs):
        assessment = Assessment.objects.filter(id=pk).first()
        assessment.is_deleted = not assessment.is_deleted
        assessment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
