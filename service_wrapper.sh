#! /usr/bin/env bash

export PG_HOST=localhost
export PG_NAME=automated_test
export PG_USER=gdc_test
export PG_PASS=gdc_test

export PG_ADMIN_USER=postgres
export PG_ADMIN_PASS=postgres

# To use:
#   ./service_wrapper.sh pytest
$@