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
from datetime import datetime
from typing import Dict, List, Any

from django.conf import settings
from django.db.models import OuterRef, Subquery, fields, F, QuerySet, Prefetch

from base.business.education_groups import general_information_sections
from base.models.academic_calendar import AcademicCalendar
from base.models.enums import academic_calendar_type
from base.models.offer_year_calendar import OfferYearCalendar
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository
from program_management.ddd.domain.node import NodeGroupYear


DomainTitle = str
SessionNumber = str
Dates = Dict['start/end_date', datetime]


class AdministrativeDate:
    def __init__(self, domain_title: str, session_number: int, start_date: datetime, end_date: datetime):
        self.domain_title = domain_title
        self.session_number = session_number
        self.start_date = start_date
        self.end_date = end_date


def get_session_dates(offer_acronym: str, year: int) -> Dict[DomainTitle: Dict[SessionNumber, Dates]]:
    dates = __get_queryset_values(offer_acronym, year)
    return {
        'exam_enrollments_dates': __get_dates_by_session(academic_calendar_type.EXAM_ENROLLMENTS, dates),
        'scores_exam_submission_dates': __get_dates_by_session(academic_calendar_type.SCORES_EXAM_SUBMISSION, dates),
        'dissertations_submission_dates': __get_dates_by_session(academic_calendar_type.DISSERTATION_SUBMISSION, dates),
        'deliberations_dates': __get_dates_by_session(academic_calendar_type.DELIBERATION, dates),
        'scores_exam_diffusion_dates': __get_dates_by_session(academic_calendar_type.SCORES_EXAM_DIFFUSION, dates),
    }


def __get_dates_by_session(domain_title: str, dates: List[AdministrativeDate]) -> Dict[SessionNumber, Dates]:
    dates = list(filter(lambda administrative_date: administrative_date.domain_title == domain_title, dates))
    return {
        'session1': __get_session_dates(1, dates),
        'session2': __get_session_dates(2, dates),
        'session3': __get_session_dates(3, dates),
    }


def __get_session_dates(session_number: int, dates: List[AdministrativeDate]) -> Dates:
    administrative_date = next(date for date in dates if date.session_number == session_number)
    return {
        'start_date': administrative_date.start_date if administrative_date else None,
        'end_date': administrative_date.end_date if administrative_date else None,
    }


def __get_queryset_values(offer_acronym: str, year: int) -> List[AdministrativeDate]:
    calendar_types_to_fetch = (
        academic_calendar_type.EXAM_ENROLLMENTS,
        academic_calendar_type.SCORES_EXAM_SUBMISSION,
        academic_calendar_type.DISSERTATION_SUBMISSION,
        academic_calendar_type.DELIBERATION,
        academic_calendar_type.SCORES_EXAM_DIFFUSION
    )
    qs = OfferYearCalendar.objects.filter(
        education_group_year__acronym=offer_acronym,
        education_group_year__academic_year__year=year,
        reference__in=calendar_types_to_fetch,
    ).annotate(
        session_number=F('academic_calendar__sessionexamcalendar__number_session'),
        start_date=F('academic_calendar__start_date'),
        end_date=F('academic_calendar__end_date'),
        domain_title=F('academic_calendar__reference'),
    )
    return [
        AdministrativeDate(
            domain_title=obj.domain_title,
            session_number=obj.session_number,
            start_date=obj.start_date,
            end_date=obj.end_date,
        )
        for obj in qs
    ]
