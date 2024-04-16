[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commitlogoColor=white)](https://github.com/pre-commit/pre-commit)

---
# gdc-ng-models

Repository for GDC models that do not have a dependency on [psqlgraph](https://github.com/NCI-GDC/psqlgraph).

The `ng` in `gdc-ng-models` stands for _non-graph_.

- [gdc-ng-models](#gdc-ng-models)
  - [Testing](#testing)
  - [Command-Line Scripts](#command-line-scripts)
  - [Setup pre-commit hook to check for secrets](#setup-pre-commit-hook-to-check-for-secrets)


## Testing

```sh
psql -c "create user gdc_test with superuser password 'gdc_test';" -U postgres
psql -c 'create database automated_test with owner "gdc_test";' -U postgres
pytest tests/
```

Or we can use [tox](https://tox.readthedocs.io/en/latest/) for testing

```
pip install tox
tox
```

## Resources
At the time of this writing, a database migration of ng-models had not occurred in awhile. There
are multiple references for running the migrations.
* This README.md
* [Confluence Wiki](https://gdc-ctds.atlassian.net/wiki/spaces/GDC/pages/19402891/Database+migration)
* [Cohort API](https://github.com/NCI-GDC/cohortapi?tab=readme-ov-file#cohort-database-tables)


## Command-Line Scripts

This repository supplies the `ng-models` script which allows you to create the databases and tables in development and production environments.

To use, supply the `-m` parameter specifying the module (and related models/tables to be created). See example usage below:

```sh
ng-models -m misc --host 127.0.0.1 -d automated_test -u postgres -p postgres
```

### Setup the execution environment
If you would like to run alembic directly.
```sh
# datatools.service.consul or repl.service.consul
sudo -i -u ubuntu # Ubuntu Pro
sudo -i -u ec2-user # Amazon Linux 

export http_proxy=http://cloud-proxy:3128 && export https_proxy=http://cloud-proxy:3128
git clone https://github.com/NCI-GDC/gdc-ng-models.git
cd gdc-ng-models/
python3 -m venv venv
source venv/bin/activate
python --version  # verify the python version, expects python 3.9
pip install -e ".[alembic]" --index-url https://nexus.osdc.io/repository/pypi-all/simple

```
> Update the alembic.ini file for local execution, if running on the datatools VM this 
>  will already be configured in /var/tungsten/services/datatools/alembic.ini
>  `sqlalchemy.url = postgres://dev_admin:<pass>@postgres.service.consul/dev_gdc`


### Option: Install database models
```bash
################################################
# Uncomment the target environment for execution
################################################
# export ENV_PREFIX=prod PASS=$(cat __path_to_password_file__/prod_admin) # PROD
# export ENV_PREFIX=qa PASS=$(cat __path_to_password_file__/qa_admin) # QA
# export ENV_PREFIX=dev PASS=$(cat __path_to_password_file__/dev_admin) # DEV
export MODEL=<model_name> # e.g., MODEL=cohort

# Create tables
ng-models \
  -m $MODEL \
  --host postgres.service.consul \
  -d ${ENV_PREFIX}_gdc \
  -u $USER \
  -p "$PASS" create

# Add write permission
ng-models \
  -m $MODEL \
  --host postgres.service.consul \
  -d ${ENV_PREFIX}_gdc \
  -u $USER \
  -p "$PASS" \
  grant -r ${ENV_PREFIX}_graph_readwrite -P write
  
# Add READ permission
ng-models \
  -m $MODEL \
  --host postgres.service.consul \
  -d ${ENV_PREFIX}_gdc \
  -u $USER \
  -p "$PASS" \
  grant -r ${ENV_PREFIX}_graph_readonly -P read
```

### Option: Migrate database models

> WARNING: That '+' sign in front of '+1' is _REALLY_ important.

Using [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) migrate existing data models

> NOTE: offline mode - alembic will print out the sql it will execute for `upgrade` and `downgrade`
>   commands if you supply the `--sql` flag. It does not accept relative identifiers.


```bash
############################################
# `alembic_migration` is a script held in tungsten and deployed to the datatools VM
# https://github.com/NCI-GDC/tungsten/blob/develop/salt/srv/services/datatools/wrappers/alembic_migration
#
# datatools uses the alembic from gdc-ng-models.
#   alembic==1.13.0
#      # via gdc-ng-models
############################################

# make sure the migration scripts you want to run are located in /var/tungsten/services/datatools/deploy/current/venv/lib/python3.9/site-packages/gdc_ng_models/alembic/versions

# check to see what version is currently in postgres (if its empty, also fine)
sudo bash alembic_migration current  # with wrapper on datatools
  # or
  alembic --config alembic.ini current # on repl (need to update the sqlalchemy.url in alembic.ini)

# apply the necessary migrations (if you want to apply all of them, do the following)
sudo bash alembic_migration upgrade head
  # or upgrade to version
  alembic --config alembic.ini upgrade +1

# if you just wanted to apply 1 revision from the current HEAD, do the following
sudo bash alembic_migration upgrade +1
  # or upgrade to version
  alembic --config alembic.ini upgrade +1
  # or get the SQL to run manually
  alembic --config alembic.ini upgrade 12dbbcac7a1d:38eab5dd7b0d --sql

# if you want to rollback 1 revision from the current HEAD, do the following
sudo bash alembic_migration downgrade -1
  # or downgrade to version
  alembic --config alembic.ini downgrade e9d53a640d5d
  # or get the SQL to run manually
  alembic --config alembic.ini downgrade 12dbbcac7a1d:e9d53a640d5d --sql
```
    
## Setup pre-commit hook to check for secrets

We use [pre-commit](https://pre-commit.com/) to setup pre-commit hooks for this repo.
We use [detect-secrets](https://github.com/Yelp/detect-secrets) to search for secrets being committed into the repo. 

To install the pre-commit hook, run
```
pre-commit install
```

To update the .secrets.baseline file run
```
detect-secrets scan --update .secrets.baseline
```

`.secrets.baseline` contains all the string that were caught by detect-secrets but are not stored in plain text. Audit the baseline to view the secrets . 

```
detect-secrets audit .secrets.baseline
```


