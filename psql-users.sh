psql -U postgres -c "create user test with superuser password 'test';"
psql -U postgres -c "create database automated_test with owner test;"
psql -U postgres -c "create database big_int_test with owner test;"
