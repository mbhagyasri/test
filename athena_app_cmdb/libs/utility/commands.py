# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

import subprocess
import json
import os
import errno
import logging
from datetime import datetime

from athena_app_cmdb.utils.helper_methods import raise_for_error
logger = logging.getLogger(__name__)


class Execute(object):

    def create_directory(self,  dirname):
        """ Create directory if it doesn't exist.  exit 1 if error for some reason """
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname, 0o755)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    return {'exitcode': 1, 'stderr': e}
        return {'exitcode': 0, 'stderr': None}

    def data_merge(self, a, b):
        """ merges b into a and return merged result

                NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen
        """
        key = None
        # ## debug output
        # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
        try:
            if a is None or isinstance(a, str)or isinstance(a, int) \
                     or isinstance(a, float):
                # border case for first run or if a is a primitive
                a = b
            elif isinstance(a, list):
                # lists can be only appended
                if isinstance(b, list):
                    for item in b:
                        if not isinstance(item, dict) or not isinstance(item, list):
                            if item not in a:
                                # Only add item if it doesn't exist
                                a.append(item)
                        else:
                            a.append(item)
                elif not isinstance(b, dict):
                    if b not in a:
                        a.append(b)
                else:
                    # append to list
                    a.append(b)
            elif isinstance(a, dict):
                # dicts must be merged
                if isinstance(b, dict):
                    for key in b:
                        if key in a:
                            a[key] = self.data_merge(a[key], b[key])
                        else:
                            a[key] = b[key]
                else:
                    a = b
            elif not a:
                a = b
            elif not b:
                pass
            else:
                raise_for_error(400, 'NOT IMPLEMENTED merging "{0}" into "{1}"'.format(b, a))
        except TypeError as e:
            raise_for_error(400, 'TypeError "{0}" in key "{1}" when merging "{2}" into "{3}"'.format(e, key, b, a))
        return a

    def run_shell_command(self,command_line):
        logger.debug('Subprocess: "%s"' % command_line)
        output = []
        popen = subprocess.Popen(
                command_line,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True
                )
        while True:
            nextline = popen.stdout.readline()
            if nextline == '' and popen.poll() is not None:
                break
            output.append(nextline)
            logger.info(nextline)
        stderr = popen.communicate()[1]
        exitCode = popen.returncode
        return {'exitcode': exitCode, 'stderr': stderr, 'output': output}

    def run_background_process(self, args):
        pid = subprocess.Popen(args).pid
        return pid

    def silent_file_remove(self, filename):
        # silent_file_remove
        # remove a file and ignore error message if the file doesn't exist
        logger.debug('Remove file: %s' % filename)
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                pass
                return {'exitcode': 1, 'stderr' : e }
        return {'exitcode': 0, 'stderr': None }

    def read_file_to_json(self, mapping_file):
        try:
            with open(mapping_file) as data_file:
                data = json.load(data_file)
        except Exception as e:
            pass
            return {'exitcode': 1, 'stderr': e, 'output': e}
        return {'exitcode': 0, 'output': data}

    def read_file(self, mapping_file):
        try:
            with open(mapping_file) as data_file:
                data = data_file.read().replace('\n', '')
        except Exception as e:
            pass
            return {'exitcode': 1, 'stderr': e, 'output': e}
        return {'exitcode': 0, 'output': data}

    def append_to_file(self, message, file):
        try:
            with open(file, "a+") as append_file:
                append_file.write(message)
        except Exception as e:
            return {'exitcode': 1, 'output': e}
        return {'exitcode' : 0, 'output': None}

    def write_file_to_json(self, file, data):
        try:
            with open(file, 'w') as fp:
                json.dump(data, fp)
        except Exception as e:
            return {'exitcode': 1, 'output': e}
        return {'exitcode': 0, 'output': None}


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

