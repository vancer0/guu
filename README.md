# Gaytor.rent Upload Utility

<img title="GUU" alt="GUU" height=400 src="https://github.com/vancer0/guu/raw/main/media/screenshot.png">

## About

Gaytor.rent Upload Utility is a cross-platform open source program that can automatically create, upload and seed torrents for gaytor.rent (former gaytorrent.ru).

## Features

- Automatic upload and seed
- Integration with qBitTorrent
- Project saving and loading
- Automatic login
- Extremely configurable

## Installation

There are two ways to run this program:
1. **Get the executable** for your OS from the [Releases](https://github.com/vancer0/guu/releases) page.

2. **Run the program directly** from the source (make sure both Python 3.10 and Qt are installed on your computer):
    1. Clone the repository `git clone https://github.com/vancer0/guu.git`
    2. Change to the program source directory `cd guu/src`
    3. Install the dependencies `pip install -r requirements.txt`
    4. Run GUU `python3 guu.py` or `python guu.py`

## To-Do

- Drag and Drop functionality for the picture list
- Support more torrent clients
- Pull the categories from the website (instead of storing them as a list in the code)
- Update checker

## License

This software is licensed under the GNU Public License v3.0.
