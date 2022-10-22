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
    'owner': 'udacity',
    'catchup_by_default': False,
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False,
}

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          catchup = False,
          )

start_operator = DummyOperator(task_id='Begin_execution', dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    aws_connection_id="aws_credentials",
    redshift_conn_id="redshift",
    target_table="staging_events",
    create_statement=SqlQueries.staging_events_table_create,
    s3_bucket="udacity-dend",
    s3_bucket_region = 'us-west-2',
    s3_key="log_data",
    s3_key_json_path="log_json_path.json"
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    aws_connection_id="aws_credentials",
    redshift_conn_id="redshift",
    target_table="staging_songs",
    create_statement=SqlQueries.staging_songs_table_create,
    s3_bucket="udacity-dend",
    s3_bucket_region = 'us-west-2',
    s3_key="song_data"
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="songplays",
    create_statement = SqlQueries.songplays_table_create,
    insert_statement = SqlQueries.songplays_table_insert,
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="users",
    create_statement=SqlQueries.user_table_create,
    insert_statement=SqlQueries.user_table_insert,
    insert_mode="recreate"
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="songs",
    create_statement=SqlQueries.song_table_create,
    insert_statement=SqlQueries.song_table_insert,
    insert_mode="recreate"
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="artists",
    create_statement=SqlQueries.artist_table_create,
    insert_statement=SqlQueries.artist_table_insert,
    insert_mode="recreate"
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    target_database_conn_id="redshift",
    target_table="time",
    create_statement=SqlQueries.time_table_create,
    insert_statement=SqlQueries.time_table_insert,
    insert_mode="recreate"
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    target_database_conn_id="redshift",
    sql_test_cases=[
        DataQualityTuple(sql_statement=SqlQueries.check_null_songplays_start_time, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_songplays_user_id, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_song_title, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_song_duration, expected_result=0),
        DataQualityTuple(sql_statement=SqlQueries.check_null_artist_name, expected_result=0),
    ],
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift

stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table

load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks

run_quality_checks >> end_operator
