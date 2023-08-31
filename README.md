
[![Pylint](https://github.com/UTXOnly/Datadog-Python-APM-DBM/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/UTXOnly/Datadog-Python-APM-DBM/actions/workflows/pylint.yml)

# Datadog_APM_DBM
Simple Python Flask app and Postgres DB for testing [Connecting DBM and APM](https://docs.datadoghq.com/database_monitoring/guide/connect_dbm_and_apm/?tab=python) and [Postgres integration](https://docs.datadoghq.com/integrations/postgres/?tab=docker) with the Datadog agent. This repo includes a `postgresql.conf` file with the necessary modifications to use [Datadog Database Monitoring](https://docs.datadoghq.com/database_monitoring/setup_postgres/selfhosted/?tab=postgres10). Part of that that script prepares discovers databases, iterating through each database to create the necessary schemas and install the `pg_stat_statements` extension if it doesn't already exist. 


## Prerequisites
* Docker-compose
* Datadog API key (If you don't already have an account, [get one here](https://www.datadoghq.com/free-datadog-trial/))
* Python3.10


## Configuration


Before running the code, make sure to configure the necessary environment variables in a `.env` file. The following environment variables should be set:

```
DB_HOST=172.16.238.2
DB_PORT=5432
DB_NAME=<Name of the database to connect to>
DB_USER=<Username for authenticating the database connection>
DB_PASSWORD=<Password for authenticating the database connection>
DD_API_KEY=<Datadog API key>
```

You will also need to install the necessary Python modules by running this command:

```
pip install -r requirements.txt
```

# Usage

After completeing above steps, start the Postgres container and Datadog agent container running this command from the reopistory's parent directory:

```
docker-compose up -d 
```

Run the `dbm_setup.py` script to add the `datadog` user and all of the necessay permissions/schemas to use DBM in each discovered databse. This creates the role with `datadog` as the username and password, you can change this to whatever you like. 

```
python3 dbm_setup.py
```

Now you can run you Flask app with `ddtrace` to collect traces

```
ddtrace-run flask_app.py
```

In another terminal you can run the `test_requests.py` script to send requests your API and also collect traces

```
ddtrace-run test_requests.py
```

## Datadog agent configuration

This program uses the Docker container Datadog agent and configures the Postgres integration via autodiscovered Docker labels. This is the configuration used to match the credentials int he `dbm_setup.py` script and the ip address assigned in the `docker-compose.yaml` file.

```
    labels:
      com.datadoghq.ad.check_names: '["postgres"]'
      com.datadoghq.ad.init_configs: '[{}]'
      com.datadoghq.ad.instances: |
        [
          {
            "dbm": true,
            "username": "datadog",
            "password" : "datadog",
            "host": "172.16.238.2",
            "port" : "5432",
            "disable_generic_tags": true,
            "tags" : "db:local_test",
            "service" : "test-pg-db",
            "reported_hostname" : "test-pg-db"
          }
        ]
```

## Results

You are now running APM for a Python application and DBM for a Postgres database and have connected the two.

![Image 2023-06-05 at 2 09 02 AM](https://github.com/UTXOnly/Datadog_APM_DBM/assets/49233513/cf2f4830-8f32-4fc7-8034-d2baf1950061)

You can now take advantage of connecting your traces and DBM data


![ezgif com-optimize](https://github.com/UTXOnly/Datadog_APM_DBM/assets/49233513/5afffa6e-5e46-4ad5-a26f-9b26449032f5)






