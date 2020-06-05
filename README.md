# Cosmic neighborhood simulator

Tool for simulating and visualizing planetary objects in the cosmic neighborhood. 

##Background

How can we simulate extraterrestrial objects given observations of them? The so-called Method of Gauss provides an algorithm for determining the orbit of such objects, given three positional observations.

The goal is to produce an efficient, numerically stable simulator of this procedure, with many flexible parameters. This project builds on observations and computations of near-Earth asteroid 6063 Jason, which I made in a team of three as part of the Summer Science Program in Astrophysics in 2017. The asteroid can be found in the default configurations. 

##Installation

Supported only on [Python 2.7.9](https://www.python.org/downloads/release/python-279/)

Follow the procedure to install [Visual Python 6 (legacy)](https://vpython.org/contents/download_windows.html)

Store input parameters and textures (in TGA format) in folder "input", which should be kept in the same directory as the script. Instructions for input file formatting can be found in "Object Input.txt".

##Usage

###Mouse

The solar system is navigated with the left (pivot) and center (scroll to zoom) mouse buttons.
![Zoom features](doc/Oort.png)

###Control Panel

A slider controls the rate of the simulation. The focusing object may be set to any object specified in the input file, and the corresponding orbital elements are displayed. Rotational axes may be toggled if obliquity information is provided.
![Control panel](doc/control panel.png)

###Visuals

![Timelapse](doc/Timelapse.png)
![View from moon](doc/Earth orbit2.png)
![Saturn](doc/Saturn closeup.png)
![Earth](doc/Earth closeup.png)
![Solar System](doc/Overhead.png)

##Contributing

Pull requests welcome.