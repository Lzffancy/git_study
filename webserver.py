"""
web server 服务程序
"""
from socket import *
from select import select
import os


# 处理客户端请求
class Handle:
    def __init__(self, html=""):
        self.html = html

    # 具体处理浏览器http请求,供其他程序调用的入口
    def manager(self, connfd):
        request = connfd.recv(1024).decode()
        # print(request)
        if not request:
            raise Exception  # 防止客户端异常退出
        else:
            self.__deal_req(request, connfd)

    def __deal_req(self, req, connfd):
        req = req.split(" ", 3)
        # print(req)
        req_type = req[0]
        req_data = req[1]
        print('req_Type %s,data_path%s' % (req_type, req_data))

        if req_type == "GET":
            # if req_data =='/':
            self.__responese_get(req_data, connfd)

    def __responese_get(self, req_data, connfd):
        """
        处理GET请求
        :param req_data: 请求的数据
        :param connfd: 连接套接字
        :return: none
        """
        res = "HTTP/1.1 200 OK\r\n"
        res += "Content-Type:text/html\r\n"
        res += "\r\n"
        res = res.encode()
        # 访问主页
        if req_data == '/':
            with open(self.html + "/" + "index.html", 'rb') as index_html:
                res += index_html.read()
                connfd.send(res)  # 发送响应
        # 访问其他位置
        else:
            if os.path.exists(self.html + "/" + "%s" % req_data):
                with open(self.html + "/" + "%s" % req_data, 'rb') as index_html:
                    res += index_html.read()
                    connfd.send(res)
            else:
                with open(self.html + "/" + "404.html", 'rb') as index_html:
                    res += index_html.read()
                    connfd.send(res)


class WebServer:
    '''
    IO多路复用　服务器
    '''

    def __init__(self, host="", port=0, html=None):
        """
        :param host:服务器ip
        :param port:开放端口
        :param html: web文件位置
        """
        self.host = host
        self.port = port
        self.html = html
        self.address = (host, port)

        self.handle = Handle(self.html)  # 实例化处理类对象
        self.sock = self.__create_socket()
        self.rlist = []
        self.wlist = []
        self.xlist = []

    # 准备tcp套接字
    def __create_socket(self):
        sock = socket()
        sock.bind(self.address)
        sock.setblocking(False)
        return sock

    # 处理浏览器连接
    def __connect(self):
        connfd, add = self.sock.accept()
        connfd.setblocking(False)
        self.rlist.append(connfd)
        print("connect from", add)

    # 启动服务
    def start(self):
        self.sock.listen(5)
        print("Listen the port %d" % self.port)
        self.rlist.append(self.sock)  # 监控监听套接字
        # IO多路服用模型
        '''
          使用BS框架中，浏览器访问服务器在申请资源时候
          会大量多次的创建connect_socket下载不同资源,
          此场景使用io多路复用　最大化提高访问效率
        '''
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sock:
                    self.__connect()
                else:
                    try:
                        self.handle.manager(r)
                    except Exception as e:
                        print(e)
                    finally:
                        self.rlist.remove(r)
                        r.close()


if __name__ == '__main__':
    # 先确定类的使用方法
    # 什么数据量是用户决定的
    # host="176.140.10.139"教室局域网
    # host = "192.168.2.103"家庭局域网
    httpd = WebServer(host="176.140.10.139", port=8889, html="./static")
    httpd.start()  # 启动服务

# 为什么本地加了host访问指定IP的服务器要加端口号？??????????????????????????????
