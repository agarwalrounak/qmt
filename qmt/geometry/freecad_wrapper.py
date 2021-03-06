# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Wrapping FreeCAD calls within a Python 3 environment."""

from __future__ import print_function
import os
import pickle
import subprocess

import qmt


def fcwrapper(pyenv='python2', instruction=None, data=None, debug=False):
    """Wrapper to isolate FreeCAD Python 2.7 calls from the Python 3 code base.

    :param str pyenv:       Python interpreter, defaults to 'python2'.
    :param str instruction: A registered instruction for the QMT FreeCAD module.
    :param     data:        Any data type serialisable through pickle.
    :return:                Any data type serialisable through pickle.
    """

    qmtPath = os.path.join(os.path.dirname(qmt.__file__))
    runPath = os.path.join(qmtPath, 'geometry', 'freecad', 'run.py')
    serial_data = pickle.dumps(data, protocol=2)
    proc = subprocess.Popen([pyenv, runPath, instruction],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.communicate(serial_data)

    # output[1] not checked because stderr is used for mere warnings too often.
    if proc.returncode != 0:
        print(output[1].decode())
        print(os.linesep + ' --- END OF FC WRAPPED STDERR ---' + os.linesep)
        raise ValueError('pywrapper returned ' + str(proc.returncode))

    # The returned serialised byte stream is demarcated by the separator string
    # "MAGICQMTRANSFERBYTES". Most data preceding the separator corresponds to
    # FreeCAD notifications and gets discarded.
    pipe_data = output[0].decode().split('MAGICQMTRANSFERBYTES')
    if debug is True:
        print(os.linesep + ' --- FC WRAPPED STDOUT ---' + os.linesep)
        print(str(*pipe_data[0:-1]).decode())
        print(os.linesep + ' --- FC WRAPPED STDERR ---' + os.linesep)
        print(output[1].decode())
        print(os.linesep + ' --- END OF FC WRAPPED STDERR ---' + os.linesep)
    serial_data = pipe_data[-1].encode()
    return pickle.loads(serial_data)
