from kivy.config import Config

Config.set('graphics', 'height', '700')
Config.set('graphics', 'width', '1024')
Config.write()

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, StringProperty, BooleanProperty, DictProperty, BoundedNumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader,TabbedPanelStrip
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.graphics import Color,Rectangle
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.core.image import Image as CImage
from kivy.animation import Animation

import time
import random

class WSprite(Widget):
    pos = ListProperty()
    def __init__(self,tex, **kwargs):
        super(WSprite, self).__init__(**kwargs)
        self.tex = tex
        self.rect = Rectangle(texture = self.tex,
                              size = self.size,
                              pos = self.pos)
        with self.canvas:
            self.rect
    
    def on_pos(self, instance, value):
        print 'moved'
                   
class AGSprite(Image):
    player = BooleanProperty(False)
    solid = BooleanProperty(False)
    enemy = BooleanProperty(False)
    town = BooleanProperty(False)
    boundary = BooleanProperty(False)
    
    def __init__(self, size=(64,64),**kwargs):
        super(AGSprite, self).__init__(**kwargs)
        self.size_hint=(None,None)
        self.size = size
        self.allow_stretch = True
    
    def on_start(self):
        print 'i started' 
           
class AGBoundary(AGSprite):
    boundary = BooleanProperty(True)
    opacity = NumericProperty(0)
    solid = BooleanProperty(True)
    
    def __init__(self,**kwargs):
        super(AGSprite, self).__init__(**kwargs)
        
class AGScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(AGScreenManager, self).__init__(**kwargs)
        self.intro = IntroScreen(name='intro')
        self.add_widget(self.intro)
        
        self.world = WorldScreen(name='world')
        self.add_widget(self.world)
        
        self.town = TownScreen(name='town')
        self.add_widget(self.town)
        
        self.transition=WipeTransition()
        
    def endIntro(self):
        self.current = 'world'
    
    def moveField(self, direction):
        pass
        
class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs) 
        self.build()
    
    def build(self):
        
        txt = ("""\
        Long ago, in a little town called Sheepville,
        lived a young peasant boy, not a girl, he longed
        to serve the king as a knight, but being a peasant, he could not.
        However, in the fateful town of Sheepville,
        while the boy was farming his wheat he spotted a tall, hairy beast!
        The town had been overrun by an ogre horde. 
        Many fled their homes, yet only few survived. 
        The king and princess had been captured!
        Now it's up to you to save the royal family,
        and gain the knighthood you always dreamed of!
        """)
        box = BoxLayout(orientation = 'horizontal')
        lbl = Label(text=txt, color=(0,0,0,1), font_size='18sp',
                    font_name='resources/fonts/LibreBaskerville-Regular.ttf')
        img = Image(source = 'resources/icons/japan1.png', size_hint=(0.5,1))
        btn = Button(text='start the adventure', on_release=self.endIntro,
                     center_x=350, font_size='18sp', size_hint=(.3,0.1))
        
        box.add_widget(img)
        box.add_widget(lbl)
        self.add_widget(btn)
        self.add_widget(box)
        
        with self.canvas.before:
            Color(1,1,1,1, mode='rgba')
            Rectangle(source ='', pos=(0,0), size=(1000,600))
        
    def endIntro(self, value):
        self.parent.endIntro()
        
