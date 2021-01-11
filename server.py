
import socket  # 导入 socket 模块
from threading import Thread
import threading
 
ADDRESS = ('此处填写服务器私网ip', 6688)  # 绑定地址
#ADDRESS = ('localhost', 6688)
g_socket_server = None  # 负责监听的socket
g_conn_pool = []  # 连接池


oneOK=False
twoOK=False
 
def init():
    """
    初始化服务端
    """
    global g_socket_server
    global ADDRESS
    g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
    g_socket_server.bind(ADDRESS)
    g_socket_server.listen(5)  # 最大等待数（有很多人理解为最大连接数，其实是错误的）
    print("服务端已启动，等待客户端连接...")
 
 
def accept_client():
    """
    接收新连接
    """
    while True:
        client, _ = g_socket_server.accept()  # 阻塞，等待客户端连接
        # 加入连接池
        g_conn_pool.append(client)
        # 给每个客户端创建一个独立的线程进行管理
        thread = Thread(target=message_handle, args=(client,len(g_conn_pool)-1,))
        # 设置成守护线程
        thread.setDaemon(True)
        thread.start()

  

def message_handle(client,index):
    #建立一个新线程用于处理开始游戏
    global oneOK,twoOK
    global g_conn_pool
    while True:
        bytes = client.recv(1024)
        msg=bytes.decode(encoding='utf8')
        if msg=="1":
            if index==0:
                oneOK=True
                print("1 ok")
            else:
                twoOK=True
                print("2 ok")
            break
        if msg=="Error":
            client.close()
            # 删除连接
            g_conn_pool.remove(client)
            print("有一个客户端下线了。")
            return

    
    while len(g_conn_pool)<2 or oneOK==False or twoOK==False:
        pass
    msgs=str(index)
    g_conn_pool[index].sendall(msgs.encode(encoding='utf8'))  
    """
    消息处理
    """
    while True:
        print(index,"waiting for message")
        bytes = client.recv(1024)
        print("客户端",index,"消息:", bytes.decode(encoding='utf8'))

        
        msg=bytes.decode(encoding='utf8')
        #如果msg长度为1说明是正在连接状态
        if len(msg)>20:
            client.close()
            # 删除连接
            g_conn_pool.remove(client)
            print("有一个客户端下线了。")
            break

        if index==0:
            print("send to 1")
            g_conn_pool[1].sendall(msg.encode(encoding='utf8'))
        else:
            print("send to 0")
            g_conn_pool[0].sendall(msg.encode(encoding='utf8'))
        
        if msg=="Error":
            client.close()
            # 删除连接
            g_conn_pool.remove(client)
            print("有一个客户端下线了。")
            return
        
        if len(bytes) == 0:
            client.close()
            # 删除连接
            g_conn_pool.remove(client)
            print("有一个客户端下线了。")
            break
 
 
if __name__ == '__main__':
    init()
    # 新开一个线程，用于接收新连接
    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()
    # 主线程逻辑
    while True:
        cmd = input("""--------------------------
输入1:查看当前在线人数
输入2:给指定客户端发送消息
输入3:关闭服务端
""")
        if cmd == '1':
            print("--------------------------")
            print("当前在线人数：", len(g_conn_pool))
        elif cmd == '2':
            print("--------------------------")
            index, msg = input("请输入“索引,消息”的形式：").split(",")
            g_conn_pool[int(index)].sendall(msg.encode(encoding='utf8'))
        elif cmd == '3':
            exit()
