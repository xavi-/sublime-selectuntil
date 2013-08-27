import sublime, sublime_plugin
from sublime import Region

import sys
if sys.version_info[0] < 3:
	from edit import Edit
else:
	from SelectUntil.edit import Edit

import re

# In ST3, view.find returns Region(-1,-1) if there are no occurrences.
# In ST2, however, it returns None, so we have to check for that.
def safe_end(region):
	if region is None:
		return -1
	return region.end()

def clean_up(view):
	view.erase_regions("select-until-extended")
	view.erase_regions("select-until")
	view.erase_regions("select-until-originals")

	SelectUntilCommand.input_panel = None
	SelectUntilCommand.first_opened = True

def on_done(view, extend):
	if extend:
		newSels = view.get_regions("select-until-extended")
	else:
		newSels = view.get_regions("select-until")

	sels = view.sel()
	sels.clear()
	for sel in newSels:
		sels.add(sel)

	SelectUntilCommand.prevSelector = SelectUntilCommand.temp or SelectUntilCommand.prevSelector
	clean_up(view)

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

	if not isReverse:
		if num is not None: return sel.end() + num
		elif regex is not None: return safe_end(view.find(regex, sel.end()))
		else: return safe_end(view.find(chars, sel.end(), sublime.LITERAL))

	else:
		if num is not None: return sel.begin() - num
		elif regex is not None: regions = view.find_all(regex)
		else: regions = view.find_all(chars, sublime.LITERAL)

		for region in reversed(regions):
			if region.end() <= sel.begin():
				return region.begin()

	return -1

def negate_selector(selector):
	if selector == "": return selector

	result = rSelector.search(selector)

	if result is None: return True, "-[" + selector + "]"

	groups = result.groups()
	makeReverse = (groups[0] != "-")
	num, chars, regex = groups[1:]

	negateChar = "-" if makeReverse else ""
	if num is not None: return makeReverse, negateChar + "{" + num + "}"
	elif chars is not None: return makeReverse, negateChar + "[" + chars + "]"
	elif regex is not None: return makeReverse, negateChar + "/" + regex + "/"

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
	sels = view.sel()
	sels.clear()
	for sel in oriSels:
		sels.add(sel)

	clean_up(view)

class SelectUntilCommand(sublime_plugin.TextCommand):
	temp = ""
	prevSelector = ""
	input_panel = None
	first_opened = True

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

		# view.window().show_input_panel returns None when input_panel is already shown in subl v2
		if v is not None:
			v.sel().clear()
			v.sel().add(Region(0, v.size()))
			SelectUntilCommand.input_panel = v

		input_panel = SelectUntilCommand.input_panel
		if input_panel and not SelectUntilCommand.first_opened:
			fullRegion = Region(0, input_panel.size())

			isReverse, negSelector = negate_selector(input_panel.substr(fullRegion))
			highlight = Region(1 + (1 if isReverse else 0), len(negSelector) - 1)

			with Edit(input_panel) as edit:
				edit.replace(fullRegion, negSelector)

			input_panel.sel().clear()
			input_panel.sel().add(highlight)

		SelectUntilCommand.first_opened = False;

class ReverseSelectCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		sels = self.view.sel()

		newSels = []
		for sel in sels:
			newSels.append(Region(sel.b, sel.a))

		sels.clear()
		for sel in newSels:
			sels.add(sel)
