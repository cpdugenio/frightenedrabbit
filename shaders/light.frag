uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform int normalsShading;
uniform int zbufferShading;
uniform int activeLights;
uniform int wireframe;
uniform vec3 eye;

varying vec4 f_color;
varying vec3 f_normal;
varying vec4 f_pos;

void main()
{
    if (wireframe == 1){
        gl_FragColor = f_color;
    } else if (activeLights > 0) {

        // sum lights
        vec4 total_color = vec4(0,0,0,1);

	for(int i=0; i<activeLights; i++){

            // always add ambient (cheat GI)
	    total_color += gl_LightSource[i].ambient;

	    // place light in world transformation
	    vec4 light_pos = projection * view * gl_LightSource[i].position;

	    // diffuse
	    vec3 l_hat = normalize(vec3(light_pos - f_pos));
	    float ndotl = dot(normalize(f_normal), l_hat);	    
	    if(ndotl > 0.0){
	        total_color += (gl_LightSource[i].diffuse) * ndotl;
	    }

	    // specular
	}

	gl_FragColor = total_color;
    } else if (normalsShading == 1){
        gl_FragColor = f_color + 0.5 * vec4(f_normal, 0.0);
    } else if (zbufferShading == 1){
        float dist = 1.0 - distance(eye, f_pos.xyz) / 42.5;
        gl_FragColor = vec4(dist*.6, dist*0.6, dist, 1.0);
    } else {
        gl_FragColor = f_color;
    }
    
}

/* LIGHTING REFERENCE

struct gl_LightSourceParameters 
{   
   vec4 ambient;              // Aclarri   
   vec4 diffuse;              // Dcli   
   vec4 specular;             // Scli   
   vec4 position;             // Ppli   

   vec4 halfVector;           // Derived: Hi   
   vec3 spotDirection;        // Sdli   
   float spotExponent;        // Srli   
   float spotCutoff;          // Crli                              
                              // (range: [0.0,90.0], 180.0)   
   float spotCosCutoff;       // Derived: cos(Crli)                 
                              // (range: [1.0,0.0],-1.0)   
   float constantAttenuation; // K0   
   float linearAttenuation;   // K1   
   float quadraticAttenuation;// K2  
};    
uniform gl_LightSourceParameters gl_LightSource[gl_MaxLights];

*/