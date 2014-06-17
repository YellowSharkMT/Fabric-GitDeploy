"""
Fabric-GitDeploy
-------------

This is a WordPress-centric Fabric package that contains a number of tasks to aid in the process of deploying web apps.
"""
from setuptools import setup

setup(
    name='Fabric-GitDeploy',
    version='1.0',
    url='http://yellowsharkmt.com/fabric-gitdeploy/',
    license='BSD',
    author='YellowSharkMT',
    author_email='yellowsharkmt@gmail.com',
    description='A WordPress-centric Fabric package that contains a number of tasks to aid in the process of deploying web apps.',
    long_description=__doc__,
    #py_modules=['flask_htmlemail'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['fab_gd'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Fabric>=1.5'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)