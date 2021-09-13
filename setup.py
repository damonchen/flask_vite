"""
Flask-VITE
-------------

This is the description for that library
"""
from setuptools import setup


setup(
    name='Flask-VITE',
    version='1.0',
    url='https://github.com/damonchen/flask-vite',
    license='BSD',
    author='Damon Chen',
    author_email='netubu@gmail.com',
    description='flask for vite plugin',
    long_description=__doc__,
    py_modules=['flask_vite'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_vite'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
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