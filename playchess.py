import pygame
import sys
import time
import numpy as np
import socket
import threading

pygame.init()
pygame.font.init()
screen=pygame.display.set_mode((1020,750),0,32)
font = pygame.font.SysFont("Arial", 50)

#bgm
pygame.mixer.init()
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1)

#加载相关素材
playerBackgroud=pygame.image.load("qipan.jpg")
mainBackground=pygame.image.load("mainScene.jpg")
startButton=pygame.image.load("startGame.png")
blackChess=pygame.image.load("blackChess.png")
whiteChess=pygame.image.load("whiteChess.png")
#当前场景
currentScene="mainMenu"

#当前状态
waitingForPlayer=False

mynumber=0

#黑方
blackPlayer=True

#最近下子位置
latestX=-1
latestY=-1

#棋盘
board=np.zeros((16,16))

#棋子位置
chessX=np.linspace(25,785,16)
chessY=np.linspace(30,710,16)

#当前状态
waitingForElse=False

waitingForConnect=False

# 创建一个socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 主动去连接局域网内IP为192.168.27.238，端口为6688的进程
#client.connect(('localhost', 6688))
#此处填写服务器的公网ip
client.connect(('服务器公网ip', 6688))

def errorMessage():
    data="Error"
    data = data.encode('utf-8')
    global client
    client.sendall(data)
    pygame.quit()
    sys.exit()

def sendMessage(data):
    try:
        global waitingForElse
        waitingForElse=True
        data = data.encode('utf-8')
        global client
        client.sendall(data)
        # 接收服务端的反馈数据
        while True:
            rec_data = client.recv(1024).decode(encoding='utf8')
            if len(rec_data)>=3:
                rec_data=rec_data.split()

                #获取服务器传回的信息
                global latestX,latestY
                latestX=int(rec_data[0])
                latestY=int(rec_data[1])
                if blackPlayer:
                    board[int(rec_data[0]),int(rec_data[1])]=2
                else:
                    board[int(rec_data[0]),int(rec_data[1])]=1
                break

        waitingForElse=False
    except:
        errorMessage()
    

def firstMessage():
    try:
        global waitingForElse
        while True:
            print("i am waiting for the first message")
            rec_data = client.recv(1024).decode(encoding='utf8')
            print(rec_data)
            if len(rec_data)>=3:
                rec_data=rec_data.split()
                #获取服务器传回的信息
                if blackPlayer:
                    board[int(rec_data[0]),int(rec_data[1])]=2
                else:
                    board[int(rec_data[0]),int(rec_data[1])]=1
                break

        waitingForElse=False
    except:
        errorMessage()
    

def playerScene():
    try:
        global playerBackgroud
        global mainBackground
        global blackChess
        global whiteChess
        global chessX,chessY,board
        screen.fill((255,255,255))
        screen.blit(mainBackground,(0,0))
        screen.blit(playerBackgroud,(20,20))
        
        introduction=font.render("You:", 1, (253, 177, 6)) 
        screen.blit(introduction,(875,20))
        if blackPlayer:
            screen.blit(blackChess,(900,100))
        else:
            screen.blit(whiteChess,(900,100))

        #绘制棋子
        for i in range(16):
            for j in range(16):
                if board[i][j]==1:
                    screen.blit(blackChess,(chessX[i]-12,chessY[j]-12))
                elif board[i][j]==2:
                    #error
                    screen.blit(whiteChess,(chessX[i]-12,chessY[j]-12))
        
        global latestX,latestY
        if latestX!=-1 and latestY!=-1:
            recent=font.render("N", 1, (253, 177, 6))
            screen.blit(recent,(chessX[latestX]-30,chessY[latestY]-30))

        if waitingForElse:
            titleText=font.render("Waiting For Else to Act", 1, (253, 177, 6)) 
            screen.blit(titleText,(450,300))
        
        pygame.display.update()
    except:
        errorMessage()

def findWinner():
    global board
    #强行寻找赢家
    #从2找到13即可
    #遍历方向
    ways=[
        [[-2,0],[-1,0],[0,0],[1,0],[2,0]],
        [[-2,-2],[-1,-1],[0,0],[1,1],[2,2]],
        [[0,-2],[0,-1],[0,0],[0,1],[0,2]],
        [[-2,2],[-1,1],[0,0],[1,-1],[2,-2]]
    ]
    for i in range(2,14):
        for j in range(2,14):
            #遍历黑、白双方
            for t in range(1,3):
                #遍历四个方向
                for index in range(4):
                    if (board[i+ways[index][0][0],j+ways[index][0][1]]==t 
                    and board[i+ways[index][1][0],j+ways[index][1][1]]==t 
                    and board[i+ways[index][2][0],j+ways[index][2][1]]==t
                    and board[i+ways[index][3][0],j+ways[index][3][1]]==t 
                    and board[i+ways[index][4][0],j+ways[index][4][1]]==t):
                        return t
    #遍历边界
    index=2
    for i in range(0,16):
        for j in range(2,14):
            for t in range(1,3):
                if (board[i+ways[index][0][0],j+ways[index][0][1]]==t 
                    and board[i+ways[index][1][0],j+ways[index][1][1]]==t 
                    and board[i+ways[index][2][0],j+ways[index][2][1]]==t
                    and board[i+ways[index][3][0],j+ways[index][3][1]]==t 
                    and board[i+ways[index][4][0],j+ways[index][4][1]]==t):
                    return t
    index=0
    for i in range(2,14):
        for j in range(0,16):
            for t in range(1,3):
                if (board[i+ways[index][0][0],j+ways[index][0][1]]==t 
                    and board[i+ways[index][1][0],j+ways[index][1][1]]==t 
                    and board[i+ways[index][2][0],j+ways[index][2][1]]==t
                    and board[i+ways[index][3][0],j+ways[index][3][1]]==t 
                    and board[i+ways[index][4][0],j+ways[index][4][1]]==t):
                    return t

    return 0

