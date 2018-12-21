#version 330 core

in vec2 TexCoord;

uniform sampler2D srcTex0;
uniform sampler2D srcTex1;
uniform sampler2D srcTex2;


layout(location = 0) out vec4 Frag0;
layout(location = 1) out vec4 Frag1;
layout(location = 2) out vec4 Frag2;
layout(location = 3) out vec4 Frag3;


float a=200.0;
float b=0.2;
float t=log(-1/b);


float est(float s)
{

    //return exp(-1/b*pow((s-0.5)/0.5,a));
    return 1;

}

void main()
{
    Frag0 = texture2D(srcTex0, TexCoord);
    float r0=est(Frag0.r);
    float g0=est(Frag0.g);
    float b0=est(Frag0.b);


    Frag1 = texture2D(srcTex1, TexCoord);
    float r1=est(Frag1.r);
    float g1=est(Frag1.g);
    float b1=est(Frag1.b);


    Frag2 = texture2D(srcTex2, TexCoord);
    float r2=est(Frag2.r);
    float g2=est(Frag2.g);
    float b2=est(Frag2.b);


    Frag3.r=(Frag0.r*r0+Frag1.r*r1+Frag2.r*r2)/(r0+r1+r2);
    Frag3.g=(Frag0.g*g0+Frag1.g*g1+Frag2.g*g2)/(g0+g1+g2);
    Frag3.b=(Frag0.b*b0+Frag1.b*b1+Frag2.b*b2)/(b0+b1+b2);

 }

