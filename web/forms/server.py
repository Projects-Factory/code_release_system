# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/09 23:06 
"""
from web import models
from .base import BaseModelForm


class ServerModelForm(BaseModelForm):
    class Meta:
        model = models.Server
        fields = '__all__'
