//GLSL
#version 130
in vec4 p3d_Vertex;

uniform mat4 p3d_ModelViewProjectionMatrix;

out vec3 V;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    V=p3d_Vertex.xyz;
    }
