from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
#from dags.centaline_scraping import centaline_scraping_rent_data, centaline_scraping_transaction_data
from centaline_scraping import centaline_scraping_rent_data, centaline_scraping_transaction_data

default_args = {
    'owner': 'Ryanng',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG('centaline_scraping_dag', default_args=default_args, catchup=False, schedule_interval="@daily") as dag: 

    scraping = PythonOperator(
        task_id="centaline_scraping_rent_data",
        python_callable=centaline_scraping_rent_data
    )

    scraping2 = PythonOperator(
        task_id="centaline_scraping_transaction_data",
        python_callable=centaline_scraping_transaction_data
    )

scraping >> scraping2