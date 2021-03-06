# ########################################################################################
#  OSIS stands for Open Student Information System. It's an application                  #
#  designed to manage the core business of higher education institutions,                #
#  such as universities, faculties, institutes and professional schools.                 #
#  The core business involves the administration of students, teachers,                  #
#  courses, programs and so on.                                                          #
#                                                                                        #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)    #
#                                                                                        #
#  This program is free software: you can redistribute it and/or modify                  #
#  it under the terms of the GNU General Public License as published by                  #
#  the Free Software Foundation, either version 3 of the License, or                     #
#  (at your option) any later version.                                                   #
#                                                                                        #
#  This program is distributed in the hope that it will be useful,                       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                         #
#  GNU General Public License for more details.                                          #
#                                                                                        #
#  A copy of this license - GNU General Public License - is available                    #
#  at the root of the source code of this program.  If not,                              #
#  see http://www.gnu.org/licenses/.                                                     #
# ########################################################################################
from django.conf import settings
from django.db.models import OuterRef, Exists
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.business.education_groups import perms as education_group_perms
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import build_current_entity_version_structure_in_memory, EntityVersion
from base.models.enums import education_group_categories
from base.models.enums.education_group_types import MiniTrainingType, GroupType, TrainingType
from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import GroupElementYear, fetch_row_sql
from base.models.prerequisite_item import PrerequisiteItem
from program_management.business.group_element_years.management import EDUCATION_GROUP_YEAR, LEARNING_UNIT_YEAR


