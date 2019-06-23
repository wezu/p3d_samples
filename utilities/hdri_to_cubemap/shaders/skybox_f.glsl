#version 130
uniform sampler2D sky_map;
uniform sampler2D noise_tex;
uniform float sky_lod;
uniform float value;
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

vec3 rgb2hsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main()
{
    vec2 noise_size=textureSize(noise_tex, 0).xy/(sky_lod+1.0);
    vec2 noise_uv=(gl_FragCoord.xy/noise_size);
    vec3 noise=texture(noise_tex, noise_uv).rgb;

    vec2 uv1 = SampleSphericalMap(normalize(V+(noise*0.004*sky_lod)));
    vec2 uv2 = SampleSphericalMap(normalize(V+(noise*0.009*sky_lod)));

    vec3 color = mix(textureLod(sky_map, uv1, sky_lod).rgb, textureLod(sky_map, uv2, sky_lod*0.7).rgb, 0.5);

    vec3 hsv=rgb2hsv(color);
    hsv.z*=1.0+value;

    final_color=vec4(hsv2rgb(hsv), 1.0);

}
