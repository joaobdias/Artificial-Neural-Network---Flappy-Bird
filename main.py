# Importação das bibliotecas
import pygame
import os
import random
import neat
import visualizeNEAT
import pickle as pk

os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

# Variáveis globais
screenWidth = 500
screenHeight = 800
fontSize = 50
fontSize2 = 16
fontSize3 = 32
generation = 0
trainning = True
ambientHard = True

# Salvar o melhor genoma para posterior utilização
file = open('BestWinnerEasy.pkl', 'rb')  # Abre arquivo
genomeWin = pk.load(file)  # Carrega o arquivo na varável local
file.close()  # Fecha o arquivo

# Importação dos arquivos de imagem dos elementos do jogo
imgPipe = pygame.transform.scale2x(pygame.image.load(
    os.path.join('imgs', 'pipe.png')))
imgGround = pygame.transform.scale2x(pygame.image.load(
    os.path.join('imgs', 'base.png')))
imgBackground = pygame.transform.scale2x(pygame.image.load(
    os.path.join('imgs', 'bg.png')))
imgBird = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird3.png')))]
imgExplosion = [pygame.image.load(os.path.join('imgs', 'explosion1.png')),
                pygame.image.load(os.path.join('imgs', 'explosion2.png')),
                pygame.image.load(os.path.join('imgs', 'explosion3.png')),
                pygame.image.load(os.path.join('imgs', 'explosion4.png')),
                pygame.image.load(os.path.join('imgs', 'explosion5.png')),
                pygame.image.load(os.path.join('imgs', 'explosion6.png'))]

# Determinação das fontes
pygame.font.init()

# Definir a fonte e o tamanho da letra
fontFlappy = pygame.font.Font(os.path.join('fonts', '04B_19__.ttf'), fontSize)
fontBack = pygame.font.Font(os.path.join('fonts', '04B_19O.otf'), fontSize)

fontFlappy2 = pygame.font.Font(
    os.path.join('fonts', '04B_19__.ttf'), fontSize2)
fontBack2 = pygame.font.Font(os.path.join('fonts', '04B_19O.otf'), fontSize2)

fontFlappy3 = pygame.font.Font(
    os.path.join('fonts', '04B_19__.ttf'), fontSize3)
fontBack3 = pygame.font.Font(os.path.join('fonts', '04B_19O.otf'), fontSize3)


class Bird:

    bird = imgBird
    maxRotation = 25
    speedRotation = 15
    maxAngle = -45

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = random.randrange(50, 450)
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.imgCount = 0
        self.img = self.bird[0]

    # Função de pulo
    def jump(self):

        self.speed = -10.5
        self.time = 0
        self.height = self.y  # Grava a posição inicial do pulo

    # Fução de movimento (gravidade)
    def move(self):

        self.time += 1
        # S = s0 + v0t + (at^2)/2
        deslocamento = 1.5 * (self.time**2) + self.speed * self.time
        # Exemplo, no frame que pula: 1.5 * 1 - 10.5 * 1 = -9
        # No proximo frame, o speed diminui, movendo menos para cima e positivando o deslocamento e começando a cair

        if deslocamento >= 16:
            deslocamento = 16  # Limita a "gravidade" (cartesiano invertido)
        elif deslocamento <= 0:
            deslocamento -= 2  # Acrescenta um pouco no pulo

        self.y += deslocamento

        # Obtenção dos valores do angulo
        if deslocamento < 0 or self.y < (self.height + 50):
            if self.angle < self.maxRotation:
                self.angle = self.maxRotation
        else:
            if self.angle > self.maxAngle:
                self.angle -= self.speedRotation

    def draw(self, screen):

        self.imgCount = (self.imgCount + 1) % 3
        self.img = self.bird[self.imgCount]

        if self.angle <= self.maxAngle:
            self.img = self.bird[1]

        rotateImg = pygame.transform.rotate(self.img, self.angle)
        centerImg = self.img.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotateImg.get_rect(center=centerImg)

        screen.blit(rotateImg, rectangle.topleft)

    # Define a máscara do agente
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Explosion:

    explosion = imgExplosion

    def __init__(self, x, y):

        self.explosionCount = 0
        self.img = self.explosion[0]
        self.cont = 0
        self.x = x
        self.y = y

    def draw(self, tela):

        self.explosionCount = (self.explosionCount + 1) % 6
        self.img = self.explosion[self.explosionCount]
        self.cont += 1

        if self.cont >= 5:
            self.cont = 5

        tela.blit(self.img, (self.x-20, self.y-48))


