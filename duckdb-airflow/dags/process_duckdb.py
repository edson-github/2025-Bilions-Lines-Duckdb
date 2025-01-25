import duckdb
from airflow.decorators import dag, task
from datetime import datetime, timedelta


@dag(
    schedule_interval="0 0 * * *",  # Daily at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['duckdb', 'etl'],
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)
def process_duckdb_daily():
    @task()
    def process_data():
        conn = duckdb.connect(database=":memory:")
        conn.execute("PRAGMA threads=16")
        conn.execute("PRAGMA memory_limit='12GB'")
        
        result = conn.execute("""
            SELECT station,
                MIN(temperature) AS min_temperature,
                CAST(AVG(temperature) AS DECIMAL(3,1)) AS mean_temperature,
                MAX(temperature) AS max_temperature
            FROM read_csv(
                'data/medicoes_1000000000.txt',
                AUTO_DETECT=FALSE,
                sep=';',
                columns={'station': 'VARCHAR', 'temperature': 'DECIMAL(3,1)'}
            )
            GROUP BY station
            ORDER BY station
        """).fetchall()
        
        return len(result)
    
    @task()
    def log_results(count: int):
        print(f"Processed {count} unique stations")
    
    # Define task dependencies
    log_results(process_data())


# Initialize the DAG
dag = process_duckdb_daily()
