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
from collections import Counter

from django.utils.translation import gettext as _

import osis_common.ddd.interface
from base.ddd.utils import business_validator
from program_management.ddd.business_types import *


class PasteAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    # TODO: Work with tree (ProgramTree), path (str), node_to_path (Node) because
    #       working with node_to_paste_into as instance of NODE, we can forget to load children property and
    #       validation of is_maximum_children_types_reached is done in bad way
    def __init__(self, tree: 'ProgramTree', node_to_paste: 'Node', node_to_paste_into: 'Node'):
        super(PasteAuthorizedRelationshipValidator, self).__init__()
        self.tree = tree
        self.node_to_paste = node_to_paste
        self.parent = node_to_paste_into
        self.auth_relations = tree.authorized_relationships

    def validate(self):
        exception_messages = []
        if not self.auth_relations.is_authorized(self.parent.node_type, self.node_to_paste.node_type):
            exception_messages.append(
                _("You cannot add \"%(child)s\" of type \"%(child_types)s\" "
                  "to \"%(parent)s\" of type \"%(parent_type)s\"") % {
                    'child': self.node_to_paste,
                    'child_types': self.node_to_paste.node_type.value,
                    'parent': self.parent,
                    'parent_type': self.parent.node_type.value,
                }
            )
        if self.is_maximum_children_types_reached(self.parent, self.node_to_paste):
            exception_messages.append(
                _("Cannot add \"%(child)s\" because the number of children of type(s) \"%(child_types)s\" "
                  "for \"%(parent)s\" has already reached the limit.") % {
                    'child': self.node_to_paste,
                    'child_types': self.node_to_paste.node_type.value,
                    'parent': self.parent
                }
            )
        if exception_messages:
            raise osis_common.ddd.interface.BusinessExceptions(messages=exception_messages)

    def is_maximum_children_types_reached(self, parent_node: 'Node', child_node: 'Node'):
        if not self.auth_relations.is_authorized(parent_node.node_type, child_node.node_type):
            return False
        counter = Counter(parent_node.get_children_types(include_nodes_used_as_reference=True))
        current_count = counter[child_node.node_type]
        relation = self.auth_relations.get_authorized_relationship(parent_node.node_type, child_node.node_type)
        return current_count == relation.max_count_authorized


class AuthorizedRelationshipLearningUnitValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_attach: 'Node', position_to_attach_from: 'Node'):
        super().__init__()
        self.tree = tree
        self.node_to_attach = node_to_attach
        self.position_to_attach_from = position_to_attach_from

    def validate(self):
        if not self.tree.authorized_relationships.is_authorized(
                self.position_to_attach_from.node_type,
                self.node_to_attach.node_type
        ):
            raise osis_common.ddd.interface.BusinessExceptions(
                [_("You can not attach a learning unit like %(node)s to element %(parent)s of type %(type)s.") % {
                    "node": self.node_to_attach,
                    "parent": self.position_to_attach_from,
                    "type": self.position_to_attach_from.node_type.value
                }]
            )


class DetachAuthorizedRelationshipValidator(business_validator.BusinessValidator):
    def __init__(self, tree: 'ProgramTree', node_to_detach: 'Node', detach_from: 'Node'):
        super(DetachAuthorizedRelationshipValidator, self).__init__()
        self.node_to_detach = node_to_detach
        self.detach_from = detach_from
        self.tree = tree

    def validate(self):
        minimum_children_types_reached = self._get_minimum_children_types_reached(self.detach_from, self.node_to_detach)
        if minimum_children_types_reached:
            raise osis_common.ddd.interface.BusinessExceptions([
                _("The parent must have at least one child of type(s) \"%(types)s\".") % {
                    "types": ','.join(str(node_type.value) for node_type in minimum_children_types_reached)
                }
            ])

    def _get_minimum_children_types_reached(self, parent_node: 'Node', child_node: 'Node'):
        children_types_to_check = [child_node.node_type]
        if self.tree.get_link(parent_node, child_node).is_reference():
            children_types_to_check = [link_obj.child.node_type for link_obj in child_node.children]

        counter = Counter(parent_node.get_children_types(include_nodes_used_as_reference=True))

        types_minimum_reached = []
        for child_type in children_types_to_check:
            current_count = counter[child_type]
            relation = self.tree.authorized_relationships.get_authorized_relationship(parent_node.node_type, child_type)
            if not relation:
                # FIXME :: business cass to fix (cf unit test)
                continue
            if current_count == relation.min_count_authorized:
                types_minimum_reached.append(child_type)

        return types_minimum_reached
