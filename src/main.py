# Copyright (c) 2023-2024 Westfall Inc.
#
# This file is part of Windchest.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, and can be found in the file NOTICE inside this
# git repository.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import time
start_time = time.time()

from env import *

import os

from windbinder.sample_action import SAMPLE_ACTION
from windbinder.minio.login import login_minio
from windbinder.windstorm.authentication import login_windstorm_api, \
    update_thread_status
from windbinder.git.repo import git_configure
from windbinder.windstorm.thread import update_verification, \
    find_dependent_tasks_by_id, execute_dependent_thread

def main(action=SAMPLE_ACTION, thread_execution_id=0):
    print('Logging into minio')
    client = login_minio()

    print('Logging into windstorm')
    token = login_windstorm_api()

    print('Updating thread execution {} status'.format(thread_execution_id))
    thread_name = update_thread_status(token, thread_execution_id, 'windchest_1')

    print('\n'+'-'*20)
    print('Finding modified files')
    files = git_configure()

    print('Making temporary directory for changed files.')
    if not os.path.exists('/tmp'):
        os.mkdir('/tmp')
    if not os.path.exists('/tmp/digitalforge'):
        os.mkdir('/tmp/digitalforge')

    print('Copying all changed files to temporary directory.')
    error = check_files(files)
    update_verification(action['verifications_id'], error)

    print('Collecting all changed files for storage')
    create_bucket(client, action, thread_name, name='output', tmp_location='/tmp/digitalforge')

    action2 = find_dependent_tasks_by_id(token, action)
    if isinstance(action2, dict):
        execute_dependent_thread(token, action2, thread_name)

    print('Updating thread execution {} status'.format(thread_execution_id))
    update_thread_status(token, thread_execution_id, 'windchest_2')

if __name__ == "__main__":
    os.mkdir('tmp')
    # This part is a workaround until volume is attached.
    if not os.path.exists(VOLUME):
        raise NotImplementedError('Volume is not attached.')

    import fire
    fire.Fire(main)
    print("--- %s seconds ---" % (time.time() - start_time))
