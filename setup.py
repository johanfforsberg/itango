"""Setup file for itango."""

import json
import os
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
from shutil import rmtree
import sys
from tempfile import mkdtemp

try:
    from jupyter_client.kernelspec import KernelSpecManager
    HAVE_JUPYTER = True
except ImportError:
    HAVE_JUPYTER = False


def get_entry_points():
    major = int(platform.python_version_tuple()[0])
    name = 'itango3' if major == 3 else 'itango'
    return {
        "console_scripts": ["{0} = itango:run".format(name)],
        "gui_scripts": ["{0}-qt = itango:run_qt".format(name)]}


def install_jupyter_hook(prefix=None, root=None):
    """Make ITango available as a Jupyter kernel."""
    if not HAVE_JUPYTER:
        print("No jupyter installation detected; not installing itango kernel.")
        return
    spec = {"argv": [sys.executable,
                     "-m", "ipykernel",
                     "--profile", "tango",
                     "-f", "{connection_file}"],
            "display_name": 'ITango %i' % sys.version_info[0],
            "language": "python",
            }
    d = mkdtemp()
    os.chmod(d, 0o755)  # Starts off as 700, not user readable
    if sys.platform == 'win32':
        # Ensure that conda-build detects the hard coded prefix
        spec['argv'][0] = spec['argv'][0].replace(os.sep, os.altsep)
    with open(os.path.join(d, 'kernel.json'), 'w') as f:
        json.dump(spec, f, sort_keys=True, indent=4)
    if 'CONDA_BUILD' in os.environ:
        prefix = sys.prefix
        if sys.platform == 'win32':
            prefix = prefix.replace(os.sep, os.altsep)
    user = ('--user' in sys.argv)
    print('Installing Jupyter kernel spec:')
    print('  root: {0!r}'.format(root))
    print('  prefix: {0!r}'.format(prefix))
    print('  as user: {0}'.format(user))
    KernelSpecManager().install_kernel_spec(
        d, 'itango%d' % sys.version_info[0], user=user,
        replace=True, prefix=prefix)
    rmtree(d)


CLASSIFIERS = """\
Framework :: IPython
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: System :: Shells
""".splitlines()


class ITangoInstall(install):

    def run(self):
        root = self.root if self.root else None
        prefix = self.prefix if self.prefix else None
        try:
            install_jupyter_hook(prefix=prefix, root=root)
        except Exception:
            import traceback
            traceback.print_exc()
            print('Installing Jupyter hook failed.')
        install.run(self)


setup(
    name='itango',
    version='0.1.2',

    packages=find_packages(),
    package_data={'itango': [
        'resource/*.png', 'resource/*.svg']},
    entry_points=get_entry_points(),
    install_requires=[
        'IPython>=1.0',
        'PyTango>=9.2'],

    license='LGPL',
    classifiers=CLASSIFIERS,
    author='Tiago Coutinho',
    author_email="coutinho@esrf.fr",
    description='An interactive Tango client',
    long_description=open('README.rst').read(),
    url='https://github.com/tango-cs/itango',
    download_url='http://pypi.python.org/pypi/itango',
    platforms=['Linux', 'Windows XP/Vista/7/8'],
    keywords=['PyTango', 'IPython'],
    cmdclass={"install": ITangoInstall}
)
