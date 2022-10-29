
DROP TABLE IF EXISTS public.staging_reviews;
DROP TABLE IF EXISTS public.staging_companies;
DROP TABLE IF EXISTS public.reviews;
DROP TABLE IF EXISTS public.companies;
DROP TABLE IF EXISTS public.employee_roles;
DROP TABLE IF EXISTS public.time;

CREATE TABLE public.staging_reviews (
	index int,
	column_label varchar(10),
	firm varchar(256),
	date_review varchar(10),
	job_title varchar(256),
	current varchar(256),
	location varchar(256),
	overall_rating int,
	work_life_balance varchar,
	culture_values varchar,
	diversity_inclusion int,
	career_opp int,
	comp_benefits int,
	senior_mgmt int,
	recommend char(1),
	ceo_approv char(1),
	outlook char(1),
	headline varchar(max),
	pros varchar(max),
	cons varchar(max),
	use varchar(10)
);

CREATE TABLE public.staging_companies (
	name varchar(256),
	country varchar(25),
	sector varchar(50),
	industry varchar(50)
);

CREATE TABLE public.reviews (
	review_id varchar(32) not null,
	start_time date not null,
	company_name varchar(100) not null,
	employee_role varchar(50) not null,
	number_positive_reviews int not null,
	number_negative_reviews int not null,
	number_total_reviews int not null
);

CREATE TABLE public.companies (
	name varchar(100) primary key,
	country varchar(25) null,
	sector varchar(50) null,
	industry varchar(50) null
);

CREATE TABLE public.employee_roles (
	name varchar(50) primary key,
	status varchar(100)
);

CREATE TABLE public.time (
    start_time date primary key,
    day int,
    week int,
    month int,
    year int,
    weekday int
);
