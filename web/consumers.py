# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/12 23:06 
"""
import json

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync


class PublishConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        """客户端向服务端创建链接"""
        # 接受客户端连接
        self.accept()

        task_id = self.scope['url_route']['kwargs'].get('task_id')
        # 创建群组
        async_to_sync(self.channel_layer.group_add)(task_id, self.channel_name)

    def websocket_receive(self, message):
        text = message['text']
        if text == 'init':
            node_list = [
                {'key': 'start', 'text': '开始', 'figure': 'Ellipse'},
                {'key': 'download', 'parent': 'start', 'text': '下载代码'},
                {'key': 'compile', 'parent': 'download', 'text': '本地编译'},
            ]
            # 给一个人发
            # self.send(text_data=json.dumps({'code': 'init', 'data': node_list}))

            # 群发
            task_id = self.scope['url_route']['kwargs'].get('task_id')
            async_to_sync(self.channel_layer.group_send)(
                task_id, {'type': 'my.send',
                          'message': {'code': 'init', 'data': node_list}})

    def my_send(self, event):
        message = event['message']
        self.send(json.dumps(message))

    def websocket_disconnect(self, message):
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        # 关闭群组
        async_to_sync(self.channel_layer.group_discard)(
            task_id, self.channel_name)
        raise StopConsumer()
