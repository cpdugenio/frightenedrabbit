uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform float RADIUS;
uniform float r;

attribute vec4 color;
attribute vec4 position;

varying vec4 v_color;
varying vec3 f_normal;

void main()
{
    float PI = 3.14159265358979323846264;
    //float RADIUS = 1.0; // radius to center
    //float r = .3; // radius of tube

    vec4 realposition = vec4(1,1,1,1);

    float U = position.x * 2.0 * PI;
    float V = position.y * 2.0 * PI;

    realposition.x = (RADIUS + r * cos(U)) * cos(V);
    realposition.y = (RADIUS + r * cos(U)) * sin(V);
    realposition.z = r * sin(U);
    realposition.w = 1.0;

    gl_Position = projection * view * model * realposition;


    v_color = color;

    // calculate normal
    vec3 T = vec3(-sin(V), cos(V), 0.0);
    vec3 S = vec3(-cos(V)*sin(U), -sin(V)*sin(U), cos(U));
    vec3 N = cross(T,S);
    f_normal = normalize(N);
}