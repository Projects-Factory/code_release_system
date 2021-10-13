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

        queryset = models.Node.objects.filter(task_id=task_id)
        if queryset:
            # 给一个人发
            self.send(json.dumps(
                {'code': 'init', 'data': self.node_convert_data(queryset)}
            ))

    def websocket_receive(self, message):
        text = message['text']
        if text == 'init':
            # node_list = [
            #     {'key': 'start', 'text': '开始', 'figure': 'Ellipse'},
            #     {'key': 'download', 'parent': 'start', 'text': '下载代码'},
            #     {'key': 'compile', 'parent': 'download', 'text': '本地编译'},
            # ]
            # 给一个人发
            # self.send(text_data=json.dumps({'code': 'init', 'data': node_list}))

            task_id = self.scope['url_route']['kwargs'].get('task_id')
            queryset = models.Node.objects.filter(task_id=task_id)

            if not queryset:
                node_object_list = self.create_nodes(task_id)
            else:
                node_object_list = queryset

            # 群发
            async_to_sync(self.channel_layer.group_send)(
                task_id, {'type': 'my.send',
                          'message': {
                              'code': 'init',
                              'data': self.node_convert_data(node_object_list)}}
            )

    @staticmethod
    def node_convert_data(node_object_list):
        node_list = []
        for node_obj in node_object_list:
            temp = {'key': str(node_obj.id), 'text': node_obj.text}
            if node_obj.parent:
                temp.update({'parent': str(node_obj.parent_id)})

            node_list.append(temp)
        return node_list

    @staticmethod
    def create_nodes(task_id):
        node_object_list = []
        start_node = models.Node.objects.create(text='开始',
                                                task_id=task_id)
        node_object_list.append(start_node)

        download_node = models.Node.objects.create(
            text='下载', task_id=task_id, parent=start_node)
        node_object_list.append(download_node)

        upload_node = models.Node.objects.create(
            text='上传', task_id=task_id, parent=download_node)
        node_object_list.append(upload_node)

        task_obj = models.DeployTask.objects.filter(id=task_id).first()
        for server_obj in task_obj.project.servers.all():
            row = models.Node.objects.create(
                text=server_obj.hostname,
                task_id=task_id,
                parent=upload_node,
                server=server_obj
            )
            node_object_list.append(row)

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
