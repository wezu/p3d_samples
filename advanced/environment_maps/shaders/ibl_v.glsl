//GLSL
#version 130
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelMatrixInverseTranspose;

uniform vec3 wspos_camera;

out vec3 V;
out vec3 N;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    N=(p3d_ModelMatrixInverseTranspose* vec4(p3d_Normal, 1.0)).xyz;
    V= vec3(p3d_ModelMatrix * p3d_Vertex - vec4(wspos_camera, 1.0)).xyz;
    }
