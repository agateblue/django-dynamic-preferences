import os
from setuptools import setup, find_packages
import dynamic_preferences
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dynamic-preferences',
    version=dynamic_preferences.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD',  # example license
    description='A django app for registering dynamic global, site and user preferences',
    long_description=README,
    url='http://code.eliotberriot.com/eliotberriot/django-dynamic-preferences',
    author='Eliot Berriot',
    author_email='contact@eliotberriot.com',
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "django",
    ],
)