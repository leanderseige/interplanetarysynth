# Interplanetary Synth

This is a synthesizer DIY project based on @bleeptrack's [Picoplanets](https://github.com/bleeptrack/picoplanet).

It features:
- 3 voices polyphonic synthesis, based on PWM
- recording and looped playback of sequences
- pitch control
- PT2399 echo/reverb unit
- Sync in/out jacks on order to sync the Interplanetary Synth with other analog synthesizers

LEDs:
Blue: live mode, synth plays what is currently played on the touch buttons
Red: recording of what is currently played on the touch buttons
Green: playback of recorded frequencies
Purple: waiting for next rising edge of sync signal to restart playback
