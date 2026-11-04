from django.core.management import call_command
from django.db import migrations


CACHE_TABLE = "django_cache"


def create_cache_table(apps, schema_editor):
    call_command(
        "createcachetable",
        CACHE_TABLE,
        database=schema_editor.connection.alias,
        verbosity=0,
    )


def drop_cache_table(apps, schema_editor):
    schema_editor.execute(
        f"DROP TABLE {schema_editor.quote_name(CACHE_TABLE)}"
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(create_cache_table, drop_cache_table),
    ]
