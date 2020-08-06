import argparse
import datetime
import os
import uuid
from typing import Type

import django
import dotenv
from django.db import models, IntegrityError
from django.db.models import Subquery, Q


base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv.read_dotenv(os.path.join(base_dir, '.env'))
settings_file = os.environ.get('DJANGO_SETTINGS_MODULE', 'backoffice.settings.local')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)
django.setup()
if os.environ.get('DJANGO_SETTINGS_MODULE'):
    from base.models.learning_unit_year import LearningUnitYear
    from base.models.academic_year import AcademicYear
    from base.models.education_group_year import EducationGroupYear
    from base.models.group_element_year import GroupElementYear
    from base.models.education_group_language import EducationGroupLanguage
    from base.models.education_group_year_domain import EducationGroupYearDomain
    from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
    from base.models.education_group_achievement import EducationGroupAchievement
    from base.models.education_group_certificate_aim import EducationGroupCertificateAim
    from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
    from base.models.education_group_organization import EducationGroupOrganization
    from base.models.education_group_publication_contact import EducationGroupPublicationContact
    from base.models.learning_component_year import LearningComponentYear
    from base.models.learning_unit_enrollment import LearningUnitEnrollment
    from base.models.learning_achievement import LearningAchievement
    from cms.enums.entity_name import OFFER_YEAR, LEARNING_UNIT_YEAR
    from cms.models.translated_text import TranslatedText
    from base.models.prerequisite import Prerequisite
    from base.models.enums import education_group_categories
    from base.models.education_group import EducationGroup


VERBOSITY = False
LOGGING = True
LOGGING_FILE = None


def write_logging_file(msg, msg_type='-'):
    if LOGGING_FILE:
        LOGGING_FILE.write('[{}] {} "{}"\n'.format(datetime.datetime.now(), msg_type, msg))


class CopyLuyOldModel:
    def __init__(self, old_learning_unit_year: LearningUnitYear, new_learning_unit_year: LearningUnitYear):
        self.old_learning_unit_year = old_learning_unit_year
        self.new_learning_unit_year = new_learning_unit_year

    def run(self):
        self.copy_data_from_model(LearningAchievement, 'LEARNINGACHIEVEMENT')
        self.copy_data_from_model(LearningComponentYear, 'LEARNINGCOMPONENTYEAR')
        self.copy_data_from_model(LearningUnitEnrollment, 'LEARNINGUNITENROLLMENT')
        self.copy_general_information()

    def copy_data_from_model(self,
                             model: Type[models.Model],
                             msg_type_error=None):
        result = []
        old_datas = model.objects.filter(
            learning_unit_year=self.old_learning_unit_year
        )
        for data in old_datas:
            old_data = data
            data.id = None
            data.pk = None
            if getattr(data, 'external_id', None):
                data.external_id = None
            if getattr(data, 'uuid', None):
                data.uuid = uuid.uuid4()
            data.learning_unit_year = self.new_learning_unit_year
            try:
                data.save()
            except IntegrityError as e:
                write_logging_file(e.args, msg_type_error)
            if VERBOSITY:
                print("\t\t\t", data)
            result.append({'new': data, 'old': old_data})
        if not old_datas:
            write_logging_file('No {} found for {}'.format(model._meta.object_name, self.new_learning_unit_year),
                               msg_type_error)
        return result

    def copy_general_information(self):
        old_translated_texts = TranslatedText.objects.filter(
            entity=LEARNING_UNIT_YEAR,
            reference=Subquery(
                LearningUnitYear.objects.filter(
                    pk=self.old_learning_unit_year.pk
                ).values('id')[:1]
            )
        )

        for translated_text in old_translated_texts:
            translated_text.id = None
            translated_text.pk = None
            translated_text.reference = self.new_learning_unit_year.id
            try:
                translated_text.save()
            except IntegrityError as e:
                write_logging_file(e.args, 'GENERAL_INFO')
            if VERBOSITY:
                print('\t\t\t', translated_text)
        if not old_translated_texts:
            write_logging_file('No TranslatedText found for {}'.format(self.old_learning_unit_year), 'GENERAL_INFO')