class Pipe:

    distancePipes = 200

    def __init__(self, x):
        self.x = x
        self.cont = 0
        self.height = random.randrange(50, 450)

        if ambientHard:
            self.aux = random.randrange(1, 5)
            self.speed = random.randrange(5, 8)
            self.type = random.randrange(1, 5)
        else:
            self.speed = 5
            self.type = 1

        self.heightBase = self.height
        self.positionTop = 0
        self.positionBase = 0
        self.topPipe = pygame.transform.flip(imgPipe, False, True)
        self.basePipe = imgPipe
        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.positionTop = self.height - self.topPipe.get_height()
        self.positionBase = self.height + self.distancePipes

    def move(self):

        # Movimento no eixo vertical
        if self.type > 1:
            if self.heightBase < 200:
                self.height += self.aux
                self.setHeight()
                self.cont += 1
                if self.cont >= 32:
                    self.aux *= -1
                    self.cont = 0
            else:
                self.height -= self.aux
                self.setHeight()
                self.cont += 1
                if self.cont >= 32:
                    self.aux *= -1
                    self.cont = 0

        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.topPipe, (self.x, self.positionTop))
        screen.blit(self.basePipe, (self.x, self.positionBase))

    # Verificar colisão com o pássaro
    def colision(self, bird):
        birdMask = bird.get_mask()
        maskTop = pygame.mask.from_surface(self.topPipe)
        maskBase = pygame.mask.from_surface(self.basePipe)

        topDistance = (self.x - bird.x,
                       self.positionTop - round(bird.y))
        baseDistance = (self.x - bird.x,
                        self.positionBase - round(bird.y))

        top = birdMask.overlap(maskTop, topDistance)
        base = birdMask.overlap(maskBase, baseDistance)

        if base or top:
            return True
        else:
            return False


class Ground:
    speed = 5
    groundWidth = imgGround.get_width()
    img = imgGround

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.groundWidth

    # Movimentação do chão
    def move(self):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 + self.groundWidth < 0:
            self.x1 = self.x2 + self.groundWidth
        if self.x2 + self.groundWidth < 0:
            self.x2 = self.x1 + self.groundWidth

    def draw(self, tela):
        tela.blit(self.img, (self.x1, self.y))
        tela.blit(self.img, (self.x2, self.y))


def drawScreen(screen, birds, pipes, ground, rate, gen, explosions, info, genomes, fit):

    screen.blit(imgBackground, (0, 0))

    # Desenho dos elementos
    for bird in birds:
        bird.draw(screen)

    for pipe in pipes:
        pipe.draw(screen)

    ground.draw(screen)

    # Textos em tela e entradas da RNA
    if info:
        for bird in birds:
            pygame.draw.line(screen, (0, 0, 0), (bird.x+52,
                                                 bird.y+25), (pipe.x+52, pipe.height), 10)
            pygame.draw.line(screen, (255, 255, 255), (bird.x+52,
                                                       bird.y+25), (pipe.x+52, pipe.height), 4)

            pygame.draw.line(screen, (0, 0, 0), (bird.x+52,
                                                 bird.y+25), (pipe.x+56, pipe.positionBase), 10)
            pygame.draw.line(screen, (255, 255, 255), (bird.x+52,
                                                       bird.y+25), (pipe.x+56, pipe.positionBase), 4)

            textHeightFront = fontFlappy2.render(
                f"{bird.y}", 1, (255, 255, 255))
            textHeighBack = fontBack2.render(f"{bird.y}", 1, (0, 0, 0))

            textGen = fontFlappy.render(f"Gen: {gen}", 1, (255, 255, 255))
            textPop = fontFlappy.render(
                f"Pop: {len(birds)}", 1, (255, 255, 255))

            textGenBack = fontBack.render(f"Gen: {gen}", 1, (0, 0, 0))
            textPopBack = fontBack.render(f"Pop: {len(birds)}", 1, (0, 0, 0))

            screen.blit(textHeightFront, (bird.x+16, bird.y-24))
            screen.blit(textHeighBack, (bird.x+16, bird.y-24))
            screen.blit(textGen, (30, screenHeight-60))
            screen.blit(textGenBack, (27, screenHeight-60))
            screen.blit(textPop, (screenWidth/2+30, screenHeight-60))
            screen.blit(textPopBack, (screenWidth/2+27, screenHeight-60))

        for i, bird in enumerate(birds):

            if round(genomes[i].fitness, 2) > fit:
                fit = round(genomes[i].fitness, 2)

        textHeightFront = fontFlappy3.render(f"Fit: {fit}", 1, (255, 255, 255))
        textHeighBack = fontBack3.render(f"Fit: {fit}", 1, (0, 0, 0))
        screen.blit(textHeightFront, (screenWidth/2-50, 72))
        screen.blit(textHeighBack, (screenWidth/2-52, 72))

    for explosion in explosions:
        explosion.draw(screen)

    # Pontuação
    textRate = fontFlappy.render(f"{rate}", 1, (255, 255, 255))
    textRateBack = fontBack.render(f"{rate}", 1, (0, 0, 0))

    screen.blit(textRate, (screenWidth/2-8, 20))
    screen.blit(textRateBack, (screenWidth/2-11, 20))

    pygame.display.update()


