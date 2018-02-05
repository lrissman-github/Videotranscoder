# Videotranscoder

This project is not functional yet.

**Description:**    
This project will eventually replace my powershell based project.   
The purpose of this project is to create a transcoding script that is windows and linux comaptible and will fit nicely into a Docker container.  

#StoryBoard: 

- Create Settings file
    - Allow for custom directories
    - Allow for setting the allowable 
        - codecs
        - resolutions
        - target bitrate for 2 pass
        - crf for 1 pass
- Create watcher script
    - Intented to be included in a schedular
    - will check for running transcodes
    - will look for new content in input folder
    - Will use mediainfo to get information about file
    - will launch transcodes based on settings using ffmpeg
- consider using CUDA, NVENC, and Intel QuickSync as options
       