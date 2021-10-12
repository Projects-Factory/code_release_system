# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/12 23:04 
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from web import consumers

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        url(r'^publish/(?P<task_id>\d+)/$',
            consumers.PublishConsumer.as_asgi()),
    ])
})
