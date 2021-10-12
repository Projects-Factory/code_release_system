# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/11 21:55 
"""
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse

from web import models
from web.forms.task import TaskModelForm


def task_list(request, project_id):
    project_obj = models.Project.objects.filter(pk=project_id).first()
    tasks_list = models.DeployTask.objects.filter(project_id=project_id).all()
    print(tasks_list)
    return render(request, 'task_list.html',
                  {'task_list': tasks_list, 'project_obj': project_obj})


def task_add(request, project_id):
    project_obj = models.Project.objects.filter(pk=project_id).first()

    if request.method == 'GET':
        form = TaskModelForm(project_obj)
        return render(request, 'task_form.html',
                      {'form': form, 'project_obj': project_obj})

    form = TaskModelForm(project_obj, request.POST)
    if form.is_valid():
        form.save()

        url = reverse('task_list', kwargs={'project_id': project_id})
        return redirect(url)

    return render(request, 'task_form.html',
                  {'form': form, 'project_obj': project_obj})


def hook_template(request, tid):
    template = models.HookTemplate.objects.filter(id=tid).first()
    return JsonResponse({'status': True, 'content': template.content})


def deploy(request, task_id):
    task_obj = models.DeployTask.objects.filter(id=task_id).first()
    return render(request, 'deploy.html',
                  {'project_obj': task_obj.project, 'task_obj': task_obj})
