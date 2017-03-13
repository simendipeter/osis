##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class AcademicYearAdmin(SerializableModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    fieldsets = ((None, {'fields': ('year', 'start_date', 'end_date')}),)


class AcademicYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    year = models.IntegerField(unique=True)
    start_date = models.DateField(default=timezone.now, blank=True, null=True)
    end_date = models.DateField(default=timezone.now, blank=True, null=True)

    @property
    def name(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.year > now.year:
            raise AttributeError("An academic year cannot be created in the future.")
        if self.start_date and self.year != self.start_date.year:
            raise AttributeError("The start date should be in the same year of the academic year.")
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise AttributeError("Start date should be before the end date.")
        super(AcademicYear, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s-%s" % (self.year, self.year + 1)

    class Meta:
        permissions = (
            ("can_access_academicyear", "Can access academic year"),
        )


def find_academic_year_by_id(academic_year_id):
    return AcademicYear.objects.get(pk=academic_year_id)


def find_academic_years():
    return AcademicYear.objects.all().order_by('year')


def current_academic_years():
    now = timezone.now()
    academic_yrs = AcademicYear.objects.filter(start_date__lte=now) \
                                       .filter(end_date__gte=now) \
                                       .order_by('year')
    return academic_yrs


def current_academic_year():
    current_academic_year = current_academic_years()
    if current_academic_year.count():
        return current_academic_years().first()
    raise ObjectDoesNotExist


def starting_academic_year():
    current_academic_year = current_academic_years()
    if current_academic_year.count():
        return current_academic_year.last()
    raise ObjectDoesNotExist

def find_academic_year_by_year(year):
    try:
        return AcademicYear.objects.get(year=year)
    except ObjectDoesNotExist:
        return None
