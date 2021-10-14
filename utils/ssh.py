# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/10/14 23:15 
"""
import paramiko


class SSHProxy(object):

    def __init__(self, hostname, port, username, private_key_path):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.private_key_path = private_key_path

        self.transport = None

    def open(self):
        private_key = paramiko.RSAKey.from_private_key_file(
            self.private_key_path)
        self.transport = paramiko.Transport(f'{self.hostname}:{self.port}')
        self.transport.connect(username=self.username, pkey=private_key)

    def close(self):
        self.transport.close()

    def command(self, cmd):
        ssh = paramiko.SSHClient()
        ssh._transport = self.transport
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        # ssh.close()
        return result

    def upload(self, local_path, remote_path):
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        sftp.put(local_path, remote_path)
        sftp.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
