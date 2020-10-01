# MCP Root CA Python Client
A simple client application written in Python that can be used to interact with the MCP root CA web service. 

## Requirements
* Python 3.8 (earlier versions of Python 3 might also work, but has not been tested)
* OpenSSL - is already installed in most operating systems by default

## Installation 
To install the requirements run ```pip install -r requirements.txt```. 

If you don't want to mix up the installation with your existing Python packages you can choose to install the 
requirements in a virtual environment. How that can be done is described [here](https://docs.python.org/3/tutorial/venv.html). 

## Running the Application
Running the application is as simple as executing ```python main.py <arguments>```. To see what arguments can be 
specified you can run ```python main.py -h```.
