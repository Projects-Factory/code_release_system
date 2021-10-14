# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/12 23:06 
"""
import os
import json
import time
import shutil
import threading
import subprocess

from django.conf import settings
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

from web import models
from utils.repo import GitRepository
from utils.ssh import SSHProxy


class PublishConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        """客户端向服务端创建链接"""
        # 接受客户端连接
        self.accept()

        task_id = self.scope['url_route']['kwargs'].get('task_id')
        # 创建群组
        async_to_sync(self.channel_layer.group_add)(task_id, self.channel_name)

        # 当用户打开也页面时，如果已经创建节点了就自动展示节点
        queryset = models.Node.objects.filter(task_id=task_id)
        if queryset:
            # 给一个人发
            self.send(json.dumps(
                {'code': 'init', 'data': self.node_convert_data(queryset)}
            ))

    def websocket_receive(self, message):
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        task_obj = models.DeployTask.objects.filter(id=task_id).first()

        text = message['text']
        if text == 'init':
            node_object_list = self.create_nodes(task_id, task_obj)

            # 群发
            async_to_sync(self.channel_layer.group_send)(
                task_id, {'type': 'my.send',
                          'message': {
                              'code': 'init',
                              'data': self.node_convert_data(node_object_list)}}
            )

        if text == 'deploy':
            # 子线程负责处理，主线程负责去队列里取状态然后返回
            thread = threading.Thread(target=self.deploy,
                                      args=(task_id, task_obj))
            thread.start()

    @staticmethod
    def run_script(script, script_name, script_folder):
        try:
            script_path = os.path.join(script_folder, script_name)
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)

            subprocess.check_output(f'python "{script_name}"', shell=True,
                                    cwd=script_folder)
            return 'green'
        except:
            return 'red'

    def deploy(self, task_id, task_obj):
        self.update_node('开始', task_id)

        project_name = task_obj.project.title
        uid = task_obj.uid

        script_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name,
                                     uid, 'scripts')
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)

        project_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name,
                                      uid, project_name)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)

        package_folder = os.path.join(settings.PACKAGE_PATH, project_name)
        if not os.path.exists(package_folder):
            os.makedirs(package_folder)

        if task_obj.before_download_script:
            # 发布机执行下载前脚本
            status = self.run_script(task_obj.before_download_script,
                                     'before_download_script.py', script_folder)

            self.update_node('下载前', task_id, color=status)
            if status == 'red':
                return

        # 去仓库下载
        try:
            GitRepository(project_folder, task_obj.project.repo, task_obj.tag)
            status = 'green'
        except:
            status = 'red'
        self.update_node('下载', task_id, color=status)
        if status == 'red':
            return

        if task_obj.after_download_script:
            status = self.run_script(task_obj.after_download_script,
                                     'after_download_script.py', script_folder)
            self.update_node('下载后', task_id, color=status)
            if status == 'red':
                return

        self.update_node('上传', task_id)

        # 压缩代码
        upload_path = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid)

        package_path = shutil.make_archive(
            base_name=os.path.join(package_folder, uid + '.zip'),
            format='zip',
            root_dir=upload_path
        )

        # 连接每台服务器
        for server_obj in task_obj.project.servers.all():
            try:
                with SSHProxy(server_obj.hostname, settings.SSH_PORT,
                              settings.SSH_USER,
                              settings.PRIVATE_RSA_PATH) as ssh:
                    remote_folder = os.path.join(settings.SERVER_PACKAGE_PATH,
                                                 project_name)
                    ssh.command(f'mkdir -p "{remote_folder}"')
                    ssh.upload(package_path,
                               os.path.join(remote_folder, uid + '.zip'))
                    status = 'green'
            except:
                status = 'red'

            filters = {'server': server_obj}
            self.update_node(server_obj.hostname, task_id, filters, status)
            if status == 'red':
                continue

            if task_obj.before_deploy_script:
                self.update_node('发布前', task_id, filters)

            self.update_node('发布', task_id, filters)

            if task_obj.after_deploy_script:
                self.update_node('发布后', task_id, filters)

    def update_node(self, filter_text, task_id, filters=None, color='green'):
        filters = filters or {}

        node = models.Node.objects.filter(
            text=filter_text, task_id=task_id, **filters).first()
        node.status = color
        node.save()

        async_to_sync(self.channel_layer.group_send)(
            task_id, {'type': 'my.send',
                      'message': {
                          'code': 'update',
                          'node_id': node.id, 'color': color}}
        )

    @staticmethod
    def node_convert_data(node_object_list):
        """根据node对象转换成gojs数据"""
        node_list = []
        for node_obj in node_object_list:
            temp = {'key': str(node_obj.id), 'text': node_obj.text,
                    'color': node_obj.status}
            if node_obj.parent:
                temp.update({'parent': str(node_obj.parent_id)})

            node_list.append(temp)
        return node_list

    @staticmethod
    def create_nodes(task_id, task_obj):
        queryset = models.Node.objects.filter(task_id=task_id)
        if queryset:
            return queryset

        node_object_list = []
        start_node = models.Node.objects.create(text='开始', task_id=task_id)
        node_object_list.append(start_node)

        if task_obj.before_download_script:
            before_download = models.Node.objects.create(
                text='下载前', task_id=task_id, parent=start_node)
            node_object_list.append(before_download)

        download_node = models.Node.objects.create(
            text='下载', task_id=task_id, parent=node_object_list[-1])
        node_object_list.append(download_node)

        if task_obj.after_download_script:
            after_download = models.Node.objects.create(
                text='下载后', task_id=task_id, parent=node_object_list[-1])
            node_object_list.append(after_download)

        upload_node = models.Node.objects.create(
            text='上传', task_id=task_id, parent=node_object_list[-1])
        node_object_list.append(upload_node)

        task_obj = models.DeployTask.objects.filter(id=task_id).first()
        for server_obj in task_obj.project.servers.all():
            server_node = models.Node.objects.create(
                text=server_obj.hostname,
                task_id=task_id,
                parent=upload_node,
                server=server_obj
            )
            node_object_list.append(server_node)

            if task_obj.before_deploy_script:
                server_node = models.Node.objects.create(
                    text='发布前',
                    task_id=task_id,
                    parent=server_node,
                    server=server_obj
                )
                node_object_list.append(server_node)

            deploy_node = models.Node.objects.create(
                text='发布', task_id=task_id, parent=server_node,
                server=server_obj)
            node_object_list.append(deploy_node)

            if task_obj.after_deploy_script:
                after_deploy = models.Node.objects.create(
                    text='发布后', task_id=task_id, parent=deploy_node,
                    server=server_obj)
                node_object_list.append(after_deploy)

        return node_object_list

    def my_send(self, event):
        message = event['message']
        self.send(json.dumps(message))

    def websocket_disconnect(self, message):
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        # 关闭群组
        async_to_sync(self.channel_layer.group_discard)(
            task_id, self.channel_name)
        raise StopConsumer()
