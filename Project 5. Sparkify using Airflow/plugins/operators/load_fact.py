from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadFactOperator(BaseOperator):
    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 target_database_conn_id="",
                 target_table="",
                 insert_statement="",
                 *args, **kwargs):
        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.target_database_conn_id = target_database_conn_id
        self.target_table = target_table
        self.insert_statement = insert_statement

    def execute(self, context):
        database_conn = PostgresHook(postgres_conn_id=self.target_database_conn_id)

        insert_script = f"INSERT INTO {self.target_table} {self.insert_statement}"
        self.log.info(f"Appending the data into the Fact table [{self.target_table}] using the following script {insert_script}")
        database_conn.run(insert_script)