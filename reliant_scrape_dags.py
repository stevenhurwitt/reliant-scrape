import sys
import logging
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator

log = logging.getLogger("airflow.task.operators")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
log.addHandler(handler)

args = {
    'owner': 'steven',
    'start_date': datetime(2020, 10, 21),
    'depends_on_past': True,
}

dag = DAG(
    dag_id = 'reliant-scrape',
    schedule_interval = '0 3 * * *',
    default_args = args,
)

anaconda_dag = BashOperator(
    task_id = 'anaconda',
    bash_command = 'conda activate reliant',
    dag = dag
)

reliant_scrape_dag = BashOperator(
    task_id='reliant_scrape',
    bash_command = 'python /media/steven/big_boi/reliant-scrape/reliant_scrape.py',
    dag = dag
)

anaconda_dag >> reliant_scrape_dag
