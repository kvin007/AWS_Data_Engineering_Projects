import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    '''Reads a song JSON file and inserts corresponding data to song and artist tables'''
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_columns = ['song_id', 'title', 'artist_id', 'year', 'duration']
    song_data = list(df[song_columns].values[0])
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_columns = ['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    artist_data = list(df[artist_columns].values[0])
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    '''Reads a log JSON file and inserts corresponding data to time, users and songplays tables'''
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')

    # insert time data records
    start_time = (pd.to_datetime(df['ts'], unit='ms')).tolist()
    hours = (t.dt.hour).tolist()
    days = (t.dt.day).tolist()
    weeks = (t.dt.week).tolist()
    months = (t.dt.month).tolist()
    years = (t.dt.year).tolist()
    weekdays = (t.dt.weekday).tolist()

    time_data = [start_time, hours, days, weeks, months, years, weekdays]
    column_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    input_dict = dict(zip(column_labels, time_data))
    time_df = pd.DataFrame(input_dict)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_columns = ['userId', 'firstName', 'lastName', 'gender', 'level']
    user_df = df[user_columns]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (
            pd.to_datetime(row.ts, unit='ms'), row.userId, row.level, songid, artistid, row.sessionId, row.location,
            row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    '''Processes data contained in a root directory applying a specific process'''
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    '''Connects to sparkifydb in PostgreSQL and processes data for songs and log files'''
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
