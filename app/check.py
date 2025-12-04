import os
import sys

print("=== SYSTEM CHECK ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print()

# Run this in Python to find your files
import os
import subprocess
import sys

print("=== FIXING ALL ISSUES ===")

# 1. Check current directory
print(f"\n1. Current directory: {os.getcwd()}")

# 2. Create templates folder if missing
if not os.path.exists('templates'):
    print("2. Creating templates folder...")
    os.makedirs('templates', exist_ok=True)
    
# 3. Create shows.html if missing
if not os.path.exists('templates/shows.html'):
    print("3. Creating shows.html...")
    with open('templates/shows.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>TV Shows</title>
</head>
<body>
    <h1>TV Shows</h1>
    <ul>
    {% for show in shows %}
        <li>{{ show.title }}</li>
    {% endfor %}
    </ul>
</body>
</html>''')

# 4. Check for necessary files
print("\n4. Checking for required files:")
required_files = ['app.py', 'server.py', 'db.py', 'tv_shows.csv', 'newdb.py']
all_exist = True
for file in required_files:
    exists = os.path.exists(file)
    print(f"   {'✓' if exists else '✗'} {file}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n✗ Missing files! Please run this script from the directory containing all project files.")
    sys.exit(1)

# 5. Recreate database
print("\n5. Recreating database...")
try:
    subprocess.run([sys.executable, "newdb.py"], check=True)
    print("   ✓ Database created successfully")
except Exception as e:
    print(f"   ✗ Error creating database: {e}")

# 6. Test database
print("\n6. Testing database...")
try:
    import sqlite3
    conn = sqlite3.connect('tv_shows.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM show")
    count = cursor.fetchone()[0]
    print(f"   ✓ Database has {count} shows")
    conn.close()
except Exception as e:
    print(f"   ✗ Database error: {e}")

# 7. Start server
print("\n" + "="*50)
print("READY TO GO!")
print("Now run: python server.py")
print("Then visit: http://localhost:9000/shows/")
print("="*50)