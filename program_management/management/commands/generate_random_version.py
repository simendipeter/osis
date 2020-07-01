# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import copy
import random
import string

from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear
from education_group.models.group_year import GroupYear
from program_management.models.education_group_version import EducationGroupVersion
from program_management.models.element import Element


def generate_new_version(from_acronym: str, from_year: int, version_name: str):
    from_version = EducationGroupVersion.objects.get(
        offer__acronym=from_acronym,
        offer__academic_year__year=from_year,
        version_name='',
        is_transition=False
    )

    new_root_group = copy.deepcopy(from_version.root_group.group)
    new_root_group.id = None
    new_root_group.start_year = from_version.offer.academic_year
    new_root_group.end_year = from_version.offer.academic_year
    new_root_group.save()

    new_root_group_year = copy.deepcopy(from_version.root_group)
    new_root_group_year.id = None
    # Keep same subdivision (Validator check)
    new_root_group_year.partial_acronym = generate_partial_acronym()[:-1] + new_root_group_year.partial_acronym[-1]
    new_root_group_year.group = new_root_group
    new_root_group_year.save()

    Element.objects.create(group_year=new_root_group_year)
    new_version = EducationGroupVersion.objects.create(
        offer=from_version.offer,
        root_group=new_root_group_year,
        version_name=version_name,
        is_transition=False,
        title_en="[GENERATED - VERSION ]{}".format(from_version.title_en),
        title_fr="[GENERATED - VERSION ]{}".format(from_version.title_fr),
    )
    generate_structure(from_version, new_version)


def generate_structure(from_education_group_version, to_education_group_version):
    # System Group (level 1) should be different
    from_systems_groups = GroupElementYear.objects.select_related(
        'child_element__group_year'
    ).filter(
        parent_element=from_education_group_version.root_group.element
    )
    for from_system_group in from_systems_groups:
        new_group_year = __create_group_year(from_system_group.child_element.group_year)

        new_link_root_level_1 = copy.deepcopy(from_system_group)
        new_link_root_level_1.id = None
        new_link_root_level_1.parent_element = to_education_group_version.root_group.element
        new_link_root_level_1.child_element = Element.objects.create(group_year=new_group_year)

        # RANDOM VALUE - column will be removed after migration
        new_link_root_level_1.parent_id = EducationGroupYear.objects.filter(
            groupelementyear__isnull=True
        ).first().pk
        new_link_root_level_1.comment = "[GENERATED - VERSION]{}".format(from_system_group.comment)
        new_link_root_level_1.comment_english = "[GENERATED - VERSION]{}".format(from_system_group.comment_english)
        new_link_root_level_1.save()

        ######################################
        # LEVEL 2 randomize take existing
        from_level_2_link = GroupElementYear.objects.select_related(
            'child_element__group_year'
        ).filter(parent_element=from_system_group.child_element)
        for from_lvl_2_link in from_level_2_link:
            child_element = from_lvl_2_link.child_element
            if child_element.group_year is not None:
                element = GroupYear.objects.filter(
                    education_group_type=child_element.group_year.education_group_type,
                    academic_year=child_element.group_year.academic_year,
                    element__isnull=False,
                ).order_by("?").first().element
            elif from_lvl_2_link.child_element.learning_unit_year is not None:
                element = LearningUnitYear.objects.filter(
                    academic_year=child_element.learning_unit_year.academic_year,
                    element__isnull=False,
                ).order_by("?").first().element

            from_lvl_2_link.id = None
            from_lvl_2_link.parent_element = new_link_root_level_1.child_element
            from_lvl_2_link.child_element = element

            # RANDOM VALUE - column will be removed after migration
            from_lvl_2_link.parent_id = EducationGroupYear.objects.filter(
                groupelementyear__isnull=True
            ).first().pk
            from_lvl_2_link.comment = "[GENERATED - VERSION]{}".format(from_lvl_2_link.comment)
            from_lvl_2_link.comment_english = "[GENERATED - VERSION]{}".format(from_lvl_2_link.comment_english)
            from_lvl_2_link.save()


def __create_group_year(from_group_year):
    new_root_group = copy.deepcopy(from_group_year.group)
    new_root_group.id = None
    new_root_group.start_year = from_group_year.academic_year
    new_root_group.end_year = from_group_year.academic_year
    new_root_group.save()

    new_root_group_year = copy.deepcopy(from_group_year)
    new_root_group_year.id = None
    # Keep same subdivision (Validator check)
    new_root_group_year.partial_acronym = generate_partial_acronym()[:-1] + \
        from_group_year.partial_acronym[-1]
    new_root_group_year.group = new_root_group
    new_root_group_year.save()
    return new_root_group_year


def generate_partial_acronym():
    sigle_ele = "".join(random.sample(string.ascii_uppercase, k=4))
    cnum = "".join(random.sample(string.digits, k=3))
    subdivision = random.choice(string.ascii_uppercase)
    return "L{sigle_ele}{cnum}{subdivision}".format(
        sigle_ele=sigle_ele,
        cnum=cnum,
        subdivision=subdivision
    )


generate_new_version('GEST2M', 2020, 'CEMS')
generate_new_version('BIR1BA', 2020, 'CEMS')
