# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/09 21:08 
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.forms import ModelForm

from web import models


def server_list(request):
    queryset = models.Server.objects.all()
    return render(request, 'server_list.html', {'queryset': queryset})


class ServerModelForm(ModelForm):
    exclude_bootstrap = []

    class Meta:
        model = models.Server
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ServerModelForm, self).__init__(*args, **kwargs)

        # 给字段添加样式
        for key, field in self.fields.items():
            if key not in self.exclude_bootstrap:
                field.widget.attrs['class'] = 'form-control'


def server_add(request):
    if request.method == 'GET':
        form = ServerModelForm()
        return render(request, 'form.html', {'form': form})

    form = ServerModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('server_list')
    else:
        return render(request, 'form.html', {'form': form})


def server_edit(request, pk):
    server_object = models.Server.objects.filter(id=pk).first()
    if request.method == 'GET':
        # 将server_object当作默认值
        form = ServerModelForm(instance=server_object)
        return render(request, 'form.html', {'form': form})

    form = ServerModelForm(data=request.POST, instance=server_object)
    if form.is_valid():
        form.save()
        return redirect('server_list')
    else:
        return render(request, 'form.html', {'form': form})


def server_del(request, pk):
    models.Server.objects.filter(id=pk).delete()
    return JsonResponse({'status': True})
