# polycut api
A tiny REST API that cuts polygons along a plane


## Pre-requisites

- python 3.10


## Usage

```console

// clone the repo
git clone git@github.com:dominikganghofer/cut-polygon-api.git
cd cut-polygon-api

// optional: create a virtual environment
virtualenv venv
source venv/bin/activate

// install dependencies
pip install -r requirements.txt

//start the server
python -m uvicorn polycut.main:app --reload

// run tests
python -m pytest

// swagger docs
http://localhost:8000/docs

