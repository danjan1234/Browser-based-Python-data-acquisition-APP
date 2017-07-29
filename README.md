# Browser-based data acquisition via Python, Bokeh, Flask, and State Machine (Python 3)

## Introduction
This project offers a simple way of creating browser-based data acquisition programs in Python.

Recently data acquisition using Python has gained significant popularity in the scientific society. Compared to LabVIEW acquisition programs, Python is free, more legible, and easier to manage. However, the downside is also obvious -- creating a GUI in Python can be a daunting task. Modules such as PyQt can get the work done but takes some effort to learn. Hence, this project is created to address this issue by offering a backbone/template data acquisition program using the browser interface.

The advantages of adopting a web browser interface are two folds:
1. There are many Python modules on web framework available, hence, developing a web browser based application is relatively easy. In this work, Bokeh and Flask are implemented
1. The deployment of a web browser based application is not limited to local machines. One can push it in the serve and run it remotely, which can be handy in a certain circumstances

**Note: there is incompatibility issue with tornado 4.5. If you are running tornado 4.5, please degrade it to version 4.4 by running:**
```sh
pip uninstall tornado
pip install tornado==4.4.2
```

## Basic idea
The main goal of this project is to offer a browser GUI interface. This article assumes you already know in advance how to write a Python script for data acquisition. Tools such as [PyDAQmx](https://pythonhosted.org/PyDAQmx/) and [PyVISA](https://pyvisa.readthedocs.io/en/stable/) are not included. Once you are familiar with writing Python acquisition scripts, this article will assist you converting them to a browser based applications.

Let's first take a look at the code-generated browser GUI:
<div>
  <img src="Flask+Bokeh App UI.jpg" style="max-width: 50%; border:20 box-shadow: none; padding-top:20px" alt="Browser-based Python data acquisition APP UI">
</div>

I'm trying to make the GUI generation process as standard and as simple as possible. The generated browser GUI may not be suitable for a beauty contest but should meet the purpose. To achieve this, the following philosophy is adopted: each acquisition program can be considered as a function of the output responses on the inputs under controlled circumstances (let's call them parameters). In one acquisition task, one fixes the control parameters, varies only the inputs and takes measurement of the outputs. Therefore, at minimum the GUI needs to have the following three components:
1. One field for the inputs and the control parameters
1. A plot that shows the dependence of the outputs on the inputs
1. A text field that display application status and system messages, e.g., error messages

## Requirement
Note this project is for Python 3 only. The following Python modules are required:
1. Bokeh
1. Flask
1. Numpy
1. Pandas