# TODO: Remove this class because will not be used any more !
class EducationGroupHierarchy:
    """ Use to generate json from a list of education group years compatible with jstree """
    element_type = EDUCATION_GROUP_YEAR

    _cache_hierarchy = None
    _cache_structure = None
    _cache_entity_parent_root = None

    def __init__(self, root: EducationGroupYear, link_attributes: GroupElementYear = None,
                 cache_hierarchy: dict = None, tab_to_show: str = None, pdf_content: bool = False,
                 max_block: int = 0,
                 cache_structure=None,
                 cache_entity_parent_root: str = None,
                 exclude_options: bool = False,
                 parent_path: str = None):

        self.children = []
        self.included_group_element_years = []
        self.root = root
        self.group_element_year = link_attributes
        self.reference = self.group_element_year.link_type == LinkTypes.REFERENCE.name \
            if self.group_element_year else False
        self.icon = self._get_icon()
        self._cache_hierarchy = cache_hierarchy
        self._cache_structure = cache_structure
        self._cache_entity_parent_root = cache_entity_parent_root
        self.tab_to_show = tab_to_show
        self.pdf_content = pdf_content
        self.max_block = max_block
        self.exclude_options = exclude_options
        self.path = self._construct_path(parent_path)

        if not self.pdf_content or \
                (not (self.group_element_year and
                      self.group_element_year.child.type == GroupType.MINOR_LIST_CHOICE.name)):
            self.generate_children()

        self.modification_perm = ModificationPermission(self.root, self.group_element_year)
        self.attach_perm = AttachPermission(self.root, self.group_element_year)
        self.detach_perm = DetachPermission(self.root, self.group_element_year)

    def _construct_path(self, parent_path: str):
        if not parent_path:
            return "{}".format(self.root.id)

        path = "{parent_path}_{node_id}".format(parent_path=parent_path, node_id=self.group_element_year.child.id)
        return path

    @property
    def cache_hierarchy(self):
        if self._cache_hierarchy is None:
            self._cache_hierarchy = self._init_cache()
        return self._cache_hierarchy

    @property
    def cache_structure(self):
        if self._cache_structure is None:
            self._cache_structure = build_current_entity_version_structure_in_memory()
        return self._cache_structure

    @property
    def cache_entity_parent_root(self) -> EntityVersion:
        if self._cache_entity_parent_root is None:
            self._cache_entity_parent_root = self.root.management_entity.most_recent_entity_version
        return self._cache_entity_parent_root

    def _init_cache(self):
        return fetch_all_group_elements_in_tree(self.education_group_year,
                                                self.get_queryset(),
                                                self.exclude_options) or {}

    def generate_children(self):

        for group_element_year in self.cache_hierarchy.get(self.education_group_year.id) or []:
            self._check_max_block(group_element_year.block)
            if group_element_year.child_branch and group_element_year.child_branch != self.root:
                node = EducationGroupHierarchy(self.root, group_element_year,
                                               cache_hierarchy=self.cache_hierarchy,
                                               tab_to_show=self.tab_to_show,
                                               pdf_content=self.pdf_content,
                                               max_block=self.max_block,
                                               cache_structure=self.cache_structure,
                                               cache_entity_parent_root=self.cache_entity_parent_root,
                                               parent_path=self.path)
                self._check_max_block(node.max_block)
                self.included_group_element_years.extend(node.included_group_element_years)
            elif group_element_year.child_leaf:
                node = NodeLeafJsTree(self.root, group_element_year, cache_hierarchy=self.cache_hierarchy,
                                      tab_to_show=self.tab_to_show, cache_structure=self.cache_structure,
                                      cache_entity_parent_root=self.cache_entity_parent_root,
                                      parent_path=self.path)

            else:
                continue

            self.children.append(node)
            self.included_group_element_years.append(group_element_year)

    def get_queryset(self):
        has_prerequisite = PrerequisiteItem.objects.filter(
            prerequisite__education_group_year__id=self.root.id,
            prerequisite__learning_unit_year__id=OuterRef("child_leaf__id"),
        )

        is_prerequisite = PrerequisiteItem.objects.filter(
            learning_unit__learningunityear__id=OuterRef("child_leaf__id"),
            prerequisite__education_group_year=self.root.id,
        )

        return GroupElementYear.objects.all() \
            .annotate(has_prerequisite=Exists(has_prerequisite)) \
            .annotate(is_prerequisite=Exists(is_prerequisite)) \
            .select_related('child_branch__academic_year',
                            'child_branch__education_group_type',
                            'child_branch__administration_entity',
                            'child_branch__management_entity',
                            'child_leaf__academic_year',
                            'child_leaf__learning_container_year',
                            'child_leaf__learning_container_year__requirement_entity',
                            'child_leaf__learning_container_year__allocation_entity',
                            'child_leaf__proposallearningunit',
                            'child_leaf__externallearningunityear',
                            'child_leaf__learning_unit',
                            'parent')\
            .prefetch_related('child_branch__administration_entity__entityversion_set',
                              'child_branch__management_entity__entityversion_set',
                              'child_leaf__learning_container_year__requirement_entity__entityversion_set',
                              'child_leaf__learning_container_year__allocation_entity__entityversion_set',
                              'child_leaf__learningcomponentyear_set')\
            .order_by("order", "parent__partial_acronym")

    def to_list(self, flat=False, pruning_function=None):
        """ Generate list of group_element_year without reference link
        @:param flat: return a flat list
        @:param pruning_function: Allow to prune the tree
        """
        result = []
        _children = filter(pruning_function, self.children) if pruning_function else self.children

        for child in _children:
            child_list = child.to_list(flat=flat, pruning_function=pruning_function)

            if child.reference:
                result.extend(child_list)
            else:
                result.append(child.group_element_year)
                if child_list:
                    result.extend(child_list) if flat else result.append(child_list)
        return result

    def _get_icon(self):
        if self.reference:
            return static('img/reference.jpg')

    @property
    def education_group_year(self):
        return self.root if not self.group_element_year else self.group_element_year.child_branch

    def url_group_to_parent(self):
        return "?group_to_parent=" + str(self.group_element_year.pk if self.group_element_year else 0)

    def get_url(self):
        default_url = reverse('education_group_read', args=[self.root.pk, self.education_group_year.pk])
        add_to_url = ""
        urls = {
            'show_identification': self.__get_base_url('education_group_read'),
            'show_diploma': self.__get_base_url('education_group_diplomas'),
            'show_administrative': self.__get_base_url('education_group_administrative'),
            'show_content': self.__get_base_url('education_group_content'),
            'show_utilization': self.__get_base_url('education_group_utilization'),
            'show_general_information': self.__get_base_url('education_group_general_informations'),
            'show_skills_and_achievements': self.__get_base_url('education_group_skills_achievements'),
            'show_admission_conditions': self.__get_base_url('education_group_year_admission_condition_edit'),
            None: default_url
        }

        return self._construct_url(add_to_url, urls)

    def _construct_url(self, add_to_url, urls):
        try:
            url = urls[self.tab_to_show]
        except KeyError:
            self.tab_to_show = None
            url = urls[self.tab_to_show]
        finally:
            if self.tab_to_show:
                add_to_url = "&tab_to_show=" + self.tab_to_show
            return url + self.url_group_to_parent() + add_to_url

    def __get_base_url(self, view_name):
        return reverse(view_name, args=[self.root.pk, self.education_group_year.pk])

    def get_option_list(self):
        def pruning_function(node):
            return node.group_element_year.child_branch and \
                   node.group_element_year.child_branch.education_group_type.name not in \
                   [GroupType.FINALITY_120_LIST_CHOICE.name, GroupType.FINALITY_180_LIST_CHOICE.name]

        return [
            element.child_branch for element in self.to_list(flat=True, pruning_function=pruning_function)
            if element.child_branch.education_group_type.name == MiniTrainingType.OPTION.name
        ]

    def get_finality_list(self):
        return [
            element.child_branch for element in self.to_list(flat=True)
            if element.child_branch and element.child_branch.education_group_type.name in TrainingType.finality_types()
        ]

    def get_learning_unit_year_list(self):
        return [element.child_leaf for element in self.to_list(flat=True) if element.child_leaf]

    def _check_max_block(self, group_element_year_block):
        if group_element_year_block:
            block = str(group_element_year_block)[-1:]
            if int(block) > self.max_block:
                self.max_block = int(block)

    def get_main_parent(self, edg_id: int):
        for gey in self.cache_hierarchy.get(edg_id, list()):
            if gey.parent:
                if gey.parent.education_group_type.category in [education_group_categories.TRAINING,
                                                                education_group_categories.MINI_TRAINING] or \
                        gey.parent and gey.parent.education_group_type.name == GroupType.COMPLEMENTARY_MODULE.name:
                    return gey.parent
                else:
                    return self.get_main_parent(self._get_parent_in_hierarchy(gey))
            else:
                continue
        return None

    def _get_parent_in_hierarchy(self, gey):
        parent_in_tree = None
        for parent in gey.parent.direct_parents_of_branch:
            if self.cache_hierarchy.get(parent.id):
                parent_in_tree = parent.id
                break
        return parent_in_tree


