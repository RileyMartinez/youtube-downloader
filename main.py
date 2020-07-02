import utils


# Main method
def main():
    url = utils.get_url()
    output_path = utils.get_output_path()
    audio_only = utils.get_audio_only()
    stream_list = utils.list_streams(url, audio_only)
    if len(stream_list) == 0:
        print('There are no streams available for the options that you specified.')
        return
    itag = utils.get_itag()
    utils.download_video(url, itag, audio_only, output_path)


# Run main
user_input = ''
while user_input != 'n':
    count = 0
    main()
    user_input = str.lower(input('\nWould you like to download another video (y/n)? '))
    if user_input != 'y' and user_input != 'n':
        print('Invalid entry.')
