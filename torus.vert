uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform float RADIUS;
uniform float r;

attribute vec4 color;
attribute vec4 position;
attribute vec3 normal;

varying vec4 v_color;

void main()
{
    float PI = 3.14159265358979323846264;
    //float RADIUS = 1.0; // radius to center
    //float r = .3; // radius of tube

    vec4 realposition = vec4(1,1,1,1);

    float theta = position.x * 2.0 * PI;
    float phi = position.y * 2.0 * PI;

    realposition.x = (RADIUS + r * cos(theta)) * cos(phi);
    realposition.y = (RADIUS + r * cos(theta)) * sin(phi);
    realposition.z = r * sin(theta);
    realposition.w = 1.0;

    if(position.w == 1.0){
        gl_Position = projection * view * model * realposition;
    } else {
        gl_Position = projection * view * model * (realposition + vec4(normal, 1.0));
    }

    v_color = color;
}