from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class DataQualityOperator(BaseOperator):
    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 target_database_conn_id="",
                 sql_test_cases=[],
                 *args, **kwargs):
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.target_database_conn_id = target_database_conn_id
        self.sql_test_cases = sql_test_cases

    def execute(self, context):
        if len(self.sql_test_cases) == 0:
            raise Exception("There should be at least 1 sql test case")

        database_conn = PostgresHook(postgres_conn_id=self.target_database_conn_id)

        for sql_test_case in self.sql_test_cases:
            self.log.info(f'Checking the following sql statement {sql_test_case.sql_statement}')
            self.log.info(f'The expected value should be {sql_test_case.expected_result}')
            records = database_conn.get_records(sql_test_case.sql_statement)
            if len(records) < 1 or len(records[0]) < 1:
                raise ValueError(f"Data quality check failed. No results were return")
            num_records = records[0][0]
            if num_records != sql_test_case.expected_result:
                raise ValueError(
                    f"Data quality check failed. Obtained {num_records} and was expecting {sql_test_case.expected_result}")
            self.log.info(f"Data quality check passed")
