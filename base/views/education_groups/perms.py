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
from django.contrib.auth.mixins import AccessMixin, ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from waffle.models import Flag

from base.business.education_groups import perms as business_perms
from base.models.education_group_year import EducationGroupYear
from base.models.person import Person


def can_change_education_group(user, education_group):
    pers = get_object_or_404(Person, user=user)
    if not business_perms.is_eligible_to_change_education_group(pers, education_group, raise_exception=True):
        raise PermissionDenied
    return True


def can_change_general_information(view_func):
    def f_can_change_general_information(request, *args, **kwargs):
        education_group_year = get_object_or_404(EducationGroupYear, pk=kwargs['education_group_year_id'])
        perm_name = 'base.change_commonpedagogyinformation' if education_group_year.is_common else \
            'base.change_pedagogyinformation'
        if not request.user.has_perm(perm_name, education_group_year):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return f_can_change_general_information


def can_change_admission_condition(view_func):
    def f_can_change_admission_condition(request, *args, **kwargs):
        education_group_year = get_object_or_404(EducationGroupYear, pk=kwargs['education_group_year_id'])
        perm_name = 'base.change_commonadmissioncondition' if education_group_year.is_common else \
            'base.change_admissioncondition'
        if not request.user.has_perm(perm_name, education_group_year):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return f_can_change_admission_condition
