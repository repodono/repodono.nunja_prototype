What is going on here?
======================

So here we have a mix of Python code and JavaScript code with almost the
same name, and the JavaScript code here doesn't seem to use any normal
boilerplate cruft, what is going on here?

Rationale on usage of AMD without UMD
=====================================

First off, the author would like emphasize on his preference on standard
looking import systems and statements, where namespaces are defined to
be separated by '.'.

He also want to point out that he had spent more than too much time
trying to figure out the best way to approach modularizing the code to
make it work in the most generic case, however given the hideous
fragmentation on the entire JavaScript ecosystem and also the different
requirements that spawned that in the first place resulted in just utter
distaste in trying to make everything play nice with each other (because
they really don't, and this is why UMD exists and looks so ugly and
bloated).

The AMD format and usage by requirejs (plus the text loader) fits my
purpose best, as the intention is to provide a set of JavaScript
"modules" that serve as counterparts to the Python modules under the
same module prefixes and names.  Also the desire for a way to
dynamically fetch templates (a)synchronously during early stages of
development cycle when prototyping benefits greatly if a page reload
triggers a new dynamic template being fetched.  This also saves me time
from having to write a proper loader when the loader itself can defer to
the requirejs text loader.

Of course, other integrators can throw out bits they don't care about,
and if their solution make something that offers something that is laid
out in a way that is analogous to the same "Pythonic" layout, those can
be candidates for consideration of inclusion into this project.

Lastly, it's not like the author haven't tried the other formats.  He
has contemplated just writing things out as CommonJS format and use the
``shim`` option in the ``requirejs.config``, however getting that stack
working with this layout proved to be way too troublesome.

Of course, one can use the CommonJS format, except later during the
development of the final thing it was discovered that CommonJS format
doesn't work at all with r.js.

End of the day is, the raw, unwrapped UMD format to the rescue.  Turns
out the inner wrapped bits is fairly standardized, just that there are
many wrappers to pick from.  So the CommonJS Adapter one was tried and
it didn't work.  As r.js was done in node anyway, that one was tried,
with a modification to return the export object that was being assigned
with the names to be returned.  That worked.

Long story short, js.py was born into this module.  Maybe this should be
spun off into something separate, say CALMJS, or Compile Assemble Link
My JavaScript.  Or even PCALMJS, Pretty Calm... err rather Preprocess...
which the current compile step kind of does, but it really is a
transpiler of some kind.  Though none the less the C toolchain analogy
kind of works here because not treating JavaScript as something that can
be executed immediately and treat it as a language and a compilation
target somehow just made life somewhat easier.  At least for the core
library.

Though, for the actual plugins, of course the names and whatever can be
used, as they will be exposed as proper requirejs AMD style imports with
translations or something, but this one will need to be sorted out later
to assist with the usual live development with some site for UI
prototyping, which was the goal of this project.
