# Cosmic neighborhood simulator

Tool for simulating and visualizing planetary objects in the cosmic neighborhood. 

## Background

How can we simulate extraterrestrial objects given observations of them? The so-called Method of Gauss provides an algorithm for determining the orbit of such objects, given three positional observations.

The goal is to produce an efficient, numerically stable simulator of this procedure, with many flexible parameters. This project builds on observations and computations of near-Earth asteroid 6063 Jason, which I made with a team of three as part of the Summer Science Program in Astrophysics in 2017. The asteroid can be found in the default configurations. The observations are [published in the Smithsonian Minor Planet Circulars](https://www.minorplanetcenter.net/iau/ECS/MPCArchive/2017/MPC_20171005.pdf).

## Installation

Supported only on [Python 2.7.9](https://www.python.org/downloads/release/python-279/)

Follow the procedure to install [Visual Python 6 (legacy)](https://vpython.org/contents/download_windows.html)

Store input parameters and textures (in TGA format) in folder "input", which should be kept in the same directory as the script. Instructions for input file formatting can be found in "Object Input.txt".

## Usage

### Mouse

The solar system is navigated with the left (pivot) and center (scroll to zoom) mouse buttons.

### Control Panel

A slider controls the rate of the simulation. The focusing object may be set to any object specified in the input file, and the corresponding orbital elements are displayed. Rotational axes may be toggled if obliquity information is provided.

<img src="https://github.com/charliecb/cosmic-neighborhood-simulator/blob/master/doc/control%20window.PNG" alt="Control panel" height="400"/>

### Visuals

<img src="https://github.com/charliecb/cosmic-neighborhood-simulator/blob/master/doc/Timelapse.PNG" alt="Timelapse" height="400"/><img src="https://github.com/charliecb/cosmic-neighborhood-simulator/blob/master/doc/Overhead.PNG" alt="Solar system" height="400"/>

<img src="https://github.com/charliecb/cosmic-neighborhood-simulator/blob/master/doc/Earth%20orbit2.PNG" alt="View from moon" height="400"/><img src="https://github.com/charliecb/cosmic-neighborhood-simulator/blob/master/doc/Earth%20closeup.PNG" alt="Earth" height="400"/>

<img src="https://github.com/charliecb/cosmic-neighborhood-simulator/blob/master/doc/Saturn%20closeup.PNG" alt="Saturn" height="400"/>


## Contributing

Pull requests welcome.
