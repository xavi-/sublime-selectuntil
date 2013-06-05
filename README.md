# Select-Until
Fill a void in your Sublime Text multiple selection capabilities! This plugin allows you to extend each selection until the next instance of a search term, making it super easy to edit multiple pieces of text that are similar but not quite the same enough.

## Usage
`ctrl+shift+s` pulls up an input field, where you can type:

 - `search term` or `[search term]`: extend each selection up through the first occurrence of the search term.
 - `/regex search/`: extend through the first occurrence of the regex.
 - `{character count}`: extend forward the given number of characters.
 - `-[search term]`: extend backwards up to and including the search term.
 - `-/regex/`: backwards regex.
 - `-{character count}`: extend backwards a certain number of characters (`{-count}` works too).

`ctrl+shift+r`: reverse all selections (so if the insertion point is at the end of the selection, it is moved to the beginning, and vice versa).

You can also add your own keybinding and set the "extend" argument to false to just move the selections instead of extending them.
