
varying vec4 v_color;
varying vec3 f_normal;

void main()
{
    gl_FragColor = v_color + 0.75 * vec4(f_normal, 0.0);
}