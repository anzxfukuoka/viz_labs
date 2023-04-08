#version 130

in vec3 lightDir;
in vec3 viewDir;
in vec3 normal;

in vec4 baseColor;
in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;

out vec4 color;

void main() {
    //color = baseColor * texture(imageTexture, fragmentTexCoord);
    gl_FragColor =  baseColor;

    float spec = 0.0;

    bool blinn = true;

    if(blinn)
    {
        vec3 halfwayDir = normalize(lightDir + viewDir);
        spec = pow(max(dot(normal, halfwayDir), 0.0), 16.0);
    }
    else
    {
        vec3 reflectDir = reflect(-lightDir, normal);
        spec = pow(max(dot(viewDir, reflectDir), 0.0), 8.0);
    }

    //gl_FragColor = baseColor;
}