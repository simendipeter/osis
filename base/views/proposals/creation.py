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

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import BLANK_CHOICE_DASH
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from base import models as mdl_base
from base.business.learning_unit import create_learning_unit, create_learning_unit_structure
from base.forms.learning_unit_proposal import _copy_learning_unit_data
from base.forms.proposal.creation import LearningUnitProposalCreationForm, LearningUnitProposalForm
from base.models import proposal_folder, proposal_learning_unit
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.proposal_state import ProposalState
from base.models.enums.proposal_type import ProposalType
from base.models.learning_container import LearningContainer
from base.models.person import Person
from base.views import layout
from reference.models import language


@login_required
@permission_required('base.can_create_learningunit', raise_exception=True)
def proposal_learning_unit_creation_form(request, academic_year):
    person = get_object_or_404(Person, user=request.user)
    learning_unit_form = LearningUnitProposalCreationForm(person, initial={'academic_year': academic_year,
                                                                           'subtype': learning_unit_year_subtypes.FULL,
                                                                           "container_type": BLANK_CHOICE_DASH,
                                                                           'language': language.find_by_code('FR')})
    proposal_form = LearningUnitProposalForm()
    return layout.render(request, "proposal/creation_form.html", {'learning_unit_form': learning_unit_form,
                                                                  'proposal_form': proposal_form,
                                                                  'person': person})


@login_required
@permission_required('base.can_propose_learningunit', raise_exception=True)
def proposal_learning_unit_add(request):
    person = get_object_or_404(Person, user=request.user)
    learning_unit_form = LearningUnitProposalCreationForm(person, request.POST)
    proposal_form = LearningUnitProposalForm(request.POST)
    if learning_unit_form.is_valid() and proposal_form.is_valid():
        data_learning_unit = learning_unit_form.cleaned_data
        data_proposal = proposal_form.cleaned_data
        year = data_learning_unit['academic_year'].year
        status = data_learning_unit['status']
        additional_requirement_entity_1 = data_learning_unit.get('additional_requirement_entity_1')
        additional_requirement_entity_2 = data_learning_unit.get('additional_requirement_entity_2')
        allocation_entity_version = data_learning_unit.get('allocation_entity')
        requirement_entity_version = data_learning_unit.get('requirement_entity')
        campus = data_learning_unit.get('campus')
        new_learning_container = LearningContainer.objects.create()
        new_learning_unit = create_learning_unit(data_learning_unit, new_learning_container, year)
        academic_year = mdl_base.academic_year.find_academic_year_by_year(year)
        luy_created = create_learning_unit_structure(additional_requirement_entity_1,
                                                     additional_requirement_entity_2, allocation_entity_version,
                                                     data_learning_unit, new_learning_container, new_learning_unit,
                                                     requirement_entity_version, status, academic_year, campus)
        folder_entity = data_proposal.get('folder_entity').entity
        folder_id = data_proposal.get('folder_id')
        initial_data = _copy_learning_unit_data(luy_created)
        folder, created = proposal_folder.ProposalFolder.objects.get_or_create(entity=folder_entity,
                                                                               folder_id=folder_id)
        proposal_learning_unit.ProposalLearningUnit.objects.create(folder=folder, learning_unit_year=luy_created,
                                                                   type=ProposalType.CREATION.name,
                                                                   state=ProposalState.FACULTY.name,
                                                                   initial_data=initial_data, author=person)
        _show_success_proposal_learning_unit_creation_message(request, luy_created)
        return redirect('learning_units')
    return layout.render(request, "proposal/creation_form.html", {'learning_unit_form': learning_unit_form,
                                                                  'proposal_form': proposal_form,
                                                                  'person': person})


def _show_success_proposal_learning_unit_creation_message(request, learning_unit_year_created):
    link = reverse("learning_unit", kwargs={'learning_unit_year_id': learning_unit_year_created.id})
    success_msg = _('proposal_learning_unit_successfuly_created') % {'link': link,
                                                                     'acronym': learning_unit_year_created.acronym,
                                                                     'academic_year': learning_unit_year_created.academic_year}
    messages.add_message(request, messages.SUCCESS, success_msg, extra_tags='safe')
