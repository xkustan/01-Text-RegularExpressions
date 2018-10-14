import sqlite3


conn = sqlite3.connect('scorelib.sql')
c = conn.cursor()
# Create table
c.execute("SELECT 1;")
c.commit()

