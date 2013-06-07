# Select-Until
Fill a void in your Sublime Text multiple selection capabilities! This plugin allows you to extend each selection until the next instance of a search term, making it super easy to edit multiple pieces of text that are similar but not quite the same enough.

## Usage
`ctrl+shift+s` pulls up an input field, where you can type:

 - `search term` or `[search term]`: for each selection, select up to and including the first occurrence of the search term.
 - `/regex search/`: select through the first occurrence of the regex.
 - `{character count}`: select forward the given number of characters.
 - `-[search term]`: select backwards up to and including the search term.
 - `-/regex/`: backwards regex.
 - `-{character count}`: select backwards a certain number of characters (`{-count}` works too).

`ctrl+shift+r`: reverse all selections (so if the insertion point is at the end of the selection, it is moved to the beginning, and vice versa).
