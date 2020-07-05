from pytube import YouTube
from pytube.exceptions import *
import ffmpeg
import tkinter.filedialog
from datetime import datetime
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
            root.attributes("-topmost", True)
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
            print('File will be saved to the default location within the current working directory (video/audio).')
            break


# Prompt the user if they want to download an audio-only stream
def get_audio_only():
    user_input = ''
    while user_input != 'y' and user_input != 'n':
        user_input = str.lower(input('Audio only (y/n)? '))
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print('Invalid entry.')


# List available streams based on users input
def list_streams(url, audio_only=False, progressive=False):
    yt = YouTube(url)
    print('Available streams for {} based on your input:\n'.format(yt.title))
    if audio_only:
        audio_stream_list = yt.streams.filter(only_audio=audio_only).order_by('bitrate').desc()
        print_audio_streams(audio_stream_list)
        return audio_stream_list
    elif progressive:
        video_stream_list = yt.streams.filter(progressive=True).order_by('resolution').desc()
        print_video_streams(video_stream_list)
        return video_stream_list
    else:
        video_stream_list = yt.streams.filter(adaptive=True, only_video=True).order_by('subtype').desc()
        audio_stream_list = yt.streams.filter(adaptive=True, only_audio=True).order_by('subtype').desc()
        print('--------------------Video Streams--------------------')
        print_video_streams(video_stream_list)
        print('\n--------------------Audio Streams--------------------')
        print_audio_streams(audio_stream_list)
        return video_stream_list, audio_stream_list


def print_audio_streams(stream_list):
    for stream in stream_list:
        print('ITAG: {}, File Type: {}, Codec: {}, '
              'Average Bitrate: {}, File Size: {:.2f}MB'.format(stream.itag, stream.subtype,
                                                                stream.audio_codec, stream.abr,
                                                                stream.filesize * 1e-6))


def print_video_streams(stream_list):
    for stream in stream_list:
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


def get_adaptive_itags():
    while True:
        try:
            video_itag = int(input('\nEnter an ITAG ID from the video stream list: '))
            audio_itag = int(input('Enter an ITAG ID from the audio stream list: '))
            return video_itag, audio_itag
        except ValueError as e:
            print('Invalid ITAG ID:', e)


# Prompt user for either DASH (high quality) or Progressive (lower quality and combined audio/video) streams.
def get_stream_quality():
    while True:
        user_input = int(input('Video Quality Select:\n\n[1] Progressive (<= 720p)\n[2] Adaptive (>= 1080p)\n\n'
                               'Enter selection: '))
        if user_input == 1 or user_input == 2:
            return user_input
        else:
            print('Invalid entry.')


# Downloads youtube video specified by itag id
def download_stream(url, itag, audio_only=False, output_path=None):
    yt = YouTube(url, on_progress_callback=download_progress)
    stream = yt.streams.get_by_itag(itag)
    video_title = yt.player_response.get("videoDetails", {}).get("title")
    print('\nDownload Started - {}'.format(video_title))
    dl_string = datetime.now().strftime("%m%d%Y_%H%M%S")

    if output_path is None:
        if os.name == 'nt':
            dir_sep = '\\'
        else:
            dir_sep = '/'
        if audio_only:
            folder = 'audio'
        else:
            folder = 'video'
        stream.download(output_path=f'./{folder}', filename_prefix=f'{dl_string}_', filename=video_title)
        print('\nDownload Completed - Saved to {}'.format(os.getcwd() + dir_sep + folder))
    else:
        stream.download(output_path=output_path, filename_prefix=f'{dl_string}_', filename=video_title)
        print('\nDownload Completed - Saved to {}'.format(output_path))


def download_and_mux(url, video_itag, audio_itag, output_path=None):
    yt = YouTube(url, on_progress_callback=download_progress)
    video_stream = yt.streams.get_by_itag(video_itag)
    audio_stream = yt.streams.get_by_itag(audio_itag)
    video_type = video_stream.subtype
    audio_type = audio_stream.subtype
    dl_string = datetime.now().strftime("%m%d%Y_%H%M%S")

    print('\nDownloading Video Stream...')
    video_stream.download(output_path='./temp', filename='video')
    print('Downloading Audio Stream...')
    audio_stream.download(output_path='./temp', filename='audio')

    if os.name == 'nt':
        dir_sep = '\\'
    else:
        dir_sep = '/'

    if output_path is None:
        file_path = f'{os.getcwd()}{dir_sep}video{dir_sep}{dl_string}_{video_stream.default_filename}'
        if not os.path.exists('./video'):
            os.makedirs('./video')
    else:
        file_path = f'{output_path}{dir_sep}{dl_string}_{video_stream.default_filename}'

    video_stream = ffmpeg.input(f'./temp{dir_sep}video.{video_type}')
    audio_stream = ffmpeg.input(f'./temp{dir_sep}audio.{audio_type}')

    ffmpeg.output(video_stream, audio_stream, file_path).run(overwrite_output=True)

    os.remove(f'./temp{dir_sep}video.{video_type}')
    os.remove(f'./temp{dir_sep}audio.{audio_type}')

    print_video_statistics(url)


def print_video_statistics(url):
    yt = YouTube(url)
    video_title = yt.player_response.get("videoDetails", {}).get("title")
    video_author = yt.player_response.get("videoDetails", {}).get("author", "unknown")
    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    print("\nYou just downloaded",
          bcolors.OKBLUE + video_title + bcolors.ENDC,
          "by", bcolors.OKBLUE + video_author + bcolors.ENDC)

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
    percent_complete = '{0:.1f}'.format(current_progress * 100)
    filled_length = int(bar_length * current_progress)
    bar = fill * filled_length + '-' * (bar_length - filled_length)
    print(f'{prefix} |{bar}| {percent_complete}% {suffix}', end=print_end)


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

