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

import xml.etree.ElementTree as ET
import time
import random

class TileManager():
    '''take in XML sheet, and produce <map>, <tileSet>, and <layerTiles>
    '''
    def __init__(self, field, atlas):
        self.field = field
        self.source = ''
        self.sourceWidth = 0
        self.sourceHeight = 0
        self.tileHeight = 0
        self.tileWidth = 0
        self.firstgid = 0
        
        # layer width height == mapWidth mapHeight
        self.layer = '' 
        self.gid = 0
        self.tileSet = {}
        self.layerTiles = {}
        self.main(atlas)
        
        self.send(self.field, self.tileMap,self.tileSet,self.layerTiles)
            
    def main(self, atlas):
        tree = ET.parse(atlas)
        root = tree.getroot()
        
        self.mapWidth = int(root.attrib['width'])
        self.mapHeight = int(root.attrib["height"])
        self.mapTileWidth = int(root.attrib["tilewidth"])
        self.mapTileHeight = int(root.attrib["tileheight"])
        
        self.tileMap = dict(
                        mapWidth = self.mapWidth,
                        mapHeight = self.mapHeight,
                        mapTileWidth = self.mapTileWidth,
                        mapTileHeight = self.mapTileHeight
                        )
        
        for child in root:
            
            if child.tag == 'tileset':
                self.tileName = child.attrib['name']
                self.tileHeight = int(child.attrib['tileheight'])
                self.tileWidth = int(child.attrib['tilewidth'])
                self.firstgid = int(child.attrib['firstgid'])
                for image in child:
                    self.source = image.attrib['source']
                    self.sourceWidth = int(image.attrib['width'])
                    self.sourceHeight = int(image.attrib['height'])
                    y = self.sourceHeight/self.tileHeight
                    x = self.sourceWidth/self.tileWidth
                    self.lastgid = x * y + self.firstgid - 1
                    
                self.tileSet[self.firstgid] = dict(
                                                   source = "{}.png".format(self.tileName),
                                                   sourceWidth = self.sourceWidth,
                                                   sourceHeight = self.sourceHeight,
                                                   tileHeight = self.tileHeight,
                                                   tileWidth = self.tileWidth,
                                                   firstgid = self.firstgid,
                                                   lastgid = self.lastgid
                                                   )
            elif child.tag == 'layer':
                self.layer = child.attrib['name']
                self.layerTiles[self.layer] = [] # new list of tiles for each layer
                
                for index, tile in enumerate(child[0]): # skip <data> iter
                    gid = int(tile.attrib['gid'])
                    if gid > 0: # pass empty tiles
                        self.layerTiles[self.layer].append({index:gid})
                    else:
                        pass
                
    def send(self, field, tileMap, tileSet, layerTiles):
        print tileMap
        print tileSet
        print layerTiles
        BuildTiles(field, tileMap, tileSet, layerTiles)

