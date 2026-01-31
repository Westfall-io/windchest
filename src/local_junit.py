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

"""
Simple local JUnit reader used during development.

This module demonstrates a lightweight read of a local `junit.xml`
file and inspects test case results. It is not a full validator;
it is intended for quick local checks during development and
prototyping.
"""

from junitparser import JUnitXml, Error, Failure


class JUnitErrorException(Exception):
    """Raised when a JUnit test case contains an error entry.

    This exception is available for callers that want a clear
    signal that one or more test cases contained an error result.
    """
    pass

file = "src/junit.xml"
xml = JUnitXml.fromfile(file)
for suite in xml:
    # iterate through test suites and cases and print whether the
    # first result for a failing case is a `Failure` type
    for case in suite:
        e = case.result
        if len(e) > 0:
            print(e[0].__class__==Failure)
