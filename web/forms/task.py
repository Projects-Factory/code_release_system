# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/11 22:12 
"""
import datetime

from web import models
from .base import BaseModelForm


class TaskModelForm(BaseModelForm):
    class Meta:
        model = models.DeployTask
        exclude = ['uid', 'project', 'status']

    def __init__(self, project_obj, *args, **kwargs):
        self.project_obj = project_obj
        super(TaskModelForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # 手动给未填写的字段赋值
        self.instance.uid = self.create_uid()
        self.instance.project_id = self.project_obj.id

        super(TaskModelForm, self).save(*args, **kwargs)

    def create_uid(self):
        return f'{self.project_obj.title}-{self.project_obj.env}-' \
               f'{self.cleaned_data.get("tag")}-' \
               f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
