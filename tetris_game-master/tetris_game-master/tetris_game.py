import sys, random
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWIDGETSIZE_MAX, QBoxLayout, QMainWindow, QApplication, QHBoxLayout, QLabel ,QMessageBox, QStackedLayout, QWidget, QVBoxLayout, QPushButton, QDesktopWidget,QFrame
from PyQt5.QtCore import QSize, Qt, QBasicTimer, pyqtSignal, QCoreApplication, scientific
from PyQt5.QtGui import QBrush, QImage, QPainter, QColor, QPalette, QPixmap, QFont, QPen
from PyQt5 import QtWidgets, QtCore

from tetris_model import BOARD_DATA1, BOARD_DATA2,BoardData, Shape 
from tetris_ai import TETRIS_AI


# TETRIS_AI = None

class Tetris(QMainWindow):
    def __init__(self):
        super().__init__()
        self.isStarted = False
        self.isPaused = False
        self.nextMove = None
        self.lastShape = Shape.shapeNone   #shape.shapeNone == 0

        self.initUI()

    def initUI(self):
        self.gridSize = 30      # 전체 화면 크기
        self.speed = 200        # 도형이 떨어지는 속도       

        self.timer = QBasicTimer()     #basic timer 생성
        self.setFocusPolicy(Qt.StrongFocus)     #focusPolicy 속성을 포커스를 받도록 설정

        wid = QWidget(self)     # 레이아웃을 정렬하기 위한 센트럴위젯 선언
        self.setCentralWidget(wid)
        Layout = QHBoxLayout()  #메인 레이아웃

        leftLayout = QHBoxLayout()     #왼쪽 수평정렬 레이아웃
        self.tboard1 = Board(self, self.gridSize, BOARD_DATA1)
        leftLayout.addWidget(self.tboard1)          #보드1 위젯을 레이아웃에 추가
        self.sidePanel1 = SidePanel1(self, self.gridSize, BOARD_DATA1)
        leftLayout.addWidget(self.sidePanel1)          #사이드 패널1 위젯을 레이아웃에 추가
        Layout.addLayout(leftLayout)    #메인 레이아웃에 왼쪽 레이아웃 추가

        rightLayout = QHBoxLayout()     #오른쪽 수평정렬 레이아웃
        self.tboard2 = Board(self, self.gridSize, BOARD_DATA2)
        rightLayout.addWidget(self.tboard2)          #보드2 위젯을 레이아웃에 추가
        self.sidePanel2 = SidePanel2(self, self.gridSize,  BOARD_DATA2)
        rightLayout.addWidget(self.sidePanel2)          #사이드 패널2 위젯을 레이아웃에 추가
        Layout.addLayout(rightLayout)   #메인 레이아웃에 오른쪽 레이아웃 추가

        self.statusbar1 = self.statusBar()       #상태바1 만들기
        self.tboard1.msg2Statusbar[str].connect(self.statusbar1.showMessage)  #사용자 정의 시그널을 상태바 메시지랑 연결
 

        self.statusbar2 = self.statusBar()       #상태바2 만들기
        self.tboard2.msg2Statusbar[str].connect(self.statusbar2.showMessage)  #사용자 정의 시그널을 상태바 메시지랑 연결
        self.tboard2.show_alert_page_1.connect(self.show_alert_gameover)    # 사용자 보드가 패배시 gameover 출력

        wid.setLayout(Layout)

        self.start()
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

        # 전체 화면 크기 설정
        self.setFixedSize(self.tboard1.width() + self.sidePanel1.width() + self.tboard2.width() + self.sidePanel2.width(),
                          self.sidePanel1.height() + self.statusbar1.height() + 20)      

    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.tboard1.score = 5
        self.tboard2.score = 0
        BOARD_DATA1.clear()
        BOARD_DATA2.clear()

        self.tboard1.msg2Statusbar.emit(str(self.tboard1.score))

        BOARD_DATA1.createNewPiece()
        BOARD_DATA2.createNewPiece()
        self.timer.start(self.speed, self)


    def center(self):
        screen = QDesktopWidget().screenGeometry()  #화면 해상도
        size = self.geometry()      #0, 0, 640, 480 으로 설정되어있음
        self.move((screen.width() - size.width()) // 3, (screen.height() - size.height()) // 5)     # 게임 화면 위치

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.tboard1.msg2Statusbar.emit("paused")
        else:
            self.timer.start(self.speed, self)
            self.updateWindow()

    def updateWindow(self):
        self.tboard1.updateData()
        self.sidePanel1.updateData()
        self.tboard2.updateData()
        self.sidePanel2.updateData()
        self.update()

    def show_alert_gameover(self): #게임 오버되면 안내 메시지 출력후 게임 종료
        alert1 = QMessageBox()
        alert1.setIcon(QMessageBox.Warning)

        alert = QMessageBox.warning(
            self, 'Game Over', 'Game over',
            QMessageBox.Yes 
        )

        alert.exec_()

    #시간이 지남에 따라 도형의 다음 위치를 바꿈
    def timerEvent(self, event):    #위젯에 상속되어있는 함수를 수정
        if event.timerId() == self.timer.timerId():
            if TETRIS_AI and not self.nextMove:     #AI 사용시
                self.nextMove = TETRIS_AI.nextMove()
            if self.nextMove:
                k = 0
                while BOARD_DATA1.currentDirection != self.nextMove[0] and k < 4:
                    BOARD_DATA1.rotateRight()
                    k += 1
                k = 0
                while BOARD_DATA1.currentX != self.nextMove[1] and k < 5:
                    if BOARD_DATA1.currentX > self.nextMove[1]: 
                        BOARD_DATA1.moveLeft()
                    elif BOARD_DATA1.currentX < self.nextMove[1]:
                        BOARD_DATA1.moveRight()
                    k += 1
            # lines = BOARD_DATA1.dropDown()
            lines1 = BOARD_DATA1.moveDown()
            lines2 = BOARD_DATA2.moveDown()
            self.tboard1.score += lines1
            self.tboard2.score += lines2
            if self.lastShape != BOARD_DATA1.currentShape:
                self.nextMove = None
                self.lastShape = BOARD_DATA1.currentShape

            #점수    
            self.sidePanel1.label.setText(str(self.tboard1.score))
            self.sidePanel1.label.setFont(QtGui.QFont("맑은 고딕",20))

            self.sidePanel2.label.setText(str(self.tboard2.score))
            self.sidePanel2.label.setFont(QtGui.QFont("맑은 고딕",20))

            # 승리 조건
            if self.tboard2.score >= self.tboard1.score + 10:   #AI보다 10점 이상을 앞서면 승리
                alert = QMessageBox.information(
                self, 'You Win!!!', 'Congratulations 👍👍',
                QMessageBox.Yes)
                alert.exec_()

            if self.tboard1.score >= self.tboard2.score + 10:   #AI보다 10점 이상을 뒤쳐지면 패배
                alert = QMessageBox.information(
                self, 'You Lose...', 'TephaGo is Winner 😢😢',
                QMessageBox.Yes)
                alert.exec_()

            
            self.updateWindow()
        else:
            super(Tetris, self).timerEvent(event)

    def keyPressEvent(self, event):
        if not self.isStarted or BOARD_DATA1.currentShape == Shape.shapeNone:
            super(Tetris, self).keyPressEvent(event)
            return

        if not self.isStarted or BOARD_DATA2.currentShape == Shape.shapeNone:
            super(Tetris, self).keyPressEvent(event)
            return

        key = event.key()
        
        if key == Qt.Key_P:
            self.pause()
            return
            
        if self.isPaused:
            return
        elif key == Qt.Key_Left:
            BOARD_DATA2.moveLeft()
        elif key == Qt.Key_Right:
            BOARD_DATA2.moveRight()
        elif key == Qt.Key_Up:
            BOARD_DATA2.rotateLeft()
        elif key == Qt.Key_Down:
            BOARD_DATA2.rotateRight()
        elif key == Qt.Key_D:
            self.tboard2.score += BOARD_DATA2.moveDown()
        elif key == Qt.Key_Space:
            self.tboard2.score += BOARD_DATA2.dropDown()
        else:
            super(Tetris, self).keyPressEvent(event)

        self.updateWindow()

def drawSquare(painter, x, y, val, s):
    colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                  0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

    if val == 0:
        return

    color = QColor(colorTable[val])
    painter.fillRect(x + 1, y + 1, s - 2, s - 2, color) #직사각형 그리기

    painter.setPen(color.lighter())     #선 색깔 조정
    painter.drawLine(x, y + s - 1, x, y)    
    painter.drawLine(x, y, x + s - 1, y)

    painter.setPen(color.darker())
    painter.drawLine(x + 1, y + s - 1, x + s - 1, y + s - 1)
    painter.drawLine(x + s - 1, y + s - 1, x + s - 1, y + 1)

class SidePanel1(QFrame):
    def __init__(self, parent, gridSize, BOARD_DATA):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * 22)   #위젯의 가로, 세로 크기 설정
        self.move(gridSize * 10, 0)   #사이드 패널의 도형 위치
        self.gridSize = gridSize
        self.BOARD_DATA = BOARD_DATA

        self.label = QLabel("score", self)
        self.label.setGeometry(QtCore.QRect(gridSize * 2, gridSize * 5, 50, 30))

        self.name = QLabel("AI🤖", self)
        self.name.setGeometry(QtCore.QRect(gridSize * 1.5, gridSize * 2, 70, 70))
        self.name.setFont(QtGui.QFont("맑은 고딕",15))

    def updateData(self):
        self.update()

    # 다음에 나올 도형의 모양을 그려준다
    def paintEvent(self, event):        #QPainter 함수
        painter = QPainter(self)
        minX, maxX, minY, maxY = self.BOARD_DATA.nextShape.getBoundingOffsets(0)

        dy = 18 * self.gridSize # 도형의 상하 위치
        dx = (self.width() - (maxX - minX) * self.gridSize) / 2 + 10    # 도형의 좌우 위치

        
        val = self.BOARD_DATA.nextShape.shape
        for x, y in self.BOARD_DATA.nextShape.getCoords(0, 0, -minY):
            drawSquare(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize)

        #중앙 경계선
        painter.setPen(QPen(Qt.black, 5, Qt.DashDotLine))      #색, 굵기 설정
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QPen(Qt.black, 5, Qt.DashDotLine))
        painter.drawLine(self.width(), 0, self.width(), self.height())

