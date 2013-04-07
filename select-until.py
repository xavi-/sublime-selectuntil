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

rSelector = re.compile("^(-?)(?:\{(-?\d+)\}|\[(.+)\]|/(.+)/)$")
def find_matching_region(view, sel, selector):
	if selector == "": return None

	result = rSelector.search(selector)

	if result is None: return view.find(selector, sel.end(), sublime.LITERAL)

	groups = result.groups()
	isReverse = (groups[0] == "-")
	num = int(groups[1]) if groups[1] is not None else None
	chars = groups[2]
	regex = groups[3]

	if num is not None:
		if isReverse: return Region(sel.begin() - num, sel.end())
		else: return Region(sel.begin(), sel.end() + num)

	if not isReverse:
		if regex is not None: return view.find(regex, sel.end())
		else: return view.find(chars, sel.end(), sublime.LITERAL)

	if regex is not None: regions = view.find_all(regex)
	else: regions = view.find_all(chars, sublime.LITERAL)

	for region in reversed(regions):
		if region.end() <= sel.begin():
			return Region(region.begin(), sel.end())

def on_change(view, oriSels, selector):
	newSels = []
	for sel in oriSels:
		regFind = find_matching_region(view, sel, selector)

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

class SelectUntilCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		oriSels = [ sel for sel in view.sel() ]

		view.window().show_input_panel(
			"Select Until Next -- chars or [chars] or {count} or /regex/.  Use minus (-) to reverse search:",
			"",
			lambda selector: on_done(view),
			lambda selector: on_change(view, oriSels, selector),
			lambda : on_cancel(view, oriSels)
		)

class ReverseSelectCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		sels = self.view.sel()

		newSels = []
		for sel in sels:
			newSels.append(Region(sel.b, sel.a))

		sels.clear()
		for sel in newSels:
			sels.add(sel)