class CopyEgyOldModel:

    def __init__(self, old_education_group_year: EducationGroupYear, new_education_group_year: EducationGroupYear):
        self.old_education_group_year = old_education_group_year
        self.new_education_group_year = new_education_group_year

    def run(self):
        self.copy_data_from_model(EducationGroupYearDomain, 'SECOND_DOMAIN')
        self.copy_data_from_model(EducationGroupLanguage, 'LANGUAGE')
        self.copy_education_group_achievement()
        self.copy_data_from_model(EducationGroupCertificateAim, 'CERTIFICATE_AIM')
        self.copy_data_from_model(EducationGroupOrganization, 'ORGANIZATION')
        self.copy_data_from_model(EducationGroupPublicationContact, 'PUBLICATIONCONTACT')
        self.copy_admission_condition()
        self.copy_general_information()

    def copy_education_group_detailed_achievement(self,
                                                  old_education_group_achievement_id: int,
                                                  new_old_education_group_achievement: EducationGroupAchievement):
        old_egy_detailed_achievements = EducationGroupDetailedAchievement.objects.filter(
            education_group_achievement_id=old_education_group_achievement_id
        )
        for egyda in old_egy_detailed_achievements:
            egyda.id = None
            egyda.pk = None
            egyda.external_id = None
            egyda.education_group_achievement = new_old_education_group_achievement
            try:
                egyda.save()
            except IntegrityError as e:
                write_logging_file(e.args, 'DETAILED_ACHIEVEMENT')
            if VERBOSITY:
                print("\t\t\t", egyda)
        if not old_egy_detailed_achievements:
            write_logging_file('No EducationGroupDetailedAchievement found for {}'
                               .format(old_egy_detailed_achievements),
                               'DETAILED_ACHIEVEMENT')

    def copy_education_group_achievement(self):
        old_egy_achievements = EducationGroupAchievement.objects.filter(
            education_group_year=self.old_education_group_year
        )
        for egya in old_egy_achievements:
            old_id = egya.id
            egya.id = None
            egya.pk = None
            egya.external_id = None
            egya.education_group_year = self.new_education_group_year
            egya.save()
            self.copy_education_group_detailed_achievement(old_id, egya)
            if VERBOSITY:
                print("\t\t\t", egya)
        if not old_egy_achievements:
            write_logging_file('No EducationGroupAchievement found for {}'.format(self.old_education_group_year),
                               'ACHIEVEMENT')

    def copy_data_from_model(self,
                             model: Type[models.Model],
                             msg_type_error=None):
        result = []
        old_datas = model.objects.filter(
            education_group_year=self.old_education_group_year
        )
        for data in old_datas:
            old_data = data
            data.id = None
            data.pk = None
            if getattr(data, 'external_id', None):
                data.external_id = None
            if getattr(data, 'uuid', None):
                data.uuid = uuid.uuid4()
            data.education_group_year = self.new_education_group_year
            try:
                data.save()
            except IntegrityError as e:
                write_logging_file(e.args, msg_type_error)
            if VERBOSITY:
                print("\t\t\t", data)
            result.append({'new': data, 'old': old_data})
        if not old_datas:
            write_logging_file('No {} found for {}'.format(model._meta.object_name, self.old_education_group_year),
                               msg_type_error)
        return result

    def copy_admission_condition(self):
        admission_list = self.copy_data_from_model(AdmissionCondition, 'ADMISSION_CONDITION')
        for admission in admission_list:
            old_lines = AdmissionConditionLine.objects.filter(admission_condition=admission['old'])
            for line in old_lines:
                line.id = None
                line.pk = None
                line.admission_condition = admission['new']
                if getattr(line, 'uuid', None):
                    line.uuid = uuid.uuid4()
                try:
                    line.save()
                except IntegrityError as e:
                    write_logging_file(e.args, 'ADMISSION_LINE')
                if VERBOSITY:
                    print("\t\t\t", line)
            if not old_lines:
                write_logging_file('No AdmissionConditionLine found for {}'.format(admission['old']), 'ADMISSION_LINE')

    def copy_general_information(self):
        old_translated_texts = TranslatedText.objects.filter(
            entity=OFFER_YEAR,
            reference=Subquery(
                EducationGroupYear.objects.filter(
                    pk=self.old_education_group_year.pk
                ).values('id')[:1]
            )
        )

        for translated_text in old_translated_texts:
            translated_text.id = None
            translated_text.pk = None
            translated_text.reference = self.new_education_group_year.id
            try:
                translated_text.save()
            except IntegrityError as e:
                write_logging_file(e.args, 'GENERAL_INFO')
            if VERBOSITY:
                print('\t\t\t', translated_text)
        if not old_translated_texts:
            write_logging_file('No TranslatedText found for {}'.format(self.old_education_group_year), 'GENERAL_INFO')


