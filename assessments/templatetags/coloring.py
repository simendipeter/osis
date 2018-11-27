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
from django import template
from base.models.enums import exam_enrollment_state as enrollment_states
from base import models as mdl

register = template.Library()


@register.filter
def get_line_color(enrollment):
    if enrollment.enrollment_state == enrollment_states.ENROLLED:
        current_session = mdl.session_exam_calendar.current_session_exam()
        print(current_session.academic_calendar.start_date)
        if enrollment.date_enrollment > current_session.academic_calendar.start_date:
            return '#01DF74'
        return None
    else:
        return '#FE2E2E'
