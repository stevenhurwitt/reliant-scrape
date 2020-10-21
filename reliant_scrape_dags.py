from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator

args = {
    'owner': 'steven',
    'start_date': datetime(2020, 10, 20),
    'depends_on_past': True,
}

dag = DAG(
    dag_id = 'reliant-scrape',
    schedule_interval = '0 22 * * *',
    default_args = args,
)

anaconda_dag = BashOperator(
    task_id = 'anaconda',
    bash_command = 'conda activate reliant-37',
    dag = dag
)

reliant_scrape_dag = BashOperator(
    task_id='reliant_scrape',
    bash_command = '~/miniconda3/envs/reliant-37/bin/python ~/reliant-scrape/reliant_scrape.py',
    dag = dag
)

anaconda_dag >> reliant_scrape_dag