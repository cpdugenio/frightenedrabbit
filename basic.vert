uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

attribute vec4 color;
attribute vec4 position;
attribute vec3 normal;

varying vec4 v_color;
varying vec3 f_normal;

void main()
{
    if(position.w == 1.0){
        gl_Position = projection * view * model * position;
    } else {
        gl_Position = projection * view * model * (position + vec4(normal, 1.0));
    }

    v_color = color;
    f_normal = normal;
}