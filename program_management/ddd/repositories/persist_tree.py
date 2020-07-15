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
from django.db import transaction

from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import GroupElementYear
from osis_common.decorators.deprecated import deprecated
from program_management.ddd.domain import program_tree
from program_management.ddd.domain.node import Node
from program_management.ddd.repositories import _persist_prerequisite


@deprecated  # use ProgramTreeRepository.create() or .update() instead
@transaction.atomic
def persist(tree: program_tree.ProgramTree) -> None:
    __update_or_create_links(tree.root_node)
    __delete_links(tree, tree.root_node)
    _persist_prerequisite.persist(tree)


def __update_or_create_links(node: Node):
    for link in node.children:
        if link.has_changed:
            __persist_group_element_year(link)

        __update_or_create_links(link.child)


def __persist_group_element_year(link):
    group_element_year, _ = GroupElementYear.objects.update_or_create(
        parent_element_id=link.parent.pk,
        child_element_id=link.child.pk,
        defaults={
            'relative_credits': link.relative_credits,
            'min_credits': link.min_credits,
            'max_credits': link.max_credits,
            'is_mandatory': link.is_mandatory,
            'block': link.block,
            'access_condition': link.access_condition,
            'comment': link.comment,
            'comment_english': link.comment_english,
            'own_comment': link.own_comment,
            'quadrimester_derogation': link.quadrimester_derogation,
            # FIXME : Find a rules for enum in order to be consistant
            'link_type': link.link_type.name if isinstance(link.link_type, LinkTypes) else link.link_type,
            'order': link.order,

        }
    )


def __delete_links(tree: program_tree.ProgramTree, node: Node):
    for link in node._deleted_children:
        __persist_deleted_prerequisites(tree, link.child)
        __delete_group_element_year(link)
    for link in node.children:
        __delete_links(tree, link.child)


def __persist_deleted_prerequisites(tree: program_tree.ProgramTree, node: Node):
    if node.is_learning_unit():
        _persist_prerequisite._persist(tree.root_node, node)
    else:
        for child_node in node.get_all_children_as_learning_unit_nodes():
            _persist_prerequisite._persist(tree.root_node, child_node)


def __delete_group_element_year(link):
    GroupElementYear.objects.filter(pk=link.pk).delete()
