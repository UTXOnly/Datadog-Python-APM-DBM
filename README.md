# Datadog_APM_DBM
Simple Python Flask app and Postgres DB for testing [Connecting DBM and APM](https://docs.datadoghq.com/database_monitoring/guide/connect_dbm_and_apm/?tab=python) with the Datadog agent. 

## Prerequisites
* Docker-compose
* Datadog API key (If you don't already have an account, [get one here](https://www.datadoghq.com/free-datadog-trial/))


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

## Results

You are now running APM for a Python application and DBM for a Postgres database and have connected the two.

![Image 2023-06-05 at 1 28 20 AM](https://github.com/UTXOnly/Datadog_APM_DBM/assets/49233513/65ece23c-e522-4fcb-8754-88a420f16a78)

You can take advantage of connecting your traces and DBM data


![ezgif com-optimize](https://github.com/UTXOnly/Datadog_APM_DBM/assets/49233513/5afffa6e-5e46-4ad5-a26f-9b26449032f5)






