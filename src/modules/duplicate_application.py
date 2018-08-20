# -*- coding: utf-8 -*-
# Copyright 2018 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Detect whether there are multiple processes with the same name."""
import psutil


def is_duplicate_application(program_name):
    """ docstring pass1
    """
    count = 0
    for proc in psutil.process_iter():
        if proc.as_dict(attrs=['name'])['name'] == program_name:
            count += 1
        if count >= 4:
            return True
    return False
