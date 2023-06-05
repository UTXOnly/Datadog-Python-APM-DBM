import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

GREEN = "\033[0;32m"
RED = "\033[0;31m"
RESET = "\033[0m"

connection_params = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def create_datadog_user_and_schema(conn, db):
    db = db
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname='datadog'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE USER datadog WITH password 'datadog'")
            print(f"{GREEN}datadog user created in {db}{GREEN} database{RESET}")
            conn.commit()

    with conn.cursor() as cur:
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'datadog')")
        schema_exists = cur.fetchone()[0]

    if schema_exists:
        print(f"{RED}datadog schema already exists in db{RESET}")

    else:

        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA datadog")
            cur.execute("GRANT USAGE ON SCHEMA datadog TO datadog")
            cur.execute("GRANT USAGE ON SCHEMA public TO datadog")
            cur.execute("GRANT pg_monitor TO datadog")
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
            print(f"{GREEN}datadog schema created and permissions granted in {RESET}{db}{GREEN} database{RESET}")
            conn.commit()


    with conn.cursor() as cur:
        #cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
        cur.execute("""
        CREATE OR REPLACE FUNCTION datadog.explain_statement(
            l_query TEXT,
            OUT explain JSON
        )
        RETURNS SETOF JSON AS
        $$
        DECLARE
            curs REFCURSOR;
            plan JSON;
        BEGIN
            OPEN curs FOR EXECUTE pg_catalog.concat('EXPLAIN (FORMAT JSON) ', l_query);
            FETCH curs INTO plan;
            CLOSE curs;
            RETURN QUERY SELECT plan;
        END;
        $$
        LANGUAGE 'plpgsql'
        RETURNS NULL ON NULL INPUT
        SECURITY DEFINER;
        """)
        conn.commit()
        time.sleep(2)
     
    print(f"{GREEN}Explain plans statement completed for:{RESET}{db}{GREEN} database{RESET}")


def check_postgres_stats(connection_params,db):
    try:
        conn = psycopg2.connect(**connection_params)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_stat_database LIMIT 1;")
            print(f"{GREEN}Postgres connection - OK in {RESET}{db}")
        
            cur.execute("SELECT 1 FROM pg_stat_activity LIMIT 1;")
            print(f"{GREEN}Postgres pg_stat_activity read OK in {RESET}{db}")

            cur.execute("SELECT 1 FROM pg_stat_statements LIMIT 1;")
            print(f"{GREEN}Postgres pg_stat_statements read OK {RESET}{db}")

        print(f"{RED}\n############### Moving On... to next database ###############################\n{RESET}")
        conn.close()
    except psycopg2.OperationalError:
        print(f"{RED}Cannot connect to Postgres databse to check stats{RESET}{db}")
    except psycopg2.Error:
        print(f"{RED}Error while accessing Postgres statistics{RESET} in {db}")

def list_databases(conn):
    
    with conn.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = [row[0] for row in cur.fetchall() if not row[0].startswith('template')]

    return databases

conn = psycopg2.connect(**connection_params)
databases = list_databases(conn)

# Iterate through the list of database names, run 
for db_name in databases:

    print(f"{GREEN}Discovered database: {RESET}{db_name} \n Creating schema and checking premissions + stats")
    connection_params['dbname'] = db_name
    conn = psycopg2.connect(**connection_params)
    create_datadog_user_and_schema(conn, connection_params['dbname'])
    check_postgres_stats(connection_params, db_name)

print("Setup complete!")