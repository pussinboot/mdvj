from setuptools import setup

import sys;

is64bit = sys.maxsize > 2**32
if is64bit:
    pygame_whl="http://www.lfd.uci.edu/~gohlke/pythonlibs/xmshzit7/pygame-1.9.2a0-cp34-none-win_amd64.whl"
    pywin32_whl = "https://pypi.python.org/packages/cp34/p/pypiwin32/pypiwin32-219-cp34-none-win_amd64.whl"
else:
    pygame_whl="http://www.lfd.uci.edu/~gohlke/pythonlibs/xmshzit7/pygame-1.9.2a0-cp34-none-win32.whl"
    pywin32_whl = "https://pypi.python.org/packages/cp34/p/pypiwin32/pypiwin32-219-cp34-none-win32.whl"
setup(
    name='mdvj',
    version='0.5.1',
    description='Milkdrop VJ Tool',
    long_description="""
mdvj - milkdrop vj midi controller
""",
    url='https://github.com/pussinboot/mdvj',

    keywords='vj midi',
    packages=['mdvj'],

    install_requires=[
        "Pillow",
        "pywin32",
        "pygame"
    ],

    dependency_links=[
        pygame_whl,
        pywin32_whl
    ],
    package_data={
            'mdvj' : ['error_scrot.bmp']
            },
    entry_points = {
            'console_scripts': [
                'mdvj = mdvj.mdvj:main'
            ]
        }
)