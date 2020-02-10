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
from unittest.mock import PropertyMock, patch

from django.test import TestCase

from base.models.enums.link_type import LinkTypes
from program_management.ddd.contrib.validation import MessageLevel, BusinessValidationMessage
from program_management.ddd.service import attach_node_service
from program_management.ddd.validators import _validator_groups
from program_management.ddd.validators._validator_groups import AttachNodeValidatorList
from program_management.ddd.validators.authorized_relationship import AttachAuthorizedRelationshipValidator
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory

from django.utils.translation import gettext as _


class TestAttachNode(TestCase):
    validators_to_mock = {
        AttachNodeValidatorList: [BusinessValidationMessage('error message text', MessageLevel.ERROR)],
        # AttachAuthorizedRelationshipValidator: [BusinessValidationMessage('error message text', MessageLevel.ERROR)],
    }

    @classmethod
    def setUpTestData(cls):
        cls.root_node = NodeEducationGroupYearFactory()
        cls.tree = ProgramTreeFactory(root_node=cls.root_node)
        cls.root_path = str(cls.root_node.node_id)
        cls.node_to_attach = NodeEducationGroupYearFactory()

    # def setUp(self):
    #     self._mock()
    #
    # def _mock(self):
    #     for validator_class, return_messages in self.validators_to_mock.items():
    #         patcher = patch.object(validator_class, 'validate', auto_spec=True)
    #         self.addCleanup(patcher.stop)
    #         self.mock_validate = patcher.start()
    #
    #         patcher2 = patch.object(validator_class, 'messages', new_callable=PropertyMock)
    #         self.addCleanup(patcher2.stop)
    #         self.mock_messages = patcher2.start()
    #         patcher2.return_value = return_messages

    @patch.object(_validator_groups.AttachNodeValidatorList, 'validate', auto_spec=True)
    @patch.object(_validator_groups.AttachNodeValidatorList, 'messages', new_callable=PropertyMock)
    def test_validator_list_called(self, mock_messages, mock_validate):
        mock_messages.return_value = [BusinessValidationMessage('error message text', MessageLevel.ERROR)]
        result = attach_node_service.attach_node(self.tree, self.node_to_attach, self.root_path)
        self.assertEqual('error message text', result[0])

    @patch('program_management.ddd.repositories.fetch_tree.fetch_trees_from_children')
    @patch.object(_validator_groups.AttachAuthorizedRelationshipValidator, 'messages', new_callable=PropertyMock)
    @patch.object(_validator_groups.AttachAuthorizedRelationshipValidator, 'validate', auto_spec=True)
    @patch.object(_validator_groups.AttachNodeValidatorList, 'validate', auto_spec=True)
    def test_when_node_used_as_reference_is_not_valid(self, mock_validate_list, mock_validate_auth, mock_messages, mock_fetch):
        link1 = LinkFactory(child=self.root_node, link_type=LinkTypes.REFERENCE)
        link2 = LinkFactory(child=self.root_node, link_type=LinkTypes.REFERENCE)
        mock_fetch.return_value = [
            ProgramTreeFactory(root_node=link1.parent),
            ProgramTreeFactory(root_node=link2.parent)
        ]
        mock_messages.return_value = [BusinessValidationMessage('error link reference', MessageLevel.ERROR)]
        result = attach_node_service.attach_node(self.tree, self.node_to_attach, self.root_path)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].message, 'error link reference')
        self.assertEqual(result[0].level, MessageLevel.ERROR)

    @patch('program_management.ddd.repositories.fetch_tree.fetch_trees_from_children')
    @patch.object(_validator_groups.AttachAuthorizedRelationshipValidator, 'messages', new_callable=PropertyMock)
    @patch.object(_validator_groups.AttachAuthorizedRelationshipValidator, 'validate', auto_spec=True)
    @patch.object(_validator_groups.AttachNodeValidatorList, 'validate', auto_spec=True)
    def test_when_node_used_as_reference_is_valid(self, mock_validate_list, mock_validate_auth, mock_messages, mock_fetch):
        link1 = LinkFactory(child=self.root_node, link_type=LinkTypes.REFERENCE)
        link2 = LinkFactory(child=self.root_node, link_type=LinkTypes.REFERENCE)
        mock_fetch.return_value = [
            ProgramTreeFactory(root_node=link1.parent),
            ProgramTreeFactory(root_node=link2.parent)
        ]
        mock_messages.return_value = []
        result = attach_node_service.attach_node(self.tree, self.node_to_attach, self.root_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].message, _('Success message'))
        self.assertEqual(result[0].level, MessageLevel.SUCCESS)
