uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

attribute vec4 color;
attribute vec4 position;

varying vec4 v_color;
varying vec3 f_normal;

void main()
{
    float PI = 3.14159265358979323846264;

    vec4 realposition = vec4(1,1,1,1);

    float theta = position.x * 2.0 * PI;
    float phi = position.y * PI;

    realposition.x = cos(theta) * sin(phi);
    realposition.y = sin(theta) * sin(phi);
    realposition.z = cos(phi);
    realposition.w = 1.0;

    gl_Position = projection * view * model * realposition;


    v_color = color;
    f_normal = realposition.xyz;
}