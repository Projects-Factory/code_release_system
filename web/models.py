from django.db import models


class Server(models.Model):
    hostname = models.CharField(max_length=32, verbose_name='主机名')
