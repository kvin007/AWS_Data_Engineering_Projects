from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):
    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 target_database_conn_id="",
                 target_table="",
                 create_statement="",
                 insert_statement="",
                 insert_mode="truncate",
                 *args, **kwargs):
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.target_database_conn_id = target_database_conn_id
        self.target_table = target_table
        self.create_statement = create_statement
        self.insert_statement = insert_statement
        self.insert_mode = insert_mode

    def execute(self, context):
        database_conn = PostgresHook(postgres_conn_id=self.target_database_conn_id)

        self.log.info('Creating the table if not exists with statement')
        database_conn.run(self.create_statement)

        self.log.info(f'The insert mode is {self.insert_mode}')
        if self.insert_mode == "truncate":
            database_conn.run(f"TRUNCATE TABLE {self.target_table}")

        self.log.info(f'Appending the data into the Fact {self.target_table}')
        database_conn.run(self.insert_statement)
