
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helper.tools import sqlite_execute_sql


# sql_query = """
# CREATE TABLE IF NOT EXISTS my_table (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     age INTEGER
# );
# """
# sqlite_execute_sql(sql_query)

# insert_query = """
# INSERT INTO my_table (name, age) VALUES
# ('Alice', 30),
# ('Bob', 25),
# ('Charlie', 35);
# """
# sqlite_execute_sql(insert_query)

select_query = "SELECT * FROM news;"
rows = sqlite_execute_sql(select_query)
print(rows)