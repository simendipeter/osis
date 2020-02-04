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

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Value, Case, When, IntegerField, CharField

from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear
from program_management.domain import node
from program_management.models.enums import node_type


def fetch_by_type(type, element_id: int) -> node.Node:
    if type == node_type.EDUCATION_GROUP:
        return fetch_node_education_group_year(element_id)
    elif type == node_type.LEARNING_UNIT:
        return fetch_node_learning_unit_year(element_id)


def fetch_node_education_group_year(node_id: int) -> node.Node:
    try:
        node_data = __fetch_multiple_node_education_group_year([node_id])[0]
        return node.factory.get_node(**node_data)
    except IndexError:
        raise node.NodeNotFoundException


def fetch_node_learning_unit_year(node_id: int) -> node.Node:
    try:
        node_data = __fetch_multiple_node_learning_unit_year([node_id])[0]
        return node.factory.get_node(**node_data)
    except IndexError:
        raise node.NodeNotFoundException


def fetch_multiple(element_ids: List[int]) -> List[node.Node]:
    aggregate_qs = GroupElementYear.objects.filter(pk__in=element_ids)\
        .annotate(
            node_type=Case(
                When(child_branch_id__isnull=False, then=Value(node_type.EDUCATION_GROUP)),
                When(child_leaf_id__isnull=False, then=Value(node_type.LEARNING_UNIT)),
                default=Value('Unknown'),
                output_field=CharField()
            ),
            node_id=Case(
                When(child_branch_id__isnull=False, then=F('child_branch_id')),
                When(child_leaf_id__isnull=False, then=F('child_leaf_id')),
                default=Value(-1),
                output_field=IntegerField()
            ),
        ).values('node_type').annotate(node_ids=ArrayAgg('node_id')).exclude(node_type='Unknown')

    union_qs = None
    for result_aggregate in aggregate_qs:
        qs_function = {
            node_type.EDUCATION_GROUP: __fetch_multiple_node_education_group_year,
            node_type.LEARNING_UNIT: __fetch_multiple_node_learning_unit_year,
        }[result_aggregate['node_type']]
        qs = qs_function(result_aggregate['node_ids']) \
            .values('node_id', 'type', 'acronym', 'title', 'year', 'proposal_type')

        union_qs = qs if union_qs is None else union_qs.union(qs)

    if union_qs is not None:
        return [node.factory.get_node(**node_data) for node_data in union_qs]
    return[]


def __fetch_multiple_node_education_group_year(node_group_year_ids: List[int]):
    return EducationGroupYear.objects.filter(pk__in=node_group_year_ids).annotate(
        node_id=F('pk'),
        type=Value(node_type.EDUCATION_GROUP, output_field=CharField()),
        node_acronym=F('acronym'),
        node_title=F('title'),
        year=F('academic_year__year'),
        proposal_type=Value(None, output_field=CharField())
    ).values('node_id', 'type', 'year', 'proposal_type', 'node_acronym', 'node_title')\
     .annotate(title=F('node_title'), acronym=F('node_acronym'))


def __fetch_multiple_node_learning_unit_year(node_learning_unit_year_ids: List[int]):
    return LearningUnitYear.objects.filter(pk__in=node_learning_unit_year_ids).annotate_full_title().annotate(
        node_id=F('pk'),
        type=Value(node_type.LEARNING_UNIT, output_field=CharField()),
        node_acronym=F('acronym'),
        node_title=F('full_title'),
        year=F('academic_year__year'),
        proposal_type=F('proposallearningunit__type')
    ).values('node_id', 'type', 'year', 'proposal_type', 'node_acronym', 'node_title')\
     .annotate(title=F('node_title'), acronym=F('node_acronym'))