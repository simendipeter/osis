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

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from base.models.enums.education_group_types import TrainingType, GroupType
from program_management.ddd.validators._has_or_is_prerequisite import IsPrerequisiteValidator, HasPrerequisiteValidator
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeGroupYearFactory
from program_management.tests.ddd.factories.prerequisite import cast_to_prerequisite
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory

from program_management.tests.ddd.repositories.test_delete_tree_version import build_version_content
from django.test import TestCase

from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from education_group.models.group_year import GroupYear
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementGroupYearFactory
from program_management.tests.ddd.repositories.test_delete_tree_version import EDUCATION_GROUP_VERSION
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from program_management.ddd.validators._delete_version import DeleteVersionValidator


class TestDeleteVersionValidator(TestCase):

    def setUp(self):
        """
            (education_group_version)
            root_node
            |-link_level_1
              |-link_level_2
                |-- leaf
        """
        self.data = {}
        self.academic_year = AcademicYearFactory()
        self.previous_academic_year = AcademicYearFactory(year=self.academic_year.year - 1)
        self.next_academic_year = AcademicYearFactory(year=self.academic_year.year+1)

        self.data.update(build_version_content(self.academic_year))
        self.data.update(build_version_content(self.next_academic_year))
        self.data.update(build_version_content(self.previous_academic_year))

    def test_validator_has_not_offer_enrollments(self):
        education_group_version = self.data.get(self.academic_year).get(EDUCATION_GROUP_VERSION)
        validator = DeleteVersionValidator(education_group_versions=[education_group_version])
        self.assertTrue(validator.is_valid())
        self.assertEqual(len(validator.messages), 0)
        # self.assertListEqual(validator.messages, [])

    def test_validator_has_offer_enrollments(self):
        education_group_version = self.data.get(self.academic_year).get(EDUCATION_GROUP_VERSION)
        offer_enrollments = OfferEnrollmentFactory.create_batch(
            3,
            education_group_year=education_group_version.offer,
        )

        education_group_version = self.data.get(self.academic_year).get(EDUCATION_GROUP_VERSION)
        validator = DeleteVersionValidator(education_group_versions=[education_group_version])
        self.assertFalse(validator.is_valid())
        self.assertEqual(len(validator.messages), 1)

    def test_other(self):
        # TODO test les autres cas empechant la suppression
        # Recupérer ce qui existe dans class TestHaveContents(TestCase):
