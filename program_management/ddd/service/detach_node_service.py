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
from typing import List

from django.utils.translation import gettext as _

from base.ddd.utils.validation_message import BusinessValidationMessageList
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree import PATH_SEPARATOR
from program_management.ddd.repositories import load_tree, persist_tree
from program_management.ddd.service import prerequisite_service
from program_management.ddd.validators._path_validator import PathValidator


def detach_node(path_to_detach: 'Path', commit=True) -> BusinessValidationMessageList:
    validator = PathValidator(path_to_detach)
    if not validator.is_valid():
        return BusinessValidationMessageList(messages=validator.messages)

    root_id = int(path_to_detach.split(PATH_SEPARATOR)[0])

    working_tree = load_tree.load(root_id)
    node_to_detach = working_tree.get_node(path_to_detach)

    is_valid, messages = working_tree.detach_node(path_to_detach)
    messages += prerequisite_service.check_is_prerequisite_in_trees_using_node(node_to_detach=node_to_detach)

    if is_valid and commit:
        persist_tree.persist(working_tree)  # TODO :: unit tests persist !

    return BusinessValidationMessageList(messages=messages)
