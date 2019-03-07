# PCS
A parameter configuration space parser. This parser can read and write files in the format used by SMAC, ParamILS and GPS. It is also used by GPS.

Author: YP
Created: 2019-03-05

See PCS/examples.py for a very limitted example of what can be done with the parser. Note that it currently only prints int he most recent version of the pcs file format, although it has support for reading some older formats. 

You can also manipulate the pcs object yourself, or read the contents. Note that I first created this parser when I was very new to python, so I did a few things in odd ways. For example, I create mock "objects" using dicts, with a "mem" array that tracks the ids of the objects. In this way, nearly every element in the pcs page (including the values of categorical parameters and comments) get parsed and stored as "objects" with ids. This representatiion facilitates the manipulation (removing or adding or modifying parameters or their spaces) of the pcs, or querying properties of the pcs. For example, given a particular parameter configuration, you can then use the function "isActive()" to check to see if a particular child parameter's parents parameter values are set in such a way that the child is active. 
