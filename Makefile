# http://clarkgrubb.com/makefile-style-guide

MAKEFLAGS += --warn-undefined-variables --no-print-directory
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := test
.DELETE_ON_ERROR:
.SUFFIXES:

# Python build

$(eval NAME := $(shell python setup.py --name))
$(eval PY_NAME := $(shell python setup.py --name | sed 's/-/_/g'))
$(eval VERSION := $(shell python setup.py --version))

SOURCE := $(wildcard botocore_libfaketime/*) setup.py
SDIST := dist/$(NAME)-$(VERSION).tar.gz
WHEEL := dist/$(PY_NAME)-$(VERSION)-py2.py3-none-any.whl

.PHONY: all
all: build

$(SDIST): $(SOURCE)
	python setup.py sdist

$(WHEEL): $(SOURCE)
	python setup.py bdist_wheel

.PHONY: build
build: $(SDIST) $(WHEEL)

.PHONY: clean
clean:
	rm -rf build dist *.egg-info

# Docker testing

docker_tag := botocore-libfaketime

.PHONY: $(docker_tag)
$(docker_tag): $(WHEEL)
	cp $(WHEEL) docker/
	docker build -t $(docker_tag) docker

.PHONY: test
test: $(docker_tag)
	docker run \
		--rm \
		--interactive \
		--tty \
		--env AWS_DEFAULT_REGION \
		--env AWS_ACCESS_KEY_ID \
		--env AWS_SECRET_ACCESS_KEY \
		--env AWS_SESSION_TOKEN \
		$(docker_tag)
