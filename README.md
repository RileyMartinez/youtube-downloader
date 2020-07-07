# youtube_downloader
CLI program that implements the pytube3 module to retrieve audio and video streams from YouTube, and downloads them to local storage.

## Installation Instructions
- Install ffmpeg (may require reboot for installation to be recognized)
  - Windows
    - Download and extract ffmpeg: https://ffmpeg.zeranoe.com/builds/
    - Add your ffmpeg/bin location to PATH
  - Linux
    - `sudo apt install ffmpeg` (Debian/Ubuntu)
    - `sudo dnf install ffmpeg` (Fedora/RHEL)
  - Mac
    - `brew install ffmpeg`
- `git clone https://github.com/RileyMartinez/youtube_downloader.git`
- `pip install pipenv` (if pipenv is already installed, skip this step)
- `cd ./youtube_downloader` (cd into your chosen project directory)
- `pipenv shell`
- `pipenv install`
- `pipenv run python main.py`
