import sublime, sublime_plugin

import re
import time

def parse_input(view, input):
	sels = view.sel()
	newSels = []
	for sel in sels:
		regFind = view.find(re.escape(input), sel.begin())

		if regFind is None: continue

		regExpand = sel.cover(regFind)
		newSels.append(regExpand)

	view.add_regions("select-until", newSels, "comment", "", sublime.DRAW_OUTLINED)
	sels.clear()
	for sel in newSels:
		sels.add(sel)

class SelectUntilNextCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view

		view.window().show_input_panel(
			"Select Until Next -- [count] or {chars} or /regex/",
			"",
			lambda input: 0,
			lambda input: parse_input(view, input),
			lambda : 0
		)