## How to use
### Create your own application class
In order to create browser-based acquisition program, one only needs to work on the application class (AcquisitionAPP from `acquisition_app.py`). Note the included version is a full-fledged demo application. In order to create your own applications, inherit this class and override the following attributes and methods:
```python
self.app_name           # Application name. This parameter is used to
                        # create application URL
self.inputs             # Application inputs. Should be in the form of
                        # {'input_str': 'pythonic_string' ...}
self.parameters         # Other parameters. Should be in the form of
                        # {'parameter_str': 'pythonic_string' ...}
self.empty_data         # Used to tell the program how the empty outputs
                        # look like. It should be of the form:
                        # {'input_str': [], ... 'output_str': [] ...}
self.intro_text         # Static HTML text to be displayed. Used for
                        # showing the name and purpose of the
                        # application
def config(self):       # Things to do during program initialization.
                        # Note this method runs only once after the
                        # program starts
def acquire(self):      # Acquisition body
def save(self):         # Things to do when acquisition stops, e.g.,
                        # saving data
def exit(self):         # Things to do when exiting the application
def create_figs(self):  # Method to create Bokeh figures
```
Both the inputs (`self.inputs`) and control parameters (`self.parameters`) are dictionaries of the form `{'key_str', 'pythonic_string'}`. Using Pythonic strings offers powerful flexibility. For example, one can define a variable using an numpy array `np.linspace(0,1,100)`. Note how annoying it is in LabVIEW -- one needs to define three variables: start, stop, and number_of_step. One can also use string formatter and create fancy inputs such as `eval('np.linspace({}, {}, {})'.format(self.start, self.stop, self.n_step))`. The pythonic strings are parsed using parse(self) function. It returns an error message if parsing fails. Note, in order to take advantage of Pythonic strings, inputs and control parameters are all Bokeh text inputs. If you think this is boring, check [here](http://bokeh.pydata.org/en/latest/docs/user_guide/interaction/widgets.html) for other fancy Bokeh controls. However, in order to integrate these controls with the application, one needs to edit the UI class (AcquisitionAPPUI) and add callback handlers accordingly.

In addition, the following AcquisitionAPP class variables and methods are worth noting:

1. `self.empty_data`: a very important parameter. It is a dictionary and defines the columns that will be recorded in the final data for plotting and saving. The values of this dictionary must all be `[]`. This parameter will be used to generate the structured application outputs `self.outputs`

1. The five methods `config`, `acquire`, `create_figs`, `save`, `exit` will be called at different states of the application state machine (see the last session)

    1. `config` is called during `Initialization` state and will be executed only once when the program starts. It is ideal for instrument configuration, etc.
    1. `acquire` and `create_figs` will be called during `Run` state. This state runs indefinitely until `self.__stop_request__` is set to True. The `acquire` function is the fundamental of the data acquisition. If you have a Python acquisition script, its most part should be placed in this method. In general, there are two modes of acquiring data. The first is to upload the inputs to the instrument in one piece and wait for the response to arrive at once. In this mode, the plots will not be updated until all data become available. The second mode is to stream the inputs to the instrument and stream the outputs back to the program. In this mode, the plots are updated whenever new data become available
    1. `save` will be called during `Stop` state, which proceeds right after `Run` state when a stop request is processed. Use it for stoppinginstrument and saving data. Note, `acquire`, `create_figs` and `save` all need to access the application outputs `self.outputs`. You do not need to define this parameter manually -- it is automatically created using empty data template `self.empty_data`
    1. `exit` will be called during `Exit` state. This is where the program terminates. However, the assistant Bokeh and Flask servers will keep on running. Use this function for shutting down / resetting instrument

To assist application development, the following UI events related variables can be used for flexible control of the application:
```python
self.__run_request__    # Request to start the acquisition. Equivalent to
                        # pressing the Run button
self.__just_started__   # Set True right after the acquisition starts. It's
                        # useful when some specific operations are needed
                        # at the very initial stage of acquisition. It
                        # should be set to False when the specific 
                        # operations are completed
self.__pause_request__  # Request to pause the application
self.__stop_request__   # Request to stop the application
self.__exit_request__   # Request to exit the application
```

I strongly advise you checking the example `example_apps.py`, which includes two demo acquisition programs. These two demos correspond to the two acquisition modes discussed above. Note how `acquire` method is defined differently in the two programs.

### Run the application
Take running `example_app.py` as an example:
    
1. In one terminal, run Bokeh server
```sh
$ bokeh serve --host localhost:5000 --host localhost:5006
```
2. In another terminal, run the Bokeh application
```sh
$ python example_apps.py
```
3. In the 3rd window, run flask (`export` should be `set` in Windows):
```sh
$ export FLASK_APP=app.py
$ flask run
```

Your default web browser should automatically open separate tabs for displaying the two applications. If you cannot see them, try to copy the URLs to a different web browser. The two URLs should be: http://localhost:5000/R_vs_H and http://localhost:5000/ErrRate_vs_Volt. Whatever appears after http://localhost:5000/ is the application name. Since it's used to generate the application URL, a valid application name should not contain any whitespaces.

For convenience, I include a batch file `batch.bat` file that is programed to run the three steps in Windows. It shouldn't be too hard to create a Linux version. Pressing the Exit button only terminates the Bokeh application. Both Bokeh and Flask serves will keep on running.

## Further reading
This section discusses about some of the fundamentals of this project.

The application class (AcquisitionAPP) comprises of two parts: one UI class (AcquisitionAPPUI from `acquisition_app_UI.py`) responsible for creating the browser interface and managing UI events; one class (AcquisitionAPPStateMachine from `acquisition_app_statemachine.py`) for taking care of requests such as instrument configuration, acquisition, data saving, etc. Each application instance has a UI instance and a state machine instance run in separate threads. UI instance and state machine instance share data via variables in the application class instance.

The state machine class has five states:
```python
Initialization:     Good for configuring instrument. It runs only once at the
                    very beginning
Idle:               Waiting for inputs
Run:                Take measurement. This state runs indefinitely until a
                    __stop_request__ is issued
Stop:               The target state after a __stop_request__ is issued. Good
                    for saving data
Exit:               Reset the instrument, close any open sessions, and exit the
                    program safely
```
The state machine first enters `Initialization` state. The code in `Initialization` will only be executed once. The state machine then moves to `Idle` state and waits for user inputs. Depending on the button pressed or UI event variables set, the next state can be `Run`, `Stop`, or `Exit`. In case of `Run` state, it will try to run indefinitely until a `__stop_request__` is issued. The five application class methods `config`, `acquire`, `create_figs`, `save`, `exit` are invoked in different states. For example, `config` is called in `Initialization` state, `save` is called in `Stop` state, etc.

This project makes heavy use of Bokeh interactive plotting module. The Bokeh server can be deployed in two manners: [running Bokeh APPs directly on a Bokeh server or using bokeh.client](http://bokeh.pydata.org/en/latest/docs/user_guide/server.html). This project adopts the latter approach. The advantage is when multiple browsers open the same URL, they will all share the exact same application state. This is very important for a data acquisition program. `flask_app.py` creates a Flask app in order to easily manage multiple acquisition applications.
