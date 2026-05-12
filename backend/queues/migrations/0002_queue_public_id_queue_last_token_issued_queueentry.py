import uuid

import django.db.models.deletion
from django.db import migrations, models


def assign_public_ids(apps, schema_editor):
    Queue = apps.get_model("queues", "Queue")
    for queue in Queue.objects.all():
        queue.public_id = uuid.uuid4()
        queue.save(update_fields=["public_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("queues", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="queue",
            name="last_token_issued",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="queue",
            name="public_id",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.RunPython(assign_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="queue",
            name="public_id",
            field=models.UUIDField(db_index=True, editable=False, unique=True),
        ),
        migrations.CreateModel(
            name="QueueEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("WAITING", "Waiting"),
                            ("CALLED", "Called"),
                            ("COMPLETED", "Completed"),
                        ],
                        db_index=True,
                        default="WAITING",
                        max_length=16,
                    ),
                ),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "queue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entries",
                        to="queues.queue",
                    ),
                ),
            ],
            options={
                "ordering": ("token",),
            },
        ),
        migrations.AddConstraint(
            model_name="queueentry",
            constraint=models.UniqueConstraint(fields=("queue", "token"), name="queues_queueentry_queue_token_uniq"),
        ),
    ]