class WorldScreen(Screen):
    move = NumericProperty(32)
    spriteList = ListProperty()
    player = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(WorldScreen, self).__init__(**kwargs)
        
        field = self.buildField()
        self.buildPlayer()
        bg = self.loadBackground()
        self.buildBackground(field, bg)
        sprites = self.loadSprites()
        #self.buildSprites(sprites)
        
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.movePlayer(keycode[1])
        return True
        
    def movePlayer(self, direction):
        #print 'moving field'
        y = self.player.y
        x = self.player.x
        
        if direction == 'up':
            y += self.move
        elif direction == 'down':
            y -= self.move
        elif direction == 'left':
            x -= self.move
        elif direction == 'right':
            x += self.move
        
        self.changePlayerImage(direction)
        speed = 0.3
        anim = Animation(x=x, y=y, d=speed)
        anim.bind(on_start=self.startPlayerAnim, on_complete=self.stopPlayerAnim)
        
        anim.start(self.player)
        self.checkCollision(direction) 
           
    def changePlayerImage(self, direction):
        if direction == 'up':
            self.player.source = 'resources/assets/Clyde_up.zip'
        elif direction == 'down':
            self.player.source = 'resources/assets/Clyde_down.zip'
        elif direction == 'left':
            self.player.source = 'resources/assets/Clyde_left.zip'
        elif direction == 'right':
            self.player.source = 'resources/assets/Clyde_right.zip'
            
    def startPlayerAnim(self, instance, value):
        self.player.anim_delay=.1
    
    def stopPlayerAnim(self, instance, value):
        self.player.anim_delay=-1
             
    def on_transition_state(self, instance, value):    
        sound = SoundLoader.load('resources/sound/overworld.wav')
        if value == 'in':
            if sound:
                print("Sound found at %s" % sound.source)
                print("Sound is %.3f seconds" % sound.length)
                sound.loop = True
                sound.play()
        else:
            sound.stop()
    
    def on_touch_down(self, value):
        print('value.pos: {} value.spos: {}'.format(value.pos, value.spos))
    
    def loadBackground(self):
        bg = CImage.load('resources/bg/grass_field1.png', keep_data=True).texture
        return bg
    
    def buildBackground(self, field, bg):
        with field.canvas.before:
            Rectangle(texture = bg, pos=(0,0), size=(640,640))
            
    def buildField(self):
        self.field = RelativeLayout()
        self.add_widget(self.field)
        
        return self.field
        
    def buildPlayer(self):
        self.player = AGSprite(source = 'resources/assets/Clyde_down.zip', size=(30,30), center=(513,257))
        self.player.anim_delay=-1
        self.field.add_widget(self.player)   
    
    def loadSprites(self):
        bush1 = 'resources/assets/qubodup-bush_0.png'    
        cat = 'resources/assets/giphy.gif'
        town = 'resources/icons/buddhist.png'
        
        sprites = dict(bush1 = bush1,
                       cat = cat,
                       town = town
                       )
        return sprites
       
    def buildSprites(self, sprites):
        
        block = AGSprite(solid=True, size=(32,32), source=sprites['bush1'], center = (512,512))
        town1 = AGSprite(town = True, size=(96,96), source=sprites['town'], center = (256,512))
        self.field.add_widget(block)
        self.field.add_widget(town1)
        self.spriteList.append(block)
        self.spriteList.append(town1)
    
    def checkCollision(self, direction):
        for child in self.spriteList:
            if self.player.collide_widget(child):
                print 'collision!'
                self.didCollision(direction, child)
        
    def didCollision(self, direction, child):
        print 'collided with {} at {}'.format(child,child.pos)
        if child.solid:
            self.solidCollision(direction)
        elif child.town:
            self.enterTown()
    
    def solidCollision(self, direction):
        # reverse direction
        txt = 'you cannot go that way, the way is blocked'
        self.parent.parent.updateInfoScreen(txt) # callback to Manager
        
        if direction == 'up':
            self.movePlayer('down')
        elif direction == 'down':
            self.movePlayer('up')
        elif direction == 'left':
            self.movePlayer('right')
        elif direction == 'right':
            self.movePlayer('left')
    
    def enterTown(self):
        print 'town discovered' 
        txt = 'entering the town...'
        self.parent.parent.updateInfoScreen(txt)
        self.parent.current = 'town'
          
class TownScreen(Screen):
    def __init__(self, **kwargs):
        super(TownScreen, self).__init__(**kwargs)
        self.build()
        
    def build(self):
        box = BoxLayout()
        lbl = Label(text='town screen!')
        box.add_widget(lbl)
        self.add_widget(box)
        
