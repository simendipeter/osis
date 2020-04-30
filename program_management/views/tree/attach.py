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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import RedirectView, CreateView, FormView

from base.ddd.utils.validation_message import BusinessValidationMessage
from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import ElementCache
from base.views.common import display_warning_messages, display_business_messages, display_error_messages
from base.views.education_groups import perms
from base.views.mixins import AjaxTemplateMixin
from program_management.business.group_element_years import management
from program_management.business.group_element_years.attach import AttachEducationGroupYearStrategy, \
    AttachLearningUnitYearStrategy
from program_management.business.group_element_years.detach import DetachEducationGroupYearStrategy, \
    DetachLearningUnitYearStrategy
from program_management.business.group_element_years.management import fetch_elements_selected, fetch_source_link
from program_management.ddd.repositories import load_authorized_relationship, load_node
from program_management.ddd.service import attach_node_service
from program_management.forms.tree.attach import AttachNodeFormSet, GroupElementYearForm, \
    BaseGroupElementYearFormset, attach_form_factory
from program_management.models.enums.node_type import NodeType
from program_management.views.generic import GenericGroupElementYearMixin


class AttachMultipleNodesView(LoginRequiredMixin, AjaxTemplateMixin, FormView):
    template_name = "tree/attach/attach_inner.html"

    @cached_property
    def root_id(self):
        return self.kwargs["root_id"]

    @cached_property
    def parent_node(self):
        parent_node_id = int(self.request.GET["path"].split("|")[-1])
        return load_node.load_by_type(NodeType.EDUCATION_GROUP, parent_node_id)

    @cached_property
    def elements_to_attach(self):
        return management.fetch_elements_selected(self.request.GET, self.request.user)

    def get_form_class(self):
        return formset_factory(
            form=attach_form_factory,
            formset=AttachNodeFormSet,
            extra=len(self.elements_to_attach)
        )

    def get_form_kwargs(self):
        formset_kwargs = []
        authorized_relationships = load_authorized_relationship.load()
        if not self.elements_to_attach:
            display_warning_messages(self.request, _("Please cut or copy an item before attach it"))
        for idx, element in enumerate(self.elements_to_attach):
            child_node = load_node.load_by_type(
                NodeType.EDUCATION_GROUP if isinstance(element, EducationGroupYear) else NodeType.LEARNING_UNIT,
                element.pk
            )
            formset_kwargs.append({
                'parent_node': self.parent_node,
                'child_node': child_node,
                'to_path': self.request.GET['path'],
                'authorized_relationship': authorized_relationships
            })
        return formset_kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(form_kwargs=self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["formset"] = context_data["form"]
        context_data["is_parent_a_minor_major_list_choice"] = self.parent_node.is_minor_major_list_choice()
        return context_data

    def form_valid(self, formset: AttachNodeFormSet):
        messages = formset.save()
        self.__clear_cache(messages)
        display_business_messages(self.request, messages)
        return redirect(
            reverse('education_group_read', args=[self.root_id, self.root_id])
        )

    def form_invalid(self, formset: AttachNodeFormSet):
        return self.render_to_response(self.get_context_data(formset=formset))

    def __clear_cache(self, messages):
        if not BusinessValidationMessage.contains_errors(messages):
            ElementCache(self.request.user).clear()


class AttachCheckView(GenericGroupElementYearMixin, View):
    rules = []

    def get(self, request, *args, **kwargs):
        error_messages = []

        try:
            perms.can_change_education_group(self.request.user, self.education_group_year)
        except PermissionDenied as e:
            error_messages.append(str(e))

        elements_to_attach = fetch_elements_selected(self.request.GET, self.request.user)
        if not elements_to_attach:
            error_messages.append(_("Please select an item before adding it"))

        #  TODO create service to check attach
        error_messages.extend(_check_attach(self.education_group_year, elements_to_attach))

        return JsonResponse({"error_messages": [str(msg) for msg in error_messages]})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.rules:
            try:
                self.rules[0](self.request.user, self.education_group_year)

            except PermissionDenied as e:
                return render(request, 'education_group/blocks/modal/modal_access_denied.html', {'access_message': e})

        return super(AttachCheckView, self).dispatch(request, *args, **kwargs)


class PasteElementFromCacheToSelectedTreeNode(GenericGroupElementYearMixin, RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        self.pattern_name = 'group_element_year_create'

        try:
            perms.can_change_education_group(self.request.user, self.education_group_year)
        except PermissionDenied as e:
            display_warning_messages(self.request, str(e))

        cached_data = ElementCache(self.request.user).cached_data

        if cached_data:

            action_from_cache = cached_data.get('action')

            if action_from_cache == ElementCache.ElementCacheAction.CUT.value:
                kwargs['group_element_year_id'] = fetch_source_link(self.request.GET, self.request.user).id
                self.pattern_name = 'group_element_year_move'

        return super().get_redirect_url(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.rules:
            try:
                self.rules[0](self.request.user, self.education_group_year)

            except PermissionDenied as e:
                return render(request, 'education_group/blocks/modal/modal_access_denied.html', {'access_message': e})

        return super(PasteElementFromCacheToSelectedTreeNode, self).dispatch(request, *args, **kwargs)


class CreateGroupElementYearView(GenericGroupElementYearMixin, CreateView):
    template_name = "group_element_year/group_element_year_comment_inner.html"

    def get_form_class(self):
        elements_to_attach = fetch_elements_selected(self.request.GET, self.request.user)
        if not elements_to_attach:
            display_warning_messages(self.request, _("Please cut or copy an item before attach it"))

        return modelformset_factory(
            model=GroupElementYear,
            form=GroupElementYearForm,
            formset=BaseGroupElementYearFormset,
            extra=len(elements_to_attach),
        )

    def get_form_kwargs(self):
        """ For the creation, the group_element_year needs a parent and a child """
        kwargs = super().get_form_kwargs()

        # Formset don't use instance parameter
        if "instance" in kwargs:
            del kwargs["instance"]
        kwargs_form_kwargs = []

        children = fetch_elements_selected(self.request.GET, self.request.user)

        messages = _check_attach(self.education_group_year, children)
        if messages:
            display_error_messages(self.request, messages)

        for child in children:
            kwargs_form_kwargs.append({
                'parent': self.education_group_year,
                'child_branch': child if isinstance(child, EducationGroupYear) else None,
                'child_leaf': child if isinstance(child, LearningUnitYear) else None,
                'empty_permitted': False
            })

        kwargs["form_kwargs"] = kwargs_form_kwargs
        kwargs["queryset"] = GroupElementYear.objects.none()
        return kwargs

    def form_valid(self, form):
        ElementCache(self.request.user).clear()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = context["form"]
        if len(context["formset"]) > 0:
            context['is_education_group_year_formset'] = bool(context["formset"][0].instance.child_branch)
        context["education_group_year"] = self.education_group_year
        return context

    def get_success_message(self, cleaned_data):
        return _("The content of %(acronym)s has been updated.") % {"acronym": self.education_group_year.verbose}

    def get_success_url(self):
        """ We'll reload the page """
        return


class MoveGroupElementYearView(CreateGroupElementYearView):
    template_name = "group_element_year/group_element_year_comment_inner.html"

    @cached_property
    def detach_strategy(self):
        obj = self.get_object()
        strategy_class = DetachEducationGroupYearStrategy if obj.child_branch else DetachLearningUnitYearStrategy
        return strategy_class(obj)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            perms.can_change_education_group(self.request.user, self.get_object().parent)
        except PermissionDenied as e:
            msg = "{}: {}".format(str(self.get_object().parent), str(e))
            display_warning_messages(self.request, msg)

        if not self.detach_strategy.is_valid():
            display_error_messages(self.request, self.detach_strategy.errors)

        return kwargs

    def form_valid(self, form):
        self.detach_strategy.post_valid()
        obj = self.get_object()
        obj.delete()
        return super().form_valid(form)


def _check_attach(parent: EducationGroupYear, elements_to_attach):
    children_types = NodeType.LEARNING_UNIT if elements_to_attach and isinstance(elements_to_attach[0], LearningUnitYear) else NodeType.EDUCATION_GROUP
    return attach_node_service.check_attach(
        parent.pk,
        [element.pk for element in elements_to_attach],
        children_types
    )
