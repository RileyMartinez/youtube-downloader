import utils

# Main method
def main():
    url = utils.get_url()
    output_path = utils.get_output_path()
    audio_only = utils.get_audio_only()
    if not audio_only:
        video_quality = utils.get_stream_quality()
    if audio_only:
        stream_list = utils.list_streams(url, audio_only)
        if len(stream_list) == 0:
            print('There are no streams available for the options that you specified.')
            return
        itag = utils.get_itag()
        utils.download_video(url, itag, audio_only, output_path)
        utils.print_video_statistics(url)
    elif video_quality == 1:
        progressive = True
        stream_list = utils.list_streams(url, audio_only, progressive)
        if len(stream_list) == 0:
            print('There are no streams available for the options that you specified.')
            return
        itag = utils.get_itag()
        utils.download_video(url, itag, audio_only, output_path)
        utils.print_video_statistics(url)
    else:
        progressive = False
        stream_lists = utils.list_streams(url, audio_only, progressive)
        if not stream_lists[0]:
            print('There are no video streams available for the options that you specified.')
            return
        elif not stream_lists[1]:
            print('There are no audio streams available for the options that you specified.')
            return
        elif not stream_lists:
            print('There are no video or audio streams available for the options that you specified.')
            return
        itags = utils.get_dash_itags()
        utils.mux(url, itags[0], itags[1], output_path)

# Run main
user_input = ''
while user_input != 'n':
    count = 0
    main()
    user_input = str.lower(input('\nWould you like to download another video (y/n)? '))
    if user_input != 'y' and user_input != 'n':
        print('Invalid entry.')
