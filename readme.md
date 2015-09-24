LaTeX preprocessor to make commonly used idioms easier to use
=============================================================

This was mainly written for use by myself since I often find myself writing lots of LaTeX equations and
they often don't end up a lot larger than they have to be due to the bloat which LaTeX adds to it, which makes it harder to spot errors while writing them.

Features
-------
* Skip backslashes for common commands in math mode
	- Trigonometric functions (sin, cos, etc.)
	- Greek alphabet, so now you can write $cos(alpha)$ instead of $\cos(\alpha)$
* Replace '*' with '\cdot'
* Use '#', '##' and '###' as shorthands for \section, \subsection and \subsubsection respectively (like # my section)
	- Also supports adding * after the #s as a shorthand for \section*, \subsection*, etc.
* Match ( and ) parens automatically and add \left and \right commands before them.
	- Can be disabled by escaping the parens like '\(' and '\)'
* [key] and a shortcut for \cite{key}. Might have to be changed since brackets are used for a lot of other things.


Examples
--------

$$cos(\frac{alpha}{2})*2$$ => $$\cos\left(\frac{\alpha}{2}\right)\cdot 2$$

# Section
## Subsection
### Subsubsection

#* Section without numbering
