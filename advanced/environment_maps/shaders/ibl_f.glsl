#version 130
//NOTE: This shader is *NOT* PBR!
uniform sampler2D env_map;
uniform float roughness;
uniform float metallic;
uniform vec3 color;


in vec3 V;
in vec3 N;

out vec4 final_color;

void main()
{
    vec3 n=normalize(N);
    vec3 v=normalize(V);
    //uv for the reflection
    vec3 r = normalize(reflect(v, n));
    float m = 2.82842712474619 * sqrt( r.z+1.0 );
    vec2 uv = r.xy / m + .5;
    //f0 for fresnel, internet says 2-5%, oh well..
    vec3 f0=vec3(0.004);
    //use a lower (blurred) LOD for higher roughness
    vec3 base_reflection=textureLod(env_map, uv, (roughness)*7.0).rgb;
    //modulate reflection based on roughness???
    vec3 reflection=base_reflection*(1.0-roughness);
    reflection*=mix(vec3(pow(1.0-roughness, 2.0)), color, metallic);

    vec3 fresnel = mix(f0, base_reflection, pow(1.0 - dot(n,-v), 5.0));
    fresnel*=mix(vec3(1.0), color, metallic);
    //modulate fresnel based on roughness.. maybe? but not like this
    fresnel*=pow(((1.0-roughness)*0.4)+0.6, 2.0);
    //uv for the diffuse
    m = 2.82842712474619 * sqrt( n.z+1.0 );
    uv = n.xy / m + .5;
    //lod 10 is practically one color - say ambient
    //lod 9 is too weak, lod 8 looks too much as reflection
    //8.8 is just fine,
    //multiply it by 2 because the texture is not hdr, and needs more light
    vec3 light=textureLod(env_map, uv, 10.0).rgb + (textureLod(env_map, uv, 8.8).rgb*2.0);

    vec3 diffuse = mix( (color*light), vec3(0.0), metallic);

    final_color=vec4(diffuse+reflection+fresnel, 1.0);






}
