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
"""MerLink setup.py"""
from setuptools import setup

setup(
    name='merlink',
    version='0.8.6',
    packages=['src'],
    url='pocc.github.io/merlink',
    license='Apache 2.0',
    author='Ross Jacobs',
    author_email='merlinkproject@gmail.com',
    description='Cross-platform VPN client to connect to Meraki firewalls',
    python_requires='>=3.5',)
