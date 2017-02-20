#!/bin/bash

python ./caipirinha/manage.py db upgrade
python ./caipirinha/app.py
