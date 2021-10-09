# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/09 21:08 
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse

from web import models
from web.forms.project import ProjectModelForm


def project_list(request):
    queryset = models.Project.objects.all()
    return render(request, 'project_list.html', {'queryset': queryset})


def project_add(request):
    if request.method == 'GET':
        form = ProjectModelForm()
        return render(request, 'form.html', {'form': form})

    form = ProjectModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('project_list')
    else:
        return render(request, 'form.html', {'form': form})


def project_edit(request, pk):
    project_object = models.Project.objects.filter(id=pk).first()
    if request.method == 'GET':
        # 将project_object当作默认值
        form = ProjectModelForm(instance=project_object)
        return render(request, 'form.html', {'form': form})

    form = ProjectModelForm(data=request.POST, instance=project_object)
    if form.is_valid():
        form.save()
        return redirect('project_list')
    else:
        return render(request, 'form.html', {'form': form})


def project_del(request, pk):
    models.Project.objects.filter(id=pk).delete()
    return JsonResponse({'status': True})
