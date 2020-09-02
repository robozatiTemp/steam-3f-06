import gym, pygame, random
from gym import error, spaces, utils
from gym.utils import seeding
from pygame.locals import *
import numpy as np

class MlSteamEnv002(gym.Env):

	def transformar_reward_em_float(self, x):
		if x >= 0:
			return (float(x) / 10)
		else:
			return 0.0
	
	def __init__(self):
		#self.lastComando = 10
		self.numDeRodadasParadas = 0
		self.numeroIteracao = 0

		self.numBlueParados = 0
		self.numGreenParados = 0
		self.numRedParados = 0
		self.numPinkParados = 0

		#Lista de carros azuis
		self.blueList = [[20,31],[20,32],[20,33],[20,34],[20,35]]
		self.blueDirectionList = ["Cima", "Cima", "Cima", "Cima", "Cima"]

		#Lista de carros verdes
		self.greenList = [[9,10],[8,10],[7,10],[6,10],[5,10]]
		self.greenDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

		#Lista de carros vermelhos
		self.redList = [[9,30],[8,30],[7,30],[6,30],[5,30]]
		self.redDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

		#Lista de carros rosas
		self.pinkList = [[10,9],[10,8],[10,7],[10,6],[10,5]]
		self.pinkDirectionList = ["Baixo", "Baixo", "Baixo", "Baixo", "Baixo"]

		#Lista de pontos de virada azul
		self.blueTurningPoints = [[20,10]]
		self.blueTurningPointsDic = {"[20, 10]":"Direita"}
		self.blueEndingPoint = [40,10]

		#Lista de pontos de virada verde
		self.greenTurningPoints = [[10,10],[10,20]]
		self.greenTurningPointsDic = {"[10, 10]":"Baixo", "[10, 20]":"Direita"}
		self.greenEndingPoint = [40,20]

		#Lista de pontos de virada vermelho
		self.redTurningPoints = [[30,30]]
		self.redTurningPointsDic = {"[30, 30]":"Cima"}
		self.redEndingPoint = [30,0]

		#Lista de pontos de virada rosa
		self.pinkTurningPoints = [[10,30]]
		self.pinkTurningPointsDic = {"[10, 30]":"Direita"}
		self.pinkEndingPoint = [40,30]

		#Lista dos semaforos
		self.trafficLightsList = [[10,10],[20,10],[30,10],[10,20],[20,20],[30,20],[10,30],[20,30],[30,30]]
		self.trafficLightsState = [1, 0, 0, 0, 0, 1, 1, 0, 0] #0: O (passa vertical), 1: X (passa horizontal)

		#Lista dos quadrados das ruas
		self.streetList = self.FazerListaDasRuas()

		# 0 a 9
		self.action_space = spaces.Discrete(10)

		#espaco de observacao
		highTemp = []
		lowTemp = []
		for i in range(240):
			if i < 231:
				highTemp.append(4)
				lowTemp.append(0)
			else:
				highTemp.append(1)
				lowTemp.append(0)
			
		high = np.array(highTemp)
		low = np.array(lowTemp)
		self.observation_space = spaces.Box(low, high, dtype=np.int8)

		self.screen = None

	def step(self, action):
		reward = 0
		for i in range(len(self.blueList)):
			reward += 1
		for i in range(len(self.greenList)):
			reward += 1
		for i in range(len(self.redList)):
			reward += 1
		for i in range(len(self.pinkList)):
			reward += 1
		
		comando = int(round(action, 0))
		if comando != 0:
			if self.trafficLightsState[comando-1] == 0:
				self.trafficLightsState[comando-1] = 1
			else:
				self.trafficLightsState[comando-1] = 0

		#if self.lastComando != 0 and comando == self.lastComando:
			#reward -= 5
		#self.lastComando = comando

		i = 0
		tempNumDeCarrosParados = 0
		estadoDeFinalizacao = 0 #3 quer dizer q RGB acabaram
		tempNumBlueParados = 0
		while i < len(self.blueList):
			x = self.blueList[i][0]
			y = self.blueList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, self.blueEndingPoint) == True:
				del self.blueList[i]
				del self.blueDirectionList[i]
				reward += 3
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, self.blueDirectionList, self.blueTurningPoints, self.blueTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, self.blueDirectionList[i], self.trafficLightsList, self.trafficLightsState, 
				self.blueList, self.greenList, self.redList, self.pinkList) == False:
				self.CarroMoverParaFrente(i, self.blueList, self.blueDirectionList[i])
			else:
				tempNumDeCarrosParados += 1
				tempNumBlueParados += 1
				reward -= 1
			
			i += 1
		
		if len(self.blueList) == 0:
			estadoDeFinalizacao += 1

		i = 0
		tempNumGreenParados = 0
		while i < len(self.greenList):
			x = self.greenList[i][0]
			y = self.greenList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, self.greenEndingPoint) == True:
				del self.greenList[i]
				del self.greenDirectionList[i]
				reward += 3
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, self.greenDirectionList, self.greenTurningPoints, self.greenTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, self.greenDirectionList[i], self.trafficLightsList, self.trafficLightsState, 
				self.blueList, self.greenList, self.redList, self.pinkList) == False:
				self.CarroMoverParaFrente(i, self.greenList, self.greenDirectionList[i])
			else:
				tempNumDeCarrosParados += 1
				tempNumGreenParados += 1
				reward -= 1
			
			i += 1
		
		if len(self.greenList) == 0:
			estadoDeFinalizacao += 1

		i = 0
		tempNumRedParados = 0
		while i < len(self.redList):
			x = self.redList[i][0]
			y = self.redList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, self.redEndingPoint) == True:
				del self.redList[i]
				del self.redDirectionList[i]
				reward += 3
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, self.redDirectionList, self.redTurningPoints, self.redTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, self.redDirectionList[i], self.trafficLightsList, self.trafficLightsState, 
				self.blueList, self.greenList, self.redList, self.pinkList) == False:
				self.CarroMoverParaFrente(i, self.redList, self.redDirectionList[i])
			else:
				tempNumDeCarrosParados += 1
				tempNumRedParados += 1
				reward -= 1
			
			i += 1
		
		if len(self.redList) == 0:
			estadoDeFinalizacao += 1

		
		i = 0
		tempNumPinkParados = 0
		while i < len(self.pinkList):
			x = self.pinkList[i][0]
			y = self.pinkList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, self.pinkEndingPoint) == True:
				del self.pinkList[i]
				del self.pinkDirectionList[i]
				reward += 3
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, self.pinkDirectionList, self.pinkTurningPoints, self.pinkTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, self.pinkDirectionList[i], self.trafficLightsList, self.trafficLightsState, 
				self.blueList, self.greenList, self.redList, self.pinkList) == False:
				self.CarroMoverParaFrente(i, self.pinkList, self.pinkDirectionList[i])
			else:
				tempNumDeCarrosParados += 1
				tempNumPinkParados += 1
				reward -= 1
			
			i += 1
		
		if len(self.pinkList) == 0:
			estadoDeFinalizacao += 1
		

		self.ColocarCarroNovo(self.blueList, self.greenList, self.redList, self.pinkList,
			self.blueDirectionList, self.redDirectionList, self.greenDirectionList, self.pinkDirectionList)


		if tempNumDeCarrosParados > 70:
			self.numDeRodadasParadas += 1
		else:
			self.numDeRodadasParadas = 0

		if tempNumBlueParados >= 8:
			self.numBlueParados += 1
		else:
			self.numBlueParados = 0
		
		if tempNumGreenParados >= 8:
			self.numGreenParados += 1
		else:
			self.numGreenParados = 0
		
		if tempNumRedParados >= 8:
			self.numRedParados += 1
		else:
			self.numRedParados = 0
		
		if tempNumPinkParados >= 8:
			self.numPinkParados += 1
		else:
			self.numPinkParados = 0

		self.numeroIteracao += 1	
		ob = self.RetornarArray(self.blueList, self.greenList, self.redList, self.pinkList,self.trafficLightsState, self.trafficLightsList)
		episode_over = False
		if self.numeroIteracao > 999 or self.numDeRodadasParadas >= 50:
			episode_over = True
		if self.numBlueParados >= 60 or self.numGreenParados >= 60 or self.numRedParados >= 60 or self.numPinkParados >= 60: #14
			episode_over = True
		
		return ob, self.transformar_reward_em_float(reward), episode_over, {}

	def reset(self):
		#self.lastComando = 10
		self.numDeRodadasParadas = 0
		self.numeroIteracao = 0

		self.numBlueParados = 0
		self.numGreenParados = 0
		self.numRedParados = 0
		self.numPinkParados = 0

		#Lista de carros azuis
		self.blueList = [[20,31],[20,32],[20,33],[20,34],[20,35]]
		self.blueDirectionList = ["Cima", "Cima", "Cima", "Cima", "Cima"]

		#Lista de carros verdes
		self.greenList = [[9,10],[8,10],[7,10],[6,10],[5,10]]
		self.greenDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

		#Lista de carros vermelhos
		self.redList = [[9,30],[8,30],[7,30],[6,30],[5,30]]
		self.redDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

		#Lista de carros rosas
		self.pinkList = [[10,9],[10,8],[10,7],[10,6],[10,5]]
		self.pinkDirectionList = ["Baixo", "Baixo", "Baixo", "Baixo", "Baixo"]

		#Lista de pontos de virada azul
		self.blueTurningPoints = [[20,10]]
		self.blueTurningPointsDic = {"[20, 10]":"Direita"}
		self.blueEndingPoint = [40,10]

		#Lista de pontos de virada verde
		self.greenTurningPoints = [[10,10],[10,20]]
		self.greenTurningPointsDic = {"[10, 10]":"Baixo", "[10, 20]":"Direita"}
		self.greenEndingPoint = [40,20]

		#Lista de pontos de virada vermelho
		self.redTurningPoints = [[30,30]]
		self.redTurningPointsDic = {"[30, 30]":"Cima"}
		self.redEndingPoint = [30,0]

		#Lista de pontos de virada rosa
		self.pinkTurningPoints = [[10,30]]
		self.pinkTurningPointsDic = {"[10, 30]":"Direita"}
		self.pinkEndingPoint = [40,30]

		#Lista dos semaforos
		self.trafficLightsList = [[10,10],[20,10],[30,10],[10,20],[20,20],[30,20],[10,30],[20,30],[30,30]]
		self.trafficLightsState = [1, 0, 0, 0, 0, 1, 1, 0, 0] #0: O (passa vertical), 1: X (passa horizontal)

		#Lista dos quadrados das ruas
		self.streetList = self.FazerListaDasRuas()

		return self.RetornarArray(self.blueList, self.greenList, self.redList, self.pinkList, self.trafficLightsState, self.trafficLightsList)
	
	def b_render(self): #mode='human'):
		if self.screen is None:
			pygame.init();
			self.screen=pygame.display.set_mode((800, 800));
			pygame.display.set_caption('PySteamTest002');

		blueimage = pygame.Surface((20,20));
		blueimage.fill((0, 0, 255));
		greenimage = pygame.Surface((20,20));
		greenimage.fill((0, 255, 0));
		redimage = pygame.Surface((20, 20));
		redimage.fill((255, 0, 0));
		pinkimage = pygame.Surface((20,20));
		pinkimage.fill((199, 21, 133));
		yellowimage = pygame.Surface((20,20));
		yellowimage.fill((255, 255, 0));
		orangeimage = pygame.Surface((20,20));
		orangeimage.fill((255, 165, 0));
		greyimage = pygame.Surface((20,20));
		greyimage.fill((128, 128, 128));
		f = pygame.font.SysFont('Arial', 20);
		clock = pygame.time.Clock()

		self.screen.fill((0,0,0))

		for i in range(len(self.streetList)):
			self.screen.blit(greyimage, (self.streetList[i][0]*20, self.streetList[i][1]*20))

		for i in range(len(self.blueList)):
			self.screen.blit(blueimage, (self.blueList[i][0]*20, self.blueList[i][1]*20))
		for i in range(len(self.greenList)):
			self.screen.blit(greenimage, (self.greenList[i][0]*20, self.greenList[i][1]*20))
		for i in range(len(self.redList)):
			self.screen.blit(redimage, (self.redList[i][0]*20, self.redList[i][1]*20))
		for i in range(len(self.pinkList)):
			self.screen.blit(pinkimage, (self.pinkList[i][0]*20, self.pinkList[i][1]*20))

		for num in range(len(self.trafficLightsList)):
			if self.trafficLightsState[num] == 0:
				self.screen.blit(yellowimage, (self.trafficLightsList[num][0]*20, self.trafficLightsList[num][1]*20))
			else:
				self.screen.blit(orangeimage, (self.trafficLightsList[num][0]*20, self.trafficLightsList[num][1]*20))

		pygame.display.update()
		clock.tick(30)
	
	def c_render(self): #mode='human'):
		if self.screen is None:
			pygame.init();
			self.screen=pygame.display.set_mode((400, 400));
			pygame.display.set_caption('PySteamTest002');

		blueimage = pygame.Surface((10,10));
		blueimage.fill((0, 0, 255));
		greenimage = pygame.Surface((10,10));
		greenimage.fill((0, 255, 0));
		redimage = pygame.Surface((10, 10));
		redimage.fill((255, 0, 0));
		pinkimage = pygame.Surface((10,10));
		pinkimage.fill((199, 21, 133));
		yellowimage = pygame.Surface((10,10));
		yellowimage.fill((255, 255, 0));
		orangeimage = pygame.Surface((10,10));
		orangeimage.fill((255, 165, 0));
		greyimage = pygame.Surface((10,10));
		greyimage.fill((128, 128, 128));
		f = pygame.font.SysFont('Arial', 20);
		clock = pygame.time.Clock()

		self.screen.fill((0,0,0))

		for i in range(len(self.streetList)):
			self.screen.blit(greyimage, (self.streetList[i][0]*10, self.streetList[i][1]*10))

		for i in range(len(self.blueList)):
			self.screen.blit(blueimage, (self.blueList[i][0]*10, self.blueList[i][1]*10))
		for i in range(len(self.greenList)):
			self.screen.blit(greenimage, (self.greenList[i][0]*10, self.greenList[i][1]*10))
		for i in range(len(self.redList)):
			self.screen.blit(redimage, (self.redList[i][0]*10, self.redList[i][1]*10))
		for i in range(len(self.pinkList)):
			self.screen.blit(pinkimage, (self.pinkList[i][0]*10, self.pinkList[i][1]*10))

		for num in range(len(self.trafficLightsList)):
			if self.trafficLightsState[num] == 0:
				self.screen.blit(yellowimage, (self.trafficLightsList[num][0]*10, self.trafficLightsList[num][1]*10))
			else:
				self.screen.blit(orangeimage, (self.trafficLightsList[num][0]*10, self.trafficLightsList[num][1]*10))

		pygame.display.update()
		clock.tick(30)

	def close(self):
		pygame.quit()

	#region defFunctionSelf

	def CarroVerSeTemSemaforoAFrente(self, x, y, direction, tempTrafficLightsList, tempTrafficLightsState):
		for num in range(len(tempTrafficLightsList)):
			xs = tempTrafficLightsList[num][0]
			ys = tempTrafficLightsList[num][1]
			if self.ChecarColisaoAFrente(x, y, xs, ys, direction) == True:
				if direction == "Direita" and tempTrafficLightsState[num] != 0:
					return True
				elif direction == "Esquerda" and tempTrafficLightsState[num] != 0:
					return True
				elif direction == "Cima" and tempTrafficLightsState[num] != 1:
					return True
				elif direction == "Baixo" and tempTrafficLightsState[num] != 1:
					return True
		
		return False

	def ChecarColisaoAFrente(self, x1, y1, x2, y2, direction):
		if direction == "Cima":
			if x1 == x2 and y1 - 1 == y2:
				return True
			else:
				return False

		elif direction == "Baixo":
			if x1 == x2 and y1 + 1 == y2:
				return True
			else:
				return False

		elif direction == "Direita":
			if x1 + 1 == x2 and y1 == y2:
				return True
			else:
				return False

		elif direction == "Esquerda":
			if x1 - 1 == x2 and y1 == y2:
				return True
			else:
				return False

	def MacroCarroVerSeTemAlgoAFrente(self, x, y, direction, tempTrafficLightsList, tempTrafficLightsState, blueList, greenList, redList, pinkList):
		if self.CarroVerSeTemSemaforoAFrente(x, y, direction, tempTrafficLightsList, tempTrafficLightsState) == True:
			return True

		for num in range(len(blueList)):
			x2 = blueList[num][0]
			y2 = blueList[num][1]
			if self.ChecarColisaoAFrente(x, y, x2, y2, direction) == True:
				return True

		for num in range(len(greenList)):
			x2 = greenList[num][0]
			y2 = greenList[num][1]
			if self.ChecarColisaoAFrente(x, y, x2, y2, direction) == True:
				return True

		for num in range(len(redList)):
			x2 = redList[num][0]
			y2 = redList[num][1]
			if self.ChecarColisaoAFrente(x, y, x2, y2, direction) == True:
				return True

		for num in range(len(pinkList)):
			x2 = pinkList[num][0]
			y2 = pinkList[num][1]
			if self.ChecarColisaoAFrente(x, y, x2, y2, direction) == True:
				return True

		return False

	def ChecarPontoDeViradaAFrenteEVirar(self, x, y, i, directionList, turningPoints, turningPointsDic):
		direction = directionList[i]

		for num in range(len(turningPoints)):
			xp = turningPoints[num][0]
			yp = turningPoints[num][1]
			if x == xp and y == yp:
				directionTemp = turningPointsDic[str(turningPoints[num])]
				directionList[i] = directionTemp
				return

	def CarroMoverParaFrente(self, i, colorList, direction):
		x = colorList[i][0]
		y = colorList[i][1]

		if direction == "Cima":
			colorList[i][1] = y - 1

		elif direction == "Baixo":
			colorList[i][1] = y + 1

		elif direction == "Direita":
			colorList[i][0] = x + 1

		elif direction == "Esquerda":
			colorList[i][0] = x - 1

		return

	def ChecarSeChegouAoFim(self, x, y, i, endingPoint):
		if x == endingPoint[0] and y == endingPoint[1]:
			return True
		else:
			return False
	
	'''
	def MacroIteracaoCarros(self, blueList, greenList, redList, pinkList, blueDirectionList, greenDirectionList, redDirectionList, 
		pinkDirectionList, blueTurningPoints, blueTurningPointsDic, blueEndingPoint, greenTurningPoints, greenTurningPointsDic,
		greenEndingPoint,redTurningPoints, redTurningPointsDic, redEndingPoint, pinkTurningPoints, pinkTurningPointsDic, pinkEndingPoint,
		trafficLightsList, trafficLightsState):
		
		i = 0
		while i < len(blueList):
			x = blueList[i][0]
			y = blueList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, blueEndingPoint) == True:
				del blueList[i]
				del blueDirectionList[i]
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, blueDirectionList, blueTurningPoints, blueTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, blueDirectionList[i], trafficLightsList, trafficLightsState, 
				blueList, greenList, redList, pinkList) == False:
				self.CarroMoverParaFrente(i, blueList, blueDirectionList[i])
			i += 1

		i = 0
		while i < len(greenList):
			x = greenList[i][0]
			y = greenList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, greenEndingPoint) == True:
				del greenList[i]
				del greenDirectionList[i]
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, greenDirectionList, greenTurningPoints, greenTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, greenDirectionList[i], trafficLightsList, trafficLightsState, 
				blueList, greenList, redList, pinkList) == False:
				self.CarroMoverParaFrente(i, greenList, greenDirectionList[i])
			i += 1

		i = 0
		while i < len(redList):
			x = redList[i][0]
			y = redList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, redEndingPoint) == True:
				del redList[i]
				del redDirectionList[i]
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, redDirectionList, redTurningPoints, redTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, redDirectionList[i], trafficLightsList, trafficLightsState, 
				blueList, greenList, redList, pinkList) == False:
				self.CarroMoverParaFrente(i, redList, redDirectionList[i])
			i += 1

		i = 0
		while i < len(pinkList):
			x = pinkList[i][0]
			y = pinkList[i][1]

			if self.ChecarSeChegouAoFim(x, y, i, pinkEndingPoint) == True:
				del pinkList[i]
				del pinkDirectionList[i]
				continue

			self.ChecarPontoDeViradaAFrenteEVirar(x, y, i, pinkDirectionList, pinkTurningPoints, pinkTurningPointsDic)

			if self.MacroCarroVerSeTemAlgoAFrente(x, y, pinkDirectionList[i], trafficLightsList, trafficLightsState, 
				blueList, greenList, redList, pinkList) == False:
				self.CarroMoverParaFrente(i, pinkList, pinkDirectionList[i])
			i += 1
	'''

	def FazerListaDasRuas(self):
		streetList = []
		for x in range(40):
			streetList.append([x, 10])
			streetList.append([x, 20])
			streetList.append([x, 30])

		for y in range(40):
			if y != 10 and y != 20 and y != 30:
				streetList.append([10, y])
				streetList.append([20, y])
				streetList.append([30, y])

		return streetList

	def RetornarArray(self, blueList, greenList, redList, pinkList, trafficLightsState, trafficLightsList):
		array = []
		for i in range(231):
			array.append(0)

		for i in range(len(blueList)):
			x = blueList[i][0]
			y = blueList[i][1]
			if y == 10:
				array[x] = 1
			elif y == 20:
				array[x+40] = 1
			elif y == 30:
				array[x+80] = 1
			elif x == 10:
				array[y+120] = 1
			elif x == 20:
				array[y+157] = 1
			elif x == 30:
				array[y+194] = 1

		for i in range(len(greenList)):
			x = greenList[i][0]
			y = greenList[i][1]
			if y == 10:
				array[x] = 2
			elif y == 20:
				array[x+40] = 2
			elif y == 30:
				array[x+80] = 2
			elif x == 10:
				array[y+120] = 2
			elif x == 20:
				array[y+157] = 2
			elif x == 30:
				array[y+194] = 2

		for i in range(len(redList)):
			x = redList[i][0]
			y = redList[i][1]
			if y == 10:
				array[x] = 3
			elif y == 20:
				array[x+40] = 3
			elif y == 30:
				array[x+80] = 3
			elif x == 10:
				array[y+120] = 3
			elif x == 20:
				array[y+157] = 3
			elif x == 30:
				array[y+194] = 3

		for i in range(len(pinkList)):
			x = pinkList[i][0]
			y = pinkList[i][1]
			if y == 10:
				array[x] = 4
			elif y == 20:
				array[x+40] = 4
			elif y == 30:
				array[x+80] = 4
			elif x == 10:
				array[y+120] = 4
			elif x == 20:
				array[y+157] = 4
			elif x == 30:
				array[y+194] = 4

		for i in range(len(trafficLightsState)):
			array.append(trafficLightsState[i])

		return array

	def ColocarCarroNovo(self, blueList, greenList, redList, pinkList, blueDirectionList, redDirectionList, greenDirectionList, pinkDirectionList):
		numeroDeCarros = random.randint(0, 3)
		qualSeraAListaAntigos = []
		qualSeraALista = 0

		if numeroDeCarros != 0:
			qualSeraALista = random.randint(0, 3) #0: azul, 1: verde, 2: vermelho, 3: rosa
			if qualSeraALista == 0:
				if blueList[-1] != [20,40]:
					blueList.append([20,40])
					blueDirectionList.append("Cima")
					qualSeraAListaAntigos.append(0)
			elif qualSeraALista == 1:
				if greenList[-1] != [0,10]:
					greenList.append([0,10])
					greenDirectionList.append("Direita")
					qualSeraAListaAntigos.append(1)
			elif qualSeraALista == 2:
				if redList[-1] != [0,30]:
					redList.append([0,30])
					redDirectionList.append("Direita")
					qualSeraAListaAntigos.append(2)
			else:
				if pinkList[-1] != [10,0]:
					pinkList.append([10,0])
					pinkDirectionList.append("Baixo")
					qualSeraAListaAntigos.append(3)

			numeroDeCarros -= 1

		while numeroDeCarros != 0:
			qualSeraALista = random.randint(0, 3)

			for i in range(len(qualSeraAListaAntigos)):
				if qualSeraAListaAntigos[i] == qualSeraALista:
					continue

			if qualSeraALista == 0:
				if blueList[-1] != [20,40]:
					blueList.append([20,40])
					blueDirectionList.append("Cima")
					qualSeraAListaAntigos.append(0)
			elif qualSeraALista == 1:
				if greenList[-1] != [0,10]:
					greenList.append([0,10])
					greenDirectionList.append("Direita")
					qualSeraAListaAntigos.append(1)
			elif qualSeraALista == 2:
				if redList[-1] != [0,30]:
					redList.append([0,30])
					redDirectionList.append("Direita")
					qualSeraAListaAntigos.append(2)
			else:
				if pinkList[-1] != [10,0]:
					pinkList.append([10,0])
					pinkDirectionList.append("Baixo")
					qualSeraAListaAntigos.append(3)

			numeroDeCarros -= 1
	
	#endregion