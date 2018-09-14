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
"""Settings file for dmgbuild.

Note that as this is a python file, any python can be used.
Use like this: dmgbuild -s settings.py "Test Volume" test.dmg

You can actually use this file for your own application (not just TextEdit)
by doing e.g.

    dmgbuild -s settings.py -D app=/path/to/My.app "My Application" MyApp.dmg
"""
from os import path, getcwd

import biplist

# .. Useful stuff .............................................................

CURRENT_DIR = getcwd()
print("dmgbuild directory: " + CURRENT_DIR)
dest = '/Applications/Merlink.app'
application = defines.get('app', dest)  # pylint:disable=undefined-variable
appname = path.basename(application)


def icon_from_app(app_path):
    """Get icon from app."""
    plist_path = path.join(app_path, 'Contents', 'Info.plist')
    plist = biplist.readPlist(plist_path)
    icon_name = plist['CFBundleIconFile']
    icon_root, icon_ext = path.splitext(icon_name)
    if not icon_ext:
        icon_ext = '.icns'
    icon_name = icon_root + icon_ext
    return path.join(app_path, 'Contents', 'Resources', icon_name)


# .. Basics ...................................................................

# Uncomment to override the output filename
# filename = 'MerLink.dmg'

# Uncomment to override the output volume name
volume_name = 'MerLink'

# Volume format (see hdiutil create -help)
format = defines.get('format', 'UDBZ')  # pylint:disable=undefined-variable

# Volume size
# size = defines.get('size', None)

# Files to include
files = [CURRENT_DIR + '/dist/merlink.app']

# Symlinks to create
symlinks = {'Applications': '/Applications'}

# Volume icon
#
# You can either define icon, in which case that icon file will be copied to
# the image, *or* you can define badge_icon, in which case the icon file you
#  specifywill be used to badge the system's Removable Disk icon.
#
# badge_icon = /path/to/icon
badge_icon = icon_from_app(CURRENT_DIR + '/dist/merlink.app')
# print(appname)
# badge_icon = icon_from_app(application)

# Where to put the icons
icon_locations = {appname: (140, 120), 'Applications': (500, 120)}

# .. Window configuration .....................................................

# Background
#
# This is a STRING containing any of the following:
#
#    #3344ff          - web-style RGB color
#    #34f             - web-style RGB color, short form (#34f == #3344ff)
#    rgb(1,0,0)       - RGB color, each value is between 0 and 1
#    hsl(120,1,.5)    - HSL (hue saturation lightness) color
#    hwb(300,0,0)     - HWB (hue whiteness blackness) color
#    cmyk(0,1,0,0)    - CMYK color
#    goldenrod        - X11/SVG named color
#    builtin-arrow    - A simple built-in background with a blue arrow
#    /foo/bar/baz.png - The path to an image file
#
# The hue component in hsl() and hwb() may include a unit; it defaults to
# degrees ('deg'), but also supports radians ('rad') and gradians ('grad'
# or 'gon').
#
# Other color components may be expressed either in the range 0 to 1, or
# as percentages (e.g. 60% is equivalent to 0.6).
background = 'builtin-arrow'

show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Window position in ((x, y), (w, h)) format, default  100,100 , 640,280
window_rect = ((100, 100), (640, 340))

# Select the default view; must be one of
#
#    'icon-view'
#    'list-view'
#    'column-view'
#    'coverflow'
#
default_view = 'icon-view'

# General view configuration
show_icon_preview = False

# Set these to True to force inclusion of icon/list view settings (otherwise
# we only include settings for the default view)
include_icon_view_settings = True

# .. Icon view configuration ..................................................

arrange_by = None
grid_offset = (0, 0)
# Max 100 or macOS uses its own default config
grid_spacing = 100
scroll_position = (0, 0)
label_pos = 'bottom'
text_size = 16
icon_size = 192
