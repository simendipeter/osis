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
from typing import Optional, List

from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity, Entity
from program_management.ddd.business_types import *
from program_management.ddd.repositories import persist_tree, load_tree
from program_management.models.element import Element
from program_management.models.education_group_version import EducationGroupVersion
from program_management.ddd.domain.node import Node


class ProgramTreeVersionRepository(interface.AbstractRepository):

    @classmethod
    def search(cls, entity_ids: Optional[List['ProgramTreeVersionIdentity']] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'ProgramTreeVersionIdentity') -> None:
        tree = cls.get(entity_id)
        update_or_create_links(tree.root_node)
        # persist_tree__delete_links(tree, tree.root_node)
        # persist_tree._persist_prerequisite.persist(tree)

        return None

    @classmethod
    def create(cls, program_tree: 'ProgramTreeVersion') -> 'ProgramTreeVersionIdentity':
        raise NotImplementedError

    @classmethod
    def update(cls, program_tree: 'ProgramTreeVersion') -> 'ProgramTreeVersionIdentity':
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'ProgramTreeVersionIdentity') -> 'ProgramTreeVersion':
        return load_version(entity_id.offer_acronym, entity_id.year, entity_id.version_name, entity_id.is_transition)


def update_or_create_links(node: Node):
    for link in node.children:
        print(link)


def load_version(acronym: str, year: int, version_name: str, transition: bool) -> 'ProgramTreeVersion':

    education_group_version = EducationGroupVersion.objects\
        .filter(root_group__element__isnull=False)\
        .select_related('root_group__element').get(
            offer__acronym=acronym,
            offer__academic_year__year=year,
            version_name=version_name,
            is_transition=transition
        )
    print(education_group_version.root_group.element.pk)

    tree = load_tree.load(education_group_version.root_group.element.pk)
    identity = ProgramTreeVersionIdentity(offer_acronym=acronym,
                               year=year,
                               version_name=version_name,
                               is_transition=transition)

    return ProgramTreeVersion(
        tree,
        entity_identity=identity
    )
