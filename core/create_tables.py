import sqlite3

conn = sqlite3.connect('calendar_settings.sqlite')

#Create tables
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


#Delete tables

delete_settings = 'DROP TABLE settings'

delete_backup = 'DROP TABLE settings_backup'


conn.execute(save_backup)
