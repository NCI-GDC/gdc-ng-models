# gdc-ng-models

Repository for GDC models that do not have a dependency on [psqlgraph](https://github.com/NCI-GDC/psqlgraph).

The `ng` in `gdc-ng-models` stands for _non-graph_.

## Testing

```sh
psql -c "create user gdc_test with superuser password 'gdc_test';" -U postgres
psql -c 'create database automated_test with owner "gdc_test";' -U postgres
./service_wrapper_testing.sh pytest tests/
```