"""Replace the migration history of the project's apps with the versioned files.

One-off, for the Django 5.2 upgrade: the production database recorded
migrations whose files were lost, while its schema matches the models. This
records the fresh initial migrations as applied, without touching any table
but django_migrations. `migrate --fake` cannot do it: it refuses a history
where admin.0001 was applied before users.0001.

    env/bin/python manage.py shell < deploy/reset-migration-history.py
"""
from django.db import connection, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder

APPS = ["activities", "agenda", "blog", "budget", "info", "users", "work"]

loader = MigrationLoader(connection, ignore_no_migrations=True)
recorder = MigrationRecorder(connection)
with transaction.atomic():
    deleted, _ = recorder.migration_qs.filter(app__in=APPS).delete()
    names = sorted(key for key in loader.disk_migrations if key[0] in APPS)
    for app, name in names:
        recorder.record_applied(app, name)
print(f"removed {deleted} old rows, recorded {len(names)}: {names}")

loader = MigrationLoader(connection)
loader.check_consistent_history(connection)
print("history consistent")
