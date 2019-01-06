##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import mock

from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from waffle.testutils import override_flag

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import CentralManagerFactory
from base.tests.factories.prerequisite_item import PrerequisiteItemFactory


@override_flag('education_group_update', active=True)
class TestDetach(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        cls.group_element_year = GroupElementYearFactory(parent=cls.education_group_year)
        cls.person = CentralManagerFactory()
        cls.person.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))
        cls.url = reverse("education_groups_management")
        cls.post_valid_data = {
            "root_id": cls.education_group_year.id,
            "element_id": cls.education_group_year.id,
            "group_element_year_id": cls.group_element_year.id,
            'action': 'detach',
        }

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_edit_case_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.post_valid_data)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    @override_flag('education_group_update', active=False)
    def test_detach_case_flag_disabled(self):
        response = self.client.post(self.url, data=self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
        self.assertTemplateUsed(response, "page_not_found.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=False)
    def test_detach_case_user_not_have_access(self, mock_permission):
        response = self.client.post(self.url, data=self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group", return_value=True)
    def test_detach_case_get_with_ajax_success(self, mock_permission):
        response = self.client.get(reverse("group_element_year_delete", args=[
            self.education_group_year.id,
            self.education_group_year.id,
            self.group_element_year.id
        ]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "education_group/group_element_year/confirm_detach_inner.html")

    @mock.patch("base.business.group_element_years.management.is_min_child_reached")
    @mock.patch("base.models.group_element_year.GroupElementYear.delete")
    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_detach_case_post_success(self, mock_permission, mock_delete, mock_is_min_child_reached):
        mock_permission.return_value = True
        mock_is_min_child_reached.return_value = False
        http_referer = reverse('education_group_read', args=[
            self.education_group_year.id,
            self.education_group_year.id
        ])
        response = self.client.post(reverse("group_element_year_delete", args=[
            self.education_group_year.id,
            self.education_group_year.id,
            self.group_element_year.id
        ]), follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # response = self.client.post(self.url, data=self.post_valid_data, follow=True, HTTP_REFERER=http_referer)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        print(response)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        print(messages)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {})
        self.assertRedirects(response, http_referer)
        self.assertTrue(mock_delete.called)


@override_flag('education_group_update', active=True)
class TestDetachLearningUnitPrerequisite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        cls.luy = LearningUnitYearFactory()
        cls.group_element_year_root = GroupElementYearFactory(
            child_branch=cls.education_group_year
        )
        cls.group_element_year = GroupElementYearFactory(
            parent=cls.education_group_year,
            child_branch=None,
            child_leaf=cls.luy
        )
        cls.person = CentralManagerFactory()
        cls.person.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))
        cls.url = reverse("education_groups_management")
        cls.post_valid_data = {
            "root_id": cls.education_group_year.id,
            "element_id": cls.luy.id,
            "group_element_year_id": cls.group_element_year.id,
            'action': 'detach',
        }

    def setUp(self):
        self.client.force_login(self.person.user)

    @mock.patch("base.models.group_element_year.GroupElementYear.delete")
    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_detach_case_learning_unit_being_prerequisite(self, mock_permission, mock_delete):
        mock_permission.return_value = True

        PrerequisiteItemFactory(
            prerequisite__education_group_year=self.group_element_year_root.parent,
            learning_unit=self.luy.learning_unit
        )

        http_referer = reverse('education_group_read', args=[
            self.education_group_year.id,
            self.education_group_year.id
        ])

        response = self.client.post(self.url, data=self.post_valid_data, follow=True, HTTP_REFERER=http_referer)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(
            messages[0],
            _("Cannot detach learning unit %(acronym)s as it has a prerequisite or it is a prerequisite.") % {
                "acronym": self.luy.acronym}
        )
        self.assertFalse(mock_delete.called)

    @mock.patch("base.models.group_element_year.GroupElementYear.delete")
    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_detach_case_learning_unit_having_prerequisite(self, mock_permission, mock_delete):
        mock_permission.return_value = True

        PrerequisiteItemFactory(
            prerequisite__learning_unit_year=self.luy,
            prerequisite__education_group_year=self.group_element_year_root.parent
        )

        http_referer = reverse('education_group_read', args=[
            self.education_group_year.id,
            self.education_group_year.id
        ])

        response = self.client.post(self.url, data=self.post_valid_data, follow=True, HTTP_REFERER=http_referer)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(
            messages[0],
            _("Cannot detach learning unit %(acronym)s as it has a prerequisite or it is a prerequisite.") % {
                "acronym": self.luy.acronym}
        )
        self.assertFalse(mock_delete.called)
