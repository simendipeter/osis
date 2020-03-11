# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import tempfile

from behave.runner import Context
from django.conf import settings
from django.utils.text import slugify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from features import factories as functional_factories
from features.factories import users, score_encoding, learning_unit, education_group, organization, academic_year, reference


def before_all(context):
    context.download_directory = tempfile.mkdtemp('osis-selenium')
    fp = webdriver.FirefoxProfile()
    fp.set_preference('browser.download.dir', context.download_directory)
    fp.set_preference('browser.download.folderList', 2)
    fp.set_preference('browser.download.manager.showWhenStarting', False)
    fp.set_preference("intl.accept_languages", 'fr-be')
    fp.set_preference('pdfjs.disabled', True)
    known_mimes = ['application/vnd.ms-excel',
                   'application/pdf',
                   'text/csv',
                   'application/xls',
                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk', ','.join(known_mimes))
    options = Options()
    if settings.SELENIUM_SETTINGS["VIRTUAL_DISPLAY"]:
        options.add_argument('-headless')
    executable_path = settings.SELENIUM_SETTINGS["GECKO_DRIVER"]
    context.browser = webdriver.Firefox(firefox_profile=fp, options=options, executable_path=executable_path)

    screen_size = (settings.SELENIUM_SETTINGS['SCREEN_WIDTH'], settings.SELENIUM_SETTINGS['SCREEN_HIGH'])
    context.browser.set_window_size(*screen_size)
    setup_data(context)


def setup_data(context: Context):
    context.current_academic_year = functional_factories.academic_year.BusinessAcademicYearFactory().current_academic_year
    functional_factories.reference.BusinessLanguageFactory()
    functional_factories.organization.BusinessEntityVersionTreeFactory()
    functional_factories.organization.BusinessCampusFactory()
    functional_factories.users.BusinessUsersFactory()
    functional_factories.score_encoding.ScoreEncodingFactory()
    context.setup_data = functional_factories.learning_unit.LearningUnitBusinessFactory()
    functional_factories.education_group.OfferBusinessFactory()

    return context


def before_scenario(context, scenario):
    pass


def after_all(context):
    context.browser.quit()


def after_step(context, step):
    if settings.SELENIUM_SETTINGS["TAKE_SCREEN_ON_FAILURE"] and step.status == "failed":
        name = slugify(context.scenario.name + ' ' + step.name)
        context.browser.save_screenshot("features/logs/{}.png".format(name))
