"""code_release_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from web.views import server, project, task

urlpatterns = [
    path('admin/', admin.site.urls),

    path('server/list/', server.server_list, name='server_list'),
    path('server/add/', server.server_add, name='server_add'),
    path('server/edit/<pk>/', server.server_edit, name='server_edit'),
    path('server/del/<pk>/', server.server_del, name='server_del'),

    path('project/list/', project.project_list, name='project_list'),
    path('project/add/', project.project_add, name='project_add'),
    path('project/edit/<pk>/', project.project_edit, name='project_edit'),
    path('project/del/<pk>/', project.project_del, name='project_del'),

    path('task/list/<project_id>/', task.task_list, name='task_list'),
    path('task/add/<project_id>/', task.task_add, name='task_add'),

    path('hook/template/<tid>/', task.hook_template, name='hook_template'),
]
