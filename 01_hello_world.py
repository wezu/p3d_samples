'''
This sample shows how to:
-import and use basic Panda3D classes
-use configuration variables
-load 3d models
-move, scale, rotate 3d models
-change textures
-change colors
-setup lights
- ???
-profit!
'''

#import the most used panda3d classes
# You could just as well use:
# from panda3d.core import *
# but star imports are un-pythonic -_-'
import panda3d.core as p3d
#to save some space and keyboard wear and tear, we'll add some things under shorter name
FT_MIPMAP = p3d.SamplerState.FT_linear_mipmap_linear
FT_LINEAR = p3d.SamplerState.FT_linear
TS_NORMAL = p3d.TextureStage.M_normal
TS_NORMAL_GLOSS = p3d.TextureStage.M_normal_gloss
TS_MODULATE = p3d.TextureStage.M_modulate

#Some configuration
# Panda3D uses .prc files to configure some stuff
# but you don't need to load external files, you can put the values in code
# Do notice how 'load_prc_file_data' works:
# there's an empty string as the first argument, that's not an error.
#It's 2019, make the window 720p let's not embarrass ourself with a 800x600 window
p3d.load_prc_file_data('', 'win-size 1280 720')
#add some multisamples to enable MSAA
p3d.load_prc_file_data('', 'multisamples 1')
#we also want a framerate meter...
p3d.load_prc_file_data('', 'show-frame-rate-meter 1')
#...and we want to disable v-sync else the framerate meter will just show 60.0 fps
p3d.load_prc_file_data('', 'sync-video 0')
#there's a whole lot of options, let's just set a window title just for the fun of it
p3d.load_prc_file_data('', 'window-title Panda3D - Hello World')
#full list of options is here: https://www.panda3d.org/manual/?title=List_of_All_Config_Variables

#'direct' is the part of Panda3D written in Python ('core' is C++ with Python bindings)
# ShowBase is a singelton class that will setup a window, task manager, and all the
# other, common things that you may (or may not) want to use.
# You don't need to use it, but you'll probably want to use or use it even if you don't want to.
# It also installs itself and a bunch of other things into builtins, so that
# key objects (like the 'render' node) are accessible anywhere in your code,
# in these samples I will try not to use these, because again - un-pythonic -_-'
from direct.showbase.ShowBase import ShowBase



