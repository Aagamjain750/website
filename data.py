import sqlite3

# Database connect
conn = sqlite3.connect("project_portal.db")
cursor = conn.cursor()

# Fetch only those users who submitted a project
cursor.execute("""
    SELECT username, project_description, phone_number, email, language 
    FROM project_contacts
""")
submitted_projects = cursor.fetchall()

# Print results
for project in submitted_projects:
    print(project)

# Close connection
conn.close()
