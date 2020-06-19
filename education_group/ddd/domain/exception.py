from osis_common.ddd.interface import BusinessException
from django.utils.translation import gettext_lazy as _


class TrainingNotFoundException(Exception):
    pass


class GroupNotFoundException(Exception):
    pass


class GroupCodeAlreadyExistException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Code already exists")
        super().__init__(message, **kwargs)


class AcademicYearNotFound(Exception):
    pass


class TypeNotFound(Exception):
    pass


class ManagementEntityNotFound(Exception):
    pass


class TeachingCampusNotFound(Exception):
    pass
