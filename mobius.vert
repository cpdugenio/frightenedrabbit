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

    vec4 realposition = vec4(1,1,1,1);

    float U = position.x * 2.0 * PI;
    float V = position.y * 2.0 - 1.0;

    realposition.x = (1.0 + V / 2.0 * cos( U / 2.0 )) * cos( U );
    realposition.y = (1.0 + V / 2.0 * cos( U / 2.0 )) * sin( U );
    realposition.z = V / 2.0 * sin( U / 2.0);
    realposition.w = 1.0;

    if(position.w == 1.0){
        gl_Position = projection * view * model * realposition;
    } else {
        gl_Position = projection * view * model * (realposition + vec4(normal, 1.0));
    }

    v_color = color;
}