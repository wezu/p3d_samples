#version 150
in vec2 UV;

out vec4 final_color;

uniform sampler2D p3d_Texture0;

void main()
 {
  vec4 color = texture(p3d_Texture0,UV);
  final_color=color;
}
