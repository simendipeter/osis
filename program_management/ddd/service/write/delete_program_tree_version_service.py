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
from program_management.ddd.command import CreateProgramTreeVersionCommand, DeleteProgramTreeVersionCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity, ProgramTreeVersionBuilder
from program_management.ddd.repositories import load_tree
from program_management.ddd.domain.node import NodeLearningUnitYear, NodeGroupYear


def delete_program_tree_version(command: DeleteProgramTreeVersionCommand) -> ProgramTreeVersionIdentity:
    program_tree_version_to_delete = load_tree.load_version(
        acronym=command.offer_acronym,
        year=command.year,
        version_name=command.version_name,
        transition=command.is_transition
    )
    for path, child_node in program_tree_version_to_delete.get_tree().root_node.descendents.items():
        if isinstance(child_node, NodeGroupYear):
            print(child_node)

    return None


    # @classmethod
    # def delete_with_tree(cls, entity_id: 'ProgramTreeVersionIdentity') -> None:
    #     education_group_versions = EducationGroupVersion.objects \
    #         .select_related('root_group__element').filter(offer__acronym=entity_id.offer_acronym,
    #                                                    offer__academic_year__year__gte=entity_id.year,
    #                                                    version_name=entity_id.version_name,
    #                                                    is_transition=entity_id.is_transition)
    #     for education_group_version in education_group_versions:
    #         entity_id.year = education_group_version.offer.academic_year.year
    #         # TODO : version1  : with tree
    #         tree = cls.get(entity_id)
    #         elements_id = []
    #         elements_id = update_or_create_links(tree, tree.root_node, elements_id)
    #         print(elements_id)
    #         delete_elements(elements_id)
    #
    #         # education_group_version.root_group.delete()
    #         education_group_version.delete()