class BuildTiles():
    def __init__(self, field, tileMap, tileSet, layerTiles):  
        self.field = field
        self.tileMap = tileMap
        self.tileSet = tileSet
        self.layerTiles = layerTiles
        self.loadTextures()
        self.prepareTile()
    
    def loadTextures(self):
        self.textures = {}
        for item in self.tileSet:
            texture_name = self.tileSet[item]['firstgid']
            texture_source = "resources/assets/{}".format(self.tileSet[item]['source'])
            self.textures[texture_name] = CImage.load(texture_source, keep_data = True).texture
            
    def prepareTile(self):
        self.mapWidth = self.tileMap['mapWidth']
        self.mapHeight = self.tileMap['mapHeight']
        self.mapTileWidth = self.tileMap['mapTileWidth']
        self.mapTileHeight = self.tileMap['mapTileHeight']
        
        for tiles in self.layerTiles['Background']:
            for index in tiles:
                self.buildTile(1, index, tiles[index])
        for tiles in self.layerTiles['Foreground']:
            for index in tiles:
                self.buildTile(2, index, tiles[index])
        for tiles in self.layerTiles['Top']:    
            for index in tiles:
                self.buildTile(3, index, tiles[index])
            
    def buildTile(self, layer, location, gid):
        # find correct tile set for each tile
        for item in self.tileSet:
            last = self.tileSet[item]['lastgid']
            first = self.tileSet[item]['firstgid']
            if first <= gid <= last:
                tileSet = self.tileSet[item]
                #print tileSet
        tileWidth = tileSet['tileWidth']
        tileHeight = tileSet['tileHeight']
        tileUnitWidth = tileSet['sourceWidth']/tileSet['tileWidth']
        tileUnitHeight = tileSet['sourceHeight']/tileSet['tileHeight']
        # load tile texture for the tile set
        texture = self.textures[tileSet['firstgid']]
        
        # find location on the map for the tile
        pos_y = (location // self.mapWidth) * self.mapTileHeight
        pos_x = (location * self.mapTileWidth) - ((location // self.mapWidth) * self.mapWidth * self.mapTileWidth)
        pos_y_offset = (self.mapHeight * self.mapTileHeight) - pos_y # need to invert y position placement
        
        # find the tile in the tile set
        
        gid_offset = gid - 1
        y = (gid_offset // tileUnitWidth) * tileHeight
        x = (gid_offset * tileWidth) - ((gid_offset/tileUnitWidth)*tileSet['sourceWidth'])
        y_offset = tileSet['sourceHeight'] - y
        
        size = (tileWidth, tileHeight)
        tile = texture.get_region(x,y_offset,64,64)
        
        # place the tile
        if layer < 2:
            print pos_x, pos_y, gid_offset, x, y_offset, location
            with self.field.canvas.before:
                Rectangle(texture=tile, size=size, pos = (pos_x,pos_y))
        elif layer > 2:
            pass
            #with self.field.canvas:
            #    Rectangle(texture=tile, size=size, pos = (pos_x,pos_y_offset)) 
                   
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
        self.world.moveField(direction)
    
    def toggleBoundaries(self):
        self.world.toggleBoundaries()
        
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
    boundaries = BooleanProperty(False)
    move = NumericProperty(32)
    spriteList = ListProperty()
    player = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(WorldScreen, self).__init__(**kwargs)
        
        atlas = 'resources/atlas/grass_field1.tmx'
        
        field = self.buildField()
        self.buildPlayer()
        self.buildSprites()
        self.buildBoundaries()
        
        TileManager(field, atlas)
        
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.moveField(keycode[1])
        return True
    
    def moveField(self, direction):
        #print 'moving field'
        if direction == 'up':
            self.field.y -= self.move
            self.player.y += self.move
        elif direction == 'down':
            self.field.y += self.move
            self.player.y -= self.move
        elif direction == 'left':
            self.field.x += self.move
            self.player.x -= self.move
        elif direction == 'right':
            self.field.x -= self.move
            self.player.x += self.move 
        
        self.checkCollision(direction)    
             
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
    
    def loadTextures(self):
        # include import of file for where tiles are located in sheet
        
        sheet = CImage.load('resources/tiles/basictheme.png', keep_data=True).texture
        
        x = 0
        y = 0
        size_x = 32
        size_y = 32
        
        desert_1 = sheet.get_region(x,y,size_x,size_y)
        
        tiles = dict(desert_1 = desert_1)
        return tiles
        
        #tileGrass = CImage.load('resources/tiles/basictheme/tile_0025_Layer-55.png', keep_data=True).texture
        #return tileGrass
    
    def buildField(self):
        self.field = RelativeLayout()
        #with self.field.canvas.before:
            #Rectangle(source ='resources/bg/village.png', center=(256,256), size=(2048,2048))
        self.add_widget(self.field)
        
        return self.field
    
    def buildTiles(self, tile, field):
        # import list of where tiles will be placed
        tileHeight = 32
        tileWidth = 32
        tileSize = (tileWidth,tileHeight)
        x = 256
        y = 256
        #x_offset = x
        #y_offset = mapHeight - y
        
        with field.canvas.before:
            Rectangle(texture=tile['desert_1'], size=tileSize, pos = (256,256))
        
    def bkp_buildTiles(self, texture, field):
        x=64
        y=64
        fieldWidth = 40 # multiply by 32px
        fieldHeight = 40
        size = (64,64)
        clipbl = texture.get_region(0,0,16,16)
        cliptl = texture.get_region(0,16,16,16)
        clipbr = texture.get_region(16,0,16,16)
        cliptr = texture.get_region(16,16,16,16)
        
        with field.canvas.before:
            '''
            Rectangle(texture=clipbl, size=(64,64), pos = (128,128))
            Rectangle(texture=cliptl, size=(64,64), pos = (128,192))
            Rectangle(texture=clipbr, size=(64,64), pos = (192,128))
            Rectangle(texture=cliptr, size=(64,64), pos = (192,192))
            Rectangle(texture=texture, size=size, pos = (256,128))
            '''
        
        for ny in range(fieldHeight):
            for nx in range(fieldWidth):
                with field.canvas.before:
                    Rectangle(texture=texture,size=size, pos = (nx*x,ny*y)) 
        
    def buildPlayer(self):
        self.player = AGSprite(player = True, source = 'resources/icons/bunnyfront1.png', size=(62,62), center=(513,257))
        self.field.add_widget(self.player)
            
    def buildSprites(self):
        block = AGSprite(solid=True,size=(64,64), source='resources/icons/branches.png', center = (512,512))
        self.field.add_widget(block)
        self.spriteList.append(block)
    
    def buildBoundaries(self):
        pass
        
    def toggleBoundaries(self):
        if self.boundaries:
            self.boundaries=False
        else:
            self.boundaries=True
            
    def on_boundaries(self, instance, value):
        for child in self.field.children:
            if value:
                if child.boundary:
                    child.opacity = 0.8
            else:
                if child.boundary:
                    child.opacity = 0
    
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
            self.moveField('down')
        elif direction == 'down':
            self.moveField('up')
        elif direction == 'left':
            self.moveField('right')
        elif direction == 'right':
            self.moveField('left')
    
    def enterTown(self):
        print 'town discovered' 
        txt = 'entering the town...'
        self.parent.parent.updateInfoScreen(txt)
          
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