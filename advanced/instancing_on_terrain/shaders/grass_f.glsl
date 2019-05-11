#version 150
in vec2 UV;
in float DISTANCE_TO_CAMERA;

out vec4 final_color;

uniform sampler2D p3d_Texture0;
uniform float clip_distance;

void main()
    {
    //discard based on distance
    if (DISTANCE_TO_CAMERA > clip_distance)
        {
        discard;
        }

    vec4 color = texture(p3d_Texture0,UV);
    //discard based on alpha, because modern OGL has no alpha testing
    if (color.a < 0.5)
        {
        discard;
        }
    final_color=color;
    }
