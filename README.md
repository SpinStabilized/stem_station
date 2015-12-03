# Stem Station
Project for a low-cost weather satellite receive station for STEM education.

## Origins
This is just the beginning source files. Right now I grab raw data from the NOAA 15, 18, and 19 satellites when I can but the data with the basic antenna I am using is marginal at best. Mostly noise. There is a wave (`*.wav`) file from an APT reception project of [Mark Roland's](http://markroland.com/portfolio/weather-satellite-imaging). I use this file for practice in decoding from a signal that is already FM demodulated and sampled at 11.025 KHz.

## Contents
Right now, the contents are pretty bare but over time look for more source files, example/test files, schematics, mechanical design files, and more.

## Goal
My goal is to generate a full project that can be used for STEM education. With aspects of orbital dynamics, earth science, imaging, digital signal processing, software engineering, radio signals, and other topics, this could be a great project for classes to look at and build. The goal is to get a system that will be in the $100 range. We'll see if that goal works out in the end. Affordable for a school is the real goal or in the range where donations could purchase the equipment.

## STEM Topics
A running list of STEM topics covered by working on this project. Need to develop curriculum around these topics.
- Science
    + Meterology
    + Earth Sciences
- Technology
    + General Computing Platforms
    + Networking (Potential)
- Engineering
    + Software Engineering
    + Digital Signal Processing
    + Antenna Design
    + Radio Frequency (RF) Transmission/Reception
-Math
    + Orbital Mechanics
    + Calculus

## To-Do List (In no particular order)
- [ ] Figure out a way to find the sync bursts in the raw data file. I'm missing something and I think it should be easier than I am making it.
- [ ] Write a scheduling system that will track satellites and configure/execute a pass. Seems to be the occasional conflict between NOAA-15 and NOAA-18 so some kind of deconfliction would be good.
- [ ] Once the APT system is mastered, consider additional satellites:
  - [ ] METEOR (LRPT Generic)
  - [ ] GOES
  - [ ] HRPT Satellites
- [ ] Develop build instructions for a QFH antenna.
- [ ] Add the ability to watch for transmissions from the ISS

## Acknowledgements
As with any project, I will be standing on the shoulders of giants

* [Mark Roland - Weather Satellite Imaging](http://markroland.com/portfolio/weather-satellite-imaging) A great reference to learn from Mark's team experience and a very useful sampled APT signal.
* [GNU Radio](http://gnuradio.org/redmine/projects/gnuradio/wiki) A wonderful, open-source, digital signal processing system. All of the modems, decoders, and other signal-chain aspects of the system are being developed in GNU Radio

