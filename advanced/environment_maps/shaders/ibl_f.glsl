#version 130
//NOTE: This shader is *NOT* PBR!
uniform samplerCube env_map;
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

    //f0 for fresnel, internet says 2-5%, oh well..
    vec3 f0=vec3(0.01+roughness*0.07);
    //use a lower (blurred) LOD for higher roughness
    vec3 base_reflection=textureLod(env_map, r, (roughness)*10.0).rgb;

    //modulate reflection based on roughness???
    vec3 reflection=base_reflection*(1.0-roughness);
    reflection*=mix(vec3(pow(1.0-roughness, 2.0)), color, metallic);

    vec3 fresnel = mix(f0, base_reflection, pow(1.0 - dot(n,-v), 5.0));
    fresnel*=mix(vec3(1.0), color, metallic);
    //modulate fresnel based on roughness.. maybe? but not like this
    fresnel*=pow(((1.0-roughness)*0.4)+0.6, 2.0);
    vec3 light=textureLod(env_map, n, 8.8).rgb;
    //light=pow(light*1.22, vec3(2.0));

    vec3 diffuse = mix( (color*light), vec3(0.0), metallic);

    final_color=vec4(diffuse+fresnel+reflection, 1.0);






}
