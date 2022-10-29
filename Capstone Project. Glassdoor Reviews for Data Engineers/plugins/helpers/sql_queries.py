class SqlQueries:
    reviews_table_insert = ("""
        SELECT MD5(Z.start_time) AS review_id,
        start_time,
        company_name,
        TRIM(employee_role),
        number_positive_reviews,
        number_negative_reviews,
        number_total_reviews
        FROM (
            SELECT
                TO_DATE(r.date_review, 'YYYY-MM-DD') AS start_time, 
                TRIM(REPLACE(REPLACE(r.firm,'-s','\\'s'),'-',' ')) AS company_name,
                INITCAP(job_title) AS employee_role,
                SUM(CASE WHEN overall_rating >= 3 THEN 1 ELSE 0 END) AS number_positive_reviews,
                SUM(CASE WHEN overall_rating < 3 THEN 1 ELSE 0 END) AS number_negative_reviews,
                COUNT(overall_rating) AS number_total_reviews
            FROM staging_reviews r LEFT JOIN staging_companies c ON REPLACE(REPLACE(r.firm,'-s','\\'s'),'-',' ') = TRIM(c.name)
            WHERE UPPER(job_title) LIKE '%DATA ENGINEER%'
            GROUP BY TO_DATE(r.date_review, 'YYYY-MM-DD'),
            TRIM(REPLACE(REPLACE(r.firm,'-s','\\'s'),'-',' ')),
            INITCAP(r.job_title)
        ) Z
    """)

    companies_table_insert = ("""
        SELECT DISTINCT
            TRIM(REPLACE(REPLACE(r.firm,'-s','\\'s'),'-',' ')),
            c.country,
            c.sector,
            c.industry
        FROM staging_reviews r 
        LEFT JOIN staging_companies c ON TRIM(REPLACE(REPLACE(r.firm,'-s','\\'s'),'-',' ')) = TRIM(c.name)
    """)

    employee_roles_table_insert = ("""
        SELECT DISTINCT
            TRIM(job_title),
            current
        FROM staging_reviews
        where UPPER(job_title) LIKE '%DATA ENGINEER%'
    """)

    time_table_insert = ("""
        SELECT DISTINCT
            TO_DATE(date_review, 'YYYY-MM-DD') AS start_time,
            DATE_PART(day, TO_DATE(date_review, 'YYYY-MM-DD')) AS day,
            DATE_PART(week, TO_DATE(date_review, 'YYYY-MM-DD')) AS week,
            DATE_PART(month, TO_DATE(date_review, 'YYYY-MM-DD')) AS month,
            DATE_PART(year, TO_DATE(date_review, 'YYYY-MM-DD')) AS year,
            DATE_PART(weekday, TO_DATE(date_review, 'YYYY-MM-DD')) AS weekday
        FROM staging_reviews
    """)

    # Data quality checks

    check_null_reviews_review_id = """
        SELECT COUNT(*)
        FROM reviews
        WHERE review_id IS NULL
    """

    check_null_reviews_start_time = """
        SELECT COUNT(*)
        FROM reviews
        WHERE start_time IS NULL
    """

    check_null_reviews_company_name = """
        SELECT COUNT(*)
        FROM reviews
        WHERE company_name IS NULL
    """

    check_null_reviews_employee_role = """
        SELECT COUNT(*)
        FROM reviews
        WHERE employee_role IS NULL
    """

    check_null_reviews_number_positive_reviews = """
        SELECT COUNT(*)
        FROM reviews
        WHERE number_positive_reviews IS NULL
    """

    check_null_reviews_number_negative_reviews = """
        SELECT COUNT(*)
        FROM reviews
        WHERE number_negative_reviews IS NULL
    """
    
    check_equals_zero_reviews_number_total_reviews = """
        SELECT COUNT(*)
        FROM reviews
        WHERE number_total_reviews = 0
    """    

