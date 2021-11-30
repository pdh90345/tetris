#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random # 랜덤 모듈을 이용해 도형이 무작위로 나오도록 한다
from PyQt5.QtWidgets import QMessageBox

class Shape(object): # 도형의 모양
    shapeNone = 0
    shapeI = 1
    shapeL = 2
    shapeJ = 3
    shapeT = 4
    shapeO = 5
    shapeS = 6
    shapeZ = 7

    shapeCoord = ( #도형의 좌표
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((0, -1), (0, 0), (0, 1), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (-1, 1)),
        ((0, -1), (0, 0), (0, 1), (1, 0)),
        ((0, 0), (0, -1), (1, 0), (1, -1)),
        ((0, 0), (0, -1), (-1, 0), (1, -1)),
        ((0, 0), (0, -1), (1, 0), (-1, -1))
    )

    def __init__(self, shape=0): # 초기화
        self.shape = shape

    def getRotatedOffsets(self, direction): # 도형 각각 회전했을 때의 좌표
        tmpCoords = Shape.shapeCoord[self.shape]
        if direction == 0 or self.shape == Shape.shapeO: # 도형O 일때는 회전해도 모양이 같으므로 좌표가 변하지 않는다.
            return ((x, y) for x, y in tmpCoords)

        if direction == 1:
            return ((-y, x) for x, y in tmpCoords)

        if direction == 2:
            if self.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS): #도형 I,Z,S는 변하는 모양이 두개 밖에 없으므로 따로 지정
                return ((x, y) for x, y in tmpCoords)
            else:
                return ((-x, -y) for x, y in tmpCoords)

        if direction == 3:
            if self.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS): #도형 I,Z,S는 변하는 모양이 두개 밖에 없으므로 따로 지정
                return ((-y, x) for x, y in tmpCoords)
            else:
                return ((y, -x) for x, y in tmpCoords)

    def getCoords(self, direction, x, y): #변환된 도형의 좌표값
        return ((x + xx, y + yy) for xx, yy in self.getRotatedOffsets(direction))

    def getBoundingOffsets(self, direction): # 경계값을 넘어가면 값을 변환시킨다
        tmpCoords = self.getRotatedOffsets(direction)
        minX, maxX, minY, maxY = 0, 0, 0, 0
        for x, y in tmpCoords:
            if minX > x:
                minX = x
            if maxX < x:
                maxX = x
            if minY > y:
                minY = y
            if maxY < y:
                maxY = y
        return (minX, maxX, minY, maxY)


class BoardData(object): 
    width = 10
    height = 22
    flag = True

    def __init__(self): #게임 보드 초기화(생성자 역할)
        self.backBoard = [0] * BoardData.width * BoardData.height

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()
        self.nextShape = Shape(random.randint(1, 7))

        self.shapeStat = [0] * 8

    def getData(self): #데이터를 받는다
        return self.backBoard[:]

    def getValue(self, x, y): #속성 값을 저장한다
        return self.backBoard[x + y * BoardData.width]

    def getCurrentShapeCoord(self): #현재 도형 모양의 좌표값을 저장한다
        return self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY)

    def createNewPiece(self): # 새로운 도형을 만든다
        minX, maxX, minY, maxY = self.nextShape.getBoundingOffsets(0)
        result = False
        if self.tryMoveCurrent(0, 5, -minY):
            self.currentX = 5
            self.currentY = -minY
            self.currentDirection = 0
            self.currentShape = self.nextShape
            self.nextShape = Shape(random.randint(1, 7)) #랜덤 모듈을 이용해 다음 도형 생성
            result = True
        else:
            self.currentShape = Shape()
            self.currentX = -1
            self.currentY = -1
            self.currentDirection = 0
            result = False
            BoardData.flag = False

        self.shapeStat[self.currentShape.shape] += 1
        return result

    def tryMoveCurrent(self, direction, x, y): #현재 이동 위치
        return self.tryMove(self.currentShape, direction, x, y)

    def tryMove(self, shape, direction, x, y): #이동 관련 함수
        for x, y in shape.getCoords(direction, x, y):
            if x >= BoardData.width or x < 0 or y >= BoardData.height or y < 0: #게임 보드를 벗어나면 이동할 수 없다
                return False
            if self.backBoard[x + y * BoardData.width] > 0: #게임 보드를 벗어나면 이동할 수 없다
                return False
        return True

    def moveDown(self): #도형이 내려갈 수 있게 도와주는 함수
        lines = 0
        if self.tryMoveCurrent(self.currentDirection, self.currentX, self.currentY + 1): #현재 위치에 y좌표를 1씩 더한다.
            self.currentY += 1
        else:
            self.mergePiece()
            lines = self.removeFullLines()
            self.createNewPiece()
        return lines

    def dropDown(self): #한번에 보드의 밑줄까지 내려갈 수 있게 도와주는 함수
        while self.tryMoveCurrent(self.currentDirection, self.currentX, self.currentY + 1):
            self.currentY += 1
        self.mergePiece()
        lines = self.removeFullLines()
        self.createNewPiece()
        return lines

    def moveLeft(self): #왼쪽으로 이동할 수 있도록 도와주는 함수
        if self.tryMoveCurrent(self.currentDirection, self.currentX - 1, self.currentY):
            self.currentX -= 1

    def moveRight(self): #오른쪽으로 이동할 수 있도록 도와주는 함수
        if self.tryMoveCurrent(self.currentDirection, self.currentX + 1, self.currentY):
            self.currentX += 1

    def rotateRight(self): #오른쪽으로 회전
        if self.tryMoveCurrent((self.currentDirection + 1) % 4, self.currentX, self.currentY):
            self.currentDirection += 1
            self.currentDirection %= 4

    def rotateLeft(self): #왼쪽으로 회전
        if self.tryMoveCurrent((self.currentDirection - 1) % 4, self.currentX, self.currentY):
            self.currentDirection -= 1
            self.currentDirection %= 4

    def removeFullLines(self): #한 줄이 다차면 그 줄을 지운다
        newBackBoard = [0] * BoardData.width * BoardData.height
        newY = BoardData.height - 1
        lines = 0
        for y in range(BoardData.height - 1, -1, -1):
            blockCount = sum([1 if self.backBoard[x + y * BoardData.width] > 0 else 0 for x in range(BoardData.width)])
            if blockCount < BoardData.width:
                for x in range(BoardData.width):
                    newBackBoard[x + newY * BoardData.width] = self.backBoard[x + y * BoardData.width]
                newY -= 1
            else:
                lines += 1
        if lines > 0:
            self.backBoard = newBackBoard
        return lines

    def mergePiece(self): #떨어진 조각을 합친다
        for x, y in self.currentShape.getCoords(self.currentDirection, self.currentX, self.currentY):
            self.backBoard[x + y * BoardData.width] = self.currentShape.shape

        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()

    def clear(self): #보드 정리
        self.currentX = -1
        self.currentY = -1
        self.currentDirection = 0
        self.currentShape = Shape()
        self.backBoard = [0] * BoardData.width * BoardData.height

BOARD_DATA1 = BoardData()
BOARD_DATA2 = BoardData()
