Introduction
============


Muxing pipeline from http://ubuntuforums.org/showthread.php?p=4803648

gst-launch-0.10 filesrc location="video_input.ogg" ! decodebin name="decode" \
    decode. ! queue ! ffmpegcolorspace ! theoraenc quality=32 ! oggmux name=mux ! filesink location="dubbed_output.ogg" \
        filesrc location="audio_input.wav" ! decodebin ! queue ! audioconvert ! vorbisenc ! queue ! mux.
