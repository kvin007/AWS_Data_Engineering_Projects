from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadFactOperator(BaseOperator):
    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 target_database_conn_id="",
                 target_table="",
                 create_statement="",
                 insert_statement="",
                 *args, **kwargs):
        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.target_database_conn_id = target_database_conn_id
        self.target_table = target_table
        self.create_statement = create_statement
        self.insert_statement = insert_statement

    def execute(self, context):
        database_conn = PostgresHook(postgres_conn_id=self.target_database_conn_id)

        self.log.info('Creating the table if not exists with statement')
        database_conn.run(self.create_statement)

        self.log.info(f'Appending the data into the Fact {self.target_table}')
        database_conn.run(self.insert_statement)
