uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform float RADIUS;
uniform float r;

attribute vec4 color;
attribute vec4 position;

varying vec4 f_color;
varying vec3 f_normal;
varying vec4 f_pos;


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

    // find model position
    gl_Position = projection * view * model * realposition;

    // vary the color
    f_color = color;

    // calculate normal (in model transf)
    vec3 T = vec3(-sin(V), cos(V), 0.0);
    vec3 S = vec3(-cos(V)*sin(U), -sin(V)*sin(U), cos(U));
    vec3 N = cross(T,S);
    f_normal = vec3(projection * view * model * vec4(N,0.0));
    f_normal = normalize(f_normal);
 
    // send pos to frag
    f_pos = gl_Position;
}