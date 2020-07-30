##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import re

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import CreateView

from base.forms.education_group.version import SpecificVersionForm
from base.models.education_group_year import EducationGroupYear
from base.views.common import display_success_messages
from base.views.mixins import AjaxTemplateMixin
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch
from education_group.ddd.domain.training import TrainingIdentity
from osis_common.decorators.ajax import ajax_required
from osis_role.contrib.views import AjaxPermissionRequiredMixin
from program_management.ddd.command import SearchAllVersionsFromAttributesCommand
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.read import search_tree_versions_service
from program_management.models.education_group_version import EducationGroupVersion


class CreateProgramTreeVersion(AjaxPermissionRequiredMixin, SuccessMessageMixin, AjaxTemplateMixin, CreateView):
    template_name = "tree_version/create_specific_version_inner.html"
    form_class = SpecificVersionForm
    permission_required = 'base.create_specific_version'

    @cached_property
    def node_identity(self) -> 'NodeIdentity': # TODO to remove?
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @cached_property
    def training_identity(self) -> 'TrainingIdentity':
        return TrainingIdentitySearch().get_from_node_identity(self.node_identity)

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def education_group_year(self):
        return get_object_or_404(
            EducationGroupYear,
            academic_year__year=self.training_identity.year,
            acronym=self.training_identity.acronym,
        )

    def _call_rule(self, rule):
        return rule(self.person, self.education_group_year)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["save_type"] = self.request.POST.get("save_type")
        form_kwargs['education_group_year'] = self.education_group_year
        form_kwargs.pop('instance')
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateProgramTreeVersion, self).get_context_data(**kwargs)
        context['training_identity'] = self.training_identity
        context['node_identity'] = self.node_identity
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_message(self, cleaned_data):
        display_success_messages(self.request, cleaned_data["messages"])

    def get_success_url(self):
        return reverse(
            "training_identification",
            args=[
                self.education_group_year.academic_year.year,
                self.education_group_year.partial_acronym,
            ]
        )


@login_required
@ajax_required
def check_version_name(request, year: int, offer_acronym: str):
    version_name = request.GET['version_name']
    tree_versions = search_tree_versions_service.search_all_versions_from_attributes(
        SearchAllVersionsFromAttributesCommand(
            offer_acronym=offer_acronym.upper(),
            version_name=version_name.upper(),
        )
    )
    last_using = next((version for version in tree_versions or [] if version.entity_id.year < year), None)
    existed_version_name = bool(last_using)
    existing_version_name = any(version for version in tree_versions or [] if version.entity_id.year == year)
    valid = bool(re.match("^[A-Z]{0,15}$", version_name.upper()))
    return JsonResponse(
        {
            "existed_version_name": existed_version_name,
            "existing_version_name": existing_version_name,
            "last_using": last_using,
            "valid": valid,
            "version_name": version_name
        },
        safe=False
    )


def check_existing_version(version_name: str, acronym: str, year: int) -> bool:
    return EducationGroupVersion.objects.filter(
        version_name=version_name,
        offer__acronym=acronym,
        offer__academic_year__year=year,
    ).exists()


def find_last_existed_version(education_group_year, version_name):
    return EducationGroupVersion.objects.filter(
        version_name=version_name,
        offer__education_group=education_group_year.education_group,
        offer__academic_year__year__lt=education_group_year.academic_year.year,
    ).order_by(
        'offer__academic_year'
    ).last()
