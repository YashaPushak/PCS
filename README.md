# PCS

A parameter configuration space parser. This parser can read and write files in
the format used by SMAC, ParamILS and GPS. It is also used by GPS.

## Installing PCS

 - Download the latest sources from https://github.com/YashaPushak/PCS
 - While in the main directory, install them with `pip install .` or 
`python setup.py install --user`.

## Using the PCS Parser

    import PCS

    # Read in your pcs file
    PCS.PCS('examples/params-lkh.pcs')

    # Print the file to the console (possibly with a newer format)
    # Note that it prints in the most recent version of the pcs file 
    # format, although it has support for reading some older formats. 
    print(pcs.printDocument())

    # Print the default configuration
    print(pcs.getDefault())
    

See examples/examples.py for a few more examples of what can be done with the
parser.

You can also manipulate the pcs object yourself, or read the contents. However, 
Note that I first created this parser when I was very new to python, so I did a
few things in odd ways. For example, I create mock "objects" using dicts, with 
a "mem" array that tracks the ids of the objects. In this way, nearly every 
element in the pcs page (including the values of categorical parameters and 
comments) get parsed and stored as "objects" with ids. This representatiion 
facilitates the manipulation (removing or adding or modifying parameters or 
their spaces) of the pcs, or querying properties of the pcs. For example, given
a particular parameter configuration, you can then use the function "isActive()"
to check to see if a particular child parameter's parents parameter values are 
set in such a way that the child is active. 

Unfortunately, the fact that I did things in unusual ways means that the
documentation of the functions available in the parser is quite poor at this 
time. In some cases, you may find some helpful inline comments available in
the source code. Sorry for any inconvenience!
