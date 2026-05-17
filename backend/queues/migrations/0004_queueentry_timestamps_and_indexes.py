from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("queues", "0003_alter_queue_public_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="queueentry",
            name="called_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="queueentry",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="queue",
            index=models.Index(
                fields=["organization", "created_at"],
                name="queues_queu_organiz_0a8f0d_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="queueentry",
            index=models.Index(
                fields=["queue", "status"],
                name="queues_queu_queue_i_8e2f1a_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="queueentry",
            index=models.Index(
                fields=["queue", "joined_at"],
                name="queues_queu_queue_i_9c3b2e_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="queueentry",
            index=models.Index(
                fields=["queue", "called_at"],
                name="queues_queu_queue_i_a1d4f3_idx",
            ),
        ),
    ]
