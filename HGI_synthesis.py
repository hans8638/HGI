from OpenGL.GL import *
from function.ShaderProgram import ShaderProgram
from PIL import Image
import function.glfw as glfw
import sys,os,numpy as np
from ctypes import c_void_p
import cv2
from parameter_setting import resize_factor,path



vertices = np.array([1.0, 1.0, 0,    1.0, 1.0,
                     1.0,-1.0, 0,    1.0, 0.0,
                    -1.0,-1.0, 0,    0.0, 0.0,
                    -1.0, 1.0, 0,    0.0, 1.0], dtype = np.float32)


indices = np.array([0, 1, 3,
                    1, 2, 3], dtype = np.uint32)

vertexShaderPath=os.path.join('vertexShader','v_HGI.glsl')
fragmentShaderPath=os.path.join('fragmentShader','3s_HGI.glsl')

WINWIDTH=4352
WINHEIGHT=3264


path='src'
resize_factor=0.1


def windowInit(width, height):
    glfw.glfwInit()
    glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR, 4)
    glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR, 5)
    glfw.glfwWindowHint(glfw.GLFW_OPENGL_PROFILE, glfw.GLFW_OPENGL_CORE_PROFILE)



    window = glfw.glfwCreateWindow(width, height, "OpenGL".encode(), 0, 0)
    if window == 0:
        print("failed to create window")
        glfw.glfwTerminate()
    glfw.glfwMakeContextCurrent(window)
    return window

class MyShaderProgram(ShaderProgram):
    def __init__(self, vertPath=vertexShaderPath, fragPath=fragmentShaderPath):
        super().__init__(vertPath, fragPath)

    def use(self):
        glUseProgram(self.program_id)

def initVAO(vertices,indices):
    VAO = glGenVertexArrays(1)
    VBO, EBO = glGenBuffers(2)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, sys.getsizeof(vertices), vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sys.getsizeof(indices), indices, GL_STATIC_DRAW)
    # 设置vertex属性
    # 含义:location=0;3个元素;GL_FLOAT的类型大小;不进行NDC操作;步长，单位为字节; 初始化偏移量
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, c_void_p(12))
    glEnableVertexAttribArray(1)
    glBindVertexArray(0)
    return VAO

def packSrc2Texs(n,src,files):
    textures = glGenTextures(n)
    for i in range(n):
        glBindTexture(GL_TEXTURE_2D, textures[i])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        img = Image.open(os.path.join(src,files[i]))

        width, height = img.size
        data = np.array(list(img.getdata()), dtype=np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        glBindTexture(GL_TEXTURE_2D, 0)
    return textures

def setInitWithTex(shaderProg,NameInGLSL,indexInGPU):
    shaderProg.use()
    glUniform1i(glGetUniformLocation(shaderProg.program_id, NameInGLSL), indexInGPU)


def genFBOWithTexs(width,height,n):
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    texColorBuffers = glGenTextures(n)
    for i in range(n):
        glBindTexture(GL_TEXTURE_2D, texColorBuffers[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, eval('GL_COLOR_ATTACHMENT'+str(i)), GL_TEXTURE_2D, texColorBuffers[i], 0)
    return fbo, texColorBuffers

def activeTexUnit(textures,i):
    glActiveTexture(eval('GL_TEXTURE'+str(i)))
    glBindTexture(GL_TEXTURE_2D, textures[i])

def storePic(width,height):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (width, height), data)
    image.save('save/high_res_in.png', 'png')
    image_cv=cv2.imread('save/high_res_in.png')
    shape = np.shape(image_cv)
    image_low = cv2.resize(image_cv, (int(shape[1] * resize_factor), int(shape[0] * resize_factor)))
    cv2.imwrite('save/low_res_in.png',image_low)

def main():

    files=os.listdir(path)
    print(files)
    N=len(files)
    window=windowInit(1, 1)
    shaderProg=MyShaderProgram()
    VAO=initVAO(vertices,indices)
    textures=packSrc2Texs(N, path, files)
    for i in range(N):
        setInitWithTex(shaderProg,'srcTex'+str(i),i)
    FBO,texColorBuffers=genFBOWithTexs(WINWIDTH, WINHEIGHT, N+2)
    DRAW_BUFFERS=[]
    for i in range(N+2):
        DRAW_BUFFERS.append(eval('GL_COLOR_ATTACHMENT'+str(i)))
    glBindFramebuffer(GL_FRAMEBUFFER, FBO)
    glDrawBuffers(DRAW_BUFFERS)
    glViewport(0, 0, WINWIDTH, WINHEIGHT)
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    shaderProg.use()
    glBindVertexArray(VAO)
    for i in range(N):
        activeTexUnit(textures,i)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    glBindVertexArray(0)
    glReadBuffer(GL_COLOR_ATTACHMENT3)
    storePic(WINWIDTH, WINHEIGHT)
    glfw.glfwTerminate()


if __name__ == "__main__":
    main()
