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

"""CLI modal prompts to send information to console."""


class CliModalPrompts:
    """Class documentation."""
    def __init__(self):
        """CliModalPrompts class constructor, inits with no params."""
        super(CliModalPrompts, self).__init__()

    @staticmethod
    def show_error_dialog(message):
        """Prints an error message

        Args:
            message: An error message to show to the user"""

        print("ERROR:" + str(message))

    @staticmethod
    def show_feature_in_development_dialog():
        """Prints a message if user encounters a work in progress feature."""
        print("Thank you for your interest. This is a feature in development.")