class Manager(BoxLayout):
    
    initialLocation = dict(x = 0, y = 0)
    location = DictProperty(initialLocation)
    direction = StringProperty('north')
    playerHealth = NumericProperty(100)
    playerEnergy = NumericProperty(30)
    enemyHealth = NumericProperty(0)
    infoScreenText = StringProperty('adventure awaits!\n')
    encounter = BooleanProperty(False)
    exhausted = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        
        self.buildUI()
        self.orientation = 'vertical'
        self.padding = '5sp'
    
    def on_encounterLocations(self, instance, value):
        print value
        
    def on_direction(self, instance, value):
        txt = value
        self.lblDirection.text = "compass: {}".format(txt)
    
    def on_location(self, instance, value):
        x,y = value['x'], value['y']
        txt = "x: {}, y: {}".format(x, y)
        self.lblLocation.text = txt
    
    def on_infoScreenText(self, instance, value):
        self.infoScreen.text = self.infoScreenText
        
    def playerAttack(self, value):
        if self.encounter:
            damage = random.randrange(6)
            txt = 'you did {} damage to the enemy'.format(damage)
            self.updateInfoScreen(txt)
            self.enemyHealth -= damage
            
            if self.enemyHealth > 0:
                time.sleep(0.1)
                self.enemyAttack()
            
        elif not self.encounter:
            txt = 'there is nothing to attack, calm yourself'
            self.updateInfoScreen(txt)
    
    def enemyAttack(self):
        damage = damage = random.randrange(4)
        txt = 'the enemy hit you for {} damage'.format(damage)
        self.updateInfoScreen(txt)
        self.playerHealth -= damage
    
    def on_enemyHealth(self, instance, value):
        if value < 1:
            self.enemyDeath()
            
    def on_playerHealth(self, instance, value):
        if value < 1:
            self.playerDeath()
        else:
            pass
        
        self.lblHealth.text = str(self.playerHealth)
    
    def on_playerEnergy(self, instance, value):
        if value < 1:
            value = 0
            txt = 'you are exhausted'
            self.updateInfoScreen(txt)
            self.exhausted = True
        else:
            self.exhausted = False
                
    def playerDeath(self):
        self.lblHealth.text = str(0)
        txt = 'you have died, that is unfortunate'
        self.updateInfoScreen(txt)
        
    def enemyDeath(self):
        txt = 'you killed them, huzzah!'  
        self.updateInfoScreen(txt)
        self.encounter = False
    
    def eventCompleted(self):
        pass
        
    def update(self, dt):
        #self.infoScreen.text = self.infoScreenText
        pass
        
    def updateInfoScreen(self, txt): 
        self.infoScreenText += "\n{}".format(txt)
        
    def movePlayer(self, value):
        if self.encounter:
            txt = 'you cannot move while the enemy is near!'
            self.updateInfoScreen(txt)
            time.sleep(.1)
            
        elif self.exhausted:
            txt = 'you are exhausted, you cannot move'
            self.updateInfoScreen(txt)
        
        else:
            self.screen.movePlayer(value.text)
            if value.text == 'move forward': self.location['y'] += 1
            elif value.text == 'move backward': self.location['y'] -= 1
            elif value.text == 'move right': self.location['x'] += 1
            elif value.text == 'move left': self.location['x'] -= 1
    
    def on_encounter(self, instance, value):
        if value:
            txt = 'enemy encounter!'
            self.updateInfoScreen(txt)
            self.enemyHealth = 20
        else:
            pass
    def clickToggleBoundaries(self, value):
        self.screen.toggleBoundaries()
        
    def buildUI(self):
        self.containerTopBar = BoxLayout(padding = '5sp', size_hint=(1,0.5))
        self.containerInfo = BoxLayout(padding = '5sp')
        self.containerBottomBar = BoxLayout(padding='5sp', size_hint=(1,0.75))
        self.screen = AGScreenManager(size=(1024,512), size_hint=(None,None))
        
        #top
        self.lblHealth = Button(text=str(self.playerHealth))
        self.lblEnergy = Button(text=str(self.playerEnergy))
        self.lblLocation = Button(text="x: 0, y: 0")
        self.lblDirection = Button(text="compass: north")
        #middle
        self.infoScreen = TextInput(text=self.infoScreenText, multiline=True, readonly=True)
        #bottom
        btnForward = Button(text='move forward', on_release = self.movePlayer)
        btnBack = Button(text='move backward', on_release = self.movePlayer)
        btnLeft = Button(text='move left', on_release = self.movePlayer)
        btnRight = Button(text='move right', on_release = self.movePlayer)
        btnBodies = Button(text='boundaries', background_color=(0,0,.8,1),on_release = self.clickToggleBoundaries)
        btnEscape = Button(text='escape', background_color=(.3,0,0,1))
        
        self.containerTopBar.add_widget(self.lblHealth)
        self.containerTopBar.add_widget(self.lblEnergy)
        self.containerTopBar.add_widget(self.lblLocation)
        self.containerTopBar.add_widget(self.lblDirection)
        
        self.containerInfo.add_widget(self.infoScreen)
        
        self.containerBottomBar.add_widget(btnLeft)
        self.containerBottomBar.add_widget(btnForward)
        self.containerBottomBar.add_widget(btnBack)
        self.containerBottomBar.add_widget(btnRight)
        self.containerBottomBar.add_widget(btnBodies)
        self.containerBottomBar.add_widget(btnEscape)
        
        self.add_widget(self.containerTopBar)
        self.add_widget(self.screen)
        self.add_widget(self.containerInfo)
        self.add_widget(self.containerBottomBar)
        
class GameApp(App):
    
    def build(self):
        return Manager()

if __name__ == "__main__":
    GameApp().run()


'''
Created on Sep 17, 2014

@author: Odysseus
'''