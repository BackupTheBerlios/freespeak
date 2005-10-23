#!/usr/bin/env python
"""
    setup.py
    Fri Jun 14 13:41:56 2004
    Copyright  2005 Italian Python User Group
    http://www.italianpug.org
   
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Library General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import os
from distutils.core import setup, Extension
from distutils import sysconfig, cmd
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.command.install import install as _install
from distutils.command.build_ext import build_ext
from distutils.util import change_root
from distutils.dir_util import remove_tree, copy_tree, mkpath

# quick hack to support generating locale files
class build(_build):
    def __init__(self, *a, **kw):
        self.sub_commands = self.sub_commands + [
            ('build_locale', None),
        ]
        _build.__init__(self, *a, **kw)

class build_locale(cmd.Command):
    user_options = [
        ('build-dir=', 'd', "directory to build to"),
        ('po-dir=', 'd', "directory holding the domain dirs and in them PO-files"),
    ]
    description = 'Build locales'

    def initialize_options(self):
        self.build_dir = 'locale'
        self.build_base = None
        self.po_dir = 'lang'

    def finalize_options (self):
        self.set_undefined_options('build',
                ('build_base', 'build_base'))
        self.build_dir = change_root(self.build_base, self.build_dir)

    def run(self):
        for po in os.listdir(self.po_dir):
            if not po.endswith('.po'): continue
            locale = po[:-len('.po')]
            path = os.path.join(self.build_dir, locale, 'LC_MESSAGES')
            mkpath(path)
            self.spawn(['msgfmt', '-o',
                    os.path.join(path, '%s.mo' % 'freespeak'),
                    os.path.join(self.po_dir, po)])
                    
build_trayicon = build_ext

class build_ext(build_ext):
    def run(self): return
                                       
class clean(_clean):
    def run(self):
        self.run_command('clean_locale')
        _clean.run(self)

class clean_locale(cmd.Command):
    user_options = [
        ('build-dir=', 'd', "directory to build to"),
    ]
    description = 'Clean locales'

    def initialize_options(self):
        self.build_dir = None

    def finalize_options (self):
        self.set_undefined_options('build_locale',
                ('build_dir', 'build_dir'))

    def run(self):
        if os.path.exists(self.build_dir):
            remove_tree(self.build_dir, dry_run=self.dry_run)

class install(_install):
    def __init__(self, *a, **kw):
        self.sub_commands = self.sub_commands + [
            ('install_locale', None),
        ]
        _install.__init__(self, *a, **kw)

class install_locale(cmd.Command):
    user_options = [
        ('install-dir=', 'd', "directory to install locales to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('skip-build', None, "skip the build steps"),
    ]
    description = 'Install locales'
    boolean_options = ['skip-build']

    def initialize_options(self):
        self.build_dir = None
        self.install_dir = None
        self.root = None
        self.prefix = None
        self.skip_build = None

    def finalize_options (self):
        self.set_undefined_options('build_locale',
                ('build_dir', 'build_dir'))
        self.set_undefined_options('install',
                ('skip_build', 'skip_build'))
        if self.install_dir is None:
            self.set_undefined_options('install',
                    ('root', 'root'))
            self.set_undefined_options('install',
                    ('prefix', 'prefix'))
            prefix = self.prefix
            if self.root is not None:
                prefix = change_root(self.root, prefix)
            self.install_dir = os.path.join(prefix, 'share', 'locale')

    def run(self):
        if not self.skip_build:
            self.run_command('build_locale')
        copy_tree(src=self.build_dir,
            dst=self.install_dir,
            dry_run=self.dry_run)

def capture(cmd): return os.popen(cmd).read().strip()

setup(name='FreeSpeak',
    version='0.1.1',
    description='Frontend to already existing translation engines',
    author='Italian Python User Group',
    author_email='lethalman88@gmail.com',
    url='http://www.gna.org/projects/freespeak',
    license='GNU General Public License v2',
    packages=['freespeak', 'freespeak.src', 'freespeak.modules'],
    data_files=[
        ('share/freespeak/icons', ['icons/altavista-16x16.png',
                                   'icons/freespeak-16x16.png',
                                   'icons/freespeak-64x64.png',
                                   'icons/freetranslation-16x16.png',
                                   'icons/google-16x16.png',"icons/English.png", 
                                   "icons/Italiano.png",
                                   "icons/Nederlands.png",
                                   "icons/System Default.png"]),
        ("share/applications", ["freespeak.desktop"]),
        ("share/pixmaps", ["icons/freespeak-64x64.png"]),
    ],
    scripts=['freespeak.py'],
    ext_modules=[
            Extension("trayicon",
                    ["trayicon/trayicon.c", "trayicon/trayiconmodule.c", "trayicon/eggtrayicon.c"],
                    extra_compile_args = capture("pkg-config --cflags gtk+-2.0 pygtk-2.0").split(),
                    extra_link_args = capture("pkg-config --libs gtk+-2.0 pygtk-2.0").split()
        ),
    ],
    cmdclass={
            'build': build,
            'build_locale': build_locale,
            'build_trayicon': build_trayicon,
            'build_ext': build_ext,
            'clean': clean,
            'clean_locale': clean_locale,
            'install': install,
            'install_locale': install_locale,
    },
)

