import uuid
from django.db import models


class BlogEntry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()


class BlogEntryWithNonIntPk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    content = models.TextField()
