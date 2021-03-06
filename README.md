#Frightened Rabbit

Just another OpenGL project using PyOpenGL and GLSL and PyQT4

See `pip_requirements`

Also need PyQT4. Because I am developing on OSX, I used [Homebrew](http://brew.sh/) package manager:

```
brew install qt
brew install sip
brew install pyqt
```

(It may be wise to install PyQT4 before executing `pip install -r pip_requirements`)

I also had to put `export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH` in my `~/.bash_profile` ([reference](https://github.com/Homebrew/homebrew/issues/6176))


I am also trying my best to comment methods and classes with [Numpy](https://github.com/numpy/numpydoc)'s doc style (just for good coding commenting practice).

## Screenshots

### GLSL UV Torus, Normals Shading
![GUI](https://raw.githubusercontent.com/cpdugenio/frightenedrabbit/master/screenshots/GUI.png)

### Cow, Wireframe, Smooth Shading, Normal Vectors
![Cow with normal vectors](https://raw.githubusercontent.com/cpdugenio/frightenedrabbit/master/screenshots/Cow_Normals.png)

### Cow, Smooth Shading
![Cow with normals shader](https://raw.githubusercontent.com/cpdugenio/frightenedrabbit/master/screenshots/Cow_Lights_Shader.png)

### Bunny, Z-Buffer Shading
![Bunny with z-buffer shader](https://raw.githubusercontent.com/cpdugenio/frightenedrabbit/master/screenshots/Bunny_ZBuffer_Shader.png)

### Bunny, Wireframe, Normals Shading
![Bunny with normals shader](https://raw.githubusercontent.com/cpdugenio/frightenedrabbit/master/screenshots/Bunny_Normals_Shader.png)
