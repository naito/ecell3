Simple Model
============

About
-----

This is a very simple sample model, intended to introduce E-Cell 3 to beginners.
This model consists of only three molecular species(S, P, E), and one reaction(MichaelisUniUniProcess).

Files and directories
---------------------

* `README.md`  This file
* `simple.em`  Model file(em file) for this model
* `run_session.py`  Session script file that requires `simple.em` in the same directory

Running this model
------------------

* Run the model with EM file.
    * GUI mode  `$ ecell3-session-monitor -f simple.em`
    * Script mode  `$ ecell3-session run_session.py`

* Run the model using script file including EM (without separated EM file).

```
$ ecell3-session one_file_simulation.py
```
