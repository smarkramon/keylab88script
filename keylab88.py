from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface #main class of the Live framework
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.Util import find_if
from MainSelectorComponent import MainSelectorComponent #this class will allow us to handle several modes
from ConfigurableButtonElement import ConfigurableButtonElement

class keylab88(ControlSurface):
	""" Script for Arturia's SparkLE Controller """

	def __init__(self, c_instance):
		ControlSurface.__init__(self, c_instance)
		with self.component_guard(): # this line allows you to instanciate framework classes
			is_momentary = True # all our controlls will be momentary
			self._suggested_input_port = 'px700'
			self._suggested_output_port = 'px700'

			"definition of buttons represented by the keyboard notes"
			select_buttons = [] # row of buttons launching the clips of a track
			for index in range(10):
				button = ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 20+index)
				button.name = '_Clip_' + str(index) + '_Button'
				select_buttons.append(button)

			"buttons sound and multi are the buttons choosing he mode"
			mode_buttons = [ ConfigurableButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 118+index) for index in range(2) ]
			mode_buttons[0].name = 'Sound_Mode'
			mode_buttons[1].name = 'Multi_Mode'

			"knobs definition"
			bank1_controls = []
			for index in range(10):
				control = EncoderElement(MIDI_CC_TYPE, 0, 74+index, Live.MidiMap.MapMode.relative_binary_offset)
				control.name = "_Param_"+str(index)+"_control"
				bank1_controls.append(control)

			bank2_controls = []
			for index in range(10):
				control = EncoderElement(MIDI_CC_TYPE, 0, 74+index, Live.MidiMap.MapMode.relative_binary_offset)
				control.name = "_Param_"+str(index)+"_control"
				bank2_controls.append(control)

			bank1_faders = []
			for index in range(4):
				control = EncoderElement(MIDI_CC_TYPE, 0, 73+index, Live.MidiMap.MapMode.absolute)
				control.name = "_Param_"+str(index)+"_control"
				bank1_faders.append(control)
			for index in range(5):
				control = EncoderElement(MIDI_CC_TYPE, 0, 80+index, Live.MidiMap.MapMode.absolute)
				control.name = "_Param_"+str(index)+"_control"
				bank1_faders.append(control)

			bank2_faders = []
			for index in range(4):
				control = EncoderElement(MIDI_CC_TYPE, 0, 67+index, Live.MidiMap.MapMode.absolute)
				control.name = "_Param_"+str(index)+"_control"
				bank2_faders.append(control)
			for index in range(5):
				control = EncoderElement(MIDI_CC_TYPE, 0, 87+index, Live.MidiMap.MapMode.absolute)
				control.name = "_Param_"+str(index)+"_control"
				bank2_faders.append(control)

			self._selector = MainSelectorComponent(tuple(select_buttons), tuple(mode_buttons), tuple(bank1_controls), tuple(bank2_controls), tuple(bank1_faders), tuple(bank2_faders) , self)
			self._selector.name = 'Main_Modes'
			# self.set_highlighting_session_component(self._selector._session)

			self.log_message("SparkLE Loaded !")


	def disconnect(self):
		ControlSurface.disconnect(self)

	def handle_sysex(self, midi_bytes):
		result = find_if(lambda (id, _): midi_bytes[:len(id)] == id, self._forwarding_long_identifier_registry.iteritems())
		if result != None:
			id, control = result
			control.receive_value(midi_bytes[len(id):-1])
		else:
			self.log_message('Got unknown sysex message: ', midi_bytes)
