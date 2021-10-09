# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/09 23:05 
"""
from web import models
from .base import BaseModelForm


class ProjectModelForm(BaseModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'
