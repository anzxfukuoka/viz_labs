#version 120

uniform vec4 Color_Main;
varying vec4 baseColor;

void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    baseColor = Color_Main;
}