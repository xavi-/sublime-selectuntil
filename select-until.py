import sublime, sublime_plugin
from sublime import Region

import re

# In ST3, view.find returns Region(-1,-1) if there are no occurrences.
# In ST2, however, it returns None, so we have to check for that.
def safe_end(region):
	if region is None:
		return -1
	return region.end()

def on_done(view, extend):
	if extend:
		newSels = view.get_regions("select-until-extended")
	else:
		newSels = view.get_regions("select-until")
	view.erase_regions("select-until-extended")
	view.erase_regions("select-until")
	view.erase_regions("select-until-originals")

	sels = view.sel()
	sels.clear()
	for sel in newSels:
		sels.add(sel)

	SelectUntilCommand.prevSelector = SelectUntilCommand.temp or SelectUntilCommand.prevSelector

rSelector = re.compile("^(-?)(?:\{(-?\d+)\}|\[(.+)\]|/(.+)/)$")
def find_matching_point(view, sel, selector):
	if selector == "": return -1

	result = rSelector.search(selector)

	if result is None: return safe_end(view.find(selector, sel.end(), sublime.LITERAL))

	groups = result.groups()
	isReverse = (groups[0] == "-")
	num = int(groups[1]) if groups[1] is not None else None
	chars = groups[2]
	regex = groups[3]

	if num is not None:
		if isReverse: return sel.begin() - num
		else: return sel.end() + num

	if not isReverse:
		if regex is not None: return safe_end(view.find(regex, sel.end()))
		else: return safe_end(view.find(chars, sel.end(), sublime.LITERAL))

	if regex is not None: regions = view.find_all(regex)
	else: regions = view.find_all(chars, sublime.LITERAL)

	for region in reversed(regions):
		if region.end() <= sel.begin():
			return region.begin()
	return -1

def on_change(view, oriSels, selector, extend):
	SelectUntilCommand.temp = selector
	extendedSels = []
	newSels = []
	for sel in oriSels:
		point = find_matching_point(view, sel, selector)

		if point is -1: point = sel.b #try to keep this selection the same

		region = Region(point, point)

		extendedSel = sel.cover(region)
		extendedSels.append(extendedSel)

		newSels.append(region)

	view.add_regions("select-until-originals", oriSels, "comment", "", sublime.DRAW_EMPTY)
	if extend:
		view.add_regions("select-until-extended", extendedSels, "entity", "", sublime.DRAW_OUTLINED)
	else:
		view.add_regions("select-until", newSels, "entity", "", sublime.DRAW_EMPTY)

def on_cancel(view, oriSels):
	view.erase_regions("select-until-extended")
	view.erase_regions("select-until")
	view.erase_regions("select-until-originals")

	sels = view.sel()
	sels.clear()
	for sel in oriSels:
		sels.add(sel)

class SelectUntilCommand(sublime_plugin.TextCommand):
	temp = ""
	prevSelector = ""

	def run(self, edit, extend):
		view = self.view
		oriSels = [ sel for sel in view.sel() ]

		v = view.window().show_input_panel(
			"Select Until Next -- chars or [chars] or {count} or /regex/.  Use minus (-) to reverse search:",
			SelectUntilCommand.prevSelector,
			lambda selector: on_done(view, extend),
			lambda selector: on_change(view, oriSels, selector, extend),
			lambda : on_cancel(view, oriSels)
		)
		v.sel().clear()
		v.sel().add(Region(0, len(SelectUntilCommand.prevSelector)))

class ReverseSelectCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		sels = self.view.sel()

		newSels = []
		for sel in sels:
			newSels.append(Region(sel.b, sel.a))

		sels.clear()
		for sel in newSels:
			sels.add(sel)
