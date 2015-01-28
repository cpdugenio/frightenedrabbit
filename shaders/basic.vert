uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform int drawNormals;

attribute vec4 color;
attribute vec4 position;
attribute vec3 normal;

varying vec4 f_color;
varying vec3 f_normal;
varying vec4 f_pos;

void main()
{
    // compute model pos
    if(drawNormals == 1 && position.w == 0.0){
        gl_Position = projection * view * model * (vec4(position.xyz, 1.0) + 0.25 * vec4(normal,0.0));
    } else {
        gl_Position = projection * view * model * vec4(position.xyz, 1.0);
    }

    // vary color
    f_color = color;

    // find model normals
    f_normal = vec3(projection * view * model * vec4(normal,0.0));
    f_normal = normalize(f_normal);

    // send pos to frag
    f_pos = gl_Position;
}