class App(ShowBase):
    def __init__(self):
        #init the base class, this will give us access to all the ShowBase functionality
        #if you are using python 2.x you could use:
        #ShowBase.__init__(self)
        #but a better solution is to use Python 3.x,
        #Here's a link, go ahead, download it, I'm not going anywhere...
        # https://www.python.org/downloads/
        super().__init__(self)

        #by default the background is a dull grey, let's make it black
        #colors in Panda3D usually are red, green, blue and alpha values
        # (in a 0.0-1.0 range, where 0.0 is black and 1.1 is white )
        #but in this case we only have red, green and blue
        self.set_background_color(0.0, 0.0, 0.0)

        #load a model of a empty room
        self.room = self.loader.load_model('models/room_industrial')
        #loader returns a node (NodePath), to make it visible
        # we need to parent it to 'render' -the root node of the scene graph
        # we could use just 'render' but apparently that's un-pythonic
        self.room.reparent_to(self.render)

        #now we need to add some crates
        #can't have games without crates, I'm almost sure there's a law for that
        #we'll load a model and copy it a few times
        crate_model = self.loader.load_model('models/crate')
        #the crate should be a 1x1x1 cube, but *someone* who knows nothing
        # about Blender made the model (it's all wezu's fault!)
        #and it's just a wee bit too small- wee need to fix that
        #first resize it, just a bit
        crate_model.set_scale(1.033)
        #we don't want this extra scale to persist, so we flatten the model
        #flatten_light() will just apply the transformations (movement scale, rotation)
        # to the vertex of the model
        #flatten_strong() will try to merge meshes into as few batches as it can
        #flatten_medium() will do something in between
        crate_model.flatten_light()
        #we'll make a list of crates so it will be easy to access them later
        #copy_to() makes a copy of a node, parents it to a given node
        #and returns the NodePath with that copied node - we'll use that
        #list comprehension version for the python savvy...
        self.crates = [crate_model.copy_to(self.render) for _ in range(5)]
        #...for the non-savvy: the above code is equivalent to:
        #self.crates = []
        #for i in range(5):
        #    self.crates.append(crate_model.copy_to(self.render))

        #Now we have the crates all in one place, overlapping - that's no good
        #let's put crate #1 on top of create #0, and twist it a bit
        #the crates are 1x1x1 cubes with the pivot cantered at the bottom,
        #so placing them is easy
        # Panda3D uses a Z-up coordinate system (by default)
        #
        #   Z     Y
        #    |  /
        #    | /
        #    |/____
        #           X
        # X is right --->
        #
        #               /\
        #               /
        # Y is forward /
        #
        #         ^
        #         |
        # Z is up |
        #
        #First move it up
        self.crates[1].set_pos(0,0,1)
        #rotate it a bit, 10 degrees should be fine
        # HPR stands for Heading, Pitch, Roll
        #Heading is the rotation around a vertical axis,
        # eg. the way a top spins, the way Earth spins, looking left and right
        #Pitch is the rotation around a horizontal axis,
        # eg. the way your jaw moves, the way a bike throttle in the handle works, looking up and down
        #Roll is the rotation in the.. em.. the other axis
        #eg. the way clock hands move
        self.crates[1].set_hpr(10,0,0)
        #let's move crate #2 to the side and a bit back
        self.crates[2].set_pos(1,-0.3,0)
        #let's make the #3 and #4 crates bigger, and also move them
        self.crates[3].set_pos(3,-3,0)
        self.crates[4].set_pos(3.1,-1.35,0)
        self.crates[3].set_scale(1.6)
        self.crates[4].set_scale(1.3)
        #Still looks lame. Why don't we change the textures on the small crates?
        #I think the crate uses 2 textures - a diffuse(color) texture and a normal (bump) texture
        #let's just see what textures the crates have and change the textures if we find anything worth changing
        #we will be using some enums defined near the top
        #you can use substitute FT_MIPMAP for p3d.SamplerState.FT_linear_mipmap_linear
        #but first - load new textures
        new_diffuse_tex=self.loader.load_texture('models/texture/crate_2.png')
        #loader uses some reasonable defaults, but let's play with the filter type a
        new_diffuse_tex.set_minfilter(FT_MIPMAP)
        new_diffuse_tex.set_magfilter(FT_LINEAR)
        #same for normal map, but pass the filter types as arguments
        new_normal_tex=self.loader.load_texture('models/texture/crate_2_ng.png',
                                                minfilter = FT_MIPMAP,
                                                magfilter = FT_LINEAR)
        #change the textures only on the last two crates
        for crate in self.crates[-2:]:
            #model have textures in texture stages
            for tex_stage in crate.find_all_texture_stages():
                if crate.find_texture(tex_stage):#test if there is a texture to override
                    #texture stages have mods
                    if tex_stage.get_mode() in (TS_NORMAL, TS_NORMAL_GLOSS):
                        #we found ourself a normal map - replace!
                        crate.set_texture(tex_stage, new_normal_tex, 1)
                    if tex_stage.get_mode() == TS_MODULATE:
                        #we found ourself a diffuse map - replace!
                        crate.set_texture(tex_stage, new_diffuse_tex, 1)
        #Now it looks... wait, what?
        #The texture we loaded is grey! Someone overrode it, and now it's broken!
        #No panic - we'll just add some color to the models.
        #make crate #3 a nice yellowish-brown color
        self.crates[3].set_color((0.8, 0.696, 0.496, 1.0), 1)
        #make crate #4 a nice brown color
        self.crates[4].set_color((0.66, 0.55, 0.46, 1.0), 1)
        #that still looks bad, but at least you now know how to change colors

        #ShowBase creates a camera for us, so we can use it without any extra setup
        #...well almost, for this scene we don't want the player to move the camera
        #by default the camera can be moved and rotated using the mouse,
        # we'll disable that mouse-look, using the worst named function ever:
        self.disable_mouse() #<- this disables the camera mouse control not the mouse!
        #now we can place the camera in a good spot, say at x=-14, y=-3, z=5
        self.camera.set_pos(-6.8708, -4.59957, 4.77564)
        #we could use self.camera.set_hpr() to orient the camera, but it's
        #simpler to just point it at one of the crates, (or a point in space)
        self.camera.look_at(self.crates[4])
        #lets also change the field of view (FOV) for the camera
        lens=self.cam.node().get_lens()
        fov=lens.get_fov()
        lens.set_fov(fov*1.5)

        #Lights
        #first we need an ambient light, else everything not illuminated will be black
        self.ambient_light = self.render.attach_new_node(p3d.AmbientLight('ambient'))
        self.ambient_light.node().set_color((0.1, 0.1, 0.1, 1.0))
        self.render.set_light(self.ambient_light)
        #next a directional light
        self.dir_light = self.render.attach_new_node(p3d.DirectionalLight('directional'))
        self.dir_light.node().set_color((0.1, 0.1, 0.25, 1.0))
        #you can think of the light direction vector as:
        # 'how much is the light coming from the left, back, and bottom?'
        #on a -1.0 - 1.0 scale
        light_from_left= 0.2 # the light is a bit from the left
        light_from_back= 0.4 # the light is a bit from the back
        light_from_bottom= -1.0 #the light is coming from the top
        light_vec=p3d.Vec3(light_from_left,light_from_back,light_from_bottom)
        light_vec.normalize()
        self.dir_light.node().set_direction(light_vec)
        self.render.set_light(self.dir_light)
        #last we add a spotlight, just for shadows
        self.spot_light = self.render.attach_new_node(p3d.Spotlight('spot'))
        self.spot_light.node().set_color((1.0, 1.0, 1.0, 1.0))
        self.spot_light.node().set_shadow_caster(True, 1024, 1024)
        self.spot_light.node().get_lens().set_near_far(1, 20.0)
        self.spot_light.node().get_lens().set_fov(25)
        self.spot_light.node().set_exponent(120.0)
        self.spot_light.set_pos(-8, 0, 8)
        self.spot_light.look_at(self.crates[3])
        self.render.set_light(self.spot_light)

        #enable the shader generator
        self.render.set_shader_auto()
        #enable MSAA
        self.render.set_antialias(p3d.AntialiasAttrib.M_multisample)

# run all the code
if __name__ == "__main__":
    app=App()
    app.run()
