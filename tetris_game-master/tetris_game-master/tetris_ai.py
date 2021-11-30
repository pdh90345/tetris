#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tetris_model import BOARD_DATA1, Shape
import math
from datetime import datetime
import numpy as np


class TetrisAI(object):
    lines = 0

    def nextMove(self): #블럭의 움직임을 분석, 반복학습하는 함수
        t1 = datetime.now() #현재 시간
        if BOARD_DATA1.currentShape == Shape.shapeNone: #현재 블럭이 없으면
            return None #값이 "없음"

        currentDirection = BOARD_DATA1.currentDirection #블럭의 현재 위치
        currentY = BOARD_DATA1.currentY #블럭의 현재 y위치
        _, _, minY, _ = BOARD_DATA1.nextShape.getBoundingOffsets(0) #블럭의 모양 기본으로 지정

        # print("=======")
        strategy = None #값이 존재하지 않는 변수 생성
        if BOARD_DATA1.currentShape.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS): #현재 블럭의 모양이 I, Z, S 이면
            d0Range = (0, 1) #d0Range(:tuple)에 0과 1을 저장
        elif BOARD_DATA1.currentShape.shape == Shape.shapeO: #현재 블럭의 모양이 O 이면
            d0Range = (0,) #d0Range에 0을 저장
        else: #현재 블럭의 모양이 J, L, T 이면
            d0Range = (0, 1, 2, 3) #d0Range에 0, 1, 2, 3을 저장

        if BOARD_DATA1.nextShape.shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS): #현재 블럭의 모양이 I, Z, S 이면
            d1Range = (0, 1) #d1Range(:tuple)에 0과 1을 저장
        elif BOARD_DATA1.nextShape.shape == Shape.shapeO: #현재 블럭의 모양이 O 이면
            d1Range = (0,) #d1Range에 0을 저장
        else: #현재 블럭의 모양이 J, L, T 이면
            d1Range = (0, 1, 2, 3) #d1Range에 0, 1, 2, 3을 저장

        for d0 in d0Range: #doRange 값을 하나씩 빼서 반복문 실행
            minX, maxX, _, _ = BOARD_DATA1.currentShape.getBoundingOffsets(d0) #블럭의 기본 모양을 불러옴
            for x0 in range(-minX, BOARD_DATA1.width - maxX): #빈공간 값을 범위로 반복문 실행
                board = self.calcStep1Board(d0, x0) #calcStep1Board 함수 호출
                for d1 in d1Range: #d1Range 값을 하나씩 빼서 반복문 돌림
                    minX, maxX, _, _ = BOARD_DATA1.nextShape.getBoundingOffsets(d1)
                    dropDist = self.calcNextDropDist(board, d1, range(-minX, BOARD_DATA1.width - maxX)) #calcNextDropDist 함수 호출
                    for x1 in range(-minX, BOARD_DATA1.width - maxX): #빈공간 값을 범위로 반복문 실행
                        score = self.calculateScore(np.copy(board), d1, x1, dropDist) #calculateScore 함수 호출
                        if not strategy or strategy[2] < score:
                            strategy = (d0, x0, score)
        # print("===", datetime.now() - t1) #게임하는데 걸린 시간 출력
        return strategy #strategy(:tuple) 반환

    def calcNextDropDist(self, data, d0, xRange): #다음에 떨어질 거리를 측정하는 함수
        res = {} #res 딕셔너리 생성
        for x0 in xRange: #너비(width)값을 범위로 반복문 실행
            if x0 not in res: #x0가 딕셔너리에 있으면
                res[x0] = BOARD_DATA1.height - 1 #res의 키:xo에 값:현재 높이 -1을 저장
            for x, y in BOARD_DATA1.nextShape.getCoords(d0, x0, 0): #_model에 정의
                yy = 0
                while yy + y < BOARD_DATA1.height and (yy + y < 0 or data[(y + yy), x] == Shape.shapeNone):
                    yy += 1
                yy -= 1
                if yy < res[x0]:
                    res[x0] = yy #res의 키:xo에 값:yy을 저장
        return res #res(:dict) 반환

    def calcStep1Board(self, d0, x0): #보드 정보를 계산하는 함수
        board = np.array(BOARD_DATA1.getData()).reshape((BOARD_DATA1.height, BOARD_DATA1.width)) #(reshape: 높이값 행, 너비값 열)의 크기로 다차원배열 생성 후 저장
        self.dropDown(board, BOARD_DATA1.currentShape, d0, x0) #dropDown 함수 호출
        return board #board(:ndarray) 반환

    def dropDown(self, data, shape, direction, x0): #블럭을 떨어뜨리는 함수
        dy = BOARD_DATA1.height - 1 #블럭이 그려질 y위치에 현재 높이-1을 저장
        for x, y in shape.getCoords(direction, x0, 0): #_model에 정의
            yy = 0
            while yy + y < BOARD_DATA1.height and (yy + y < 0 or data[(y + yy), x] == Shape.shapeNone):
                yy += 1 #떨어지면 +1
            yy -= 1 
            if yy < dy:
                dy = yy
        # print("dropDown: shape {0}, direction {1}, x0 {2}, dy {3}".format(shape.shape, direction, x0, dy))
        self.dropDownByDist(data, shape, direction, x0, dy) #dropDownByDist 함수 호출, BOARD_DATA1, 블럭 모양, 블럭이 그려질 위치, x0, dy 

    def dropDownByDist(self, data, shape, direction, x0, dist): #블럭이 떨어지는 것을 계산하는 함수
        for x, y in shape.getCoords(direction, x0, 0): #_model에 정의
            data[y + dist, x] = shape.shape

    def calculateScore(self, step1Board, d1, x1, dropDist): #점수를 계산하여 반환하는 함수
        # print("calculateScore")
        t1 = datetime.now() #현재 시간
        width = BOARD_DATA1.width #tetris_model에서 불러온 너비 값을 저장
        height = BOARD_DATA1.height #tetris_model에서 불러온 높이 값을 저장

        self.dropDownByDist(step1Board, BOARD_DATA1.nextShape, d1, x1, dropDist[x1])
        # print(datetime.now() - t1)

        # Term 1: lines to be removed
        fullLines, nearFullLines = 0, 0
        roofY = [0] * width #쌓인 블럭들이 구성하는 줄의 높이(:list) y축 위치
        holeCandidates = [0] * width #구멍 후보(:list)
        holeConfirm = [0] * width #확인된 구멍(:list)
        vHoles, vBlocks = 0, 0
        for y in range(height - 1, -1, -1): #높이값을 반복문 돌림
            hasHole = False #구멍 유무를 구분하는 변수 값을 False로 저장, 구멍이 없음
            hasBlock = False #블럭 유무를 구분하는 변수 값을 False로 저장, 블럭이 없음
            for x in range(width): #너비을 반복문 돌림
                if step1Board[y, x] == Shape.shapeNone: #BOARD_DATA1에서 블럭이 없으면
                    hasHole = True #구멍이 있음
                    holeCandidates[x] += 1 #구멍 후보의 갯수 +1
                else: #BOARD_DATA1에서 블럭이 있으면
                    hasBlock = True #블럭이 있음
                    roofY[x] = height - y #전체 높이-y 값을 저장
                    if holeCandidates[x] > 0: #구멍 후보의 갯수가 양수라면
                        holeConfirm[x] += holeCandidates[x] #확인된 구멍 갯수에 구멍 후보 값을 더함
                        holeCandidates[x] = 0 #구멍 후보 값을 0으로 초기화
                    if holeConfirm[x] > 0: #확인된 구멍 갯수가 양수라면
                        vBlocks += 1 #
            if not hasBlock: #블럭이 있으면
                break #반복문 멈춤
            if not hasHole and hasBlock: #구멍이 없고 블럭이 있으면
                fullLines += 1 #완성된 줄 +1
        vHoles = sum([x ** .7 for x in holeConfirm]) #
        maxHeight = max(roofY) - fullLines #높이의 끝 = 쌓인 블럭들이 구성하는 줄의 높이 리스트의 최댓값 - 완성된 줄
        # print(datetime.now() - t1)

        roofDy = [roofY[i] - roofY[i+1] for i in range(len(roofY) - 1)] #roofDy(:list) 생성

        if len(roofY) <= 0: #쌓인 블럭들이 구성하는 줄의 높이 리스트의 길이가 0미만이면
            stdY = 0 #stdY(:literal)을 0으로 초기화
        else:
            stdY = math.sqrt(sum([y ** 2 for y in roofY]) / len(roofY) - (sum(roofY) / len(roofY)) ** 2) #제곱근
        if len(roofDy) <= 0: #roofDy의 길이가 0 이하이면
            stdDY = 0 #stdY(:literal)을 0으로 초기화
        else:
            stdDY = math.sqrt(sum([y ** 2 for y in roofDy]) / len(roofDy) - (sum(roofDy) / len(roofDy)) ** 2)

        absDy = sum([abs(x) for x in roofDy])
        maxDy = max(roofY) - min(roofY)
        # print(datetime.now() - t1)

        score = fullLines * 1.8 - vHoles * 1.0 - vBlocks * 0.5 - maxHeight ** 1.5 * 0.02 \
            - stdY * 0.0 - stdDY * 0.01 - absDy * 0.2 - maxDy * 0.3 #score 계산
        # print(score, fullLines, vHoles, vBlocks, maxHeight, stdY, stdDY, absDy, roofY, d0, x0, d1, x1)

        return score #score 반환


TETRIS_AI = TetrisAI()

