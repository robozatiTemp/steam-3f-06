import gym, pygame
from gym import error, spaces, utils
from gym.utils import seeding
from pygame.locals import *
import numpy as np

class MlSteamEnv001(gym.Env):
	metadata = {'render.modes': ['human']}

	def transformar_reward_em_float(self, x):
		if x >= 0:
			return (float(x) / 5) #10
		else:
			return 0.0
	
	def __init__(self):
		self.lastComando = 10
		self.numDeRodadasParadas = 0
		self.numeroIteracao = 0

		self.numBlueParados = 0
		self.numGreenParados = 0
		self.numRedParados = 0

		#Lista de carros azuis
		self.blueList = [[20,31],[20,32],[20,33],[20,34],[20,35]]
		self.blueDirectionList = ["Cima", "Cima", "Cima", "Cima", "Cima"]

		#Lista de carros verdes
		self.greenList = [[9,10],[8,10],[7,10],[6,10],[5,10]]
		self.greenDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

		#Lista de carros vermelhos
		self.redList = [[9,30],[8,30],[7,30],[6,30],[5,30]]
		self.redDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

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

		#Lista dos semaforos
		self.trafficLightsList = [[10,10],[20,10],[30,10],[10,20],[20,20],[30,20],[10,30],[20,30],[30,30]]
		self.trafficLightsState = [1, 0, 0, 0, 0, 1, 1, 0, 0] #0: O (passa vertical), 1: X (passa horizontal)

		#Lista dos quadrados das ruas
		self.streetList = self.FazerListaDasRuas()

		# 0 a 9
		self.action_space = spaces.Discrete(10)

		#espaco de observacao
		high = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
		low = np.array([-1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
		self.observation_space = spaces.Box(low, high, dtype=np.int8)

		self.screen = None

	def step(self, action):
		reward = 15
		comando = int(round(action, 0))
		if comando != 0:
			if self.trafficLightsState[comando-1] == 0:
				self.trafficLightsState[comando-1] = 1
			else:
				self.trafficLightsState[comando-1] = 0

		if self.lastComando != 0 and comando == self.lastComando:
			reward -= 5
		self.lastComando = comando

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
				self.blueList, self.greenList, self.redList) == False:
				self.CarroMoverParaFrente(i, self.blueList, self.blueDirectionList[i])
				#reward += 1
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
				self.blueList, self.greenList, self.redList) == False:
				self.CarroMoverParaFrente(i, self.greenList, self.greenDirectionList[i])
				#reward += 1
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
				self.blueList, self.greenList, self.redList) == False:
				self.CarroMoverParaFrente(i, self.redList, self.redDirectionList[i])
				#reward += 1
			else:
				tempNumDeCarrosParados += 1
				tempNumRedParados += 1
				reward -= 1
			
			i += 1
		
		if len(self.redList) == 0:
			estadoDeFinalizacao += 1

		if tempNumDeCarrosParados == 15:
			self.numDeRodadasParadas += 1
		else:
			self.numDeRodadasParadas = 0

		if tempNumBlueParados >= 1:
			self.numBlueParados += 1
		else:
			self.numBlueParados = 0
		
		if tempNumGreenParados >= 1:
			self.numGreenParados += 1
		else:
			self.numGreenParados = 0
		
		if tempNumRedParados >= 1:
			self.numRedParados += 1
		else:
			self.numRedParados = 0

		self.numeroIteracao += 1	
		ob = self.RetornarArray(self.blueList, self.greenList, self.redList, self.trafficLightsState, self.trafficLightsList)
		episode_over = False
		if estadoDeFinalizacao == 3 or self.numeroIteracao > 499 or self.numDeRodadasParadas >= 5:
			episode_over = True
		if self.numBlueParados >= 14 or self.numGreenParados >= 14 or self.numRedParados >= 14:
			episode_over = True
		
		return ob, self.transformar_reward_em_float(reward), episode_over, {}

	
	def reset(self):
		self.lastComando = 10
		self.numDeRodadasParadas = 0
		self.numeroIteracao = 0

		self.numBlueParados = 0
		self.numGreenParados = 0
		self.numRedParados = 0

		#Lista de carros azuis
		self.blueList = [[20,31],[20,32],[20,33],[20,34],[20,35]]
		self.blueDirectionList = ["Cima", "Cima", "Cima", "Cima", "Cima"]

		#Lista de carros verdes
		self.greenList = [[9,10],[8,10],[7,10],[6,10],[5,10]]
		self.greenDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

		#Lista de carros vermelhos
		self.redList = [[9,30],[8,30],[7,30],[6,30],[5,30]]
		self.redDirectionList = ["Direita", "Direita", "Direita", "Direita", "Direita"]

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

		#Lista dos semaforos
		self.trafficLightsList = [[10,10],[20,10],[30,10],[10,20],[20,20],[30,20],[10,30],[20,30],[30,30]]
		self.trafficLightsState = [1, 0, 0, 0, 0, 1, 1, 0, 0] #0: O (passa vertical), 1: X (passa horizontal)

		#Lista dos quadrados das ruas
		self.streetList = self.FazerListaDasRuas()

		return self.RetornarArray(self.blueList, self.greenList, self.redList, self.trafficLightsState, self.trafficLightsList)

	def b_render(self): #mode='human'):
		if self.screen is None:
			pygame.init();
			self.screen=pygame.display.set_mode((800, 800));
			pygame.display.set_caption('PySteamTest001');

		blueimage = pygame.Surface((20,20));
		blueimage.fill((0, 0, 255));
		greenimage = pygame.Surface((20,20));
		greenimage.fill((0, 255, 0));
		redimage = pygame.Surface((20, 20));
		redimage.fill((255, 0, 0));
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

		for num in range(len(self.trafficLightsList)):
			if self.trafficLightsState[num] == 0:
				self.screen.blit(yellowimage, (self.trafficLightsList[num][0]*20, self.trafficLightsList[num][1]*20))
			else:
				self.screen.blit(orangeimage, (self.trafficLightsList[num][0]*20, self.trafficLightsList[num][1]*20))

		#state_array = self.RetornarArray(self.blueList, self.greenList, self.redList, self.trafficLightsState)
		#t=f.render(str(numeroIteracao), True, (255, 255, 255));
		#st=f.render(str(state_array), True, (255, 255, 255));
		#screen.blit(t, (10, 10));
		#screen.blit(st, (10, 40));

		pygame.display.update()
		clock.tick(30)
		#return None

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

	def MacroCarroVerSeTemAlgoAFrente(self, x, y, direction, tempTrafficLightsList, tempTrafficLightsState, blueList, greenList, redList):
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

	def RetornarArray(self, blueList, greenList, redList, trafficLightsState, trafficLightsList):
		array = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		for i in range(len(blueList)):
			x = blueList[i][0]
			y = blueList[i][1]
			for num in range(len(trafficLightsList)):
				xs = trafficLightsList[num][0]
				ys = trafficLightsList[num][1]
				if y == ys and x + 1 == xs:
					array[num] = 1
				elif y == ys and x - 1 == xs:
					array[num] = 1
				elif x == xs and y + 1 == ys:
					array[num] = -1
				elif x == xs and y - 1 == ys:
					array[num] = -1

		for i in range(len(greenList)):
			x = greenList[i][0]
			y = greenList[i][1]
			for num in range(len(trafficLightsList)):
				xs = trafficLightsList[num][0]
				ys = trafficLightsList[num][1]
				if y == ys and x + 1 == xs:
					array[num] = 1
				elif y == ys and x - 1 == xs:
					array[num] = 1
				elif x == xs and y + 1 == ys:
					array[num] = -1
				elif x == xs and y - 1 == ys:
					array[num] = -1

		for i in range(len(redList)):
			x = redList[i][0]
			y = redList[i][1]
			for num in range(len(trafficLightsList)):
				xs = trafficLightsList[num][0]
				ys = trafficLightsList[num][1]
				if y == ys and x + 1 == xs:
					array[num] = 1
				elif y == ys and x - 1 == xs:
					array[num] = 1
				elif x == xs and y + 1 == ys:
					array[num] = -1
				elif x == xs and y - 1 == ys:
					array[num] = -1

		for i in range(len(trafficLightsState)):
			array.append(trafficLightsState[i])

		return array
	
	#endregion
