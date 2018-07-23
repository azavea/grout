# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.postgres.fields import JSONField


class JsonBModel(models.Model):
    data = JSONField()
