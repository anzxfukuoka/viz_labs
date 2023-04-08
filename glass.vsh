#version 330

in vec3 position;
in vec3 color;
in vec2 InTexCoords;

out vec3 newColor;
out vec2 OutTexCoords;

uniform mat4 transform;

void main() {
    gl_Position = transform * vec4(position, 1.0f);
    newColor = color;
    OutTexCoords = InTexCoords;
}