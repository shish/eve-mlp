#!/usr/bin/env python

"""
Trying to keep compile_linux.sh, compile_windows.bat, and compile_osx.sh
in sync is a pain. Also, because the windows command line is terrible,
trying to do anything at all in compile_windows.bat is also a pain.

This is an ugly bloated mess, but it seems better than the alternatives...
"""

import subprocess
import os
import platform
import tarfile
import zipfile
import textwrap


os_type = platform.system()


def get_spec():
    gui_data = [
        ("icon.ico", "icon.ico", "DATA"),
        ("help.html", "help.html", "DATA"),
        ("LICENSE.txt", "LICENSE.txt", "DATA"),
    ]

    bin_ext = ""
    if os_type == "Windows":
        bin_ext = ".exe"

    return textwrap.dedent("""
        # GUI spec
        a = Analysis(['main_gui.py'])
        pyz = PYZ(a.pure)
        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas + %(gui_data)r,
            name=os.path.join('dist', 'eve-gmlp%(bin_ext)s'),
            debug=False,
            strip=None,
            upx=True,
            console=False,
            icon='icon.ico'
        )
        app = BUNDLE(
            exe,
            name=os.path.join('dist', 'eve-gmlp.app')
        )
        # CLI spec
        a = Analysis(['main_cli.py'])
        pyz = PYZ(a.pure)
        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            name=os.path.join('dist', 'eve-mlp%(bin_ext)s'),
            debug=False,
            strip=None,
            upx=True,
            console=True,
            icon='icon.ico'
        )
    """.rstrip()) % {
        "gui_data": gui_data,
        "bin_ext": bin_ext,
    }


def init_environ():
    if os_type == "Linux":
        os.environ["LD_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu/"

    if os_type == "Windows":
        os.environ["PATH"] = os.environ.get("PATH", "") + ";C:\Python27"


def get_version():
    try:
        version = subprocess.check_output("git describe", shell=True)
        version = version.strip()[1:]
    except:
        version = "UNKNOWN"
    return version


def build(version):
    print "*** Building EVE-MLP %s Binaries" % version

    file("_compile.spec", "w").write(get_spec())
    pyinstaller = os.path.join("..", "pyinstaller-2.0", "pyinstaller.py")
    comp = subprocess.Popen("python %s _compile.spec" % pyinstaller, shell=True)
    comp.wait()
    os.unlink("_compile.spec")


def package(version):
    print "*** Building %s Packages" % os_type

    os.chdir("dist")

    if os_type == "Linux":
        tar = tarfile.open("eve-mlp-%s.tar.gz" % version, "w:gz")
        tar.add("eve-mlp")
        tar.close()

        tar = tarfile.open("eve-gmlp-%s.tar.gz" % version, "w:gz")
        tar.add("eve-gmlp")
        tar.close()

    if os_type == "Windows":
        zip = zipfile.ZipFile("eve-mlp-%s.zip" % version, "w")
        zip.write("eve-mlp.exe")
        zip.close()

        zip = zipfile.ZipFile("eve-gmlp-%s.zip" % version, "w")
        zip.write("eve-gmlp.exe")
        zip.close()


if __name__ == "__main__":
    init_environ()
    version = get_version()
    build(version)
    package(version)
