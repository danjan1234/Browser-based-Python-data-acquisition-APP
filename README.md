# Browser based Python data acquisition APP

## Motivation
The goal of this project is to offer an easy solution for creating simple browser-based data acquisition programs using Python. Data acquisition using Python has gained wider popularity in the scientific society recently. Compared to Labview acquisition programs, Python programs are more readable and easier to manage. However, it is quite a pain to create GUI based program using Python. Modules such as PyQt can get the work done but takes some effort to learn. Hence, I create this project to offer a backbone/template data acquisition programs using browser interface.

## Basic idea
This project comprises of two major parts: one UI class responsible for creating the browser interface and managing UI events; one state machine class for taking care of requests such as instrument configuration, acquisition, data saving, etc. The application class wraps the UI class and the state machine class together. The instances to each class runs in separate threads and share data via the application class variables.

This project makes heavy use of Bokeh interactive plotting module. The Bokeh server can be deployed in two manners: [running Bokeh APPs directly on a Bokeh server or using bokeh.client](http://bokeh.pydata.org/en/latest/docs/user_guide/server.html). This project adopts the latter approach. The advantage is when multiple browsers open the same URL, they will all share the exact same application state. This is very important for a data acquisition program. Futhermore, if multiple applications are running simultanuously, a Flask app is created for easy routing between the applications.

## How to use
In order to create browser-based acquisition program, one only needs to work on the application class (AcquisitionAPP). Note the included version is a full-fledged demo application. In order to create a custom application, I advise inheriting this class and override the following attributes and methods:
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
    def acquire(self):      # Acqusition body
    def save(self):         # Things to do when acqusition stops, e.g.,
                            # saving data
    def exit(self):         # Things to do when exiting the application
    def create_figs(self):  # Method to create Bokeh figures
```
The philosophy is the following: each acquisition program can be considered as a function of outputs on inputs at given conditional parameters. During one acquisition task, one fixes the conditional parameters, vary the inputs and takes measurement of the outputs. Both inputs and parameters are dictionary of the form `{'key_str', 'pythonic_string'}`. 
In addition, to assist application development, the following UI eventsrelated parameters can be used with flexibility:
```python
    self.__run_request__    # Request to start the acqusition. Equivalent to
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
