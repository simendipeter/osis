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
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from base.business.education_groups import perms
from base.models import group_element_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import TrainingType, MiniTrainingType, GroupType
from base.models.group_element_year import find_learning_unit_formations
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.models.prerequisite import Prerequisite
from base.models.utils.utils import get_object_or_none
from base.views.common import display_warning_messages
from base.views.education_groups.detail import CatalogGenericDetailView
from program_management.business.group_element_years.group_element_year_tree import EducationGroupHierarchy
from program_management.business.learning_units.prerequisite import \
    get_prerequisite_acronyms_which_are_outside_of_education_group

NO_PREREQUISITES = TrainingType.finality_types() + [
    MiniTrainingType.OPTION.name,
    MiniTrainingType.MOBILITY_PARTNERSHIP.name,
] + GroupType.get_names()


@method_decorator(login_required, name='dispatch')
class LearningUnitGenericDetailView(PermissionRequiredMixin, DetailView, CatalogGenericDetailView):
    model = LearningUnitYear
    context_object_name = "learning_unit_year"
    pk_url_kwarg = 'learning_unit_year_id'

    permission_required = 'base.can_access_education_group'
    raise_exception = True

    def get_person(self):
        return get_object_or_404(Person, user=self.request.user)

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        root = self.get_root()
        self.hierarchy = EducationGroupHierarchy(root, tab_to_show=self.request.GET.get("tab_to_show"))
        # TODO remove parent in context
        context['person'] = self.get_person()
        context['root'] = root
        context['root_id'] = root.pk
        context['parent'] = root
        context['tree'] = json.dumps(self.hierarchy.to_json())
        context['group_to_parent'] = self.request.GET.get("group_to_parent") or '0'
        context['show_prerequisites'] = self.show_prerequisites(root)
        context['selected_element_clipboard'] = self.get_selected_element_for_clipboard()
        return context

    def show_prerequisites(self, education_group_year):
        return education_group_year.education_group_type.name not in NO_PREREQUISITES


class LearningUnitUtilization(LearningUnitGenericDetailView):
    template_name = "learning_unit/tab_utilization.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_element_years"] = self.object.child_leaf.select_related("parent")
        context["formations"] = find_learning_unit_formations(
            list(grp.parent for grp in self.object.child_leaf.select_related("parent")),
            parents_as_instances=True
        )
        return context


class LearningUnitPrerequisite(LearningUnitGenericDetailView):
    def dispatch(self, request, *args, **kwargs):
        is_root_a_training = EducationGroupYear.objects.filter(
            id=kwargs["root_id"],
            education_group_type__category__in=Categories.training_categories()
        ).exists()
        if is_root_a_training:
            return LearningUnitPrerequisiteTraining.as_view()(request, *args, **kwargs)
        return LearningUnitPrerequisiteGroup.as_view()(request, *args, **kwargs)


class LearningUnitPrerequisiteTraining(LearningUnitGenericDetailView):
    template_name = "learning_unit/tab_prerequisite_training.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        luy = self.object
        root = context["root"]
        context["prerequisite"] = get_object_or_none(Prerequisite,
                                                     learning_unit_year=luy,
                                                     education_group_year=root)
        context["can_modify_prerequisite"] = perms.is_eligible_to_change_education_group(
            context['person'],
            context["root"]
        )

        context["learning_unit_years_parent"] = {}
        for grp in self.hierarchy.included_group_element_years:
            if not grp.child_leaf:
                continue
            context["learning_unit_years_parent"].setdefault(grp.child_leaf.id, grp)

        context['is_prerequisites_list'] = Prerequisite.objects.filter(
            prerequisiteitem__learning_unit=luy.learning_unit,
            education_group_year=root
        ).select_related('learning_unit_year')
        return context

    def render_to_response(self, context, **response_kwargs):
        self.add_warning_messages(context)
        return super().render_to_response(context, **response_kwargs)

    def add_warning_messages(self, context):
        root = context["root"]
        prerequisite = context["prerequisite"]
        learning_unit_year = context["learning_unit_year"]
        learning_unit_inconsistent = get_prerequisite_acronyms_which_are_outside_of_education_group(root, prerequisite)\
            if prerequisite else []
        if learning_unit_inconsistent:
            display_warning_messages(
                self.request,
                _("The prerequisites %(prerequisites)s for the learning unit %(learning_unit)s "
                  "are not inside the selected training %(root)s") % {
                    "prerequisites": ", ".join(learning_unit_inconsistent),
                    "learning_unit": learning_unit_year,
                    "root": root,
                }
            )


class LearningUnitPrerequisiteGroup(LearningUnitGenericDetailView):
    template_name = "learning_unit/tab_prerequisite_group.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        learning_unit_year = context["learning_unit_year"]
        formations_id = group_element_year.find_learning_unit_formations([learning_unit_year]). \
            get(learning_unit_year.id, [])
        qs = EducationGroupYear.objects.filter(id__in=formations_id)
        prefetch_prerequisites = Prefetch("prerequisite_set",
                                          Prerequisite.objects.filter(learning_unit_year=learning_unit_year),
                                          to_attr="prerequisites")

        context["formations"] = qs.prefetch_related(prefetch_prerequisites)

        return context