def mainScene():
    try:
        global waitingForConnect
        global waitingForPlayer
        if waitingForConnect:
            return
        if waitingForPlayer==False:
            global mainBackground
            global startButton
            screen.fill((255,255,255))
            screen.blit(mainBackground,(0,0))
            titleText=font.render("Five Sons Chess", 1, (253, 177, 6)) 
            screen.blit(titleText,(250,200))
            screen.blit(startButton,(350,350))
            pygame.display.update()
        else:
            screen.fill((255,255,255))
            screen.blit(mainBackground,(0,0))
            titleText=font.render("Waiting For Else Player...", 1, (253, 177, 6))
            screen.blit(titleText,(250,200))
            pygame.display.update()
            
            #阻塞，发送消息，直到回应游戏开始
            data="1"
            data = data.encode('utf-8')
            global client
            client.sendall(data)
            
            waitingForConnect=True
            # 接收服务端的反馈数据
            while True:
                msg=client.recv(1024).decode(encoding='utf8')
                print(msg)
                if msg=="0":
                    print('game Start:',msg)
                    break
                else:
                    print('game Start:',msg)
                    global blackPlayer,waitingForElse
                    blackPlayer=False
                    waitingForElse=True
                    global mynumber
                    mynumber=1
                    break
            #切换场景
            waitingForPlayer=False
            print('start')
            global currentScene
            currentScene="playerScene"
            
            if not blackPlayer:
                #第一次消息
                thread = threading.Thread(target = firstMessage)
                thread.start()
    except:
        errorMessage()

    
def createScene():
    global currentScene
    if currentScene=="mainMenu":
        mainScene()
    elif currentScene=="playerScene":
        playerScene()
    elif currentScene=="win":
        winScene()
    elif currentScene=="lose":
        loseScene()

def winScene():
    screen.fill((255,255,255))
    screen.blit(mainBackground,(0,0))
    titleText=font.render("You WIN!!!!!", 1, (253, 177, 6))
    screen.blit(titleText,(250,200))
    pygame.display.update()
    time.sleep(1)
    #切换场景
    restartGame()

def loseScene():
    screen.fill((255,255,255))
    screen.blit(mainBackground,(0,0))
    titleText=font.render("You LOSE......", 1, (253, 177, 6))
    screen.blit(titleText,(250,200))
    pygame.display.update()
    time.sleep(1)
    #切换场景
    restartGame()

def restartGame():
    for i in range(16):
        for j in range(16):
            board[i,j]=0
    global waitingForElse
    waitingForElse=False
    global currentScene
    currentScene="playerScene"
    if mynumber==1:
        waitingForElse=True
        thread = threading.Thread(target = firstMessage)
        thread.start()

#判断在哪个下标的棋盘格子
def boardID(x,y):
    #可点击半径为5
    radius=7
    indexX=-1
    indexY=-1

    global chessX,chessY
    minDistX=9999
    minDistY=9999

    for i in range(16):
        if np.abs(chessX[i]-x)<minDistX and np.abs(chessX[i]-x)<radius:
            minDistX=np.abs(chessX[i]-x)
            indexX=i
        if np.abs(chessY[i]-y)<minDistY and np.abs(chessY[i]-y)<radius:
            minDistY=np.abs(chessY[i]-y)
            indexY=i
    
    return indexX,indexY

#点击事件
def buttonEvent(x,y):
    try:
        print(x," ",y)
        global waitingForElse
        if (currentScene=="mainMenu" and x>=350 
        and x<=startButton.get_width()+350
        and y>=350 and y<=startButton.get_height()+350):
            #start game
            global waitingForPlayer
            waitingForPlayer=True
        #在下棋界面
        elif currentScene=="playerScene" and not waitingForElse:
            i,j=boardID(x,y)
            if i!=-1 and j!=-1 and board[i,j]==0:
                #new qizi
                waitingForElse=True
                msg=str(i)+" "+str(j)
                print(msg)
                thread = threading.Thread(target = sendMessage,args =(msg,))
                thread.start()
                
                latestX=i
                latestY=j

                if blackPlayer:
                    board[i,j]=1
                else:
                    board[i,j]=2
    except:
        errorMessage()

#主函数
if __name__ == "__main__":
    try:
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    errorMessage()
                #用户点击
                if event.type==pygame.MOUSEBUTTONDOWN:
                    #获得鼠标位置
                    x, y = pygame.mouse.get_pos()
                    buttonEvent(x,y)
            
            result=findWinner()
            if result!=0:
                if (result==1 and blackPlayer) or (result==2 and not blackPlayer):
                    #win
                    currentScene="win"
                else:
                    currentScene="lose"

            createScene()
    except:
        errorMessage()