class SidePanel2(QFrame):
    def __init__(self, parent, gridSize, BOARD_DATA):
        super().__init__(parent)
        self.setFixedSize(gridSize * 5, gridSize * 22)   #위젯의 가로, 세로 크기 설정
        self.move(gridSize * 10, 0)   #사이드 패널의 도형 위치
        self.gridSize = gridSize
        self.BOARD_DATA = BOARD_DATA
        
        self.label = QLabel("score", self)
        self.label.setGeometry(QtCore.QRect(gridSize * 2, gridSize * 5, 50, 30))

        self.name = QLabel("Player", self)
        self.name.setGeometry(QtCore.QRect(gridSize * 1.5, gridSize * 1.3, 70, 100))
        self.name.setFont(QtGui.QFont("맑은 고딕",15))

    def updateData(self):
        self.update()

    # 다음에 나올 도형의 모양을 그려준다
    def paintEvent(self, event):        #QPainter 함수
        painter = QPainter(self)
        minX, maxX, minY, maxY = self.BOARD_DATA.nextShape.getBoundingOffsets(0)

        dy = 18 * self.gridSize # 도형의 상하 위치
        dx = (self.width() - (maxX - minX) * self.gridSize) / 2 + 10    # 도형의 좌우 위치
       
        val = self.BOARD_DATA.nextShape.shape
        for x, y in self.BOARD_DATA.nextShape.getCoords(0, 0, -minY):
            drawSquare(painter, x * self.gridSize + dx, y * self.gridSize + dy, val, self.gridSize)

