#Add Phidgets Library
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.DigitalInput import *

import pgzrun
from random import randint
import math

WIDTH = 800
HEIGHT = 600

DIFFICULTY = 1
player = Actor("player")
player.pos = (395, 550)
moveSequence = 0

def draw(): #main drawing function. displays the player ship, calls draw function for lasers, aliens, bases functions.
    screen.blit('background', (0, 0))
    player.image = player.images[math.floor(player.status/8)]
    player.draw()
    drawLasers()
    drawAliens()
    drawBases()
    screen.draw.text(str(score), topright = (780, 10), owidth = 0.5, ocolor = (255,255,255), color = (0,64,255), fontsize = 60)
    if (player.status >= 30):
        screen.draw.text("GAME OVER\nPress Enter to play again" , center=(400, 300), owidth=0.5, ocolor=(255,255,255), color=(255,64,0), fontsize=60)
    if (len(aliens) == 0) :
        screen.draw.text("YOU WON!\nPress Enter to play again" , center=(400, 300), owidth=0.5, ocolor=(255,255,255), color=(255,64,0) , fontsize=60)
        
def drawClipped(self): #controls the height of the base when hit
    screen.surface.blit(self._surf, (self.x-32, self.y-self.height+30), (0,0,64,self.height))

def drawAliens(): #imports aliens into aliens list
    for a in range(len(aliens)):
        aliens[a].draw()
        
def drawBases(): #imports bases into bases list
    for b in range (len(bases)):
        bases[b].drawClipped()
        
def drawLasers(): #imports lasers into lasers list
    for l in range (len(lasers)):
        lasers[l].draw()

def update(): #main updating function that controls the player, lasers, and aliens throughout the game.
    global moveCounter, player
    if (player.status < 30 and len(aliens) > 0):
        checkControls()
        updateLasers()
        moveCounter+=1
        if (moveCounter == moveDelay):
            moveCounter = 0
            updateAliens()
        if (player.status > 0):
            player.status +=1
    else:
        if (keyboard.RETURN):
            init()
            
def updateAliens(): #updates the behaviour of the aliens/movement throughout the game.
    global moveSequence, moveDelay, lasers
    movex = movey = 0
    if (moveSequence < 10 or moveSequence > 30):
        movex = -15
    if (moveSequence == 10 or moveSequence == 30):
        movey = 50 + (10 * DIFFICULTY)
        moveDelay -= 1
    if (moveSequence > 10 and moveSequence < 30):
        movex = 15
    for a in range(len(aliens)):
        animate(aliens[a], pos=(aliens[a].x + movex, aliens[a].y + movey), duration = 0.5, tween = 'linear')
        if (randint(0, 1) == 0):
            aliens[a].image = "alien1"
        else:
            aliens[a].image = "alien1b"
            if (randint(0, 5) == 0):
                lasers.append(Actor("laser1", (aliens[a].x, aliens[a].y)))
                lasers[len(lasers) - 1].status = 0
                lasers[len(lasers) - 1].type = 0
        if (aliens[a].y > 500 and player.status == 0):
            player.status = 1
    moveSequence+=1
    if (moveSequence == 40):
        moveSequence = 0

def updateLasers(): #updates laser speed/movement throughout the game
    global lasers, aliens
    for l in range(len(lasers)):
        if (lasers[l].type == 0):
            lasers[l].y += (2*DIFFICULTY)
            checkLaserHit(l)
            if (lasers[l].y > 600):
                lasers[l].status = 1
        if (lasers[l].type == 1):
            lasers[l].y -= 5
            checkPlayerLaserHit(l)
            if (lasers[l].y < 10):
                lasers[l].status = 1
    lasers = listCleanup(lasers)
    aliens = listCleanup(aliens)

def checkControls(): #Checks what direction the player wants the ship to move.
    global player
    if (horizontal.getVoltageRatio() < -0.2):
        if (player.x > 40):
            player.x-=5
    if (horizontal.getVoltageRatio() > 0.2):
        if (player.x < 760):
            player.x+=5
            
def checkBases(): #If the bases are too short/get hit too much, they will be deleted.
    for b in range(len(bases)):
        if (l < len(bases)):
            if (bases[b].height < 5):
                del bases[b]

def checkLaserHit(l): #Checks if alien laser collides with player or base.
    global player
    if (player.collidepoint((lasers[l].x, lasers[l].y))):#Changes status of player if it hits the player
        player.status = 1
        lasers[l].status = 1
    for b in range(len(bases)):
        if (bases[b].collideLaser(lasers[l])):#Lowers the base height if it hits the base
            bases[b].height -= 10
            lasers[l].status = 1

def checkPlayerLaserHit(l): #Checks if player laser reaches enemy or the base. If it hits an enemy, reward score.
    global score
    for b in range(len(bases)):
        if (bases[b].collideLaser(lasers[l])):
            lasers[l].status = 1
    for a in range(len(aliens)):
        if (aliens[a].collidepoint((lasers[l].x, lasers[l].y))):
            lasers[l].status = 1
            aliens[a].status = 1
            score+=1000
    
def collideLaser(self, other): #Returns true if the Laser collides with another entity
    return (
        self.x-20 < other.x+5 and
        self.y-self.height+30 < other.y and
        self.x+32 > other.x+5 and
        self.y-self.height+30 + self.height > other.y
        )
                
def listCleanup(l): #Removes entities throughout the game, creates new list with entities that need to remain. 
    newList = []
    for i in range (len(l)):
        if (l[i].status == 0):
            newList.append(l[i])
    return newList

def makeLaserActive(): #Activates player laser
    global player
    player.laserActive = 1

def initAliens(): #Initializes 3 rows of aliens, with 6 in each row. 
    global aliens
    aliens = []
    for a in range(18):
        aliens.append(Actor("alien1", ((210 + (a%6) * 80), (100 + (int(a/6) * 64)))))
        aliens[a].status = 0
    
def initBases(): #Initializes the bases/walls in the game
    global bases
    bases = []
    bc = 0
    for b in range(3):
        for p in range(3):
            bases.append(Actor("base1", midbottom = (150 + (b*200) + (p*40), 520)))
            bases[bc].drawClipped = drawClipped.__get__(bases[bc])
            bases[bc].collideLaser = collideLaser.__get__(bases[bc])
            bases[bc].height = 60
            bc+=1
            
def init(): #Initializes game variables
    global lasers, score, player, moveSequence, moveCounter, moveDelay
    initAliens()
    initBases()
    moveCounter = moveSequence = player.status = score = player.laserCountdown = 0
    lasers = []
    moveDelay = 30
    player.images = ["player", "explosion1", "explosion2", "explosion3"]
    player.laserActive = 1

#Phidgets Code Start
#Event
def onGreenButton_StateChange(self, state):
    global player, lasers
    if (state):
        if (player.laserActive == 1):
            player.laserActive = 0
            clock.schedule(makeLaserActive, 1.0)
            l = len(lasers)
            lasers.append(Actor("laser2", (player.x,player.y-32)))
            lasers[l].status = 0
            lasers[l].type = 1

#Create
greenButton = DigitalInput()
horizontal = VoltageRatioInput()

#Address
greenButton.setHubPort(5)
greenButton.setIsHubPortDevice(True)
horizontal.setChannel(1)

#Subscribe to Events
greenButton.setOnStateChangeHandler(onGreenButton_StateChange)

#Open
greenButton.openWaitForAttachment(1000)
horizontal.openWaitForAttachment(1000)

#Set data interval to minimum
horizontal.setDataInterval(horizontal.getMinDataInterval())


#Runs the program
init()
pgzrun.go()