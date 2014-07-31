#!python3

import os
import re
import zipfile
import subprocess
from configparser import ConfigParser

VIM_URL = "https://vim.googlecode.com/hg"

def get_source(target):
    subprocess.check_call(['hg', 'clone', VIM_URL, 'vim'], cwd=target)

def patch(target):
    repo = os.path.join(target, 'vim')
    cp = ConfigParser(allow_no_value=True)
    cp.read('patches/patches.ini')
    for patch, _ in cp.items('patches'):
        subprocess.check_call([
            'hg', '-R', repo, 'import',
            os.path.join('patches', patch),
            '-m', cp[patch]['message']
        ])
    

def get_vsvars():
    for vc in ('VS100COMNTOOLS', 'VS90COMNTOOLS'):
        if vc in os.environ:
            return os.path.join(os.environ[vc], 'vsvars32.bat')
    raise RuntimeError("Cannot find Visual Studio 2008 or 2010")

BUILD_SCRIPT = """\
call "{}"
cd vim\\src
nmake /f make_mvc.mak CPUNR=i686 WINVER=0x0500
nmake /f make_mvc.mak GUI=yes CPUNR=i686 WINVER=0x0500
""".format(get_vsvars())

def build(target):
    batfile = os.path.join(target, 'do_build.cmd')
    with open(batfile, "w") as f:
        f.write(BUILD_SCRIPT)

    subprocess.check_call(['cmd', '/c', batfile], cwd=target)

def package(target):
    def src(name):
        return os.path.join(target, 'vim', 'src', name)
    runtime = os.path.join(target, 'vim', 'runtime')

    version_re = re.compile('.*VIM_VERSION_NODOT\\s*"(vim\\d\\d[^"]*)".*', re.S)
    with open(src('version.h')) as f:
        VIMRTDIR = version_re.match(f.read()).group(1)


    print("Writing {}".format(os.path.join(os.getcwd(), 'Vim.zip')))

    zf = zipfile.ZipFile('Vim.zip', 'w', compression=zipfile.ZIP_DEFLATED)
    zf.write(src('vim.exe'), 'Vim/vim.exe')
    zf.write(src('gvim.exe'), 'Vim/gvim.exe')
    zf.write(src('vimrun.exe'), 'Vim/vimrun.exe')
    zf.write(src('xxd/xxd.exe'), 'Vim/xxd.exe')
    zf.write(src('gvimext/gvimext.dll'), 'Vim/gvimext.dll')
    zf.write(src('vimtbar.dll'), 'Vim/vimtbar.dll')
    for dirpath, dirnames, filenames in os.walk(runtime):
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            zip_path = 'Vim/' + VIMRTDIR + '/' + os.path.relpath(fullpath, runtime)
            zf.write(fullpath, zip_path)
    zf.close()

if __name__ == '__main__':
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as d:
        get_source(d)
        patch(d)
        build(d)
        package(d)
