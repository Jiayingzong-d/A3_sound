Project Overview"Dreams and Reality" is an interactive visualization that blends sound, text, and emotion.It's inspired by the ambiguity between dreams and reality—rational speech intertwined with emotional fluctuations, just as we express our feelings.The floating letters are loose and disordered, reflecting the state of language after being "deconstructed." Words are no longer linear, rational sentences, but rather floating thoughts and fragments of the inner world. At this stage, typing is a rational act (people want to express themselves), but the system reduces words to scattered forms. "Language" itself cannot fully convey our emotions. It's reminiscent of the language in dreams—merely fragments and symbols. When sound is input (the microphone detects vibrations), the looping lines begin to overlap and spread, forming a visual "breathing." This layer corresponds to the physical manifestation of "emotion," with sound being transformed into visible ripples, just as inner fluctuations are visualized and externalized. Entering text and then pressing the spacebar (returning to the swirling vortex) is a kind of "dream backflow," where the newly clear words are sucked back into the vortex, transforming into a chaotic, hazy energy. It's difficult to discern what you just typed.

The work includes:
- Every keyboard input creates an "emotional ripple" in the center of the screen;
- Pressing the spacebar "sucks" words into a vortex, remixing and blurring them like a dream;
- Speaking into the microphone creates new particle ripples, harmoniously interweaving with the background music.
- When you start playing, the system automatically displays several letters representing the title of my album, "Slow Heat."
- Development and testing environment for this project:
System: macOS 14.6.1
Python version: 3.11.9
Dependent libraries: pygame, numpy, sounddevice
The current audio file is track_small.wav, a compressed version of the original track.
If you encounter microphone recognition issues on Windows, modify the device_index value in line 10 of mic_input.py to match your recording device.

Background Music

The background music used in this work is an original piece I created during my undergraduate Digital Media program, produced using Ableton Live.

It serves as the emotional foundation for the entire interactive experience. Since I'm using macOS, the PyAudio/Pyo libraries recommended in class are not compatible with my system environment. Therefore, I chose to use the sounddevice library for real-time microphone input. Please make sure to use headphones with a microphone when running. AirPods or wired headphones are recommended.

Music link: https://comm4044.bandcamp.com/album/slow-heat?t=1
I used my first demo, "Weightless," for this artistic creation. I hope you enjoy it!

System Structure

This project contains two main Python scripts:

1. main.py
- Responsible for overall logic, animation, and interaction;
- Loads music and analyzes audio frequencies;
- Responds to keyboard input and mouse clicks;
- Manages particles, vortices, and visual effects.

2. mic_input.py
- Responsible for real-time microphone input;
- Monitors the user's voice volume;
- Generates new ripples when voice or noise is detected;
- Runs independently from the background music audio analysis, ensuring they do not interfere with each other.

Exports part is save a screenshot of the moment

Interaction Instructions

Function Description

Type letters or numbers on the keyboard to generate emotional ripples in the center (each character is an "emotion unit").

Spacebar: Draw all text into the vortex, entering a dream.

Click/Drag with the mouse | Generate manual ripples at any location.

Speak into the microphone | Trigger additional ripples when voice recognition occurs (volume adjustable in real time)

↑ / ↓ keys | Control background music fade-in and fade-out

Enter key | Save the screenshot to the `exports/` folder

Audio-visual mapping logic

Audio frequency band | Corresponding visual elements

Bass: Controls the breathing rhythm and size of the vortex

Mid-range: Controls rotation speed and ripple rhythm

Treble: Affects halo flickering and subtle vibrations

Microphone input: Generates "breathing" ripple layers based on the human voice

Design Concept

"Dreams and Reality" A digital dream diary. Every input, every word, is recorded and transformed into a visual emotional rhythm.

Clear typing represents tangible self-expression;
Fuzzy swirls symbolize the chaos of the subconscious and dreams.

The work aims to express the blurred boundary between language and emotion.Sound, text, and ripples together form a visual "beating of the soul.



Technical Information

Language: Python 3.11
Libraries: Pygame, Numpy, Sounddevice
Features:
Music spectrum visualization (FFT analysis)
Real-time speech recognition and microphone volume response
Dynamic particle system and ripple generation
Automatic screenshot saving

![The effect after entering the text you want] (https://raw.githubusercontent.com/Jiayingzong-d/A3_sound/refs/heads/main/shot_20251022_204132.png)
![The effect it produces when you speak using wired headphones] (https://raw.githubusercontent.com/Jiayingzong-d/A3_sound/refs/heads/main/shot_20251025_191514.png)
![While playing, you can also click on other areas to generate ripple shapes.] (https://raw.githubusercontent.com/Jiayingzong-d/A3_sound/refs/heads/main/shot_20251025_191537.png)


