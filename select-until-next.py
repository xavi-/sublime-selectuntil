import sublime, sublime_plugin

import re

def on_done(view):
	newSels = view.get_regions("select-until")
	view.erase_regions("select-until")

	sels = view.sel()
	sels.clear()
	for sel in newSels:
		sels.add(sel)

def on_change(view, oriSels, text):
	newSels = []
	for sel in oriSels:
		regFind = view.find(re.escape(text), sel.begin())

		if regFind is None: continue

		regExpand = sel.cover(regFind)
		newSels.append(regExpand)

	view.add_regions("select-until", newSels, "comment", "", sublime.DRAW_OUTLINED)

def on_cancel(view, oriSels):
	view.erase_regions("select-until")

	sels = view.sel()
	sels.clear()
	for sel in oriSels:
		sels.add(sel)

class SelectUntilNextCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		oriSels = [sel for sel in view.sel()]

		view.window().show_input_panel(
			"Select Until Next -- chars or {chars} or [count] or /regex/.  Use minus (-) reverse search.",
			"",
			lambda text: on_done(view),
			lambda text: on_change(view, oriSels, text),
			lambda : on_cancel(view, oriSels)
		)
