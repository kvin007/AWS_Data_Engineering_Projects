from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator, LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries
from collections import namedtuple

DataQualityTuple = namedtuple('DataQualityTuple', ['sql_statement', 'expected_result'])

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')


default_args = {
    'owner': 'Kevin Pereda',
    'catchup_by_default': False,
    'start_date': datetime(2022, 10, 27),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False,
}

dag = DAG('data_eng_reviews_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          catchup = False,
          )

start_operator = DummyOperator(task_id='Begin_execution', dag=dag)

stage_reviews_to_redshift = StageToRedshiftOperator(
    task_id='Stage_reviews',
    dag=dag,
    aws_connection_id="aws_credentials",
    redshift_conn_id="redshift",
    target_table="staging_reviews",
    s3_bucket="data-eng-reviews-3",
    s3_bucket_region = "us-west-2",
    s3_key="reviews_data",
    #s3_key_json_path="log_json_path.json"
)

stage_companies_to_redshift = StageToRedshiftOperator(
    task_id='Stage_companies',
    dag=dag,
    aws_connection_id="aws_credentials",
    redshift_conn_id="redshift",
    target_table="staging_companies",
    s3_bucket="data-eng-reviews-3",
    s3_bucket_region = "us-west-2",
    s3_key="companies_data"
)


load_reviews_table = LoadFactOperator(
    task_id='Load_reviews_fact_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="reviews",
    insert_statement = SqlQueries.reviews_table_insert,
)

load_companies_dimension_table = LoadDimensionOperator(
    task_id='Load_companies_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="companies",
    insert_statement=SqlQueries.companies_table_insert,
    insert_mode="truncate"
)

load_employee_roles_dimension_table = LoadDimensionOperator(
    task_id='Load_employee_roles_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="employee_roles",
    insert_statement=SqlQueries.employee_roles_table_insert,
    insert_mode="truncate"
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="time",
    insert_statement=SqlQueries.time_table_insert,
    insert_mode="truncate"
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    target_database_conn_id="redshift",
    sql_test_cases=[
        DataQualityTuple(sql_statement=SqlQueries.check_null_reviews_review_id, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_reviews_start_time, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_reviews_company_name, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_reviews_employee_role, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_reviews_number_positive_reviews, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_reviews_number_negative_reviews, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_equals_zero_reviews_number_total_reviews, expected_result=0),
    ],
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)


start_operator >> stage_reviews_to_redshift
start_operator >> stage_companies_to_redshift

stage_reviews_to_redshift >> load_reviews_table
stage_companies_to_redshift >> load_reviews_table

load_reviews_table >>  [load_companies_dimension_table, load_employee_roles_dimension_table, load_time_dimension_table] >> run_quality_checks >> end_operator

