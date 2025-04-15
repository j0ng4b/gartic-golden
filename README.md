# GarticGolden (GG)

A Gartic game clone written in Python language.

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/j0ng4b/gartic-golden/test.yml?style=for-the-badge&label=Tests)
](https://github.com/j0ng4b/gartic-golden/actions?query=workflow%3Atest)
[![GitHub Tag](https://img.shields.io/github/v/tag/j0ng4b/gartic-golden?style=for-the-badge)](https://github.com/j0ng4b/gartic-golden/tags)


## Installation

1. Clone the repository:
   git clone https://github.com/j0ng4b/gartic-golden.git

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Unix or macOS
   venv\Scripts\activate     # On Windows

3. Install the dependencies:
   pip install -r requirements.txt

## Running the Program

- Default client mode:
    python main.py

- Server mode:
    python main.py --server

- GUI mode:
    python main.py --gui

You can also set a custom server address and port using command line options:
   - To set server address:
       python main.py --address 127.0.0.1

   - To set server port:
       python main.py --port 8080

If no address or port is specified, the program uses default values from the environment configuration.

