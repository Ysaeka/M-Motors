from django.db import migrations


def create_commercial_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Commercial")


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_commercial_group, migrations.RunPython.noop),
    ]