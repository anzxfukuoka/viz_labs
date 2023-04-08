#version 120
// #version 330

uniform vec4 Global_ambient;
uniform vec4 Light_ambient;
uniform vec4 Light_diffuse;
uniform vec3 Light_location;
uniform vec4 Material_ambient;
uniform vec4 Material_diffuse;

attribute vec3 Vertex_position;
attribute vec3 Vertex_normal;
attribute vec3 Vertex_color;

varying vec4 baseColor;

float phong_weightCalc(
            in vec3 light_pos,
            in vec3 frag_normal
        ){
            // get the dot product of our normal and the light position
            // we bound it at 0
            float n_dot_pos = max(0.0, dot(frag_normal, light_pos));
            return n_dot_pos;
        }

 void main(){
            gl_Position = gl_ModelViewProjectionMatrix * vec4(
                Vertex_position, 1.0
            );
            // gets the light into eye space coordinates
            vec3 EC_Light_location = gl_NormalMatrix * Light_location;
            // calculate phong weight for vertex
            // by using its normal and the
            // eye space light position
            // norm them both so they are len(1)
            float diffuse_weight = phong_weightCalc(
                normalize(EC_Light_location),
                normalize(gl_NormalMatrix * Vertex_normal)
            );
            // get a 0-1 value for this vertex color
            // that is a combination of the global light
            // the ambient light from the light source
            // and the diffuse light
            baseColor = clamp(
            (
            // interaction with ambient global light
            (Global_ambient * Material_ambient)
            // interaction with ambient light
            // from light source
            +(Light_ambient * Material_ambient)
            // interaction with direct light
            +(Light_diffuse * Material_diffuse * diffuse_weight)
            ), 0.0, 1.0);
            //baseColor = vec4(1.0f, 0.0f, 0.0f, 1.0f);
            //baseColor += vec4(Vertex_normal[0], Vertex_normal[1], Vertex_normal[2], 1);
            ///baseColor *= vec4(Vertex_color[0], Vertex_color[1], Vertex_color[2], 0);
 }