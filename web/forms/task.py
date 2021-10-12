# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/11 22:12 
"""
import datetime

from django import forms

from web import models
from .base import BaseModelForm


class TaskModelForm(BaseModelForm):
    deploy_servers = forms.MultipleChoiceField(label='选择主机', required=False)

    before_download_select = forms.ChoiceField(required=False, label='下载前')
    before_download_title = forms.CharField(required=False, label='模板名称')
    before_download_template = forms.BooleanField(
        required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_download_select = forms.ChoiceField(required=False, label='下载后')
    after_download_title = forms.CharField(required=False, label='模板名称')
    after_download_template = forms.BooleanField(
        required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    before_deploy_select = forms.ChoiceField(required=False, label='发布前')
    before_deploy_title = forms.CharField(required=False, label='模板名称')
    before_deploy_template = forms.BooleanField(
        required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_deploy_select = forms.ChoiceField(required=False, label='下载后')
    after_deploy_title = forms.CharField(required=False, label='模板名称')
    after_deploy_template = forms.BooleanField(
        required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    exclude_bootstrap = ['before_download_template', 'after_download_template',
                         'before_deploy_template', 'after_deploy_template']

    class Meta:
        model = models.DeployTask
        exclude = ['uid', 'project', 'status']

    def __init__(self, project_obj, *args, **kwargs):
        self.project_obj = project_obj
        super(TaskModelForm, self).__init__(*args, **kwargs)

        self.init_hook()

    def save(self, *args, **kwargs):
        # 手动给未填写的字段赋值
        self.instance.uid = self.create_uid()
        self.instance.project_id = self.project_obj.id

        super(TaskModelForm, self).save(*args, **kwargs)

        # 保存hook模板
        if self.cleaned_data.get('before_download_template'):
            title = self.cleaned_data['before_download_title']
            content = self.cleaned_data['before_download_script']
            models.HookTemplate.objects.create(title=title, content=content,
                                               hook_type=2)

        if self.cleaned_data.get('after_download_template'):
            title = self.cleaned_data['after_download_title']
            content = self.cleaned_data['after_download_script']
            models.HookTemplate.objects.create(title=title, content=content,
                                               hook_type=4)

        if self.cleaned_data.get('before_deploy_template'):
            title = self.cleaned_data['before_deploy_title']
            content = self.cleaned_data['before_deploy_script']
            models.HookTemplate.objects.create(title=title, content=content,
                                               hook_type=6)

        if self.cleaned_data.get('after_deploy_template'):
            title = self.cleaned_data['after_deploy_title']
            content = self.cleaned_data['after_deploy_script']
            models.HookTemplate.objects.create(title=title, content=content,
                                               hook_type=8)

    def create_uid(self):
        return f'{self.project_obj.title}-{self.project_obj.env}-' \
               f'{self.cleaned_data.get("tag")}-' \
               f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'

    def init_hook(self):
        before_download = [(0, '请选择')]
        before_download.extend(models.HookTemplate.objects.filter(
            hook_type=2).values_list('id', 'title'))
        self.fields['before_download_select'].choices = before_download

        after_download = [(0, '请选择')]
        after_download.extend(models.HookTemplate.objects.filter(
            hook_type=4).values_list('id', 'title'))
        self.fields['after_download_select'].choices = after_download

        before_deploy = [(0, '请选择')]
        before_deploy.extend(models.HookTemplate.objects.filter(
            hook_type=6).values_list('id', 'title'))
        self.fields['before_deploy_select'].choices = before_deploy

        after_deploy = [(0, '请选择')]
        after_deploy.extend(models.HookTemplate.objects.filter(
            hook_type=8).values_list('id', 'title'))
        self.fields['after_deploy_select'].choices = after_deploy

    def clean(self):
        if self.cleaned_data.get('before_download_template'):
            title = self.cleaned_data['before_download_title']
            if not title:
                self.add_error('before_download_title', '请输入模板名称')

        if self.cleaned_data.get('after_download_template'):
            title = self.cleaned_data['after_download_title']
            if not title:
                self.add_error('after_download_title', '请输入模板名称')

        if self.cleaned_data.get('before_deploy_template'):
            title = self.cleaned_data['before_deploy_title']
            if not title:
                self.add_error('before_deploy_title', '请输入模板名称')

        if self.cleaned_data.get('after_deploy_template'):
            title = self.cleaned_data['after_deploy_title']
            if not title:
                self.add_error('after_deploy_title', '请输入模板名称')
