'''
This sample shows how to control the camera, and also how to:
- respond to key events
- using tasks
- track the mouse cursor
- configure keys using a .ini file
- relative motion mumbo-jumbo
'''
import panda3d.core as p3d
p3d.load_prc_file_data('', '''win-size 1280 720
                            multisamples 1
                            show-frame-rate-meter 1
                            sync-video 0''')

#we re use the code from tutorial_01
#it sets up Panda3D, the scene, and lights
from tutorial_01.base_app import BaseApp

import configparser

class App(BaseApp):
    def __init__(self):
        super().__init__()
        #set a window title
        self.set_window_title('Panda3D - Camera Control. Use mouse!')
        #setup the scene and lights
        self.setup_scene()
        self.setup_lights()
        #let's make it a bit brighter
        self.ambient_light.node().set_color((0.3, 0.3, 0.3, 1.0))

        # we will control the camera using a rig of 2 nodes
        # the 'node' will be the point in space where the camera looks at
        # the 'gimbal' will act as an arm that the camera is attached to
        self.camera_node  = self.render.attach_new_node('camera_node')
        self.camera_gimbal  = self.camera_node.attach_new_node('gimbal')
        # the camera will orbit around the camera_node, here we'll set
        # how far that orbit is from the focus point
        camera_offset =(0, 5, 5)
        self.camera.set_pos(self.render, camera_offset)
        self.camera.look_at(self.camera_node)
        #we use 'wrt_reparent_to' to keep the offset we just set
        self.camera.wrt_reparent_to(self.camera_gimbal)
        #with the setup done, we want to move the camera to a different spot
        self.camera_node.set_pos(0, -2, 1)
        #and rotate 180
        self.camera_node.set_h(180)

        #configuration time
        # how fast can the camera rotate?
        self.camera_rotation_speed = 100.0
        # how fast can the camera move?
        self.camera_move_speed = 10.0
        # how fast can the camera zoom?
        self.camera_zoom_speed = 10.0
        self.camera_zoom_damping = 2.0
        # how much can the camera tilt? (change 'p' in HPR sense)
        self.camera_p_limit = p3d.Vec2(-45, 45)
        #how much can the camera zoom in or out?
        self.zoom_limit=[3, 20]
        # controls:
        # we'll read the keys from an .ini file
        # I'm not using the default .prc PAnda3D configuration file format
        # because most players will not even recognize .prc as a human readable,
        # configuration file, .ini on the other hand are common in games
        key_config = configparser.ConfigParser()
        key_config.read('tutorial_02/keys.ini')
        #we want mouse wheel to control zoom
        # the way the mouse wheel works is just like a button
        # it just fires the 'wheel_up' or 'wheel_down' events when the wheel is spun
        # we will zoom in (or out) some amount whenever the wheel is moved
        # self.zoom will tell us how much we still need to move and in what direction
        # the actual moving of the camera will happen in the camera_update task
        self.zoom = 0
        #the 'accept' function tells the underlying DirectObject to listen to some event
        # and run some function (method) when it happens
        # in this case the event is "key_config['camera_zoom']['zoom_in']" - and that should be just
        #"key_config['camera_zoom']['zoom_in']" should just be 'wheel_up'
        # our function is 'self.zoom_control'
        # the last argument is a list of ... em arguments passed to our function
        # in other words:
        # when a player spins the mouse wheel, panda3d will send a event named 'wheel_up'
        # and our class will respond to it by calling 'self.zoom_control(1.0)'
        self.accept(key_config['camera_zoom']['zoom_in'], self.zoom_control, [1.0] )
        self.accept(key_config['camera_zoom']['zoom_out'], self.zoom_control, [-1.0] )
        # for other keys we want to know if the player is holding down a key
        # self.key_down will be a dict that will have the names of events as keys
        # and True as the value if a key is pressed else False
        self.key_down={}
        for event, key in key_config['camera_keys'].items():
            self.key_down[event] = False
            self.accept(key, self.key_down.__setitem__, [event, True])
            #the keys can me 'compound' like 'shift-mouse1' or 'alt-mouse1'
            # the problem is - there is no -up event for such key-combos
            # we will have to react just to the first key
            # if we'd have a key bind on shift things would break :(
            if '-' in key:
                self.accept(key.split('-')[0]+'-up', self.key_down.__setitem__, [event, False])
            else:
                self.accept(key+'-up', self.key_down.__setitem__, [event, False])
        # we'll later check if this set None and skip moving the mouse
        # until we have a valid value
        self.last_mouse_pos = None

        #our App class inherits from the BaseApp class..
        # BaseApp inherits from ShowBase...
        # ShowBase inherits from DirectObject...
        # ...so we can use DirectObject methods like add_task()
        #The alternative is using taskMgr.add() and that's what
        # DirectObject is actually doing, but this is nicer (?)
        #A task is simply a function called auto-magically each frame
        self.add_task(self.camera_update, 'camera_update')

    def zoom_control(self, amount):
        self.zoom=amount

    def camera_update(self, task):
        '''This function is a task run each frame,
           it controls the camera movement/rotation/zoom'''
        #dt is 'delta time' - how much time elapsed since the last time the task ran
        #we will use it to keep the motion independent from the framerate
        dt = globalClock.get_dt()
        #we'll be tracking the mouse
        #first we need to check if the cursor is in the window
        if self.mouseWatcherNode.has_mouse():
            #let's see where the mouse cursor is now
            mouse_pos = self.mouseWatcherNode.get_mouse()
            #let's see how much it moved from last time, or if this is the first frame
            if self.last_mouse_pos is None:
                self.last_mouse_pos = p3d.Vec2(mouse_pos)
                return task.again
            mouse_delta = mouse_pos- self.last_mouse_pos
            #and let's remember where it is this frame so we can
            #check next frame where it was
            self.last_mouse_pos = p3d.Vec2(mouse_pos)
            #camera zoom
            if self.zoom != 0.0:
                #let's see how far the camera is from the pivot point
                distance=self.camera.get_distance(self.camera_node)
                #we don't want it to be too close nor to far away
                if (distance > self.zoom_limit[0] and self.zoom > 0.0) or \
                   (distance < self.zoom_limit[1] and self.zoom < 0.0):
                    #move the camera away or closer to the pivot point
                    #we do that by moving the camera relative to itself
                    self.camera.set_y(self.camera, self.zoom*dt*self.camera_zoom_speed)

                    if self.zoom >= 0.0:
                        self.zoom-=dt*self.camera_zoom_damping
                    else:
                        self.zoom+=dt*self.camera_zoom_damping
                else:
                    self.zoom=0.0
            if self.key_down['rotate']:
                h = self.camera_node.get_h()- mouse_delta.x*self.camera_rotation_speed
                self.camera_node.set_h(h)
                p = self.camera_gimbal.get_p()- mouse_delta.y*self.camera_rotation_speed
                p = min(max(p, self.camera_p_limit.x), self.camera_p_limit.y)
                self.camera_gimbal.set_p(p)
            if self.key_down['relative_move']:
                pos = p3d.Vec3(mouse_delta.x, 0, mouse_delta.y)
                pos = self.camera_node.get_pos(self.camera) - pos*self.camera_move_speed
                self.camera_node.set_pos(self.camera,  pos)
            elif self.key_down['move']:
                pos=p3d.Vec3(mouse_delta.x, mouse_delta.y, 0)
                self.camera_node.set_pos(self.camera_node, pos*self.camera_move_speed)
        return task.again



app=App()
app.run()
