# pixelPerfect
Large 30x30 LED Array Project



##NumPad Controls:
* Toggle Display									'5'
* Cycle State										ENTER
* Move Visibull Capture Area						Arrow Keys (Set Numlock for fine adjustment)
* Toggle Automatic Cycling for Visibull				'0'
* Manual Cycling for Visibull						'.'
* Over-ride during sleep hours						*

##Keyboard Controls:
* Toggle Display									SPACE
* Cycle State										TAB
* Move Visibull Capture Area						Arrow Keys (Hold SHIFT for fine adjustment)
* Toggle Automatic Cycling for Visibull				P
* Manual Cycling for Visibull						C
* Over-ride during sleep hours						O

##Configurable Settings (settings.json):
* serial.port				Set to COM port corresponding to STM32 Dev Board
* clock.time				Set desired wakeup and sleep times (am, noon, pm, and night adjust clock background colors throughout the day)
* clock.color				Set desired clock background colors
* visibul.x/y				Set default location of screen capture
* visibul.rows/columns		Set grid size of visibull campaign
* visibul.cycle_time		Set grid cycling period in seconds
* audio.max_amplitude		Set max volume for audio analyzer (unitless)
* audio.audio_rate			Set max frequency for audio capture (max frequency = audio.audio_rate/2)