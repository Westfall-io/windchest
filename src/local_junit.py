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

from junitparser import JUnitXml, Error, Failure
class JUnitErrorException(Exception):
    pass

file = "src/junit.xml"
xml = JUnitXml.fromfile(file)
for suite in xml:
    # handle suites
    for case in suite:
        e = case.result
        if len(e) > 0:
            print(e[0].__class__==Failure)
