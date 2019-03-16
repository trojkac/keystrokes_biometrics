import sqlite3 as sql
import numpy as np
import sys

table_name = 'data'
out_table = 'train_data_noorder'
db_name = 'keystrokes.db'
conn = sql.connect(db_name)
c = conn.cursor()
events_count_per_probe = 24
up_down_order = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
keys_order = [190, 84, 73, 69, 53, 16, 82, 79, 65, 78, 76, 13]

max_probes = 'SELECT user_id, MAX(probe_id) FROM data GROUP BY user_id;'
probe_query = 'SELECT * FROM data WHERE user_id = %d AND probe_id = %d;'


def clean_keystrokes(keystrokes):
    if len(keystrokes) != 24:
        skipped = 0
        new_keystrokes = []
        for key, i in zip(keystrokes, range(len(keystrokes))):
            if i == 0:
                new_keystrokes.append(key)
                continue

            if key[1] and new_keystrokes[i - 1 - skipped][1] and key[2] == new_keystrokes[i - 1 - skipped][2]:
                skipped += 1
                continue

            new_keystrokes.append(key)
        keystrokes = np.array(new_keystrokes)

    if len(keystrokes) != 24 or not proper_keys_pressed(keystrokes):
        return None

    return keystrokes


def get_feature_vector(keystrokes):
    feature_vector = np.zeros(24, dtype=np.int32)
    previous_key_up_time = -1
    for key_code, i in zip(keys_order, range(0, 24, 2)):
        flight = 0
        key_event = get_key_stroke(keystrokes, key_code)
        dwell = key_event[1, 3] - key_event[0, 3]
        if previous_key_up_time != -1:
            flight = key_event[0, 3] - previous_key_up_time
        # # condition is false only for shift but we would lose information about two possibilities
        # shift down-> r down -> r up -> shift up
        # shift down-> r down -> shift up -> r up
        # if previous_key_up_time < key_event[1, 3]:
        previous_key_up_time = key_event[1, 3]
        feature_vector[i] = flight
        feature_vector[i + 1] = dwell
    return feature_vector


def process_data(user_probes=None):
    if user_probes is None:
        # user_probes = [map(lambda e: (u_id[0], e), range(1, u_id[1]+1)) for u_id in c.execute(max_probes).fetchall()]
        # user_probes = [item for sublist in user_probes for item in sublist]
        user_probes = [(u_id[0], u_id[1]) for u_id in c.execute(max_probes).fetchall()]

    train_set = []
    fv_id = c.execute("SELECT MAX(id) FROM {0}".format(out_table)).fetchall()[0][0]
    if fv_id is None:
        fv_id = 0
    for user_id, max_probe in user_probes:
        all_keystrokes = np.array(c.execute(
            "SELECT * FROM data WHERE user_id = {0}".format(user_id)).fetchall())
        for probe_id in range(max_probe + 1):
            sys.stdout.write("\ruser: '{0}', probe: {1}".format(user_id, probe_id))
            sys.stdout.flush()
            fv_id += 1
            keystrokes = all_keystrokes[all_keystrokes[:, 5] == probe_id]
            keystrokes = np.array(keystrokes)
            keystrokes = clean_keystrokes(keystrokes)

            if keystrokes is None:
                continue
            feature = get_feature_vector(keystrokes)
            feature = np.append([user_id], feature)
            c.execute('INSERT INTO {0} VALUES ('
                      '?, ?,?,?,?,?,'
                      '?,?,?,?,?,'
                      '?,?,?,?,?,'
                      '?,?,?,?,?,'
                      '?,?,?,?,?)'.format(out_table), np.insert(feature, 0, fv_id))

            # train_set.append(feature)
    conn.commit()
    return train_set


def proper_order(keystrokes):
    key_downs = keystrokes[keystrokes[:, 1] == 1][:, 2]
    return len(key_downs) == len(keys_order) and all(key_downs == keys_order)


def proper_up_down_order(keystrokes):
    return all(keystrokes[:, 1] == up_down_order)


def proper_keys_pressed(keystrokes):
    return proper_order(keystrokes)


def get_key_stroke(keystrokes, key_code):
    return keystrokes[keystrokes[:, 2] == key_code]


def get_data(table, min_samples = 5):
    table_data = c.execute("SELECT * FROM {0} WHERE user_id IN (SELECT user_id FROM train_data_noorder GROUP BY user_id HAVING COUNT(1) >= {1})".format(table,min_samples)).fetchall()
    table_data = np.array(table_data)
    y_set = table_data[:, 1]
    x_set = table_data[:, 2:26]
    return (x_set, y_set)