def copy_to_old_model(from_year: int):
    start_time = datetime.datetime.now()
    year = AcademicYear.objects.get(year=from_year)
    new_year = year.next()
    if VERBOSITY:
        print("Start copy to old model")
    print(year, 'to', new_year)
    result = copy_link_to_next_year(new_year)
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    if VERBOSITY:
        print("End copy to old model")
    print('Copying to old model time:', total_time)
    return result


def get_next_learning_unit_year(child_leaf: LearningUnitYear, copy_to_year: AcademicYear):
    try:
        luy = LearningUnitYear.objects.get(learning_unit=child_leaf.learning_unit, academic_year=copy_to_year)
        copy_luy_to_next_year = CopyLuyOldModel(child_leaf, luy)
        copy_luy_to_next_year.run()
        if VERBOSITY:
            print("\t\t\t", luy)
        return luy
    except LearningUnitYear.DoesNotExist:
        write_logging_file('LearingUnit {} does NOT exist in {}'.format(child_leaf.learning_unit, copy_to_year),
                           'LEARNINGUNITYEAR')
        return None


def get_next_education_group_year(old_education_group_year: EducationGroupYear,
                                  copy_to_year: AcademicYear) -> EducationGroupYear:
    try:
        if old_education_group_year.education_group_type.category == education_group_categories.TRAINING \
                or old_education_group_year.education_group_type.category == education_group_categories.MINI_TRAINING:
            egy = EducationGroupYear.objects.get(education_group=old_education_group_year.education_group,
                                                 academic_year=copy_to_year)
        else:
            try:
                egy = EducationGroupYear.objects.get(
                    education_group=old_education_group_year.education_group,
                    academic_year=copy_to_year,
                )
            except EducationGroupYear.DoesNotExist:
                egy = old_education_group_year
                egy.id = None
                egy.pk = None
                egy.external_id = None
                egy.uuid = uuid.uuid4()
                egy.academic_year = copy_to_year
                try:
                    egy.save()
                except IntegrityError as e:
                    write_logging_file(e.args, 'EDUCATIONGROUPYEAR')
        copy_egy_to_next_year = CopyEgyOldModel(old_education_group_year, egy)
        copy_egy_to_next_year.run()
        if VERBOSITY:
            print("\t\t\t", egy)
        return egy
    except EducationGroupYear.DoesNotExist:
        write_logging_file('EducationGroup {} does NOT exist in {}'.format(
            old_education_group_year.education_group.most_recent_acronym,
            copy_to_year),
            'EDUCATIONGROUPYEAR'
         )
        return None


