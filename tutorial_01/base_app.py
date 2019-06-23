'''
This is a variation of the code from 01_hello_world.py
It it meant to be expanded in future tutorial/samples.
This version lacks most comments, see 01_hello_world.py

New things that are not in 01_hello_world.py:
-changing the title of the window at runtime
-adding dirs to the model path
-changing texture format for sRGB
'''

import panda3d.core as p3d
from direct.showbase.ShowBase import ShowBase

FT_MIPMAP = p3d.SamplerState.FT_linear_mipmap_linear
FT_LINEAR = p3d.SamplerState.FT_linear
TS_NORMAL = p3d.TextureStage.M_normal
TS_NORMAL_GLOSS = p3d.TextureStage.M_normal_gloss
TS_MODULATE = p3d.TextureStage.M_modulate
F_SRGB = p3d.Texture.F_srgb
F_SRGBA = p3d.Texture.F_srgb_alpha
F_RGB = p3d.Texture.F_rgb
F_RGBA = p3d.Texture.F_rgba
M_MSAA= p3d.AntialiasAttrib.M_multisample


class BaseApp(ShowBase):
    def __init__(self):
        super().__init__()
        # we are running from a sub directory
        # but we still want to load the models/textures without the extra '../'
        # so we put the up directory on the model path
        p3d.get_model_path().append_directory('..')

        self.disable_mouse()
        self.set_background_color(0.0, 0.0, 0.0)
        self.render.set_shader_auto()
        self.render.set_antialias(M_MSAA)

    def set_window_title(self, title):
        '''Change the title of the window'''
        win_props = p3d.WindowProperties()
        win_props.set_title(title)
        self.win.request_properties(win_props)

    def setup_lights(self):
        '''Adds lights to the scene '''
        # ambient
        self.ambient_light = self.render.attach_new_node(p3d.AmbientLight('ambient'))
        self.ambient_light.node().set_color((0.1, 0.1, 0.1, 1.0))
        self.render.set_light(self.ambient_light)
        # directional
        self.dir_light = self.render.attach_new_node(p3d.DirectionalLight('directional'))
        self.dir_light.node().set_color((0.1, 0.1, 0.25, 1.0))
        self.dir_light.node().set_direction(p3d.Vec3(0.2,0.4,-1.0))
        self.render.set_light(self.dir_light)
        # spot
        self.spot_light = self.render.attach_new_node(p3d.Spotlight('spot'))
        self.spot_light.node().set_color((1.0, 1.0, 1.0, 1.0))
        self.spot_light.node().set_shadow_caster(True, 1024, 1024)
        self.spot_light.node().get_lens().set_near_far(0.1, 20.0)
        self.spot_light.node().get_lens().set_fov(25)
        self.spot_light.node().set_exponent(120.0)
        self.spot_light.set_pos(-8, 0, 8)
        self.spot_light.look_at(p3d.Point3(3,-3,0))
        self.render.set_light(self.spot_light)


    def setup_scene(self):
        '''Creates a industrial style room with 5 boxes '''
        self.room = self.loader.load_model('models/room_industrial')
        self.room.reparent_to(self.render)

        crate_model = self.loader.load_model('models/crate')
        crate_model.set_scale(1.033)
        crate_model.flatten_light()

        crate_transforms=[
                        {},
                        {'pos':(0,0,1), 'hpr':(10,0,0)},
                        {'pos':(1,-0.3,0)},
                        {'pos':(3,-3,0), 'scale':(1.6), 'color':(0.8, 0.696, 0.496, 1.0),
                         'tex':'models/texture/crate_2.png','tex_n':'models/texture/crate_2_ng.png'},
                        {'pos':(3.1,-1.35,0), 'scale':(1.3), 'color':(0.66, 0.55, 0.46, 1.0),
                         'tex':'models/texture/crate_2.png','tex_n':'models/texture/crate_2_ng.png'}
                         ]
        self.crates = [crate_model.copy_to(self.render) for _ in range(5)]
        for crate, transform in zip(self.crates, crate_transforms):
            if 'pos' in transform:
                crate.set_pos(transform['pos'])
            if 'hpr' in transform:
                crate.set_hpr(transform['hpr'])
            if 'scale' in transform:
                crate.set_scale(transform['scale'])
            if 'color' in transform:
                crate.set_color(transform['color'], 1)
            if 'tex' in transform:
                self.replace_texture(crate, transform['tex'])
            if 'tex_n' in transform:
                self.replace_texture(crate, transform['tex_n'], stage=TS_NORMAL_GLOSS)

    def replace_texture(self, model, texture, stage=TS_MODULATE, minfilter = FT_MIPMAP, magfilter = FT_LINEAR):
        '''Replace the texture on a model '''
        new_tex=self.loader.load_texture(texture)
        new_tex.set_minfilter(FT_MIPMAP)
        new_tex.set_magfilter(FT_LINEAR)

        if  p3d.ConfigVariableBool('framebuffer-srgb').get_value() and stage==TS_MODULATE:
            tex_format=new_tex.get_format()
            if tex_format == F_RGB:
                new_tex.set_format(F_SRGB)
            elif tex_format == F_RGBA:
                new_tex.set_format(F_SRGBA)

        for tex_stage in model.find_all_texture_stages():
            if model.find_texture(tex_stage):
                if tex_stage.get_mode() == stage:
                    model.set_texture(tex_stage, new_tex, 1)


# run all the code
if __name__ == "__main__":
    p3d.load_prc_file_data('', '''win-size 1280 720')
                                multisamples 1
                                show-frame-rate-meter 1
                                sync-video 0''')

    app=BaseApp()
    app.set_window_title('Panda3D - Hello World')
    app.setup_scene()
    app.setup_lights()

    app.camera.set_pos(-7.0, -4.5, 4.5)
    app.camera.look_at(app.crates[4])
    app.cam_lens=app.cam.node().get_lens()
    fov=app.cam_lens.get_fov()
    app.cam_lens.set_fov(fov*1.25)

    app.run()
