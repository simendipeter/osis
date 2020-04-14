# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django.test import SimpleTestCase

from program_management.ddd.validators._prerequisites_items import PrerequisiteItemsValidator
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory


class TestPrerequisiteItemsValidator(SimpleTestCase):
    def test_should_be_valid_when_empty_prerequisite_string(self):
        prerequisite_string = ""
        codes_permitted = list()
        node = NodeLearningUnitYearFactory()
        self.assertTrue(
            PrerequisiteItemsValidator(prerequisite_string, node, codes_permitted).is_valid()
        )

    def test_should_be_invalid_when_codes_used_in_prerequisite_string_are_not_permitted(self):
        prerequisite_string = "LOSIS1121 ET MARC2547"
        codes_permitted = ["LOSIS1121"]
        node = NodeLearningUnitYearFactory()
        self.assertFalse(
            PrerequisiteItemsValidator(prerequisite_string, node, codes_permitted).is_valid()
        )

    def test_should_be_invalid_when_codes_used_in_prerequisite_string_is_node_code(self):
        prerequisite_string = "LOSIS1121 ET MARC2547"
        codes_permitted = ["LOSIS1121", "MARC2547"]
        node = NodeLearningUnitYearFactory(code="LOSIS1121")
        self.assertFalse(
            PrerequisiteItemsValidator(prerequisite_string, node, codes_permitted).is_valid()
        )

    def test_should_be_valid_when_codes_used_in_prerequisite_string_are_permitted(self):
        prerequisite_string = "LOSIS1121 ET MARC2547 ET (BREM5890 OU MECK8960)"
        codes_permitted = ["LOSIS1121", "MARC2547", "MECK8960", "BREM5890"]
        node = NodeLearningUnitYearFactory()
        self.assertTrue(
            PrerequisiteItemsValidator(prerequisite_string, node, codes_permitted).is_valid()
        )
