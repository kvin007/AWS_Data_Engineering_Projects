class SqlQueries:
    staging_events_table_create = """
        CREATE TABLE IF NOT EXISTS public.staging_events (
            artist varchar(256),
            auth varchar(256),
            firstname varchar(256),
            gender varchar(256),
            iteminsession int4,
            lastname varchar(256),
            length numeric(18,0),
            "level" varchar(256),
            location varchar(256),
            "method" varchar(256),
            page varchar(256),
            registration numeric(18,0),
            sessionid int4,
            song varchar(256),
            status int4,
            ts int8,
            useragent varchar(256),
            userid int4
        );
    """

    staging_songs_table_create = """
        CREATE TABLE IF NOT EXISTS public.staging_songs (
            num_songs int4,
            artist_id varchar(256),
            artist_name varchar(256),
            artist_latitude numeric(18,0),
            artist_longitude numeric(18,0),
            artist_location varchar(256),
            song_id varchar(256),
            title varchar(256),
            duration numeric(18,0),
            "year" int4
        );
    """

    songplays_table_create = """
        CREATE TABLE IF NOT EXISTS public.songplays (
            songplay_id int identity(0,1) primary key,
            start_time timestamp not null,
            user_id bigint not null,
            level varchar(25),
            song_id varchar(18),
            artist_id varchar(18),
            session_id bigint,
            location varchar(max),
            user_agent varchar(max)
        );
    """

    user_table_create = """
        CREATE TABLE IF NOT EXISTS public.users (
            user_id bigint primary key,
            first_name varchar(100),
            last_name varchar(100),
            gender char(2),
            level varchar(25)
        );
    """

    song_table_create = """
        CREATE TABLE IF NOT EXISTS public.songs (
            song_id varchar(18) primary key,
            title varchar(max) not null,
            artist_id varchar(18),
            year int,
            duration float not null
        );
    """

    artist_table_create = """
        CREATE TABLE IF NOT EXISTS public.artists (
            artist_id varchar(18) primary key,
            name varchar(max) not null,
            location varchar(max),
            latitude float,
            longitude float
        );
    """

    time_table_create_statement = """
        CREATE TABLE IF NOT EXISTS public.time (
            start_time timestamp primary key,
            hour int,
            day int,
            week int,
            month int,
            year int,
            weekday int
        );
    """

    # Insert statements

    songplays_table_insert = """
        INSERT INTO songplays (songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)    
        SELECT
                md5(events.sessionid || events.start_time) songplay_id,
                events.start_time, 
                events.userid, 
                events.level, 
                songs.song_id, 
                songs.artist_id, 
                events.sessionid, 
                events.location, 
                events.useragent
                FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
            FROM staging_events
            WHERE page='NextSong') events
            LEFT JOIN staging_songs songs
            ON events.song = songs.title
                AND events.artist = songs.artist_name
                AND events.length = songs.duration
    """

    user_table_insert = """
        INSERT INTO users (user_id, first_name, last_name, gender, level)    
        SELECT distinct userid, firstname, lastname, gender, level
        FROM staging_events
        WHERE page='NextSong'
    """

    song_table_insert = """
        INSERT INTO songs (song_id, title, artist_id, year, duration)    
        SELECT distinct song_id, title, artist_id, year, duration
        FROM staging_songs
    """

    artist_table_insert = """
        INSERT INTO artists (artist_id, name, location, latitude, longitude)    
        SELECT distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
        FROM staging_songs
    """

    time_table_insert = """
        INSERT INTO time (start_time, hour, day, week, month, year, weekday)
        SELECT start_time, extract(hour from start_time), extract(day from start_time), extract(week from start_time), 
               extract(month from start_time), extract(year from start_time), extract(dayofweek from start_time)
        FROM songplays
    """

    # Data quality checks

    check_null_songplays_start_time = """
        SELECT COUNT(*)
        FROM songplays
        WHERE start_time IS NULL
    """

    check_null_songplays_user_id = """
        SELECT COUNT(*)
        FROM songplays
        WHERE user_id IS NULL
    """

    check_null_song_title = """
        SELECT COUNT(*)
        FROM songs
        WHERE title IS NULL
    """

    check_null_song_duration = """
        SELECT COUNT(*)
        FROM songs
        WHERE duration IS NULL
    """

    check_null_artist_name = """
        SELECT COUNT(*)
        FROM artists
        WHERE artist IS NULL
    """
