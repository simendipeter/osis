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
from abc import ABC

from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from base.models.academic_calendar import AcademicCalendar
from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from base.models.enums import academic_calendar_type


class EventPerm(ABC):
    academic_year_field = 'academic_year'
    model = None  # To instantiate == ex : EducationGroupYear
    event_reference = None  # To instantiate == ex : academic_calendar_type.EDUCATION_GROUP_EDITION
    obj = None  # To instantiate
    raise_exception = True
    error_msg = ""  # To instantiate == ex : _("This education group is not editable during this period.")

    def __init__(self, obj=None, raise_exception=True):
        if self.model and obj and not isinstance(obj, self.model):
            raise AttributeError("The provided obj must be a {}".format(self.model.__name__))
        self.obj = obj
        self.raise_exception = raise_exception

    def is_open(self):
        if self.obj:
            return self._is_open_for_specific_object()
        return self._is_calendar_opened()

    @classmethod
    def get_open_academic_calendars_queryset(cls) -> QuerySet:
        qs = AcademicCalendar.objects.open_calendars()
        if cls.event_reference:
            qs = qs.filter(reference=cls.event_reference)
        return qs

    @cached_property
    def open_academic_calendars_for_specific_object(self) -> list:
        obj_ac_year = getattr(self.obj, self.academic_year_field)
        return list(self.get_open_academic_calendars_queryset().filter(data_year=obj_ac_year))

    def _is_open_for_specific_object(self) -> bool:
        if not self.open_academic_calendars_for_specific_object:
            if self.raise_exception:
                raise PermissionDenied(_(self.error_msg).capitalize())
            return False
        return True

    @classmethod
    def _is_calendar_opened(cls) -> bool:
        return cls.get_open_academic_calendars_queryset().exists()

    @classmethod
    def get_academic_years(cls) -> QuerySet:
        return AcademicYear.objects.filter(pk__in=cls.get_academic_years_ids())

    @classmethod
    def get_academic_years_ids(cls) -> QuerySet:
        return cls.get_open_academic_calendars_queryset().values_list('data_year', flat=True)


class EventPermEducationGroupEdition(EventPerm):
    model = EducationGroupYear
    event_reference = academic_calendar_type.EDUCATION_GROUP_EDITION
    error_msg = _("This education group is not editable during this period.")
