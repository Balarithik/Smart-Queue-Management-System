from django.db import migrations, models

import queues.models
import queues.validators


class Migration(migrations.Migration):

    dependencies = [
        ("queues", "0004_queueentry_timestamps_and_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="queue",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=queues.models.queue_image_upload_to,
                validators=[queues.validators.validate_queue_image],
            ),
        ),
        migrations.AddIndex(
            model_name="queue",
            index=models.Index(fields=["name"], name="queues_queue_name_idx"),
        ),
    ]
