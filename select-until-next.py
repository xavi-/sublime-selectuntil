import sublime, sublime_plugin
from sublime import Region

import re

def on_done(view):
	newSels = view.get_regions("select-until")
	view.erase_regions("select-until")

	sels = view.sel()
	sels.clear()
	for sel in newSels:
		sels.add(sel)

rSelector = re.compile("^(-?)(?:\[(-?\d+)\]|\{(.+)\}|/(.+)/)$")
def find_matching_region(view, sel, selector):
	result = rSelector.search(selector)

	if result is None: return view.find(re.escape(selector), sel.begin())

	groups = result.groups()
	isReverse = (groups[0] == "-")
	numVal = int(groups[1]) if groups[1] is not None else None
	chars = re.escape(groups[2]) if groups[2] is not None else None
	regex = groups[3] if groups[3] is not None else None

	if numVal is not None:
		if isReverse: return Region(sel.begin() - numVal, sel.end())
		else: return Region(sel.begin(), sel.end() + numVal)

	if not isReverse and (chars is not None or regex is not None):
		return view.find(chars or regex, sel.begin())

	for region in reversed(view.find_all(chars or regex)):
		if region.end() <= sel.end():
			return Region(region.begin(), sel.end())

def on_change(view, oriSels, text):
	newSels = []
	for sel in oriSels:
		regFind = find_matching_region(view, sel, text)

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
