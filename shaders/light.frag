uniform int normalsShading;
uniform int zbufferShading;
uniform int wireframe;
uniform vec3 eye;

varying vec4 f_color;
varying vec3 f_normal;
varying vec4 f_pos;

void main()
{
    if (wireframe == 1){
        gl_FragColor = f_color;
    } else if (normalsShading == 1){
        gl_FragColor = f_color + 0.5 * vec4(f_normal, 0.0);
    } else if (zbufferShading == 1){
        float dist = 1.0 - distance(eye, f_pos.xyz) / 42.5;
        gl_FragColor = vec4(dist*.6, dist*0.6, dist, 1.0);
    } else {
        gl_FragColor = f_color;
    }
    
}