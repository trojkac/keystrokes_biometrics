import sqlite3 as sql
import numpy as np

table_name = 'tx_badanie01'
db_name = 'keystrokes.db'
conn = sql.connect(db_name)
c = conn.cursor()

distinct_query = 'SELECT COUNT(DISTINCT user_id) FROM %s' % table_name
keystrokes_query = "SELECT input0 FROM tx_badanie01 WHERE user_id"
add_keystrokes = 'INSERT INTO data VALUES (?,?,?,?,?,?)'

distinct_users = c.execute(distinct_query).fetchone()[0]
user_ids = [u_id[0] for u_id in c.execute('SELECT user_id FROM %s GROUP BY user_id' % table_name).fetchall()]

for user_id in user_ids:
    iterator = c.execute(keystrokes_query + '=%d' % user_id)
    keystrokes = []
    probe_id = 0
    for key_stroke in iterator:
        strokes = key_stroke[0].split(' ')
        position = -1
        probe_id += 1
        for stroke in strokes:
            stroke = stroke.split('_')
            if len(stroke) < 3:
                continue
            is_down = stroke[0] == 'd'
            position = int(stroke[3]) if is_down else position
            keystrokes.append((user_id, is_down, int(stroke[1]), int(stroke[2]), position, probe_id))
    c.executemany('INSERT INTO data VALUES (?,?,?,?,?,?)', keystrokes)


conn.commit()
