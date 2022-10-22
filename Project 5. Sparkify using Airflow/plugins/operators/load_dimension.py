from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):
    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 target_database_conn_id="",
                 target_table="",
                 insert_statement="",
                 insert_mode="recreate",
                 *args, **kwargs):
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.target_database_conn_id = target_database_conn_id
        self.target_table = target_table
        self.insert_statement = insert_statement
        self.insert_mode = insert_mode

    def execute(self, context):
        database_conn = PostgresHook(postgres_conn_id=self.target_database_conn_id)

        self.log.info(f'The insert mode is {self.insert_mode}')

        if self.insert_mode == "truncate":
            database_conn.run(f"TRUNCATE TABLE {self.target_table}")
        
        insert_script = f"INSERT INTO {self.target_table} {self.insert_statement}"
        self.log.info(f"Appending the data into the Dimension table [{self.target_table}] using the following script {insert_script}")
        database_conn.run(insert_script)
