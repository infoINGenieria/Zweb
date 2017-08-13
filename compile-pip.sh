#!/bin/env bash
export LANG=es_AR.utf-8
export LC_ALL=es_AR.utf-8

pip-compile --output-file requirements/default.txt requirements.in
