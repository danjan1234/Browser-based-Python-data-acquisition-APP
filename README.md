# Browser based Python data acquisition APP using Bokeh and Flask (Python 3)

## Motivation
The goal of this project is to offer an easy solution for creating simple browser-based data acquisition programs using Python. Data acquisition using Python has gained wider popularity in the scientific society recently. Compared to LabVIEW acquisition programs, Python programs are more readable and easier to manage. However, it is quite a pain to create GUI based program using Python. Modules such as PyQt can get the work done but takes some effort to learn. Hence, I create this project to offer a backbone/template data acquisition programs using browser interface.

## Basic idea
This project comprises of two major parts: one UI class responsible for creating the browser interface and managing UI events; one state machine class for taking care of requests such as instrument configuration, acquisition, data saving, etc. The application class wraps the UI class and the state machine class together. The instances to each class runs in separate threads and share data via the application class variables.

This project makes heavy use of Bokeh interactive plotting module. The Bokeh server can be deployed in two manners: [running Bokeh APPs directly on a Bokeh server or using bokeh.client](http://bokeh.pydata.org/en/latest/docs/user_guide/server.html). This project adopts the latter approach. The advantage is when multiple browsers open the same URL, they will all share the exact same application state. This is very important for a data acquisition program. Furthermore, if multiple applications are running simultaneously, a Flask app is created for easy routing between the applications.

## How to use
### Create your own application class
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
The philosophy is the following: each acquisition program can be considered as a function of outputs on inputs at given conditional parameters. During one acquisition task, one fixes the conditional parameters, vary the inputs and takes measurement of the outputs. Both inputs (`self.inputs`) and parameters (`self.parameters`) are dictionaries of the form `{'key_str', 'pythonic_string'}`. Using Pythonic strings offer powerful flexibility. For example, one can define a variable using an numpy array `np.linspace(0,1,100)`. Traditionally in LabVIEW, one needs to define three variables: start, stop, and number_of_step. One can also use string formatter and create inputs such as `"'np.linspace({}, {}, {})'.format(self.start, self.stop, self.n_step)"`. Note, in order to take advantage of Pythonic strings, inputs and parameters are all Bokeh text inputs. If you think this is boring, check [here](http://bokeh.pydata.org/en/latest/docs/user_guide/interaction/widgets.html) for more fancy Bokeh controls. However, in order to use these controls, one needs to edit the UI class (AcquisitionAPPUI) accordingly.

In addition to inputs and parameters, the following class variables and methods are worth noting:

1. The parameter `self.empty_data` is very important. It is a dictionary and defines the columns that need to be recorded in the final data

1. The five methods `config`, `acquire`, `create_figs`, `save`, `exit` will be called at different states of the application state machine

    1. `config` is called during the Initialization state and will be executed only once when the program starts. It is good for instrument configurations
    1. `acquire` and `create_figs` will be called during the Run state. The Run state runs indefinitely until `self.__stop_request__` is set to True
    1. `save` will be called during the Stop state, which proceeds right after Run state when a stop request is processed. Use it for stopping the instrument and saving the acquired data
    1. `exit` will be called during the Exit state. After this state, the Python program will be terminated. However, the assistant Bokeh and Flask servers will keep on running (see following). Use this function for shutting down / resting instrument

In addition, to assist application development, the following UI events related parameters can be used flexible control of the application:
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

I strongly advise you check the included example `example_apps.py`. Two demo acquisition programs are defined in this file. During acquisition, the first demo waits for all the data becoming available before plotting on the browser. The second demo is a streaming acquisition example -- it receives and plots the acquired data simultaneously.

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

After running all three steps, your default web browser should automatically open two tabs for displaying the two applications. If you cannot see the UI, try to copy the URLs to a different web browser. The two URLs should be: http://localhost:5000/R_vs_H and http://localhost:5000/ErrRate_vs_Volt. A small reminder: whatever after http://localhost:5000/ is actually the provided application name. Since URL cannot have any whitespaces, a valid application name should not contain any whitespaces.

For convenience, I have included a Windows version `batch.bat` file that runs all three steps. It shouldn't be too hard to create a Linux version. Again, pressing the stop button will terminate the Bokeh application. The Bokeh and Flask serve will keep on running.
