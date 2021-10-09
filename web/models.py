from django.db import models


class Server(models.Model):
    hostname = models.CharField(max_length=32, verbose_name='主机名')

    def __str__(self):
        return self.hostname


class Project(models.Model):
    title = models.CharField(max_length=32, verbose_name='项目名')
    repo = models.CharField(max_length=255, verbose_name='仓库名')

    env_choices = (('prod', '正式'), ('test', '测试'))
    env = models.CharField(max_length=16, verbose_name='环境',
                           choices=env_choices, default='test')

    path = models.CharField(max_length=255, verbose_name='线上项目地址')
    servers = models.ManyToManyField(verbose_name='关联服务器', to='Server')
