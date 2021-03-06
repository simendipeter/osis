##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.db.models import Prefetch

import program_management.ddd.repositories.find_roots
from base.business.education_groups import perms
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_categories import Categories
from base.models.prerequisite import Prerequisite
from base.views.common import display_business_warning_messages
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.validators._prerequisites_items import PrerequisiteItemsValidator
from program_management.views.generic import LearningUnitGeneric


class LearningUnitPrerequisite(PermissionRequiredMixin, LearningUnitGeneric):
    permission_required = 'base.view_educationgroup'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if self.program_tree.root_node.is_training():
            return LearningUnitPrerequisiteTraining.as_view()(request, *args, **kwargs)
        return LearningUnitPrerequisiteGroup.as_view()(request, *args, **kwargs)


class LearningUnitPrerequisiteTraining(PermissionRequiredMixin, LearningUnitGeneric):
    template_name = "learning_unit/tab_prerequisite_training.html"

    permission_required = 'base.view_educationgroup'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["can_modify_prerequisite"] = perms.is_eligible_to_change_education_group(
            context['person'],
            context["root"]
        )
        context["program_links"] = self.program_tree.get_all_links()
        context["is_prerequisite_of_list"] = context["node"].get_is_prerequisite_of()
        return context

    def render_to_response(self, context, **response_kwargs):
        self.add_warning_messages(context)
        return super().render_to_response(context, **response_kwargs)

    def add_warning_messages(self, context):
        validator = PrerequisiteItemsValidator(str(self.node.prerequisite), self.node, self.program_tree)
        if not validator.is_valid():
            display_business_warning_messages(
                self.request,
                validator.messages
            )


class LearningUnitPrerequisiteGroup(PermissionRequiredMixin, LearningUnitGeneric):
    template_name = "learning_unit/tab_prerequisite_group.html"

    permission_required = 'base.view_educationgroup'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        # TODO : Use DDD for this part
        learning_unit_year = context["learning_unit_year"]
        formations_id = program_management.ddd.repositories.find_roots.find_roots([learning_unit_year]).get(
            learning_unit_year.id,
            []
        )
        qs = EducationGroupYear.objects.filter(id__in=formations_id)
        prefetch_prerequisites = Prefetch(
            "prerequisite_set",
            Prerequisite.objects.filter(learning_unit_year=learning_unit_year),
            to_attr="prerequisites"
        )
        context["formations"] = qs.prefetch_related(prefetch_prerequisites)
        return context
