"""Auxiliary module for creating tables for the project.
_______________________________________________________
settings - table - for storing users settings;
settings_backup - table - for storing backups just in case
save_backup - trigger - for saving previous settings before their updates
"""

import sqlite3

conn = sqlite3.connect('calendar_settings.sqlite')

#Functions for create tables and trigger
create_settings = '''CREATE TABLE IF NOT EXISTS settings (
        user_id TEXT PRIMARY KEY,
        credentials BLOB,
        time_zone TEXT,
        calendar_id TEXT)'''

create_backup = '''CREATE TABLE IF NOT EXISTS settings_backup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        credentials BLOB,
        time_zone TEXT,
        calendar_id TEXT,
        change_date DATE)'''

save_backup = '''CREATE TRIGGER IF NOT EXISTS save_backup
        BEFORE UPDATE 
        ON settings
        
        BEGIN
            INSERT INTO settings_backup (user_id, credentials, time_zone, calendar_id, change_date)
            VALUES (old.user_id, old.credentials, old.time_zone, old.calendar_id, DATETIME('NOW')) ;
        END;
'''


#Functions for delete tables and trigger

delete_settings = 'DROP TABLE IF EXISTS settings'
delete_backup = 'DROP TABLE IF EXISTS settings_backup'
delete_save_backup = 'DROP TRIGGER IF EXISTS save_backup'

#Uncomment these functions to create tables and trigger
#conn.execute(create_settings)
#conn.execute(create_backup)
#conn.execute(save_backup)

# Uncomment this to delete all
#conn.execute(delete_settings)
#conn.execute(delete_backup)
#conn.execute(delete_save_backup)
