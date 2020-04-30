[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commitlogoColor=white)](https://github.com/pre-commit/pre-commit)

---
# gdc-ng-models

Repository for GDC models that do not have a dependency on [psqlgraph](https://github.com/NCI-GDC/psqlgraph).

The `ng` in `gdc-ng-models` stands for _non-graph_.

## Testing

```sh
psql -c "create user gdc_test with superuser password 'gdc_test';" -U postgres
psql -c 'create database automated_test with owner "gdc_test";' -U postgres
./service_wrapper.sh pytest tests/
```

## Command-Line Scripts

This repository supplies the `ng-models` script which allows you to create the databases and tables in development and production environments.

To use, supply the `-m` parameter specifying the module (and related models/tables to be created). See example usage below:

```sh
./service_wrapper.sh ng-models -m download_reports
ng-models -m misc --host 127.0.0.1 -d automated_test -u postgres -p postgres
```

The examples above show how you can either: 1) supply the environment variables or 2) manually input them via parser arguments.

    
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
git add .secrets.baseline
```

`.secrets.baseline` contains all the string that were caught by detect-secrets but are not stored in plain text. Audit the baseline to view the secrets . 

```
detect-secrets audit .secrets.baseline
```


