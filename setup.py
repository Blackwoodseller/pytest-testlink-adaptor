""" Pytest-TestLink adaptor setup file """

from setuptools import setup
__author__ = 'Blackwoodseller'

long_description = 'pytest-testlink-adaptor is a plugin for ' \
                   'pytest that reports to testlink.' \
                   'It is improved fork of pytest_testlink alpha.'

VERSION = '0.32'
PYPI_VERSION = '0.32'

setup(
    name='pytest-testlink-adaptor',
    description='pytest reporting plugin for testlink',
    long_description=long_description,
    version=VERSION,

    url='https://github.com/Blackwoodseller/pytest-testlink-adaptor/',
    download_url=
    'https://github.com/Blackwoodseller/pytest-testlink-adaptor/tarball/%s' %
    PYPI_VERSION,
    license='MIT',
    author='Blackwoodseller',
    author_email='alpapot@gmail.com',
    py_modules=['pytest_testlink_adaptor'],
    entry_points={'pytest11': ['testlink = pytest_testlink_adaptor']},
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['pytest>=2.6', 'TestLink-API-Python-client', 'path.py'],
    classifiers=[
        'Environment :: Plugins',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
