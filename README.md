# Airbrakes
This is the repository we use to keep track of all the code we are writing for the Wolf-works Experimental Airbrakes.

The primary device we are using for data collection is the Parker-LORD 3DMCX5-AR. The [MicroStrain Communication Library](https://lord-microstrain.github.io/MSCL/Documentation/Getting%20Started/index.html?python#introduction) provides information on how to interact with sensors developed by LORD Sensing. MSCL has language bindings in C++, .NET (C#, VB, LabView, MATLAB), and Python, we will primarily be using Python for the airbrake code.

Here is the [MSCL Github Repository](https://github.com/LORD-MicroStrain/MSCL) needed to interact with MSCL.

Here is the documentation for the [MSCL API](https://lord-microstrain.github.io/MSCL/Documentation/MSCL%20API%20Documentation/index.html).

## Setup

### Cloning the repo with submodules

Since this repo uses submodules (for [orhelper](https://github.com/Graicc/orhelper)), you need to clone the repo with `git clone --recurse-submodules https://github.com/NCSU-High-Powered-Rocketry-Club/Airbrakes`. If you have already cloned the repo, use `git submodule update --init --recursive` to update submodules.

### OpenRocket Setup

Currently, the ORIL (OpenRocket-in-the-loop) simulation requires the nightly version of [OpenRocket](https://github.com/OpenRocket/OpenRocket). See [this issue](https://github.com/openrocket/openrocket/issues/2443), for the up to date status.
The latest build of OpenRocket can be found on the actions tab, [this version](https://github.com/openrocket/openrocket/actions/runs/7543357295/artifacts/1172510658) is known to work. Make sure to update the `CLASSPATH` in [`_orhelper.py`](/orhelper/orhelper/_orhelper.py) to point to this installation of openrocket.

### Setting Up Your Python Venv

The first thing you should do prior to running your code is set up your virtual environment. To do this open you your terminal and make sure you are in the `Airbrakes` directory. Inside of that directory call the commands:

Install pip3:
```bash
sudo apt install python3-pip
```

Install venv:
```bash
sudo apt install python3-venv
```

Make venv:
```bash
python3 -m venv env
```

to set up your virtual environment in a folder called env. Next you need to set this folder as your interpreter (your IDE might prompt you to do this automatically. If it did not prompt you, to do this in VS Code, press `ctrl+shift+p` to open your command prompt and type in `Python: Select Interpreter`. Press enter and select the one that ends in something like `('env':venv)`.

### Installing Required Packages

In order to install the required packages, open a new terminal in VS Code by pressing ```ctrl+shift+` ```. This terminal will already be in your virtual environment, and simply run the command

```bash
pip3 install -r requirements.txt
```

### Running the Program

Now that you have all the required packages installed, you can run the program by running the command

```bash
python3 main.py
```

or with arguments

```bash
python3 main.py <arguments>
```

To run locally with mocking all hardware, run `python3 main.py -si`. If you only want to mock parts of the airbrakes (e.g. for a [HWIL](https://en.wikipedia.org/wiki/Hardware-in-the-loop_simulation) test), run with `-i`(`--mock_imu`) or `-s`(`--mock_servo`) instead.
