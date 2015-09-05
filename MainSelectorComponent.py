from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonSliderElement import ButtonSliderElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.MomentaryModeObserver import MomentaryModeObserver
from _Framework.TransportComponent import TransportComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.ToggleComponent import ToggleComponent
from SpecialSessionComponent import SpecialSessionComponent
from TranslationSelectorComponent import TranslationSelectorComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialTransportComponent import SpecialTransportComponent
from StepSequencerComponent import StepSequencerComponent
import time


class MainSelectorComponent(ModeSelectorComponent):
	""" Class that reassigns the buttons on the Spark to different functions """

	def __init__(self, select_buttons, mode_buttons, bank1_controls, bank2_controls, bank1_faders, bank2_faders, parent):
		"verifies that the buttons given are compatible with the selector component"
		assert (len(select_buttons) == 10)
		assert (len(mode_buttons) == 2)
		assert (len(bank1_controls) == 10)
		assert (len(bank2_controls) == 10)
		assert (len(bank1_faders) == 9)
		assert (len(bank2_faders) == 9)
		ModeSelectorComponent.__init__(self)

		"the parent atribute allows us to control the control surface component"
		"it can be used for example to get the currently selected track"
		self._parent = parent

		"definition of all the components we will map buttons with"
		# self._session = SpecialSessionComponent(10, 16)
		self._session.name = 'Session_Control'
		self._mixer = SpecialMixerComponent(9)
		self._mixer.name = 'Mixer_Control'
		# self._transport = SpecialTransportComponent(self)
		# self._transport.name = 'Transport_Control'
		self._device = DeviceComponent()
		self._device.name = 'Device_Control'

		"definition of all the buttons that will be used"
		self._select_buttons = select_buttons
		self._mode_buttons = mode_buttons
		self._bank1_controls = bank1_controls
		self._bank2_controls = bank2_controls
		self._bank1_faders = bank1_faders
		self._bank2_faders = bank2_faders

		self._all_buttons = []
		for button in self._select_buttons + self._mode_buttons:
			self._all_buttons.append(button)

		self._all_buttons = tuple(self._all_buttons)
		self._mode_index=0
		self._previous_mode_index=-1
		self.set_mode_buttons(mode_buttons)
		self._parent = parent
		self._selected_track_index=0
		self._previous_track_index=0
		self._parent.set_device_component(self._device)
		for button in self._all_buttons:
			button.send_value(0,True)

	def disconnect(self):
		for button in self._mode_buttons:
			button.remove_value_listener(self._mode_value)
		for button in self._all_buttons:
			button.send_value(0,True)

		self._select_buttons = None
		self._mode_buttons = None
		self._bank1_controls = None
		self._bank2_controls = None
		self._bank1_faders = None
		self._bank2_faders = None
		ModeSelectorComponent.disconnect(self)

	def _update_mode(self):
		"""check if the mode selected is a new mode and if so update the controls"""
		mode = self._modes_heap[-1][0]
		assert mode in range(self.number_of_modes())
		if self._mode_index==mode or (mode == 2 and not self.song().view.selected_track.has_midi_input):
			self._previous_mode_index=self._mode_index
		else:
			self._mode_index = mode
			for button in self._all_buttons:
				button.send_value(0,True)
			self.update()

	def set_mode(self, mode):
		self._clean_heap()
		self._modes_heap = [(mode, None, None)]

	def number_of_modes(self):
		return 2

	def _update_mode_buttons(self):
		"""lights up the mode buttons if selected"""
		for index in range(self.number_of_modes()):
			if (index == self._mode_index):
				self._modes_buttons[index].turn_on()
			else:
				self._modes_buttons[index].turn_off()

	def update(self):
		"""main method of the class that calls the assignation methods corresponding to the current mode"""
		"""it is called when the mode changes and when the selected track changes"""
		assert (self._modes_buttons != None)
		"links the session to the mixer, so that when change the selected track the session also changes position"
		self._session.set_mixer(self._mixer)
		if self.is_enabled():
			self._update_mode_buttons()
			self._translation_selector.update()

			as_active = True
			as_enabled = True
			self._session.set_allow_update(False)#we dont want the controlls to change while we are updating the assignations

			if (self._mode_index == 0):
				"A: Transport mode"
				"we activate the transport buttons and tha launch scenes buttons"
				#self._parent.log_message("Launching mode")
				self._setup_select_buttons(as_active)

			elif (self._mode_index == 1):
				"B: Mixer mode"
				"we activate the track selection, arm, and mute buttons and the launch clips buttons"
				#self._parent.log_message("Launching clips mode")
				self._setup_select_buttons(not as_active)

			self._previous_mode_index=self._mode_index

			#self._parent.log_message("Updated")


	def _setup_select_buttons(self, as_active):
		"if as_active, we'll assign the pads to track selection and track control buttons"
		"pads 15 and 16 will shift and arm tha selected track"
		for index in range(len(self._select_buttons)):
			select_button = self._select_buttons[index]
			if as_active:
				"we only assign the arm and mute buttons of the selected track"
				#self._parent.log_message("set arm on "+str(index))
				self._mixer.channel_strip(index).set_arm_button(select_button)
			else:
				self._mixer.channel_strip(index).set_select_button(None)


	def _mode_value(self, value, sender):
		"method called each time the value of the mode selection changed"
		"it's been momentary overriden to avoid dysfunctionnement in the framework method"
		new_mode = self._modes_buttons.index(sender)
		if sender.is_momentary():
			#self._parent.log_message(sender.message_identifier())
			if value > 0:
				#self._parent.log_message("value = "+str(value))
				mode_observer = MomentaryModeObserver()
				mode_observer.set_mode_details(new_mode, self._controls_for_mode(new_mode), self._get_public_mode_index)
				self._modes_heap.append((new_mode, sender, mode_observer))
				self._update_mode()
			elif self._modes_heap[-1][1] == sender and not self._modes_heap[-1][2].is_mode_momentary():
				#self._parent.log_message("sender trouve")
				self.set_mode(new_mode)
			else:
				#TODO: comprendre comment le framework est sense fonctionner et remplacer supprimer cet modif du framework
				self.set_mode(new_mode)
				self._update_mode()
		else:
			#self._parent.log_message("boutton pas trouve")
			self.set_mode(new_mode)