class Board(QFrame):
    show_alert_page_1 = pyqtSignal()
    msg2Statusbar = pyqtSignal(str) #사용자 정의 시그널
    speed = 10

    def __init__(self, parent, gridSize, BOARD_DATA):
        super().__init__(parent)
        self.setFixedSize(gridSize * 10, gridSize * 22)
        self.gridSize = gridSize
        self.BOARD_DATA = BOARD_DATA
        self.initBoard()


    def initBoard(self):
        self.score = 0
        self.BOARD_DATA.clear()

    def paintEvent(self, event):        #QPainter 함수
        painter = QPainter(self)

        # Draw backboard 이미 떨어진 도형의 형태
        for x in range(10):
            for y in range(22):
                val = self.BOARD_DATA.getValue(x, y)
                drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        # Draw current shape 떨어지고 있는 현재 도형의 형태
        for x, y in self.BOARD_DATA.getCurrentShapeCoord():
            val = self.BOARD_DATA.currentShape.shape
            drawSquare(painter, x * self.gridSize, y * self.gridSize, val, self.gridSize)

        # Draw a border 세로 경계선
        painter.setPen(QColor(0x777777))    #색깔 조정
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())

    def updateData(self):
        
        if not self.BOARD_DATA.flag:
            self.show_alert_page_1.emit()
            
        for x in range(0, 10 - 1):
            if (self.BOARD_DATA.backBoard[x] > 0):
                self.show_alert_page_1.emit()
                
        self.msg2Statusbar.emit("OpenSW 5")
        self.update()

