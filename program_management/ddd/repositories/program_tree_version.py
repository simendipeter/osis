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

from django.db.models import Q

from base.models.group_element_year import GroupElementYear
from osis_common.ddd import interface
from osis_common.ddd.interface import Entity
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity, ProgramTreeVersion
from program_management.ddd.repositories import load_tree
from program_management.ddd.repositories.persist_tree import __delete_links
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element


class ProgramTreeVersionRepository(interface.AbstractRepository):

    @classmethod
    def search(cls, entity_ids: Optional[List['ProgramTreeVersionIdentity']] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'ProgramTreeVersionIdentity') -> None:
        education_group_versions = EducationGroupVersion.objects\
            .select_related('root_group__element').filter(offer__acronym=entity_id.offer_acronym,
                                                          offer__academic_year__year__gte=entity_id.year,
                                                          version_name=entity_id.version_name,
                                                          is_transition=entity_id.is_transition)
        #TODO je pense que le validator doit être appelé ailleurs
        # if DeleteVersionValidator(education_group_versions=education_group_versions).validate():
        _delete_version_trees(education_group_versions)

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


def _delete_by_links(tree, node: Node, elements_id):
    for link in node.children:
        elements_id = [link.parent.pk, link.child.pk]
        delete_group_element_year(link)
        __delete_links(tree, link.child)
        _delete_by_links(tree, link.child, elements_id)
    return elements_id


def load_version(acronym: str, year: int, version_name: str, transition: bool) -> 'ProgramTreeVersion':

    education_group_version = EducationGroupVersion.objects\
        .filter(root_group__element__isnull=False)\
        .select_related('root_group__element').get(
            offer__acronym=acronym,
            offer__academic_year__year=year,
            version_name=version_name,
            is_transition=transition
        )

    return load_tree.load(education_group_version.root_group.element.pk)


def delete_group_element_year(link):
    group_element_year = GroupElementYear.objects.get(
        parent_element_id=link.parent.pk,
        child_element_id=link.child.pk
    )

    group_element_year.delete()

    if not GroupElementYear.objects.filter(
            Q(parent_element__id__in=[link.parent.pk, link.child.pk]) | Q(child_element__id__in=[link.child.pk, link.parent.pk])
    ).exists():
        for element in Element.objects.filter(pk__in=[link.parent.pk, link.child.pk]):
            element.delete()


def _delete_version_trees(education_group_versions):

    for education_group_version in education_group_versions:
        start(education_group_version.root_group, education_group_version)

    delete_education_group_versions(education_group_versions)
    return None


def delete_education_group_versions(education_group_versions):
    for education_group_version in education_group_versions:
        group_year_to_delete = education_group_version.root_group
        education_group_version.delete()
        if not Element.objects.filter(group_year=group_year_to_delete).exists():
            group_year_to_delete.delete()


def start(group_year, education_group_version):
    """
    This function will delete group year and the default structure
    """
    child_links_to_delete = GroupElementYear.objects.filter(
        parent_element__group_year=group_year
    )

    for child_link in child_links_to_delete:
        # Remove link between parent/child
        element_parent = child_link.parent_element
        element_child = child_link.child_element
        child_link.delete()
        _delete_elements([element_child, element_parent])

        start(child_link.child_element.group_year, education_group_version)

    if not GroupElementYear.objects.filter(child_element__group_year=group_year).exists() and \
            not EducationGroupVersion.objects.filter(root_group=group_year).exists():
        # No reuse
        group_year.delete()


def _delete_elements(elt_ids):
    for elt in elt_ids:
        if not GroupElementYear.objects.filter(child_element__pk=elt.id).exists() and \
                not GroupElementYear.objects.filter(parent_element__pk=elt.id).exists():
            # No reuse
            elt.delete()
