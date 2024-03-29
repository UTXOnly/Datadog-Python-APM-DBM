import time
import psycopg2

GREEN = "\033[0;32m"
RED = "\033[0;31m"
RESET = "\033[0m"

connection_params = {
    'host': "localhost",
    'port': '5432',
    'dbname': 'nostr',
    'user': 'nostr',
    'password': 'nostr'
}


def create_datadog_user_and_schema(conn_obj, db):
    with conn_obj.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname='datadog'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE USER datadog WITH password 'datadog'")
            print(f"{GREEN}datadog user created in {db} database{RESET}")
            conn.commit()

    with conn_obj.cursor() as cur:
        cur.execute("SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'datadog')")
        schema_exists = cur.fetchone()[0]

    if schema_exists:
        print(f"{RED}datadog schema already exists in db{RESET}")

    try:
        with conn_obj.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
    except Exception as e:
        print(f"An error occurred while executing CREATE EXTENSION: {e}")
    
    try:
        with conn_obj.cursor() as cur:
            cur.execute("CREATE SCHEMA datadog; GRANT USAGE ON SCHEMA datadog TO datadog; GRANT USAGE ON SCHEMA public TO datadog; GRANT pg_monitor TO datadog;")
            print(f"{GREEN}datadog schema created and permissions granted in {db} database{RESET}")
            conn.commit()
    except Exception as e:
        print(f"An error occurred while creating datadog schema and granting permissions: {e}")

def explain_statement(conn_obj):
    try:
        with conn_obj.cursor() as cur:
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
            conn_obj.commit()
            time.sleep(2)
        print(f"{GREEN}Explain plans statement completed{RESET}")
    except Exception as e:
        print(f"An error occurred while creating explain statement: {e}")


def check_postgres_stats(conn_obj, db):
    try:
        conn_obj = psycopg2.connect(**connection_params)
        with conn_obj.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_stat_database LIMIT 1;")
            print(f"{GREEN}Postgres connection - OK in {db}")

            cur.execute("SELECT 1 FROM pg_stat_activity LIMIT 1;")
            print(f"{GREEN}Postgres pg_stat_activity read OK in {db}")

            cur.execute("SELECT 1 FROM pg_stat_statements LIMIT 1;")
            print(f"{GREEN}Postgres pg_stat_statements read OK {db}")

        print(f"{RED}\n############### Moving On... to next database ###############################\n{RESET}")
        conn_obj.close()
    except psycopg2.OperationalError:
        print(f"{RED}Cannot connect to Postgres database to check stats {db}{RESET}")
    except psycopg2.Error:
        print(f"{RED}Error while accessing Postgres statistics in {db}{RESET}")


def list_databases(conn_obj):
    with conn_obj.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = [row[0] for row in cur.fetchall() if not row[0].startswith('template')]
    return databases

try:
    conn = psycopg2.connect(**connection_params)
    databases_list = list_databases(conn)
except psycopg2.Error as e:
    print("An error occurred while connecting to the database:", e)


# Iterate through the list of database names, run checks, and create schemas
for db_name in databases_list:
    print(f"{GREEN}Discovered database: {RESET}{db_name} \nCreating schema and checking permissions + stats")
    connection_params['dbname'] = db_name
    conn = psycopg2.connect(**connection_params)
    create_datadog_user_and_schema(conn_obj=conn, db=connection_params['dbname'])
    explain_statement(conn_obj=conn)
    check_postgres_stats(conn_obj=conn, db=db_name)

print("Setup complete!")
