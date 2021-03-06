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
from education_group import publisher
from education_group.ddd import command

from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.repository.group import GroupRepository
from education_group.ddd.validators.validators_by_business_action import DeleteOrphanGroupValidatorList


def delete_orphan_group(cmd: command.DeleteOrphanGroupCommand) -> 'GroupIdentity':
    group_id = GroupIdentity(code=cmd.code, year=cmd.year)
    grp = GroupRepository.get(group_id)

    DeleteOrphanGroupValidatorList(grp).validate()
    # Emit group_deleted event
    publisher.group_deleted.send(None, group_identity=group_id)
    GroupRepository.delete(group_id)
    return group_id
