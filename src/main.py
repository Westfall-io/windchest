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
from sample_action import SAMPLE_ACTION

import shutil
from datetime import datetime, timedelta

import git
import requests
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import GOVERNANCE, Tags
from minio.retention import Retention
from junitparser import JUnitXml, Error, Failure

class JUnitErrorException(Exception):
    pass

from minio.login import login_minio

def main(action=SAMPLE_ACTION, thread_execution_id=0):
    print('Logging into minio')
    client = login_minio()

    print('Logging into windstorm')
    token = login_windstorm_api()

    print('Updating thread execution {} status'.format(thread_execution_id))
    update_thread_status(token, thread_execution_id, 'windchest_1')

    print('\n'+'-'*20)
    print('Finding modified files')
    files = get_modified_files()

    print('Making temporary directory for changed files.')
    if not os.path.exists('/tmp'):
        os.mkdir('/tmp')
    if not os.path.exists('/tmp/digitalforge'):
        os.mkdir('/tmp/digitalforge')

    print('Copying all changed files to temporary directory.')
    errors = False
    for file in files:
        # Check if this action had a junit.xml
        if not errors:
            _, ext = os.path.splitext(file)
            if '.xml' == ext:
                # This might be a junit test
                print('Checking if this file ({}) is a junit report.'.format(file))

                is_junit = True
                try:
                    xml = JUnitXml.fromfile(os.path.join(VOLUME, file))
                except Exception as e:
                    # This couldn't be parsed.
                    print("File {} wasn't a readable junit report.".format(file))
                    is_junit = False

                if is_junit:
                    try:
                        for suite in xml:
                            # handle suites
                            for case in suite:
                                #handle cases
                                r = case.result
                                if len(r) == 0:
                                    continue

                                if r[0].__class__==Error or r[0].__class__==Failure:
                                    raise JUnitErrorException
                    except JUnitErrorException:
                        print('Error Found')
                        errors = True

                    if not errors:
                        print('Successful test found.')

                    r = requests.put(
                        WINDSTORMAPIHOST+"models/verifications/{}?verify={}".format(
                            action['verifications_id'],
                            not errors
                        )
                    )

            else:
                print('File type: {} found.'.format(ext))
        try:
            shutil.copyfile(os.path.join(VOLUME, file), os.path.join('/tmp/digitalforge', file))
        except:
            # If we run into a file that we can't copy, just forget it ever existed.
            continue

    print('Making an archive.')
    shutil.make_archive('output'+thread_name, 'zip', '/tmp/digitalforge')

    retention_date = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0,
    ) + timedelta(days=7)
    tags = Tags(for_object=True)
    tags["type"] = "output"

    print('Uploading to Minio')
    try:
        bucket = action["qualifiedName"].lower().strip().replace('_', '-'). \
            replace("'", "").replace('"', "").replace("\\","").replace("/",""). \
            replace("::", ".")
        if len(bucket) > 63:
            bucket = bucket[:63]
        elif len(bucket) < 3:
            bucket = bucket+'-bucket'

        found = client.bucket_exists(bucket)
        if not found:
            client.make_bucket(bucket, object_lock=True)
            print("Bucket made!")
        else:
            print("Bucket already exists!")

        client.fput_object(
            bucket, 'output'+thread_name+'.zip', 'output'+thread_name+'.zip',
            tags=tags,
            retention=Retention(GOVERNANCE, retention_date)
        )
    except S3Error as exc:
        print("error occurred.", exc)

    # Check if this action has dependent tasks.
    print('Checking if this action has dependent tasks.')
    r = requests.get(
        WINDSTORMAPIHOST+"models/threads/dependency/{}?validate=true".format(
            action['id']
        )
    )

    # See if errors are returned
    if isinstance(r.json()['results'], dict):
        if 'error' in r.json()['results']:
            # No dependencies
            print('Received error from API: {}'.format(r.json()['results']['error']))
            print('Complete no dependencies for action {}.'.format(action['id']))

            print('Updating thread execution {} status'.format(thread_execution_id))
            r = requests.put(
                WINDSTORMAPIHOST+"auth/update_thread/{}".format(
                    thread_execution_id
                ), json ={'status':'windchest_2'}
            )
            if r.status_code != 200:
                print('Failed to update status')
            return
            return

    # This action returned from dependency
    action = r.json()['results'][0]

    # Create a new thread
    r = requests.put(
        WINDSTORMAPIHOST+"auth/add_thread/{}".format(
            action["id"]
        )
    )

    thread = r.json()["thread"]
    if thread == action:
        print('Same action found')
    else:
        print("Warning: These actions did not match")

    thread_execution_id2 = r.json()["thread_execution_id"]
    print('Submitting action {} for workflow.'.format(action['id']))
    requests.post(WINDRUNNERHOST, json = {
        'action': thread,
        'thread_execution': thread_execution_id2,
        'prev_thread_name': thread_name})

    print('Complete.')

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
