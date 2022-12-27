# Interplanetary Synth

This is a DIY synthesizer project based on Bleeptrack's [Picoplanets](https://github.com/bleeptrack/picoplanet).

Features:
- 3 voices polyphonic synthesis, based on PWM
- Recording and looped playback of sequences
- Pitch control
- PT2399 echo/reverb unit
- Sync in/out jacks on order to sync the Interplanetary Synth with other analog synthesizers

LEDs:
- Blue: live mode, synth plays what is currently played on the touch buttons
- Red: recording of what is currently played on the touch buttons
- Green: playback of recorded frequencies
- Purple: waiting for next rising edge of sync signal to restart playback
