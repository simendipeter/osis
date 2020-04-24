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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from osis_common.decorators.ajax import ajax_required
from program_management.ddd.repositories.load_tree import find_all_program_tree_versions_to_copy


@login_required
def fill_out_version(request, root_group_id, version_name):
    # TODO : Remplir le programme de transition à partir du programme original
    original = request.GET.get('radio_original_to_copy')
    args_elements = [root_group_id]
    if version_name != '':
        args_elements.append(version_name)
    return HttpResponseRedirect(reverse('education_group_read_transition', args=args_elements))


@ajax_required
def check_available_versions_for_copy(request, acronym, year):
    originals = find_all_program_tree_versions_to_copy(acronym, int(year)-1, int(year))

    originals_data = []
    for original in originals:
        originals_data.append(
            {'id': original.root_group.id,
             'label': "{} : {} {} {}".format(_('Copy from standard version') if original.is_standard else _('Copy from transition version') ,original.root_group.acronym,_('in'),original.root_group.academic_year.year)
             })
    return JsonResponse(list(originals_data), safe=False)
