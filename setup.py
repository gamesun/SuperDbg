#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#############################################################################
##
## Copyright (c) 2016, gamesun
## All right reserved.
##
## This file is part of SuperDbg.
##
## SuperDbg is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## SuperDbg is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SuperDbg.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################


from distutils.core import setup
import sys
import py2exe
import os
import glob
from py2exe.build_exe import py2exe as build_exe
import appInfo

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
    if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll"):
        return 0
    return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

if len(sys.argv) == 1:
    sys.argv.append("py2exe")
#     sys.argv.append("-q")

manifest_template = '''
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
version="0.6.8.0"
processorArchitecture="x86"
name="%(prog)s"
type="win32"
/>
<description>%(prog)s</description>
<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
<security>
<requestedPrivileges>
<requestedExecutionLevel
level="asInvoker"
uiAccess="false"
/>
</requestedPrivileges>
</security>
</trustInfo>
<dependency>
<dependentAssembly>
<assemblyIdentity
type="win32"
name="Microsoft.VC90.CRT"
version="9.0.21022.8"
processorArchitecture="x86"
publicKeyToken="1fc8b3b9a1e18e3b"
/>
</dependentAssembly>
</dependency>
<dependency>
<dependentAssembly>
<assemblyIdentity
type="win32"
name="Microsoft.Windows.Common-Controls"
version="6.0.0.0"
processorArchitecture="x86"
publicKeyToken="6595b64144ccf1df"
language="*"
/>
</dependentAssembly>
</dependency>
</assembly>
'''

CONTENT_DIRS = [ "media" ]
# EXTRA_FILES = [ "./media/icon16.ico", "./media/icon32.ico" ]
EXTRA_FILES = []

class MediaCollector(build_exe):
    def addDirectoryToZip(self, folder):
        full = os.path.join(self.collect_dir, folder)
        if not os.path.exists(full):
            self.mkpath(full)

        for f in glob.glob("%s/*" % folder):
            if os.path.isdir(f):
                self.addDirectoryToZip(f)
            else:
                name = os.path.basename(f)
                self.copy_file(f, os.path.join(full, name))
                self.compiled_files.append(os.path.join(folder, name))

    def copy_extensions(self, extensions):
        #super(MediaCollector, self).copy_extensions(extensions)
        build_exe.copy_extensions(self, extensions)

        for folder in CONTENT_DIRS:
            self.addDirectoryToZip(folder)

        for fileName in EXTRA_FILES:
            name = os.path.basename(fileName)
            self.copy_file(fileName, os.path.join(self.collect_dir, name))
            self.compiled_files.append(name)

myOptions = {
    "py2exe":{
        "compressed": 1,
        "optimize": 2,
        "ascii": 1,
        "includes": ["sip","encodings","encodings.*"],    # include encodings for codecs
        "packages": ["encodings"],                  #
        "dll_excludes": ["MSVCP90.dll","w9xpopen.exe"],
        "bundle_files": 2
     }
}

RT_MANIFEST = 24

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)

MyTerm_windows = Target(
    # used for the versioninfo resource
    copyright = appInfo.copyright,
    name = appInfo.title,
    version = appInfo.version,
    description = appInfo.file_name,
    author = appInfo.author,
    url = appInfo.url,

    # what to build
    script = "main_w.py",
    #dest_base = appInfo.file_name,
    dest_base = appInfo.title,
    icon_resources = [(1, "icon\icon.ico")],
    other_resources= [(RT_MANIFEST, 1, manifest_template % dict(prog = appInfo.title))]
)

setup(
    options = myOptions,
    cmdclass= {'py2exe': MediaCollector},
    data_files = [("", ["LICENSE", "README.txt"])],
    windows = [MyTerm_windows]
)
