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
