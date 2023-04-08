#version 130

in vec3 vertexPos;
in vec3 vertexColor;
in vec2 vertexTexCoord;

out vec3 fragmentColor;
out vec2 fragmentTexCoord;

void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * vec4(
                vertexPos, 1.0
            );
    //gl_Position = vec4(vertexPos, 1.0);
    fragmentColor = vertexColor;
    fragmentTexCoord = vertexTexCoord;
}