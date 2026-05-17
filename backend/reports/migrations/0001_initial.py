import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organizations", "0001_initial"),
        ("queues", "0004_queueentry_timestamps_and_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyQueueMetric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("joins", models.PositiveIntegerField(default=0)),
                ("called", models.PositiveIntegerField(default=0)),
                ("completed", models.PositiveIntegerField(default=0)),
                ("peak_waiting", models.PositiveIntegerField(default=0)),
                (
                    "queue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_metrics",
                        to="queues.queue",
                    ),
                ),
            ],
            options={
                "ordering": ("-date",),
            },
        ),
        migrations.CreateModel(
            name="DailyOrganizationMetric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("total_joins", models.PositiveIntegerField(default=0)),
                ("total_completed", models.PositiveIntegerField(default=0)),
                ("active_queues", models.PositiveIntegerField(default=0)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_metrics",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "ordering": ("-date",),
            },
        ),
        migrations.AddConstraint(
            model_name="dailyqueuemetric",
            constraint=models.UniqueConstraint(
                fields=("queue", "date"),
                name="reports_dailyqueuemetric_queue_date_uniq",
            ),
        ),
        migrations.AddIndex(
            model_name="dailyqueuemetric",
            index=models.Index(fields=["queue", "date"], name="reports_dai_queue_i_7a1b2c_idx"),
        ),
        migrations.AddIndex(
            model_name="dailyqueuemetric",
            index=models.Index(fields=["date"], name="reports_dai_date_8d3e4f_idx"),
        ),
        migrations.AddConstraint(
            model_name="dailyorganizationmetric",
            constraint=models.UniqueConstraint(
                fields=("organization", "date"),
                name="reports_dailyorgmetric_org_date_uniq",
            ),
        ),
        migrations.AddIndex(
            model_name="dailyorganizationmetric",
            index=models.Index(
                fields=["organization", "date"],
                name="reports_dai_organiz_9e5f6a_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="dailyorganizationmetric",
            index=models.Index(fields=["date"], name="reports_dai_date_0b7c8d_idx"),
        ),
    ]
