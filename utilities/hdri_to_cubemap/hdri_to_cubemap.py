import os
from panda3d.core import *
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 8")
from direct.showbase import ShowBase

base=ShowBase.ShowBase()
render.setAntialias(AntialiasAttrib.MMultisample)

sky_box=loader.load_model('box')
sky_box.reparent_to(render)
sky_box.set_scale(10)
sky_box.set_shader(Shader.load(Shader.SLGLSL, 'shaders/skybox_v.glsl', 'shaders/skybox_f.glsl'), 1)
sky_box.set_shader_input('noise_tex', loader.load_texture('blue_noise.png', minfilter = SamplerState.FT_nearest, magfilter = SamplerState.FT_nearest))
sky_box.set_bin('background', 100)
sky_box.set_depth_test(False)
sky_box.set_depth_write(False)

for filename in os.listdir('hdri'):
    source = filename[:-4]
    print(source)
    sky_map=loader.load_texture('hdri/'+source+'.png')
    sky_map.set_magfilter(SamplerState.FT_linear_mipmap_linear)
    sky_map.set_minfilter(SamplerState.FT_linear_mipmap_linear)
    sky_box.set_shader_input('sky_map', sky_map)
    sky_box.set_shader_input('sky_lod', 0.0)
    sky_box.set_shader_input('value', 0.0)

    lod=0
    resolution =  1024
    while resolution >= 1:
        base.saveCubeMap('temp/'+source+'_'+str(lod)+'_#.png', size = resolution)
        resolution=resolution//2
        lod+=1
        sky_box.set_shader_input('sky_lod', float(lod*1.5))
        sky_box.set_shader_input('value', lod*0.04)
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

    cubemap=loader.loadCubeMap('temp/'+source+'_#_#.png', readMipmaps = True, minfilter = SamplerState.FT_linear_mipmap_linear, magfilter = SamplerState.FT_linear_mipmap_linear)
    cubemap.set_compression(Texture.CM_dxt1)
    cubemap.write('cubemap/'+source+'.txo')

#base.run()
