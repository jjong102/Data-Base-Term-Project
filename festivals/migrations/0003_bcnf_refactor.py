from django.db import migrations, models
import django.db.models.deletion


def migrate_festival_data(apps, schema_editor):
    Festival = apps.get_model("festivals", "Festival")
    Location = apps.get_model("festivals", "Location")
    Organization = apps.get_model("festivals", "Organization")
    FestivalOrganization = apps.get_model("festivals", "FestivalOrganization")

    for f in Festival.objects.all():
        # migrate location
        has_loc = any([f.place, f.address_road, f.address_lot, f.latitude is not None, f.longitude is not None])
        if has_loc:
            loc, _ = Location.objects.get_or_create(
                name=f.place or "",
                address_road=f.address_road or "",
                address_lot=f.address_lot or "",
                latitude=f.latitude,
                longitude=f.longitude,
            )
            f.location = loc
            f.save(update_fields=["location"])

        # migrate organizations by role
        for role, name in [
            ("organizer", f.organizer),
            ("host", f.host),
            ("sponsor", f.sponsor),
        ]:
            if not name:
                continue
            org, _ = Organization.objects.get_or_create(name=name)
            FestivalOrganization.objects.get_or_create(festival=f, organization=org, role=role)


class Migration(migrations.Migration):

    dependencies = [
        ("festivals", "0002_alter_festival_options_remove_festival_category_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=200)),
                ("address_road", models.CharField(blank=True, max_length=255)),
                ("address_lot", models.CharField(blank=True, max_length=255)),
                ("latitude", models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=12, max_digits=18, null=True)),
            ],
            options={"unique_together": {("name", "address_road", "address_lot", "latitude", "longitude")}},
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True)),
                ("telephone", models.CharField(blank=True, max_length=50)),
                ("homepage", models.URLField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="festival",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="festivals",
                to="festivals.location",
            ),
        ),
        migrations.CreateModel(
            name="FestivalOrganization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "role",
                    models.CharField(
                        choices=[("organizer", "Organizer"), ("host", "Host"), ("sponsor", "Sponsor")], max_length=20
                    ),
                ),
                (
                    "festival",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="organizations", to="festivals.festival"
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="festival_roles",
                        to="festivals.organization",
                    ),
                ),
            ],
            options={"unique_together": {("festival", "role")}},
        ),
        migrations.RunPython(migrate_festival_data, migrations.RunPython.noop),
        migrations.RemoveField(model_name="festival", name="address_lot"),
        migrations.RemoveField(model_name="festival", name="address_road"),
        migrations.RemoveField(model_name="festival", name="host"),
        migrations.RemoveField(model_name="festival", name="latitude"),
        migrations.RemoveField(model_name="festival", name="longitude"),
        migrations.RemoveField(model_name="festival", name="organizer"),
        migrations.RemoveField(model_name="festival", name="place"),
        migrations.RemoveField(model_name="festival", name="sponsor"),
    ]
