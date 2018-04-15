import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_exe_options = {"includes": ["os", "idna", "queue"], "excludes": ["tkinter", "sqlite3", "QtSql", "matplotlib"
                                               
    # 'unittest',   # why can't I remove this?
    'matplotlib', 'wx', 'nose', 'Tkinter', 'distutils',

    'bitarray', 'bottleneck', 'bzip2', 'cdecimal',
    'cffi', 'comtypes', 'conda-build', 'configobj', 'console_shortcut',
    'cryptography', 'cython', 'docutils', 'fastcache', 'flask',
    'freetype', 'funcsigs', 'greenlet', 'grin', 'h5py',
    'ipaddress', 'ipython-notebook', 'ipython-qtconsole',
    'ipython_genutils', 'itsdangerous', 'jedi', 'jinja2', 'jpeg',
    'jsonschema', 'jupyter_client', 'jupyter_core', 'launcher',
    'libsodium', 'markupsafe', 'mistune', 'multipledispatch',
    'nbformat', 'nltk', 'node-webkit', 'nose', 'patsy', 'pickleshare',
    'ply', 'pyasn1', 'pycosat', 'pycparser', 'pycrypto', 'pycurl',
    'pyflakes', 'pyopenssl', 'pyparsing', 'pyreadline', 'pytables',
    'python-dateutil', 'rope', 'scikit-image', 'simplegeneric',
    'singledispatch', 'sockjs-tornado', 'ssl_match_hostname',
    'statsmodels', 'sympy', 'tk', 'toolz', 'ujson', 'unicodecsv',
    'xlrd', 'xlwt', 'zeromq', 'alabaster',
    'anaconda-client', 'appdirs', 'astroid', 'astroid', 'astropy'
                                                        'babel', 'backports_abc', 'blackwidow', 'blaze-core', 'bokeh',
    'boto', 'clyent', 'coverage',
    'curl', 'cycler', 'cytoolz', 'datashape', 'decorator', 'freeimage',
    'gl2ps', 'oce', 'pythonocc-core', 'tbb', 'enum34', 'et_xmlfile',
    'futures', 'gevent', 'gevent-websocket', 'hdf5', 'ipykernel',
    'ipython', 'ipywidgets', 'jdcal', 'jupyter', 'jupyter_console',
    'lazy-object-proxy', 'libtiff', 'llvmlite', 'logilab-common', 'menuinst', 'MeshPy',
    'msvc_runtime', 'nbconvert', 'networkx', 'notebook', 'numba',
    'numexpr', 'numpydoc', 'odo', 'openmdao', 'openpyxl',
    'openssl', 'pandas', 'path.py', 'pep8', 'pi', 'pip',
    'psutil', 'py', 'pylint', 'pylint', 'pytest',
    'pytools', 'pytz', 'pyyaml', 'pyzmq',
    'qtconsole', 'ruamel_yaml', 'RunSnakeRun',
    'scikit-learn',
    'snowballstemmer', 'sphinx', 'sphinx_rtd_theme', 'spyder',
    'spyder-app', 'sqlalchemy', 'sqlitedict', 'SquareMap', 'tornado',
    'traitlets', 'werkzeug', 'wheel',
    'wrapt', 'wxpython', 'xlsxwriter', 'xlwings',

    # not required...strange...
    'conda', 'conda-env', 'pywin32', 'python', 'vs2008_runtime',
 'anaconda',

    # things we're using
    'libpng',
    # 'sip', 'colorama', 'numpy', 'pillow', 'qt','scipy',
    # 'vtk', 'six', 'mkl', 'mkl-service',
], "optimize": 2}

includes = ['login_window']
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('./src/vpn_client.py', base=base)
]

setup(name='Merlink',
      version='0.1.0',
      description='PyQt based VPN client for Meraki firewalls',
      options=dict(build_exe=build_exe_options),
      executables=executables)
