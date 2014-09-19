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

import time
import random

class AGSprite(Image):
    player = BooleanProperty(False)
    solid = BooleanProperty(False)
    enemy = BooleanProperty(False)
    town = BooleanProperty(False)
    
    def __init__(self, size=(32,32),**kwargs):
        super(AGSprite, self).__init__(**kwargs)
        self.size_hint=(None,None)
        self.size = size

class AGScreenManager(ScreenManager):
    def __init__(self, manager, **kwargs):
        super(AGScreenManager, self).__init__(**kwargs)
        self.manager = manager
        self.intro = IntroScreen(mother = self, name='intro')
        self.add_widget(self.intro)
        
        self.world = WorldScreen(mother = self, name='world')
        self.add_widget(self.world)
        
        self.town = TownScreen(mother = self, name='town')
        self.add_widget(self.town)
        
        self.transition=WipeTransition()
        
    def endIntro(self, value):
        self.current = 'world'
    
    def moveField(self, direction):
        self.world.moveField(direction)
    
class IntroScreen(Screen):
    def __init__(self, mother, **kwargs):
        super(IntroScreen, self).__init__(**kwargs) 
        self.mother = mother
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
        btn = Button(text='start the adventure', on_release=self.mother.endIntro,
                     center_x=350, font_size='18sp', size_hint=(.3,0.1))
        
        box.add_widget(img)
        box.add_widget(lbl)
        self.add_widget(btn)
        self.add_widget(box)
        
        with self.canvas.before:
            Color(1,1,1,1, mode='rgba')
            Rectangle(source ='', pos=(0,0), size=(1000,600))
        
class WorldScreen(Screen):
    
    def __init__(self, mother, **kwargs):
        super(WorldScreen, self).__init__(**kwargs)
        self.mother = mother
        self.buildSprites()
            
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
      
    def buildSprites(self):
        self.field = RelativeLayout()
        with self.field.canvas.before:
            Rectangle(source ='resources/tiles/LightWorld-LostWoods.png', pos=(0,0), size=(2048,2048))
        '''
        for n in range(0,1000, 50):
            tree = AGSprite(solid=True, source='resources/icons/bamboo2.png', center=(n,0))
            self.field.add_widget(tree)
            tree = AGSprite(solid=True, source='resources/icons/bamboo2.png', center=(n,1000))
            self.field.add_widget(tree)
            tree = AGSprite(solid=True, source='resources/icons/bamboo2.png', center=(0,n))
            self.field.add_widget(tree)
            tree = AGSprite(solid=True, source='resources/icons/bamboo2.png', center=(1000,n))
            self.field.add_widget(tree)
        '''
        self.player = AGSprite(player = True, source = 'resources/icons/bunnyfront1.png', center=(500,250))
        
        self.field.add_widget(self.player)
        self.add_widget(self.field)
        #self.add_widget(grid)
    
    def moveField(self, direction):
        print 'move called'
        if direction == 'move forward':
            self.field.y -= 32
        elif direction == 'move backward':
            self.field.y += 32
        elif direction == 'move left':
            self.field.x += 32
        elif direction == 'move right':
            self.field.x -= 32

    def bkup_moveField(self, direction):
        print 'move called'
        for child in self.field.children:
            if not child.player:
                if direction == 'move forward':
                    child.y -= 32
                elif direction == 'move backward':
                    child.y += 32
                elif direction == 'move left':
                    child.x += 32
                elif direction == 'move right':
                    child.x -= 32
                self.checkCollision(direction, child)
    
    def checkCollision(self, direction, child):
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
        for child in self.field.children:
            if not child.player:
                if direction == 'move forward':
                    child.y += 32
                elif direction == 'move backward':
                    child.y -= 32
                elif direction == 'move left':
                    child.x -= 32
                elif direction == 'move right':
                    child.x += 32 
    
    def enterTown(self):
        print 'town discovered' 
        txt = 'entering the town...'
        self.parent.parent.updateInfoScreen(txt)
          
class TownScreen(Screen):
    def __init__(self, mother, **kwargs):
        super(TownScreen, self).__init__(**kwargs)
        self.mother = mother
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
        self.spacing = '5sp'
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        #Clock.schedule_interval(self.update, 1)
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':
            self.player1.center_y += 10
        elif keycode[1] == 's':
            self.player1.center_y -= 10
        elif keycode[1] == 'up':
            self.player2.center_y += 10
        elif keycode[1] == 'down':
            self.player2.center_y -= 10
        return True
    
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
            self.screen.moveField(value.text)
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
        
    def buildUI(self):
        self.containerTopBar = BoxLayout(padding = '5sp', size_hint=(1,0.5))
        self.containerInfo = BoxLayout(padding = '5sp')
        self.containerBottomBar = BoxLayout(padding='5sp', size_hint=(1,0.75))
        self.screen = AGScreenManager(self, size=(1024,512), size_hint=(None,None))
        
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
        btnAttack = Button(text='attack', background_color=(0,0,.8,1),on_release = self.playerAttack)
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
        self.containerBottomBar.add_widget(btnAttack)
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