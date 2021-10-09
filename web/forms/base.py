# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/09 23:09 
"""
from django.forms import ModelForm


class BaseModelForm(ModelForm):
    exclude_bootstrap = []

    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)

        # 给字段添加样式
        for key, field in self.fields.items():
            if key not in self.exclude_bootstrap:
                field.widget.attrs['class'] = 'form-control'
