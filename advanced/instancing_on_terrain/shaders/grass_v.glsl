#version 150
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

uniform samplerBuffer grass_buf_tex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform float osg_FrameTime;

out vec2 UV;
out float DISTANCE_TO_CAMERA;

void main()
    {
    vec4 vertex=p3d_Vertex;
    //animation
    float anim_co=vertex.z*0.2;
    float animation =sin(0.7*osg_FrameTime+float(gl_InstanceID))*sin(1.7*osg_FrameTime+float(gl_InstanceID))*anim_co;
    vertex.xy += animation;
    //position offset read from the buffer texture, see python code
    vec3 pos_offset= texelFetch(grass_buf_tex, gl_InstanceID).xyz;
    vertex.xyz+=pos_offset;
    gl_Position = p3d_ModelViewProjectionMatrix *vertex;

    UV = p3d_MultiTexCoord0;
    DISTANCE_TO_CAMERA= -vec4(p3d_ModelViewMatrix* vertex).z;
    }
