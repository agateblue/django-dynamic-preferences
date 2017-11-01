#!/bin/bash

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME

# Install essential packages from Apt
apt-get update -y
# Python dev packages
apt-get install -y build-essential python python3-dev curl
# python-setuptools being installed manually
wget https://bootstrap.pypa.io/ez_setup.py -O - | python3
# Dependencies for image processing with Pillow (drop-in replacement for PIL)
# supporting: jpeg, tiff, png, freetype, littlecms
# (pip install pillow to get pillow itself, it is not in requirements.txt)
apt-get install -y pango1.0-tests libcairo2-dev libffi-dev libssl-dev libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libssl-dev libxml2-dev libxslt1-dev gettext
# Git (we'd rather avoid people keeping credentials for git commits in the repo, but sometimes we need it for pip requirements that aren't in PyPI)
apt-get install -y git

# virtualenv global setup
if ! command -v pip; then
    easy_install -U pip
fi
if [[ ! -f /usr/local/bin/virtualenv ]]; then
    pip3.4 install virtualenv virtualenvwrapper stevedore virtualenv-clone
fi

# bash environment global setup
cp -p $PROJECT_DIR/install_bashrc /home/vagrant/.bashrc

# virtualenv setup for project
su - vagrant -c "/usr/local/bin/virtualenv $VIRTUALENV_DIR --python=/usr/bin/python3 && \
    echo $PROJECT_DIR > $VIRTUALENV_DIR/.project"

echo "workon $VIRTUALENV_NAME" >> /home/vagrant/.bashrc

# Django project setup
su - vagrant -c "source $VIRTUALENV_DIR/bin/activate"