uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

attribute vec4 color;
attribute vec4 position;
attribute vec3 normal;

varying vec4 v_color;

void main()
{
    float PI = 3.14159265358979323846264;

    float r = 2.5;

    vec4 realposition = vec4(1,1,1,1);

    float U = position.x * 2.0 * PI;
    float V = position.y * 2.0 * PI;

    realposition.x = (r + cos(U / 2.0) * sin( V ) - sin(U / 2.0) * sin(2.0 * V)) * cos( U );
    realposition.y = (r + cos(U / 2.0) * sin( V ) - sin(U / 2.0) * sin(2.0 * V)) * sin( U );
    realposition.z = sin(U / 2.0) * sin(V) + cos(U / 2.0) * sin(2.0 * V);
    realposition.w = 1.0;

    if(position.w == 1.0){
        gl_Position = projection * view * model * realposition;
    } else {
        gl_Position = projection * view * model * (realposition + vec4(normal, 1.0));
    }

    v_color = color;
}