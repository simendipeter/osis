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
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from attribution.models.enums.function import COORDINATOR
from base.models.enums.learning_container_year_types import COURSE
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.tutor import TutorFactory
from base.views.mixins import RulesRequiredMixin


class TestAddAttribution(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFullFactory(learning_container_year__container_type=COURSE)
        cls.lecturing_component = LecturingLearningComponentYearFactory(learning_unit_year=cls.learning_unit_year)
        cls.practical_component = PracticalLearningComponentYearFactory(learning_unit_year=cls.learning_unit_year)
        cls.person = PersonWithPermissionsFactory('can_access_learningunit')
        cls.tutor = TutorFactory(person=cls.person)
        cls.url = reverse("add_attribution", args=[cls.learning_unit_year.id])

    def setUp(self):
        self.client.force_login(self.person.user)
        self.patcher = patch.object(RulesRequiredMixin, "test_func", return_value=True)
        self.mocked_permission_function = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_template_used_with_get(self):
        response = self.client.get(self.url)

        self.assertTrue(self.mocked_permission_function.called)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "attribution/learning_unit/attribution_inner.html")

    def test_post(self):
        self.person.employee = True
        self.person.save()
        start_year = self.learning_unit_year.academic_year.year
        data = {
            'attribution_form-person': self.tutor.person.id,
            'attribution_form-function': COORDINATOR,
            'attribution_form-start_year': start_year,
            'attribution_form-duration': 3,
            'lecturing_form-allocation_charge': 50,
            'practical_form-allocation_charge': 10
        }
        response = self.client.post(self.url, data=data)

        attribution_qs = AttributionNew.objects.filter(
            tutor__id=self.tutor.id,
            function=COORDINATOR,
            start_year=start_year,
            end_year=start_year+2
        )
        self.assertTrue(attribution_qs.exists())
        attribution = attribution_qs.get()
        self.assertTrue(AttributionChargeNew.objects.filter(
            attribution=attribution,
            learning_component_year=self.lecturing_component,
            allocation_charge=50
        ).exists())
        self.assertTrue(AttributionChargeNew.objects.filter(
            attribution=attribution,
            learning_component_year=self.practical_component,
            allocation_charge=10
        ).exists())

        self.assertRedirects(response, reverse("learning_unit_attributions", args=[self.learning_unit_year.id]))
