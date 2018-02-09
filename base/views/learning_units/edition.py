##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from base.models.enums.entity_container_year_link_type import ENTITY_TYPE_LIST
from base.models.enums.learning_unit_periodicity import ANNUAL
from base.models.enums.learning_unit_year_subtypes import PARTIM, FULL
from base.views.learning_unit import get_learning_unit_identification_context, compute_learning_unit_form_initial_data
from base.business.learning_units.edition import edit_learning_unit_end_date, update_learning_unit_year, \
    update_learning_unit_year_entities
from base.forms.learning_unit.edition import LearningUnitEndDateForm, LearningUnitModificationForm, \
    FULL_READ_ONLY_FIELDS
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views import layout
from base.views.common import display_error_messages, display_success_messages
from base.views.learning_units import perms


@login_required
@permission_required('base.can_edit_learningunit_date', raise_exception=True)
@perms.can_perform_end_date_modification
def learning_unit_edition(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    user_person = get_object_or_404(Person, user=request.user)

    context = get_learning_unit_identification_context(learning_unit_year_id, user_person)

    learning_unit_to_edit = learning_unit_year.learning_unit
    form = LearningUnitEndDateForm(request.POST or None, learning_unit=learning_unit_to_edit)
    if form.is_valid():
        new_academic_year = form.cleaned_data['academic_year']
        try:
            result = edit_learning_unit_end_date(learning_unit_to_edit, new_academic_year)
            display_success_messages(request, result)

            learning_unit_year_id = _get_current_learning_unit_year_id(learning_unit_to_edit, learning_unit_year_id)

            return HttpResponseRedirect(reverse('learning_unit', args=[learning_unit_year_id]))

        except IntegrityError as e:
            display_error_messages(request, e.args[0])

    context['form'] = form
    return layout.render(request, 'learning_unit/edition.html', context)


@login_required
@permission_required('base.can_edit_learningunit', raise_exception=True)
@perms.can_perform_learning_unit_modification
def modify_learning_unit(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    person = get_object_or_404(Person, user=request.user)
    form = initialize_modification_form(learning_unit_year, person, request.POST)
    if form.is_valid():
        entities_data = extract_entities_data_from_form_data(form.cleaned_data)
        lu_type_full_data = extract_learning_unit_of_type_full_data_from_form_data(form.cleaned_data)

        update_learning_unit_year(learning_unit_year, lu_type_full_data)
        update_learning_unit_year_entities(learning_unit_year, entities_data)

        display_success_messages(request, _("success_modification_learning_unit"))

        return redirect("learning_unit", learning_unit_year_id=learning_unit_year.id)
    context = {
        "learning_unit_year": learning_unit_year,
        "form": form
    }
    return layout.render(request, 'learning_unit/modification.html', context)

def initialize_modification_form(luy, person, post_data):
    initial_data = compute_learning_unit_modification_form_initial_data(luy)

    parent_luy = luy.parent
    if luy.subtype == FULL or parent_luy is None:
        return LearningUnitModificationForm(post_data or None, person=person, initial=initial_data)

    max_credits = parent_luy.credits
    status_value = None if parent_luy.status else parent_luy.status
    can_modify_periodicity = parent_luy.learning_unit.periodicity == ANNUAL

    return LearningUnitModificationForm(post_data or None, person=person, max_credits=max_credits,
                                        status_value=status_value, can_modify_periodicity=can_modify_periodicity,
                                        initial=initial_data)


def extract_learning_unit_of_type_full_data_from_form_data(form_data):
    data_without_entities = {field: value for field, value in form_data.items()
                             if field.upper() not in ENTITY_TYPE_LIST}
    lu_full_data = {field: value for field, value in data_without_entities.items()
                    if field not in FULL_READ_ONLY_FIELDS}
    return lu_full_data


def extract_entities_data_from_form_data(form_data):
    return {entity_type.upper(): entity_version.entity if entity_version else None
            for entity_type, entity_version in form_data.items()
            if entity_type.upper() in ENTITY_TYPE_LIST}


def compute_learning_unit_modification_form_initial_data(learning_unit_year):
    other_fields_dict = {
        "partial_title": learning_unit_year.specific_title,
        "partial_english_title": learning_unit_year.specific_title_english,
        "first_letter": learning_unit_year.acronym[0],
        "acronym": learning_unit_year.acronym[1:]
    }
    fields = {
        "learning_unit_year": ("academic_year", "status", "credits", "session", "subtype", "quadrimester",
                               "attribution_procedure"),
        "learning_container_year": ("common_title", "common_title_english", "container_type", "campus", "language",
                                    "is_vacant", "team", "type_declaration_vacant"),
        "learning_unit": ("faculty_remark", "other_remark", "periodicity")
    }
    return compute_learning_unit_form_initial_data(other_fields_dict, learning_unit_year, fields)


def _get_current_learning_unit_year_id(learning_unit_to_edit, learning_unit_year_id):
    if not LearningUnitYear.objects.filter(pk=learning_unit_year_id).exists():
        result = LearningUnitYear.objects.filter(learning_unit=learning_unit_to_edit).last().pk
    else:
        result = learning_unit_year_id
    return result