class Level(Tetris):
    def setLevelButton(self, Form): #난이도 선택 버튼 생성
        self.pause() #게임 멈추고 레벨 선택
        Form.setObjectName("Form")
        Form.setGeometry(973, 331, 300, 150)

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(30, 60, 113, 32))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.easyClicked)

        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(160, 60, 113, 32))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.hardClicked)

        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(120, 30, 281, 23))
        self.label.setObjectName("label")

        self.LevelButton(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def LevelButton(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Select Level Window"))
        self.pushButton.setText(_translate("Form", "easy"))
        self.pushButton_2.setText(_translate("Form", "hard"))
        self.label.setText(_translate("Form", "난이도 선택"))

    def easyClicked(self, Form):
        speed = 300
        self.speed = speed
        LevelWindow.close()
        self.pause()

    def hardClicked(self, Form):
        speed = 100
        self.speed = speed
        LevelWindow.close()
        self.pause()

    

class startUI(QWidget):
    def __init__(self, gridSize):
        super().__init__()
        self.gridSize = gridSize
        self.initUI(self.gridSize)

    def initUI(self, gridSize):
        self.gridSize = gridSize
        self.center()
        self.setMouseTracking(True)

        #제목
        oname = QLabel('ㅗ', self)
        oname.setFont(QtGui.QFont('맑은 고딕'))
        oname.setStyleSheet("Color : white")
        oname.move(440 , 550)
        oname.setAlignment(Qt.AlignCenter)
        o_info = oname.font()
        o_info.setBold(True)
        o_info.setPointSize(50)
        oname.setFont(o_info)

        game_name = QLabel(' TETRIS GAME ', self)
        game_name.setFont(QtGui.QFont("맑은 고딕"))
        game_name.setStyleSheet("Color : white; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.857143, y2:0.857955, stop:0 rgba(10, 242, 251, 255), stop:1 rgba(224, 6, 159, 255)); border-radius: 25px")
        game_name.move(300, 200)
        game_name.setAlignment(Qt.AlignCenter)
        
        font_MainName =  game_name.font()
        font_MainName.setPointSize(30)
        font_MainName.setBold(True)

        name = QLabel(' 조 : 박다흰 김윤지 이상학 조상혁', self)
        name.setFont(QtGui.QFont('맑은 고딕'))
        name.setStyleSheet("Color : white")
        name.move(520, 600)
        name.setAlignment(Qt.AlignCenter)
        info = name.font()
        info.setBold(True)
        info.setPointSize(15)

        game_name.setFont(font_MainName)
        name.setFont(info)
        
        layout = QVBoxLayout()
        layout.addWidget(game_name)
        layout.addWidget(name)
        layout.addWidget(oname)

        #배경 지정
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.black) #배경색 지정
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    #버튼 리스너 생성
    def mouseButtonPush(self, buttons):
        if buttons & Qt.LeftButton:
            widget.setCurrentIndex(widget.currentIndex()+1)
            infowindow.show()
    def mousePressEvent(self, e):
        self.mouseButtonPush(e.buttons())
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
             
class InfoUI(QWidget):
    def __init__(self, gridSize):
        super().__init__()
        self.gridSize = gridSize
        self.initUI(self.gridSize)

    def initUI(self, gridSize):
        self.gridSize = gridSize
        game_name = QLabel(' 게임설명 ', self)
        game_name.setFont(QtGui.QFont('맑은 고딕'))
        game_name.setStyleSheet("Color : white; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.857143, y2:0.857955, stop:0 rgba(10, 242, 251, 255), stop:1 rgba(224, 6, 159, 255)); border-radius: 25px")
        game_name.move(350, 20)
        game_name.setAlignment(Qt.AlignCenter)
        font_MainName = game_name.font()
        font_MainName.setPointSize(30)
        font_MainName.setBold(True)
        #게임 설명
        level_info = QLabel('1. 난이도를 선택할 수 있습니다.',self)
        level_info.setFont(QtGui.QFont('맑은 고딕'))
        level_info.setStyleSheet("Color : white")
        level_info.move(20, 90)
        level_info.setAlignment(Qt.AlignCenter)
        font_level = level_info.font()
        font_level.setBold(True)
        font_level.setPointSize(15)
  
        first_info = QLabel('2. ↑ 키는 좌, ↓ 키는 우로 도형을 회전시킵니다.', self)
        first_info.move(20, 190)#80씩 내려감 -> 100씩 내려감
        first_info.setStyleSheet("Color : white")
        first_info.setAlignment(Qt.AlignCenter)
        font_first_info = first_info.font()
        font_first_info.setBold(True)
        font_first_info.setPointSize(15)

        second_info = QLabel('3. ←, → 키을 이용하여 도형의 내려가는 방향을 바꿀 수 있습니다.', self)
        second_info.move(20, 290)#80씩 내려감 -> 100씩 내려감
        second_info.setStyleSheet("Color : white")
        second_info.setAlignment(Qt.AlignCenter)
        font_sec_info = second_info.font()
        font_sec_info.setBold(True)
        font_sec_info.setPointSize(15)

        third_info = QLabel('4. D 키과 SPACE 키를 이용해 도형을 빠르게 내릴 수 있습니다.', self)
        third_info.move(20, 390)#80씩 내려감 -> 100씩 내려감
        third_info.setStyleSheet("Color : white")
        third_info.setAlignment(Qt.AlignCenter)
        font_th_info = third_info.font()
        font_th_info.setBold(True)
        font_th_info.setPointSize(15)
        
        four_info = QLabel('5. P키를 누르면 게임을 일시정지 할 수 있습니다.', self)
        four_info.move(20, 490)#80씩 내려감 -> 100씩 내려감
        four_info.setStyleSheet("Color : white")
        four_info.setAlignment(Qt.AlignCenter)
        font_fo_info = third_info.font()
        font_fo_info.setBold(True)
        font_fo_info.setPointSize(15)

        p_info = QLabel('6. 게임을 시작하려면 Game Start 버튼을 눌러주세요.', self)
        p_info.move(20, 590)#80씩 내려감 -> 100씩 내려감
        p_info.setStyleSheet("Color : white")
        p_info.setAlignment(Qt.AlignCenter)
        font_p_info = third_info.font()
        font_p_info.setBold(True)
        font_p_info.setPointSize(15)

        game_name.setFont(font_MainName)
        level_info.setFont(font_level)
        first_info.setFont(font_level)
        second_info.setFont(font_level)
        third_info.setFont(font_level)
        four_info.setFont(font_level)
        p_info.setFont(font_level)
  
        layout = QVBoxLayout()
        layout.addWidget(game_name)
        layout.addWidget(level_info)

        pal = QPalette()
        #pal.setColor(QPalette.Background, Qt.black) #배경색 지정
        pal.setColor(QPalette.Background, QColor(114,112,114))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

         #버튼 만들기
        btn1 = QPushButton('Game Start', self)
        btn1.setCheckable(True)
        btn1.clicked.connect(self.isClicked)
        btn1.toggle()

        layout.addWidget(btn1)
        btn1.setFont(QtGui.QFont("맑은 고딕"))
        btn1.setStyleSheet('color:white; background : Blue; border-radius: 10px')
        btn1.resize(200,50)
        btn1.move(700,600)

        #배경 지정 
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.black) #배경색 지정
        #pal.setColor(QPalette.Background, QColor(114,112,114))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
    #버튼 리스너 생성
    def isClicked(self):
        print("버튼 클릭됨")
        widget.setCurrentIndex(widget.currentIndex()+1)
        #Tetris.show()
        LevelWindow.show()
        return True

if __name__ == '__main__':
    app = QApplication([])
    LevelWindow = QtWidgets.QMainWindow()
    #화면 전환용 Widget 설정
    widget = QtWidgets.QStackedWidget()
    mainWindow = startUI(30)
    infowindow = InfoUI(30)
    lv = Level()
    lv.setLevelButton(LevelWindow)

    widget.addWidget(mainWindow)
    widget.addWidget(infowindow)
    widget.addWidget(lv)

    widget.show()

    sys.exit(app.exec_())