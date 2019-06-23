'''
This demo shows how to use cube maps for
-skyboxes
-reflections
-ambient lighting

The cube maps used in this demo are made from equirectangular environment
maps (hdri), but only use standard bit depth(8bpp), have a fuzzy blur
applied to lower lods and are compressed using dxt1.

You can check the 'utilities' folder to check the scpript used to make
the cube maps.

Instructions:
- Press *SPACE* to change the environment map
- Default mouse diver for camera movement
'''
import os
import panda3d.core as p3d
p3d.load_prc_file_data('', 'framebuffer-srgb 1')
p3d.load_prc_file_data('', 'multisamples 1')
from direct.showbase.ShowBase import ShowBase

FT_LINEAR = p3d.SamplerState.FT_linear
FT_NEAREST = p3d.SamplerState.FT_nearest
FT_MIPMAP = p3d.SamplerState.FT_linear_mipmap_linear
GLSL = p3d.Shader.SLGLSL
F_SRGB =p3d.Texture.F_srgb

class App(ShowBase):
    def __init__(self):
        super().__init__(self)
        #move the cam back without breaking the default mouse driver
        self.trackball.node().set_pos(0, 20, 0)
        #MSAA just for making thinkgs look good
        self.render.set_antialias(p3d.AntialiasAttrib.M_multisample)

        self.env_maps=[]
        for filename in os.listdir('../../models/texture/cubemap'):
            self.env_maps.append('../../models/texture/cubemap/'+filename)
        self.curren_env_map=0
        #the map_sky will be used for the skybox
        #the other one, blurred and at a lower resolution as the environment map
        self.map_env=self.loader.load_texture(self.env_maps[0])

        #make sure it's sRGB
        if  p3d.ConfigVariableBool('framebuffer-srgb').get_value():
            self.map_env.set_format(F_SRGB)
        #apply texture to render
        self.render.set_shader_input('env_map', self.map_env)
         #camera pos is needed by the shaders
        self.render.set_shader_input("camera", self.cam)
        #load a model and do some setup
        model=self.loader.load_model('../../models/monkey')
        model.set_shader(p3d.Shader.load(GLSL, 'shaders/ibl_v.glsl', 'shaders/ibl_f.glsl'), 1)
        model.set_shader_input('roughness', 0.0)
        model.set_shader_input('metallic', 1.0)
        model.set_shader_input('color', p3d.Vec3(0.8, 0.8, 0.8))
        #copy it a few times
        monkeys=[model.copy_to(render) for _ in range(15)]
        #move and apply different values
        for i, monkey in enumerate(monkeys[:5]):
            monkey.set_pos((i*3)-6, 0, 0)
            monkey.set_shader_input('roughness', i/4.0)
        for i, monkey in enumerate(monkeys[5:10]):
            monkey.set_pos((i*3)-6, 5, 0)
            monkey.set_shader_input('roughness', i/4.0)
            monkey.set_shader_input('metallic', 0.5)
        for i, monkey in enumerate(monkeys[10:]):
            monkey.set_pos((i*3)-6, 10, 0)
            monkey.set_shader_input('roughness', i/4.0)
            monkey.set_shader_input('metallic', 0.0)
        #make skybox
        self.sky_box=self.loader.load_model('../../models//box')
        self.sky_box.reparent_to(self.render)
        self.sky_box.set_scale(10)
        self.sky_box.set_shader(p3d.Shader.load(GLSL, 'shaders/skybox_v.glsl', 'shaders/skybox_f.glsl'), 1)
        self.sky_box.set_shader_input('blur', 0.0)
        self.sky_box.set_bin('background', 100)
        self.sky_box.set_depth_test(False)
        self.sky_box.set_depth_write(False)
        #add a task to update the skybox
        self.taskMgr.add(self.update, 'update')

        #press space to change the environment texture
        self.accept('space', self.cycle_map)

    def cycle_map(self):
        '''Change the environment map'''
        self.curren_env_map+=1
        if self.curren_env_map >= len(self.env_maps):
            self.curren_env_map=0
        self.map_env=self.loader.load_texture(self.env_maps[self.curren_env_map])
        if  p3d.ConfigVariableBool('framebuffer-srgb').get_value():
            self.map_env.set_format(F_SRGB)
        self.render.set_shader_input('env_map', self.map_env)

    def update(self, task):
        ''' Per frame update task'''
        self.sky_box.set_pos(self.cam.get_pos(render))
        return task.cont

app=App()
app.run()