class NodeLeafJsTree(EducationGroupHierarchy):
    element_type = LEARNING_UNIT_YEAR

    @property
    def learning_unit_year(self):
        if self.group_element_year:
            return self.group_element_year.child_leaf

    @property
    def education_group_year(self):
        return


class LinkActionPermission:
    def __init__(self, root: EducationGroupYear, link: GroupElementYear):
        self.root = root
        self.link = link
        self.errors = []

    def is_permitted(self):
        return len(self.errors) == 0


class AttachPermission(LinkActionPermission):
    def is_permitted(self):
        self._check_year_is_editable()
        self._check_if_leaf()
        return super().is_permitted()

    # FIXME :: DEPRECATED - Use MinimumEditableYearValidator
    def _check_year_is_editable(self):
        if not education_group_perms._is_year_editable(self.root, False):
            self.errors.append(
                str(_("Cannot perform action on a education group before %(limit_year)s") % {
                    "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION
                })
            )

    # FIXME :: DEPRECATED - Use ParentIsNotLeafValidator
    def _check_if_leaf(self):
        if self.link and self.link.child_leaf:
            self.errors.append(
                str(_("Cannot add any element to learning unit"))
            )


class DetachPermission(LinkActionPermission):
    def is_permitted(self):
        self._check_year_is_editable()
        self._check_if_root()
        self._check_if_prerequisites()
        return super().is_permitted()

    # FIXME :: DEPRECATED - Use MinimumEditableYearValidator
    def _check_year_is_editable(self):
        if not education_group_perms._is_year_editable(self.root, False):
            self.errors.append(
                str(_("Cannot perform action on a education group before %(limit_year)s") % {
                    "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION
                })
            )

    # FIXME :: DEPRECATED - Use DetachRootForbiddenValidator
    def _check_if_root(self):
        if self.link is None:
            self.errors.append(
                str(_("Cannot perform detach action on root."))
            )

    def _check_if_prerequisites(self):
        if self.link and (self.link.has_prerequisite or self.link.is_prerequisite):
            self.errors.append(
                str(_("Cannot detach due to prerequisites."))
            )


class ModificationPermission(LinkActionPermission):
    def is_permitted(self):
        self._check_year_is_editable()
        self._check_if_root()
        return super().is_permitted()

    # FIXME :: DEPRECATED - Use MinimumEditableYearValidator
    def _check_year_is_editable(self):
        if not education_group_perms._is_year_editable(self.root, False):
            self.errors.append(
                str(_("Cannot perform action on a education group before %(limit_year)s") % {
                    "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION
                })
            )

    def _check_if_root(self):
        if self.link is None:
            self.errors.append(
                str(_("Cannot perform modification action on root."))
            )


#  DEPRECATED remove this function when EducationGroupHierarchy is removed
def fetch_all_group_elements_in_tree(root: EducationGroupYear, queryset, exclude_options=False) -> dict:
    if queryset.model != GroupElementYear:
        raise AttributeError("The querySet arg has to be built from model {}".format(GroupElementYear))

    elements = fetch_row_sql([root.id])

    distinct_group_elem_ids = {elem['id'] for elem in elements}
    queryset = queryset.filter(pk__in=distinct_group_elem_ids)

    group_elems_by_parent_id = {}  # Map {<EducationGroupYear.id>: [GroupElementYear, GroupElementYear...]}
    for group_elem_year in queryset:
        if exclude_options and group_elem_year.child_branch and \
                group_elem_year.child_branch.education_group_type.name == GroupType.OPTION_LIST_CHOICE.name:
            if EducationGroupYear.hierarchy.filter(pk=group_elem_year.child_branch.pk).get_parents(). \
                        filter(education_group_type__name__in=TrainingType.finality_types()).exists():
                continue
        parent_id = group_elem_year.parent_id
        group_elems_by_parent_id.setdefault(parent_id, []).append(group_elem_year)
    return group_elems_by_parent_id
