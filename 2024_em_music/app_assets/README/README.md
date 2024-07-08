<div style="text-align: center;">
    <img src="logo_full.png" alt="Travis Custom Logo Image" width="70"/>
</div>

<div style="text-align: center;">
    <h1>PROJECT NAME</h1>

    Written by: <b>Travis M. Moore</b>
    <br>
    Latest version: <b>Version 0.1.0</b><br>
    Originally created: <b>March 29, 2024</b><br>
    Last edited: <b>March 29, 2024</b><br><br>
</div>

---

# Description
ONE-SENTENCE BLURB.

- POINT 1

- POINT 2
<br>
<br>

---

# Getting Started

## Dependencies

- Windows 10 or greater (not compatible with Mac OS)

## Installing

- This is a compiled app; the executable file is stored on Starfile at: \\\\starfile\Public\Temp\MooreT\Custom Software

- Simply copy the executable file and paste to a location on the local machine. 

- **DO NOT RUN FROM THE STARFILE SERVER.** This ties up the program for others, and will result in erratic app behavior. 

## First Use
- **DO NOT RUN FROM THE STARFILE SERVER.** This ties up the program for others, and will result in erratic app behavior. That's right, this statement is identical to the one above - it's just that important!

- Double-click to start the application for the first time.
<br>
<br>

---

# Main Screen
BLURB ABOUT APP IN GENERAL (OR WHAT CAN BE ACCOMPLISHED ON THE ROOT WINDOW).

<img src="main_window.png" alt="Main Window Image" width="500"/>

## LEVEL 2 HEADING
### LEVEL 3 HEADING
- POINT 1

- POINT 2
<br>
<br>

---

# Tools Menu

## Audio Settings
The Audio Settings window allows you to select an audio device and assign speakers for playback. 

<b>Device Selection.</b> The Audio Settings window displays available audio devices in a table (see lower part of image below). Simply click to choose the desired device. Your selection will be highlighted in blue. 

<b>Speaker Assignment.</b> To assign a speaker for playback, enter the speaker/channel number in the entry box (see upper part of image below). Note that you must provide a speaker for each channel in the audio file. For example, if your stimulus has eight channels, you must provide a list of eight speakers. Separate numbers with spaces when providing a list of speakers. For example: ```1 2 3 4 5 6 7 8```.

<img src="audio_settings.png" alt="Audio Settings Window" width="500"/>

## Calibration
The Calibration window provides a simple way to calibrate your stimuli using a sound level meter (SLM). 

<b>Calibration Stimulus.</b> You can choose to use the built-in white noise, or provide a custom file for the calibration signal (top group in image below).

<b>Playback Controls.</b> Use the "Level (dB)" entry box to adjust the playback level in dB FS (middle group in image below). The "Play" and "Stop" buttons allow you to start and stop the audio playback.

<b>Measured Level.</b> Use a SLM to measure the level of the calibration signal and enter the SLM reading into the "SLM Reading (dB)" entry box (bottom group in image below). Click submit, and the application will calculate an offset so that you can specify presentation levels in dB (whichever type of dB you set the SLM to when measuring). Note that the "Submit" button is disabled until you click the "Play" button.

<img src="calibration.png" alt="Calibration Window" width="400"/>
<br>
<br>

---

# Compiling from Source
```
pyinstaller...
```
<br>
<br>

---

# Contact
Please use the contact information below to submit bug reports, feature requests and any other feedback.

- Travis M. Moore: travis_moore@starkey.com
