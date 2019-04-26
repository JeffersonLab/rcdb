#!/usr/bin/python
import MySQLdb

db = MySQLdb.connect(user="rcdb", host="clasdb.jlab.org", db="rcdb")

# Create a Cursor object to execute queries.
cur = db.cursor()

# Select data from table using SQL query.
cur.execute("""
SELECT left_cnd.run_number,
       left_cnd.id as left_id,
       right_cnd.id as right_id,       
       left_cnd.condition_type_id,
       condition_types.name as cnd_name
FROM conditions left_cnd
LEFT JOIN conditions right_cnd ON
    left_cnd.run_number = right_cnd.run_number AND
    left_cnd.condition_type_id = right_cnd.condition_type_id
LEFT JOIN rcdb.condition_types ON
    condition_types.id = left_cnd.condition_type_id
WHERE left_cnd.id < right_cnd.id
""")

delete_ids = []     # conditions db id-s which are to be deleted

# print the results
print("{:<7} {:<12} {:<12} {:<10}".format('run', '1st-cnd-id', '2nd-cnd-id', 'name'))
for row in cur.fetchall():
    print("{:<7} {:<12} {:<12} {:<10}".format(row[0], row[1], row[2], row[4]))

    # and collect id for deletion
    delete_ids.append(row[1])

# comma separated ids to delete
delete_ids_csv = ",".join([str(id) for id in delete_ids])

# delete query
delete_query = "DELETE FROM `conditions` WHERE `id` IN ({});".format(delete_ids_csv)

print("DELETE query (!) Don't forget to back up first (!): \n")
print(delete_query)