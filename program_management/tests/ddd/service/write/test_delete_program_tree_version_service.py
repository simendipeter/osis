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
from unittest import mock

from django.test import SimpleTestCase

from program_management.ddd.command import CreateProgramTreeVersionCommand, DeleteProgramTreeVersionCommand
from program_management.ddd.domain import program_tree_version
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.service.write import delete_program_tree_version_service


class TestDeleteProgramTreeVersionService(SimpleTestCase):
    def setUp(self) -> None:
        identity)
        TypeError: __init__()
        missing
        2
        required
        positional
        arguments: 'program_tree_identity' and 'program_tree_repository'

        entity_identity = ProgramTreeVersionIdentity(offer_acronym="toto",
                                                     year=2021,
                                                     version_name="CEMS",
                                                     is_transition=False)

        self.standard_tree_version = program_tree_version.ProgramTreeVersion(entity_identity)
    #     self.standard_tree_version = program_tree_version.ProgramTreeVersion(
    #         entity_identity,
    #         None,
    #         "title_fr",
    #         "title_en",
    #         None
    #     )

    @mock.patch("program_management.ddd.repositories.load_tree.load_version")
    def test_delete_program_tree_version_identity(self, mock_load_tree_to_delete):
        mock_load_tree_to_delete.return_value = self.standard_tree_version
        command = DeleteProgramTreeVersionCommand(offer_acronym="toto",
                                                  year=2021,
                                                  version_name='CEMS',
                                                  is_transition=False)
        result = delete_program_tree_version_service.delete_program_tree_version(command)
        self.assertIsNone(result)
        # self.assertTrue(isinstance(result, ProgramTreeVersionIdentity))
        # self.assertEqual(result.offer_acronym, command.offer_acronym)
        # self.assertEqual(result.version_name, command.version_name)
        # self.assertEqual(result.year, command.year)
        # self.assertEqual(result.is_transition, command.is_transition)
        # mock_load_tree_to_delete.assert_called_with(
        #     acronym=command.offer_acronym,
        #     year=command.year,
        #     version_name=command.version_name,
        #     transition=command.is_transition
        # )
    #
    # @mock.patch("program_management.ddd.repositories.load_tree.load_version")
    # @mock.patch.object(program_tree_version.ProgramTreeVersionBuilder, "build_from")
    # def test_load_standard_program_tree_version(self, mock_builder, mock_load_standard):
    #     mock_load_standard.return_value = self.standard_tree_version
    #     command = CreateProgramTreeVersionCommand("toto", "tata", 2021, False)
    #     result = create_program_tree_version_service.create_program_tree_version(command)
    #     mock_load_standard.assert_called_with(
    #         acronym=command.offer_acronym,
    #         year=command.year,
    #         version_name=command.version_name,
    #         transition=command.is_transition
    #     )
    #     mock_builder.assert_called_with(self.standard_tree_version, command)
    #