def main(genomes, config):

    # Janela
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    frames = pygame.time.Clock()

    # Variaveis
    global generation
    global trainning
    running = True
    if trainning:
        info = True
    else:
        info = False
    fit = 0
    generation += 1
    rate = 0
    ground = Ground(730)

    # Listas
    listNetworks = []
    listGenomes = []
    listBirds = []
    listExplosions = []
    listPipes = [Pipe(700)]

    # Criação das listas com valor padrão(redes, genomas e pássaros)
    for _, genome in genomes:
        if not trainning:
            rna = neat.nn.FeedForwardNetwork.create(genomeWin, config)
        else:
            rna = neat.nn.FeedForwardNetwork.create(genome, config)
        listNetworks.append(rna)
        genome.fitness = 0
        listGenomes.append(genome)
        listBirds.append(Bird(230, 350))

    while running:

        # FPS do jogo
        frames.tick(24)

        # Teclas de atalho
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if info:
                    info = False
                else:
                    info = True

        # Variavel para determinar o cano atual
        indPipe = 0

        # Movimentação do chão
        ground.move()

        # Controle dos canos
        addPipe = False
        removePipes = []

        # Troca o cano atual para o próximo, considerando o x do pássaro
        if len(listBirds) > 0:
            if len(listPipes) > 1 and listBirds[0].x > (listPipes[0].x + listPipes[0].topPipe.get_width()):
                indPipe = 1
        # Se não há pássaros, reseta
        else:
            running = False
            break

        # Movimentação dos pássaros (incluindo pulo com base na rede)
        for i, bird in enumerate(listBirds):
            bird.move()
            listGenomes[i].fitness += 0.1
            output = listNetworks[i].activate((bird.y,
                                               abs(bird.y -
                                                   listPipes[indPipe].height),
                                               abs(bird.y - listPipes[indPipe].positionBase)))

            # Pula ou não de acordo com a saída da rede (de cada pássaro)
            if output[0] > 0.5:
                bird.jump()

        # Controle das explosões no jogo
        for i, explosion in enumerate(listExplosions):
            if explosion.cont >= 5:
                listExplosions.pop(i)

        # Verifica colisão do pássaro com os canos
        for pipe in listPipes:

            # Caso haja colisão, remove os elementos das listas e diminui fitness do pássaro
            for i, bird in enumerate(listBirds):
                if pipe.colision(bird):
                    listGenomes[i].fitness -= 1
                    listExplosions.append(Explosion(bird.x, bird.y))
                    listBirds.pop(i)
                    listGenomes.pop(i)
                    listNetworks.pop(i)

                # Controle dos canos
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    addPipe = True

            # Movimento dos canos
            pipe.move()

            # Se o cano passou da tela, é inserido na lista para remoção
            if pipe.x + pipe.topPipe.get_width() < 0:
                removePipes.append(pipe)

        # Controle de pontuação (fitness incluso)
        if addPipe:
            rate += 1
            listPipes.append(Pipe(600))
            for genome in listGenomes:
                genome.fitness += 5

        # Remoção dos canos do jogo com base na lista
        for pipe in removePipes:
            listPipes.remove(pipe)

        # Verificação da colisão com o chão e teto
        for i, bird in enumerate(listBirds):

            if bird.y < 0 or (bird.y + bird.img.get_height()) > ground.y:
                listGenomes[i].fitness -= 5
                listExplosions.append(Explosion(bird.x, bird.y))
                listBirds.pop(i)
                listGenomes.pop(i)
                listNetworks.pop(i)

        # Chama a função de desenho na tela (chamado de acordo com os frames por segundo)
        drawScreen(screen, listBirds, listPipes, ground,
                   rate, generation, listExplosions, info, listGenomes, fit)


def runConfig(local):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, local)
    pop = neat.Population(config)

    if trainning:

        pop.run(main, 20)
        best = pop.best_genome
        visualizeNEAT.draw_net(config, best, True)
        pop.add_reporter(neat.StdOutReporter(True))
        print('\nBest Genome:\n', best)

        # Salvar o melhor genoma para posterior utilização
        file = open('best.pkl', 'wb')  # Abre arquivo
        pk.dump(best, file)  # Salva neste arquivo
        file.close()  # Fecha o arquivo

    else:
        pop.run(main, 1)


if __name__ == '__main__':
    localConfig = os.path.join(os.path.dirname(__file__), 'config.txt')
    runConfig(localConfig)
