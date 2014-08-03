#!python3

import os
import re
import sys
import zipfile
import subprocess
from configparser import ConfigParser
from baker import Baker

class MyBaker(Baker):
    def run_all(self, args=sys.argv):
        arg0 = args[0]
        args = args[1:]
        a = []
        for arg in args:
            if arg in self.commands:
                if a:
                    self.run(a)
                a = [arg0]
            a.append(arg)

        if a:
            self.run(a)

vim = MyBaker()

VIM_URL = "https://vim.googlecode.com/hg"

@vim.command()
def get(target='.'):
    subprocess.check_call(['hg', 'clone', VIM_URL, 'vim'], cwd=target)

@vim.command()
def patch(target='.'):
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

@vim.command()
def build(target='.'):
    batfile = os.path.join(target, 'do_build.cmd')
    with open(batfile, "w") as f:
        f.write(BUILD_SCRIPT)

    subprocess.check_call(['cmd', '/c', batfile], cwd=target)

@vim.command()
def package(target='.'):
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

@vim.command()
def all():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as d:
        get(d)
        patch(d)
        build(d)
        package(d)

if __name__ == '__main__':
    vim.run_all()
