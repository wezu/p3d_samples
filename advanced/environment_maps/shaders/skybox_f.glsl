#version 130
uniform samplerCube env_map;
uniform float blur;
in vec3 V;

out vec4 final_color;

void main()
{    vec3 color =textureLod(env_map, normalize(V), blur).rgb;
    final_color=vec4(color, 1.0);
}
