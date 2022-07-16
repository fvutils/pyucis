#####################################
Best Practices for Recording Coverage
#####################################

This section offers some suggestions on best practices for recording
coverage using the UCIS API. 

Naming Cross Bins
=================
Most of the recorded cross bins will pertain to auto-cross bins
between the coverpoints. Bins have arbirary names, but downstream
tools (expecially the XML interchange format export) depend on
being able to determine the relationship between a cross bin
and its associated coverpoint bins.

The suggested name format for a cross bin is:

.. code::

    <{cp[0].bin},{cp[1].bin},...>

In other words, if the first bin of the first coverpoint is named 'a'
and the first bin of the second coverpoint is named 'b', the cross
bin for these two bins will be named: <a,b>

