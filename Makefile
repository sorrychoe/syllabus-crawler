.PHONY: init lint run clean

NAME = syllabus-crawler

SHELL := bash
python = python3

ifeq ($(OS),Windows_NT)
	python := python
endif

ifdef user
	pip_user_option = --user
endif

init:
	$(python) -m pip install $(pip_user_option) --upgrade pip
	$(python) -m pip install $(pip_user_option) -r requirements.txt
	$(python) -m pre_commit install

lint:
	$(python) -m isort --settings-file=.isort.cfg ./
	$(python) -m flake8 --config=.flake8 ./

run:
	$(python) main.py

clear:
	rm -fr __pycache__
