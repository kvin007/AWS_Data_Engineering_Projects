from airflow.hooks.postgres_hook import PostgresHook
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    # The json path could also be templated in case the data changes schema in long periods of time
    template_fields = ("s3_key",
                       "s3_key_json_path",)
    copy_sql = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        JSON '{}'
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id='redshift',
                 aws_credentials_id="aws_credentials",
                 target_table="",
                 create_statement="",
                 s3_bucket="",
                 s3_key="",
                 s3_key_json_path=None,
                 *args, **kwargs):
        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.target_table = target_table
        self.create_statement = create_statement
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.s3_key_json_path = s3_key_json_path

    def execute(self, context):
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info(f"Dropping table {self.target_table} in case exists")
        redshift.run(f"DROP TABLE IF EXISTS {self.target_table}")

        self.log.info("Creating the table with statement")
        redshift.run(self.create_statement)

        self.log.info("Copying data from S3 to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = f"s3://{self.s3_bucket}/{rendered_key}"
        json_path = f"s3://{self.s3_bucket}/{self.s3_key_json_path.format(**context)}" if self.s3_key_json_path is not None else "auto"

        formatted_sql = StageToRedshiftOperator.copy_sql.format(
            self.target_table,
            s3_path,
            credentials.access_key,
            credentials.secret_key,
            json_path
        )

        redshift.run(formatted_sql)
