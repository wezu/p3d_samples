//GLSL
#version 150

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

uniform samplerBuffer grass_buf_tex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float osg_FrameTime;

out vec2 UV;


void main()
    {
    vec3 pos_offset= texelFetch(grass_buf_tex, gl_InstanceID).xyz;
    vec4 vertex=p3d_Vertex;

    float anim_co=vertex.z*0.2;
    float animation =sin(0.7*osg_FrameTime+float(gl_InstanceID))*sin(1.7*osg_FrameTime+float(gl_InstanceID))*anim_co;

    vertex.xy += animation;
    vertex.xyz+=pos_offset;
    gl_Position = p3d_ModelViewProjectionMatrix *vertex;

    UV = p3d_MultiTexCoord0;
    }
