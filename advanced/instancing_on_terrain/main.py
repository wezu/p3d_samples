'''
This demo shows how to use instancing to place a lot of models on a height map terrain.

We'll use a samplerBuffer (Buffer Texture) to pack the position(offset) of all the grass instances,
if there's more data to pack (rotation, scale, color, etc) a floating point texture
may be a better choice because the buffer may be limited to 65536 texels.
We're rendering 'only' ~21.5k instances of the grass so there should be no problems.

The grass shader has some additional features:
- animation (for show)
- discarding far away grass (for performance, but test show it has no impact on speed)
'''
import panda3d.core as p3d
p3d.load_prc_file_data('', '''framebuffer-srgb 1
                              sync-video 0
                              show-frame-rate-meter 1
                              multisamples 1''')
from direct.showbase.ShowBase import ShowBase

from operator import itemgetter
import struct
import random

FT_LINEAR = p3d.SamplerState.FT_linear
FT_MIPMAP = p3d.SamplerState.FT_linear_mipmap_linear
GLSL = p3d.Shader.SLGLSL
F_SRGB = p3d.Texture.F_srgb
F_SRGBA = p3d.Texture.F_srgb_alpha

class App(ShowBase):
    def __init__(self):
        super().__init__(self)
        # MSAA just for making thinkgs look good
        self.render.set_antialias(p3d.AntialiasAttrib.M_multisample)

        # ShaderTerrainMesh used for terrain
        self.terrain_node = p3d.ShaderTerrainMesh()
        heightfield = self.loader.load_texture('../../models/texture/terrain/terrain_height.png')
        self.terrain_node.heightfield = heightfield
        # self.terrain_node.target_triangle_width = 10.0
        self.terrain_node.generate()
        self.terrain = self.render.attach_new_node(self.terrain_node)
        self.terrain.set_scale(512, 512, 100)
        self.terrain.set_pos(-256, -256, -30)
        self.terrain.set_shader(p3d.Shader.load(GLSL, 'shaders/terrain_v.glsl', 'shaders/terrain_f.glsl'), 1)
        # load terrain textures
        grass = self.loader.load_texture('../../models/texture/terrain/grass_c.png',
                                        minfilter = FT_MIPMAP, magfilter = FT_LINEAR)
        rock = self.loader.load_texture('../../models/texture/terrain/rock_c.png',
                                        minfilter = FT_MIPMAP, magfilter = FT_LINEAR)
        snow = self.loader.load_texture('../../models/texture/terrain/snow_c.png',
                                        minfilter = FT_MIPMAP, magfilter = FT_LINEAR)
        attribute = self.loader.load_texture('../../models/texture/terrain/terrain_atr.png')
        # make sure textures are sRGB
        if  p3d.ConfigVariableBool('framebuffer-srgb').get_value():
            grass.set_format(F_SRGB)
            rock.set_format(F_SRGB)
            snow.set_format(F_SRGB)
            attribute.set_format(F_SRGB)
        self.terrain.set_shader_input('grass_map', grass)
        self.terrain.set_shader_input('rock_map', rock)
        self.terrain.set_shader_input('snow_map', snow)
        self.terrain.set_shader_input('attribute_map', attribute)
        self.terrain.set_shader_input('camera', self.camera)

        # make the grass map more gpu friendly:
        grass_map = p3d.PNMImage()
        grass_map.read('../../models/texture/terrain/terrain_grass.png')
        grass_list=[]
        x_size = grass_map.get_read_x_size()
        y_size = grass_map.get_read_y_size()
        for x in range(x_size):
            for y in range(y_size):
                if grass_map.get_bright(x,y) > 0.5:
                    # terrain_node.uv_to_world() will give as the position of the grass
                    # but we need to flip the y because OpenGL UVs...
                    # we also want to add a bit of random to avoid 'grass grid'
                    uv_x = x/x_size
                    uv_y = 1.0-y/y_size
                    uv_x += random.uniform(-0.001, 0.001)
                    uv_y += random.uniform(-0.001, 0.001)
                    uv_x = max(0.0, min(1.0, uv_x))
                    uv_y = max(0.0, min(1.0, uv_y))
                    grass_list.append(self.terrain_node.uv_to_world(uv_x, uv_y) )
        # pack the grass_list into a buffer_texture
        grass_buf_tex = p3d.Texture('texbuffer')
        grass_buf_tex.setup_buffer_texture(len(grass_list)+1,
                                            p3d.Texture.T_float,
                                            p3d.Texture.F_rgb32,
                                            p3d.GeomEnums.UH_static)
        image = memoryview(grass_buf_tex.modify_ram_image())
        for i, pos in enumerate(grass_list):
            off = i * 12
            image[off:off+12] = struct.pack('fff', pos[0], pos[1], pos[2])
        # load the grass model
        grass_model=self.loader.load_model('../../models/grass')
        # fix texture for srgb
        if  p3d.ConfigVariableBool('framebuffer-srgb').get_value():
            for tex_stage in grass_model.find_all_texture_stages():
                tex = grass_model.find_texture(tex_stage)
                if tex:
                    tex.set_format(F_SRGBA)
                    grass_model.set_texture(tex_stage, tex, 1)
        grass_model.set_shader(p3d.Shader.load(GLSL, 'shaders/grass_v.glsl', 'shaders/grass_f.glsl'), 1)
        grass_model.set_shader_input('grass_buf_tex', grass_buf_tex)
        grass_model.set_shader_input('clip_distance', 125.0)
        grass_model.set_instance_count(len(grass_list))
        grass_model.reparent_to(self.render)
        # alpha testing will be done in the shader
        grass_model.set_transparency(p3d.TransparencyAttrib.M_none, 1)
        # set the bounds so it stays visible
        grass_model.node().set_bounds( p3d.BoundingBox( (0,0,0), max( grass_list,key=itemgetter(1) ) ) )
        grass_model.node().set_final(1)

         #make skybox
        self.sky_box=self.loader.load_model('../../models//box')
        self.sky_box.reparent_to(self.render)
        self.sky_box.set_scale(10)
        self.sky_box.set_shader(p3d.Shader.load(GLSL, 'shaders/skybox_v.glsl', 'shaders/skybox_f.glsl'), 1)
        self.sky_box.set_shader_input('blur', 0.0)
        self.sky_box.set_bin('background', 100)
        self.sky_box.set_depth_test(False)
        self.sky_box.set_depth_write(False)
        self.render.set_shader_input("camera", self.cam)
        self.render.set_shader_input('env_map', self.loader.load_texture('../../models/texture/cubemap/qwantani.txo'))
        #add a task to update the skybox
        self.taskMgr.add(self.update, 'update')

    def update(self, task):
        ''' Per frame update task'''
        self.sky_box.set_pos(self.cam.get_pos(render))
        return task.cont

app=App()
app.run()
