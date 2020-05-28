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
from django.db.models import Q

from base.models.group_element_year import GroupElementYear
from education_group.models.group_year import GroupYear
from program_management.ddd.command import DeleteProgramTreeVersionCommand
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.repositories.load_tree import load_version
from program_management.ddd.repositories.persist_tree import __delete_links
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element


def delete_program_tree_version(command: DeleteProgramTreeVersionCommand) -> ProgramTreeVersionIdentity:
    education_group_versions = EducationGroupVersion.objects \
        .select_related('root_group__element').filter(offer__acronym=command.offer_acronym,
                                                      offer__academic_year__year__gte=command.year,
                                                      version_name=command.version_name,
                                                      is_transition=command.is_transition)

    # if DeleteVersionValidator(education_group_versions=education_group_versions).validate():
    _delete_version_trees(education_group_versions)

    return None


def _delete_by_links(tree, node: Node, elements_id):
    for link in node.children:
        elements_id = [link.parent.pk, link.child.pk]
        delete_group_element_year(link)
        __delete_links(tree, link.child)
        _delete_by_links(tree, link.child, elements_id)
    return elements_id


def delete_group_element_year(link):
    group_element_year = GroupElementYear.objects.get(
        parent_element_id=link.parent.pk,
        child_element_id=link.child.pk
    )

    group_element_year.delete()

    if not GroupElementYear.objects.filter(
            Q(parent_element__id__in=[link.parent.pk, link.child.pk]) | Q(
                child_element__id__in=[link.child.pk, link.parent.pk])
    ).exists():
        for element in Element.objects.filter(pk__in=[link.parent.pk, link.child.pk]):
            element.delete()


def _delete_version_trees(education_group_versions):
    for education_group_version in education_group_versions:
        tree = load_version(education_group_version.offer.acronym,
                            education_group_version.offer.academic_year.year,
                            education_group_version.version_name,
                            education_group_version.is_transition)

        start(tree.get_tree())

    delete_education_group_versions(education_group_versions)
    return None


def delete_education_group_versions(education_group_versions):
    for education_group_version in education_group_versions:
        group_year_to_delete = education_group_version.root_group
        education_group_version.delete()
        if not Element.objects.filter(group_year=group_year_to_delete).exists():
            group_year_to_delete.delete()

#
# def start_old(group_year):
#     """
#     This function will delete group year and the default structure
#     """
#     # Attention ça reprend trop de données, il faudrait que ça ne reprenne que ce qui concerne mon educationGroupVersion
#     child_links_to_delete = GroupElementYear.objects.filter(
#         parent_element__group_year=group_year,
#         child_element__group_year__education_group_type__in=AuthorizedRelationship.objects.filter(
#             parent_type=group_year.education_group_type,
#             min_count_authorized=1
#         ).values('child_type')
#     )
#     #pas trop sûr de la partie child_element_group_year....
#     print(child_links_to_delete)
#     for child_link in child_links_to_delete:
#         print('for')
#         # Remove link between parent/child
#         element_parent = child_link.parent_element
#         element_child = child_link.child_element
#         child_link.delete()
#         _delete_elements([element_child, element_parent])
#
#         start(child_link.child_element.group_year)
#
#     if not GroupElementYear.objects.filter(child_element__group_year=group_year).exists() and \
#             not GroupElementYear.objects.filter(parent_element__group_year=group_year).exists() and \
#             not EducationGroupVersion.objects.filter(root_group=group_year).exists():
#         # No reuse
#         print('delete {}'.format(group_year.id))
#         group_year.delete()


def _delete_elements(elt_ids):
    for elt in elt_ids:
        if not GroupElementYear.objects.filter(child_element__pk=elt).exists() and \
                not GroupElementYear.objects.filter(parent_element__pk=elt).exists():
            # No reuse
            elt_to_delete = Element.objects.get(pk=elt)
            if elt_to_delete:
                elt_to_delete.delete()


def start(tree):
    """
    This function will delete group year and the default structure
    """
    group_year_ids = []
    for node in tree.get_all_nodes():
        #TODO léger doute ici...
        child_links_to_delete = GroupElementYear.objects.filter(Q(parent_element__pk=node.pk) | Q(child_element__pk=node.pk))

        elt_to_delete = Element.objects.filter(pk=node.pk).first()
        if elt_to_delete:
            group_year_ids.append(elt_to_delete.group_year.id)

        for group_element_yr_to_delete in child_links_to_delete:
            group_element_yr_to_delete.delete()
        if elt_to_delete:
            elt_to_delete.delete()

    for g in group_year_ids:
        if not GroupElementYear.objects.filter(child_element__group_year__pk=g).exists() and \
                not GroupElementYear.objects.filter(parent_element__group_year__pk=g).exists() and \
                not EducationGroupVersion.objects.filter(root_group__pk=g).exists() and \
                not Element.objects.filter(group_year__pk=g).exists():
            # No reuse
            goupr = GroupYear.objects.filter(pk=g).first()
            if goupr:
                goupr.delete()