def copy_link_to_next_year(copy_to_year: AcademicYear) -> dict:
    geys = GroupElementYear.objects.filter(
        Q(parent__education_group__end_year__isnull=True)
        | (Q(parent__education_group_type__category=education_group_categories.GROUP)
           | Q(parent__education_group__end_year__year__gte=copy_to_year.year)),
        (Q(child_branch__isnull=True)
         | Q(child_branch__education_group__end_year__isnull=True)
         | (Q(child_branch__education_group_type__category=education_group_categories.GROUP)
            | Q(child_branch__education_group__end_year__year__gte=copy_to_year.year))) |
        (Q(child_leaf__isnull=True)
         | Q(child_leaf__learning_unit__end_year__isnull=True)
         | Q(child_leaf__learning_unit__end_year__year__gte=copy_to_year.year)),
        parent__academic_year__year=copy_to_year.year - 1,
    ).select_related('parent', 'child_branch', 'child_leaf')
    links_created = 0
    for gey in geys:
        msg = None
        old_parent = gey.parent
        old_branch = gey.child_branch
        old_leaf = gey.child_leaf
        gey.id = None
        gey.pk = None
        gey.external_id = None
        gey.parent = get_next_education_group_year(old_parent, copy_to_year)
        gey.child_branch = get_next_education_group_year(old_branch, copy_to_year) if gey.child_branch else None
        gey.child_leaf = get_next_learning_unit_year(old_leaf, copy_to_year) if gey.child_leaf else None
        if gey.parent and (gey.child_leaf or gey.child_branch):
            try:
                gey.save()
                links_created += 1
            except IntegrityError as e:
                write_logging_file(e.args, 'LINK')
        else:
            msg = 'Link between {} and {} for {} has not been created'.format(old_parent,
                                                                              old_leaf or old_branch,
                                                                              copy_to_year)
            write_logging_file(msg, 'LINK')
        if VERBOSITY:
            print('\t\t', msg) if msg else print('\t\t', gey)

    return {
        'created': links_created,
        'total': len(geys),
        'percentage': (links_created/len(geys)*100)
    }


def create_prerequisites(copy_to_year: int) -> int:
    prerequisites_created = 0
    prerequisites = Prerequisite.objects.filter(
        learning_unit_year__academic_year__year=copy_to_year-1,
        education_group_year__academic_year__year=copy_to_year-1
    ).prefetch_related('prerequisiteitem_set')
    for prerequisite in prerequisites:
        try:
            new_learning_unit_year = LearningUnitYear.objects.get(
                learning_unit=prerequisite.learning_unit_year.learning_unit,
                academic_year__year=copy_to_year
            )
            new_education_group_year = EducationGroupYear.objects.get(
                education_group=prerequisite.education_group_year.education_group,
                academic_year__year=copy_to_year
            )
            prerequisite.id = None
            prerequisite.pk = None
            prerequisite.external_id = None
            prerequisite.learning_unit_year = new_learning_unit_year
            prerequisite.education_group_year = new_education_group_year
            prerequisite.save()
            for item in prerequisite.prerequisiteitem_set.all():
                item.prerequisite = prerequisite
                item.save()
                if VERBOSITY:
                    print('\t\t', item.learning_unit)
                    print('\t\t', item.prerequisite)
            prerequisites_created += 1
        except Exception as e:  # TODO correct except clause
            write_logging_file(e, 'PREREQUISITE')
    return {
        'created': prerequisites_created,
        'total': len(prerequisites),
        'percentage': (prerequisites_created/len(prerequisites)*100)
    }


def delete_data_from_learning_unit_year(luy: LearningUnitYear):
    LearningAchievement.objects.filter(learning_unit_year=luy).delete()
    LearningComponentYear.objects.filter(learning_unit_year=luy).delete()
    LearningUnitEnrollment.objects.filter(learning_unit_year=luy).delete()
    TranslatedText.objects.filter(
        entity=LEARNING_UNIT_YEAR,
        reference=Subquery(
            LearningUnitYear.objects.filter(
                pk=luy.pk
            ).values('id')[:1]
        )
    ).delete()


