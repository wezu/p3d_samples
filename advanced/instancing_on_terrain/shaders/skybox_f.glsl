#version 130
uniform sampler2D sky_map;

in vec3 V;

out vec4 final_color;



const vec2 invAtan = vec2(0.1591, 0.3183);
vec2 SampleSphericalMap(vec3 v)
{
    vec2 uv = vec2(atan(v.z, v.x), asin(v.y));
    uv *= invAtan;
    uv += 0.5;
    return uv;
}

void main()
{
    vec2 uv = SampleSphericalMap(normalize(V));

    final_color=vec4(texture(sky_map, uv).rgb, 1.0);

}
