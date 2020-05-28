from typing import Dict

from django.db.models import Prefetch, F, Value

from base.models.academic_calendar import AcademicCalendar
from base.models.education_group_year import EducationGroupYear
from base.models.enums import academic_calendar_type
from base.models.enums.academic_calendar_type import EXAM_ENROLLMENTS, SCORES_EXAM_SUBMISSION, DISSERTATION_SUBMISSION, \
    DELIBERATION
from base.models.enums.mandate_type import MandateTypes
from base.models.mandatary import Mandatary
from base.models.offer_year_calendar import OfferYearCalendar
from base.models.program_manager import ProgramManager
from education_group.views.serializers import training_administrative_dates as serializer
from education_group.views.serializers.training_administrative_dates import DomainTitle, Dates, SessionNumber
from education_group.views.training.common_read import TrainingRead, Tab


class TrainingAdmnistrativeData(TrainingRead):
    template_name = "training/administrative_data.html"
    active_tab = Tab.ADMINISTRATIVE_DATA

    def get_context_data(self, **kwargs):
        offer_acronym = self.get_object().title
        year = self.get_object().year
        return {
            **super().get_context_data(**kwargs),
            "children": self.get_object().children,
            "learning_unit_enrollment_dates": self.__get_learning_unit_enrollment_date(),
            "administrative_dates": serializer.get_session_dates(offer_acronym, year),
            "additional_informations": self.__get_complementary_informations(),
            "mandataries": self.__get_mandataries(),
            "program_managers": self.__get_program_managers()
        }

    def __get_learning_unit_enrollment_date(self) -> OfferYearCalendar:
        return OfferYearCalendar.objects.filter(
            education_group_year__acronym=self.get_object().title,
            education_group_year__academic_year__year=self.get_object().year,
            academic_calendar__reference=academic_calendar_type.COURSE_ENROLLMENT,
        ).first()

    def __get_complementary_informations(self):
        qs = EducationGroupYear.objects.filter(
            acronym=self.training_identity.acronym, academic_year__year=self.training_identity.year
        ).values('weighting', 'default_learning_unit_enrollment')
        return {
            'weighting': qs[0]['weighting'],
            'has_learning_unit_default_enrollment': qs[0]['default_learning_unit_enrollment'],
        }

    def __get_mandataries(self):
        qs = Mandatary.objects.filter(
            mandate__education_group__educationgroupyear__acronym=self.get_object().title,
            mandate__education_group__educationgroupyear__academic_year__year=self.get_object().year,
            start_date__lte=F('mandate__education_group__educationgroupyear__academic_year__end_date'),
            end_date__gte=F('mandate__education_group__educationgroupyear__academic_year__start_date')
        ).order_by(
            'mandate__function',
            'person__last_name',
            'person__first_name'
        ).annotate(
            function=F('mandate__function'),
            qualification=F('mandate__qualification'),
            first_name=F('person__first_name'),
            middle_name=F('person__middle_name'),
            last_name=F('person__last_name'),
            # function=Value(MandateTypes[F('mandate__function')])
        ).values(
            'function',
            'qualification',
            'first_name',
            'middle_name',
            'last_name',
        )
        for values in qs:
            values['function'] = MandateTypes[values['function']]
        return qs

    def __get_program_managers(self):
        return ProgramManager.objects.filter(
            education_group__educationgroupyear__acronym=self.get_object().title,
            education_group__educationgroupyear__academic_year__year=self.get_object().year,
        ).order_by("person__last_name", "person__first_name")
