import sys, random
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QLabel, QMessageBox, QWidget
from PyQt5.QtCore import QTime, QTimer, Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5 import QtWidgets, QtCore

from tetris_model import BOARD_DATA1, BOARD_DATA2, Shape 
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
        self.tboard1.score = 0
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


    def closeEvent(self, QCloseEvent): # 종료키를 누르면 안내메시지 출력
        if self.isPaused == False:
            self.pause()
    
        close_ans = QMessageBox.question(self, "종료 확인", "종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if close_ans == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()
            self.pause()


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
            self.sidePanel1.label.setText(str(self.tboard1.score))#점수
            self.sidePanel2.label.setText(str(self.tboard2.score))
            # 승리 조건
            if self.tboard2.score >= 10:
                alert = QMessageBox.information(
                self, 'You Win!!!', 'Congratulations 👍👍',
                QMessageBox.Yes)
                alert.exec_()

            if self.tboard1.score >= 10:
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
        self.label.move(gridSize * 2, gridSize * 5)

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
        self.label.move(gridSize * 2, gridSize * 5)


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
        self.pause() #수정 필요

    def hardClicked(self, Form):
        speed = 100
        self.speed = speed
        LevelWindow.close()
        self.pause()

    

if __name__ == '__main__':
    # random.seed(32)
    app = QApplication([])
    LevelWindow = QtWidgets.QMainWindow()
    lv = Level()
    lv.setLevelButton(LevelWindow)
    LevelWindow.show()
    sys.exit(app.exec_())