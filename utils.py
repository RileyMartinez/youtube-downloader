from pytube import YouTube
from pytube.exceptions import *
import tkinter.filedialog
import datetime
import os


# Prompts the user for a YouTube URl, handles any invalid inputs, and returns the URL as a string
def get_url():
    while True:
        url = input('URL: ')
        if 'http' not in url:
            url = 'https://www.youtube.com/watch?v={}'.format(url)
        try:
            YouTube(url)
            return url
        except RegexMatchError as e:
            print('Invalid URL: {}'.format(e))


# Browses for download path using tkinter. Returns None if no path specified.
def get_output_path():
    while True:
        browse = str.lower(input('Choose download directory (y/n)? '))
        if browse == 'y':
            root = tkinter.Tk()
            root.withdraw()
            current_dir = os.getcwd()
            output_dir = tkinter.filedialog.askdirectory(parent=root, initialdir=current_dir,
                                                         title='Please select a download directory', mustexist=True)
            if len(output_dir) > 0:
                return output_dir
            else:
                print('No directory was specified.')
        elif browse != 'y' and browse != 'n':
            print('Invalid entry.')
        else:
            print('File will be saved to the default location within the current working directory (videos/audio).')
            break


# Prompt the user if they want to download an audio-only stream
def get_audio_only():
    response = ''
    while response != 'y' and response != 'n':
        response = str.lower(input('Audio only (y/n)? '))
        if response != 'y' and response != 'n':
            print('Invalid entry.')
    if response == 'y':
        return True
    else:
        return False


# List available streams based on users input
def list_streams(url, audio_only=False):
    yt = YouTube(url)
    print('Available streams for {} based on your input:\n'.format(yt.title))
    if audio_only:
        for stream in yt.streams.filter(only_audio=audio_only):
            print('ITAG: {}, File Type: {}, Codec: {}, '
                  'Average Bitrate: {}, File Size: {:.2f}MB'.format(stream.itag, stream.subtype,
                                                            stream.audio_codec, stream.abr, stream.filesize * 1e-6))
    else:
        for stream in yt.streams.filter(progressive=True):
            print('ITAG: {}, File Type: {}, Video Codec: {}, '
                  'Audio Codec: {}, Resolution: {}, '
                  'Framerate: {}, File Size: {:.2f}MB'.format(stream.itag, stream.subtype,
                                                        stream.video_codec, stream.audio_codec,
                                                        stream.resolution, stream.fps, stream.filesize * 1e-6))


# Prompt user for ITAG ID and return the ID converted to an int.
def get_itag():
    while True:
        try:
            itag = int(input('\nTo download a specific stream, enter an ITAG ID from the stream list: '))
            return itag
        except ValueError:
            print('Invalid ITAG ID.')


# Downloads youtube video specified by itag id
def download_video(url, itag, audio_only, output_path=None):
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    yt.register_on_progress_callback(download_progress)

    print('\nDownload Started - {}'.format(yt.title))
    now = datetime.datetime.now()
    dl_string = now.strftime("%m%d%Y_%H%M%S")
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

    if output_path is None:
        if os.name == 'nt':
            dir_sep = '\\'
        else:
            dir_sep = '/'
        if audio_only:
            folder = 'audio'
        else:
            folder = 'videos'
        stream.download(output_path=f'./{folder}', filename_prefix=f'{dl_string}_')
        print('\nDownload Completed - Saved to {}'.format(os.getcwd() + dir_sep + folder))
    else:
        stream.download(output_path=output_path, filename_prefix=f'{dl_string}_')
        print('\nDownload Completed - Saved to {}'.format(output_path))

    print("\nYou just downloaded",
          bcolors.OKBLUE + yt.player_response.get("videoDetails", {}).get("title") + bcolors.ENDC,
          "by", bcolors.OKBLUE + yt.player_response.get("videoDetails", {}).get("author", "unknown") + bcolors.ENDC)
    print("The video is described as:", bcolors.OKBLUE + yt.player_response.get("videoDetails", {}).get(
        "shortDescription") + bcolors.ENDC, "and is",
          bcolors.OKBLUE + str(int((yt.player_response.get("videoDetails", {}).get("lengthSeconds"))) // 60),
          "minutes and", int((yt.player_response.get("videoDetails", {}).get("lengthSeconds"))) % 60,
          "seconds long." + bcolors.ENDC)
    print("This video has",
          bcolors.OKBLUE + "{:,}".format(
              int(yt.player_response.get("videoDetails", {}).get("viewCount"))) + bcolors.ENDC,
          "views as of", bcolors.OKBLUE + dt_string + bcolors.ENDC)


# Download progress functions used for the progress_callback parameter in download_video()
def download_progress(stream, chunk, bytes_remaining):
    bar_length = 50
    file_size = stream.filesize
    prefix = '↳'
    fill = '█'
    suffix = 'complete'
    print_end = '\r'
    current_progress = (file_size - bytes_remaining) / file_size
    percentage = '{0:.1f}'.format(current_progress * 100)
    filled_length = int(bar_length * current_progress)
    bar = fill * filled_length + '-' * (bar_length - filled_length)
    print(f'\r{prefix} |{bar}| {percentage}% {suffix}', end=print_end)


# Class that contains color attribute constants for displayed video stats in download_video()
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
