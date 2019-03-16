import sqlite3 as sql
import matplotlib.pyplot as plt
import sys
import numpy as np

db_name = 'keystrokes.db'
conn = sql.connect(db_name)
c = conn.cursor()

counters_query = 'SELECT tx.user_id, COUNT(tx.user_id) as original_samples, IFNULL(td.cnt,0) as train_data_ordered, IFNULL(td2.cnt_td2, 0) as train_data_unordered FROM tx_badanie01  tx LEFT JOIN (SELECT user_id, COUNT(1) as cnt FROM train_data GROUP BY user_id ) td ON tx.user_id = td.user_id LEFT JOIN (SELECT user_id, COUNT(1) as cnt_td2 FROM train_data_noorder GROUP BY user_id ) td2 ON td.user_id = td2.user_id GROUP BY tx.user_id ORDER BY tx.user_id'

counters = c.execute(counters_query).fetchall()
counters = np.array(counters, dtype=np.int32)
fig = plt.figure()
bins = np.linspace(0, 400, 401)

x = plt.hist(counters[:, 1], bins, alpha=0.5, label='original')
y = plt.hist(counters[:, 2], bins, alpha=0.5, label='td1')
z = plt.hist(counters[:, 3], bins, alpha=0.5, label='td2')
plt.legend()

fig.show()
fig.savefig('hist.png')

fig = plt.figure()
bins = np.linspace(0, 400, 401)

n, bins, patches = plt.hist(counters[:, 1:4], label=['orginal','td1','td2'])

plt.legend()

fig.show()
fig.savefig('hist2.png')
