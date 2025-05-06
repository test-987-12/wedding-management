import os
import sys
import django
import shutil

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wms_project.settings')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

def reset_database():
    """Reset the database by removing the db.sqlite3 file and all migrations except __init__.py"""
    print("Resetting database...")

    # Remove the database file
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("  ✓ Removed db.sqlite3")

    # Remove migration files except __init__.py
    apps = ['core', 'guests', 'weddings', 'tasks', 'gallery']

    for app in apps:
        migrations_dir = os.path.join(app, 'migrations')
        if os.path.exists(migrations_dir):
            for filename in os.listdir(migrations_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migrations_dir, filename)
                    os.remove(file_path)
                    print(f"  ✓ Removed migration: {file_path}")

    # Remove __pycache__ directories in migrations folders
    for app in apps:
        pycache_dir = os.path.join(app, 'migrations', '__pycache__')
        if os.path.exists(pycache_dir):
            shutil.rmtree(pycache_dir)
            print(f"  ✓ Removed __pycache__: {pycache_dir}")

    print("Database reset complete.")

def run_migrations():
    """Run makemigrations and migrate commands"""
    print("Running migrations...")

    # Make migrations
    os.system('python manage.py makemigrations')

    # Apply migrations
    os.system('python manage.py migrate')

    print("Migrations complete.")

def seed_data():
    """Run the comprehensive seed script"""
    print("Seeding database...")

    # Run the new comprehensive seed script
    print("Running seed.py...")
    os.system('python seed.py')

    print("Database seeding complete.")

if __name__ == "__main__":
    # Confirm with the user
    confirm = input("This will delete the database and all migrations. Are you sure? (y/n): ")

    if confirm.lower() == 'y':
        reset_database()
        run_migrations()
        seed_data()
        print("Database has been reset and reseeded successfully.")
    else:
        print("Operation cancelled.")