def delete_data_from_education_group_year(egy: EducationGroupYear):
    EducationGroupYearDomain.objects.filter(education_group_year=egy).delete()
    EducationGroupLanguage.objects.filter(education_group_year=egy).delete()
    EducationGroupCertificateAim.objects.filter(education_group_year=egy).delete()
    EducationGroupOrganization.objects.filter(education_group_year=egy).delete()
    EducationGroupPublicationContact.objects.filter(education_group_year=egy).delete()
    TranslatedText.objects.filter(
        entity=OFFER_YEAR,
        reference=Subquery(
            EducationGroupYear.objects.filter(
                pk=egy.pk
            ).values('id')[:1]
        )
    ).delete()
    old_egy_achievements = EducationGroupAchievement.objects.filter(education_group_year=egy)
    EducationGroupDetailedAchievement.objects.filter(education_group_achievement__in=old_egy_achievements).delete()
    old_egy_achievements.delete()
    admission_list = AdmissionCondition.objects.filter(education_group_year=egy)
    AdmissionConditionLine.objects.filter(admission_condition__in=admission_list).delete()
    admission_list.delete()


def delete_prerequisites(year_to_delete: int):
    prerequisites = Prerequisite.objects.filter(
        learning_unit_year__academic_year__year=year_to_delete
    ).prefetch_related('prerequisiteitem_set')
    try:
        for prerequisite in prerequisites:
            prerequisite.prerequisiteitem_set.delete()
    except Exception as e:
        write_logging_file(e, 'PREREQUISITEITEMS')
    try:
        prerequisites.delete()
    except Exception as e:
        write_logging_file(e, 'PREREQUISITE')


def delete_links_old_model(year_to_delete: int):
    if VERBOSITY:
        print('Start delete link')
    geys = GroupElementYear.objects.filter(Q(child_leaf__academic_year__year=year_to_delete)
                                           | Q(child_branch__academic_year__year=year_to_delete))
    for gey in geys:
        msg = 'Link between {} and {} deleted'.format(gey.parent, gey.child_branch or gey.child_leaf)
        delete_data_from_education_group_year(gey.parent)
        if gey.child_branch:
            delete_data_from_education_group_year(gey.child_branch)
        if gey.child_leaf:
            delete_data_from_learning_unit_year(gey.child_leaf)
        gey.delete()
        if VERBOSITY:
            print(msg)
        write_logging_file(msg, 'DELETION')
    if VERBOSITY:
        print(len(geys), 'links deleted.')


def correct_end_date_education_group_type_groups(year: int):
    try:
        EducationGroup.objects.filter(
            educationgroupyear__education_group_type__category=education_group_categories.GROUP,
            educationgroupyear__academic_year__year=year
        ).update(end_year=None)
    except Exception as e:
        write_logging_file(e, 'UPDATE')


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Copy program from 'year' to 'year + 1'")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", "--all", help="copy to old and new models", action="store_true")
        group.add_argument("-n", "--new_model", help="copy only in new model (not working at this moment)",
                           action="store_true")
        group.add_argument("-o", "--old_model", help="copy only in old model", action="store_true")
        group.add_argument("-p", "--prerequisite", help="copy prerequisites", action="store_true")
        parser.add_argument("-d", "--delete", help="delete old link", action="store_true")
        parser.add_argument("-u", "--update_education_group", help="update end year of education groups",
                            action="store_true")
        parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
        parser.add_argument("year", help="year to copy", type=int)
        args = parser.parse_args()
        start_time = datetime.datetime.now()
        year = args.year
        to_year = year + 1
        print(year, 'to', to_year)
        if LOGGING:
            LOGGING_FILE = open('error_copy.log', 'w+')
        if args.verbose:
            VERBOSITY = args.verbose
            print("verbosity turned on")
        if args.all or args.delete:
            delete_links_old_model(to_year)
            delete_prerequisites(to_year)
        if args.all or args.old_model:
            link_created = copy_to_old_model(year)
            print('Links successfully copied : {}%'.format(link_created['percentage']))
        if args.all or args.old_model or args.prerequisite:
            preq_created = create_prerequisites(to_year)
            print('Prerequisites successfully copied : {}%'.format(preq_created['percentage']))
        if args.update_education_group:
            correct_end_date_education_group_type_groups(year)
        if args.new_model:
            print('Not implemented yet')
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        print('Total time:', total_time)
    finally:
        if LOGGING_FILE:
            LOGGING_FILE.close()
