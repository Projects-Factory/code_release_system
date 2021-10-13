# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/12 23:06 
"""
import json

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

from web import models


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

        text = message['text']
        if text == 'init':
            node_object_list = self.create_nodes(task_id)

            # 群发
            async_to_sync(self.channel_layer.group_send)(
                task_id, {'type': 'my.send',
                          'message': {
                              'code': 'init',
                              'data': self.node_convert_data(node_object_list)}}
            )

        if text == 'deploy':
            start_node = models.Node.objects.filter(
                text='开始', task_id=task_id).first()
            # todo

    @staticmethod
    def node_convert_data(node_object_list):
        """根据node对象转换成gojs数据"""
        node_list = []
        for node_obj in node_object_list:
            temp = {'key': str(node_obj.id), 'text': node_obj.text}
            if node_obj.parent:
                temp.update({'parent': str(node_obj.parent_id)})

            node_list.append(temp)
        return node_list

    @staticmethod
    def create_nodes(task_id):
        queryset = models.Node.objects.filter(task_id=task_id)
        if queryset:
            return queryset

        task_obj = models.DeployTask.objects.filter(id=task_id).first()

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
                )
                node_object_list.append(server_node)

            deploy_node = models.Node.objects.create(
                text='发布', task_id=task_id, parent=server_node)
            node_object_list.append(deploy_node)

            if task_obj.after_deploy_script:
                after_deploy = models.Node.objects.create(
                    text='发布后', task_id=task_id, parent=deploy_node)
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
