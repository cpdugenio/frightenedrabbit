uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

attribute vec4 color;
attribute vec4 position;
attribute vec3 normal;

varying vec4 f_color;
varying vec3 f_normal;
varying vec4 f_pos;

void main()
{
    gl_Position = projection * view * model * position;


    f_color = color;
    f_normal = normal;

    f_pos = gl_Position;
}