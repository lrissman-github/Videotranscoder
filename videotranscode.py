#requires https://pymediainfo.readthedocs.io/en/latest/  pip install pymediainfo
#requires pyYAML:   pip install PyYAML
debug = 1
# Imports
import yaml #Required to process yaml
import argparse #required to process arguments
import os #Required to be cross platform
import time #Only required for debugging
import sys #Required for sys.exit() calls
import subprocess #REquired to launch programs like ffmpeg and ffprobe
#from pymediainfo import MediaInfo https://pymediainfo.readthedocs.io/en/latest/
#I didnt like it, so i'll write my own.
import fnmatch #Required to match multiple files
from datetime import datetime
import logging # Required for log output
import json # Required to get output from ffprobe
import shutil # Required for moving files

version = '0.1 alpha'
### Functions

def videofoldercheck( str ):
   output(("checking folder ", str),'info')
   if os.path.isdir(str):
       output(("folder exists",str),'info')
   else:
       if os.path.isfile (str):
           output(("ERROR: path specified is a folder, not a file:",str),'info')
           sys.exit("ERROR: path specified is a folder, not a file: ",str)
       os.makedirs(str)
   return

def absolutepath( base, path ):
    if os.path.isabs(path):
        abspath = path
    else:
        abspath = os.path.join (base, path)
    return(abspath)

def output ( message, msgloglevel) :
    sendmessage = 0
    if msgloglevel not in ['debug','warning','info']:
        msgloglevel = 'debug'

    if config['loglevel'] == 'debug': #If loglevel is debug, send all messages
        sendmessage = 1
    elif (config['loglevel'] == 'warning') and ((msgloglevel == 'warning') or (msgloglevel == 'info')): #if loglevel is warning send warning and info
        sendmessage = 1
    elif (config['loglevel'] == 'info') and (msgloglevel == 'info'):
        sendmessage = 1

    if sendmessage == 1:
        print (str(datetime.now()), ' - ',msgloglevel, ' - ', message)
        if msgloglevel == 'info':
            logging.info(message)
        elif msgloglevel == 'warning':
            logging.warning(message)
        elif msgloglevel == 'debug':
            logging.debug(message)
    return;

#def run_command(command):
#    p = subprocess.Popen(command,
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.STDOUT)
#    return iter(p.stdout.readline, b'')

## Configs
with open('config.yaml') as f:
    # use safe_load instead load
    config = yaml.safe_load(f)
    #example print data['Person'].name

    if config['loglevel'] not in ['debug','warning','info']:
        output((' - loglevel value,', config['loglevel'], 'in config file invalid, setting to debug'),'debug')
        config['loglevel'] = 'debug'

logging.basicConfig(filename=config['logfile'],level=logging.DEBUG,format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

output("after yaml load",'debug')
output(config,'debug')
output(("config.mode", config['mode']),'debug')

#Get Arguments
parser = argparse.ArgumentParser(description='This is a video transcoding script')
parser.add_argument('-m', '--mode', help='Processing mode', choices=set(['crf','2pass']) )
parser.add_argument('-s', '--scale', help='Scaling', choices=set(['off','480p','720p','1080p','uhd']))
parser.add_argument('-v', '--vcodec', help='Output video codec', choices=set(['AVC','HEVC','VP9']))
parser.add_argument('-i', '--inputfolder', help='Input video folder')
parser.add_argument('-o', '--outputfolder', help='Output video folder')
args = parser.parse_args()

if args.mode:
    output(("mode argument provided", args.mode),'info')
    config['mode']=args.mode
if args.scale:
    output(("scale argument provided ",args.scale),'info')
    config['scale']=args.scale
if args.vcodec:
    output(("vcodec argument provided ",args.vcodec),'info')
    config['vcodec']=args.vcodec
if args.inputfolder:
    output(("input folder specified ",args.inputfolder),'info')
    if os.path.isdir(args.inputfolder):
        output(("folder exists"),'info')
        config['input']=args.inputfolder
    else:
        output(("folder does not exist, using path in config file"),'info')
if args.outputfolder:
    output(("output folder specified ",args.outputfolder),'info')
    if os.path.isdir(args.outputfolder):
        output(("folder exists"),'info')
        config['output']=args.outputfolder
    else:
        output(("folder does not exist, using path in config file"),'info')

output(("final config after arguments",config),'debug')


#Make paths absolute
print ("Base: ",config['base'])
config['input'] = absolutepath( config['base'], config['input'] )
config['output'] = absolutepath( config['base'], config['output'] )
config['unknown'] = absolutepath( config['base'], config['unknown'] )
config['bad'] = absolutepath( config['base'], config['bad'] )
config['multiaudio'] = absolutepath( config['base'], config['multiaudio'] )
config['tool']['ffmpeg'] = absolutepath(config['base'], config['tool']['ffmpeg'])
config['tool']['ffprobe'] = absolutepath(config['base'], config['tool']['ffprobe'])

#Welcome messages
output('############################','info')
output('##Starting VideoTranscoder##','info')
output('############################','info')
output('https://github.com/lrissman-github/Videotranscoder','info')
output(('Version: ',version),'info')
output('This script is intended to batch transcode video files to a predefined set of bitrates','info')
output('The script will copy audio/video that meets the standards and transcdoe the rest','info')
output('All questions, information and bugreports are handled via GitHub','info')


#Initial Verify processing directories exist, if not create them
videofoldercheck(config['input'])
videofoldercheck(config['output'])
videofoldercheck(config['unknown'])
videofoldercheck(config['bad'])
videofoldercheck(config['multiaudio'])

#intiail verify of existance of required tools
# FFPROBE
if os.path.isfile (config['tool']['ffprobe']):
    output(("FFPRobe exec found"),'debug')
else:
    exitmessage = "FFProbe not found at ",config['tool']['ffprobe']
    output(exitmessage,'info')
    sys.exit(exitmessage)

# FFMPEG
if os.path.isfile (config['tool']['ffmpeg']):
    output(("FFMPEG exec found"),'debug')
else:
    exitmessage = "FFmpeg not found at ",config['tool']['ffmpeg']
    output(exitmessage,'info')
    sys.exit(exitmessage)

filematches = []
for root, dirnames, filenames in os.walk(config['input']):
#    for filename in fnmatch.filter(filenames, config['SupportedInputContainers']):
    output(("config-supportedinput: ",config['SupportedInputContainers']),debug)
    for filename in filenames:
        if filename.lower().endswith(tuple(config['SupportedInputContainers'])):
            output(("matched filename: ",filename),debug)
            filematches.append(os.path.join(root, filename))

output(("file Matches: ",filematches),'debug')
output(("all Filenames:", filenames),'debug')
numfilenames = len(filenames)

############  Enter processor/encoder loop

#Lets process all matches

for filename in filematches:
    #Get list of files from input path, recursive
    #find a good video file
    # still exists
    # not with a lock file
    # a good codec
    output(("Working with: ",filename),'info')
    if not os.path.isfile(filename):
        #Making sure that file was not removed
        output(("File no longer in source folder"),'info')
    basefilename, extension = os.path.splitext(filename)
    lockfile = absolutepath(config['input'], (basefilename + ".LOCK"))
    if os.path.isfile(lockfile):
        output(("Found a lockfile, skipping media file:", lockfile),'info')
        continue

    output(("Will process this file: ",filename),'info')

    # Get Media Info
    command = [config['tool']['ffprobe'],
            "-loglevel",  "quiet",
            "-print_format", "json",
             "-show_format",
             "-show_streams",
             filename
             ]

    pipe = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    out,err = pipe.communicate()
    #    return [x for x in result.stdout.readlines() if "Duration" in x]
    out = out.decode('utf-8')
    mediainfo = json.loads(out)
    if 'streams' not in mediainfo:  #Media has no streams = bad media
        output (('No stream information detected in file: ', filename),'info')
        videofoldercheck(config['bad'])
        shutil.move(filename,os.path.join(config['bad'],os.path.basename(filename)))
        continue
    numaudiostreams = 0
    #SEtup input mediainfo dict
    output('Raw Data from Media Container',debug)
    output(mediainfo,debug)
    containerinfo = {'vCodec':'',  #Video Codec Type
                 'vBitRate':0, #Video Bitrate -- note, sometimes ffprobe does not return a bitrate, then calculate
                 'vWidth':0, #Video Resolution Width
                 'vHeight':0, #Video Resolution Hight
                 'aCodec':'', #Audio Codec -- Note, Script can only process 1 audio stream, if multiple, move to multi
                 'aBitRate':0, #Audio Bitrate
                 'aChannels':0, #Audio Channels
                 'cTitle':'', #Container title -- Always reset to empty for ffmpeg to clear originally stored title
                 'cDuration':0, #Container Duration
                 'cBitRate':0, #container Bitrate
                 'cSize':0 #Container Size
                 }

    containerinfo['cBitRate'] = int(mediainfo['format']['bit_rate'])
    containerinfo['cDuration'] = float(mediainfo['format']['duration'])
    containerinfo['cSize'] = int(mediainfo['format']['size'])

    for stream in mediainfo['streams']:
        output (('Stream Found: ',stream['codec_type']),debug)
        if stream['codec_type'] == 'audio':
            numaudiostreams = numaudiostreams + 1
            output(('Number of Audio Streams :',numaudiostreams),debug)
            containerinfo['aCodec'] = stream['codec_name']
            containerinfo['aChannels'] = int(stream['channels'])
            containerinfo['aBitRate'] = int(stream['bit_rate'])
        if stream['codec_type'] == 'video':
            containerinfo['vCodec'] = stream['codec_name']
            containerinfo['vHeight'] = int(stream['height'])
            containerinfo['vWidth'] = int(stream['width'])
            #Sometimes video channels do not have bitrate, if not included, calculate after all channel processing
            if 'bit_rate' not in stream:
                output("No Bitrate found in ffprobe output",debug)
            else:
                containerinfo['vBitRate'] = int(stream['bit_rate'])
            #IS there a CRF value if the video was CRF encoded
        # other types of streams like subtitles
    if containerinfo['vBitRate'] == 0:  #no bitrate previously found
        containerinfo['vBitRate'] = containerinfo['cBitRate'] - containerinfo['aBitRate']

    if numaudiostreams > 1:
        output(('More than one Audio track Found:', numaudiostreams),debug )
        videofoldercheck(config['multiaudio'])
        shutil.move(filename, os.path.join(config['multiaudio'],os.path.basename(filename)))
        continue
        # Move to "multi folder"
    #End Info Gathering

    #Subtitle extractor
    subtitlecount = -1  #First subtitle is 0
    for stream in mediainfo['streams']:
        if stream['codec_type'] == 'subtitle':
            output('found Subtitle',debug)
            subtitlecount = subtitlecount + 1
            if stream['codec_name'] in config['SupportedInputSubtitles']:
                output (('found supported codec: ',stream['codec_name']),debug)
                output (('language is: ',stream['tags']['language']),debug)
                #Launch FFMEPG to extract subtitle
                if 'language' in stream['tags']:
                    lang = stream['tags']['language']
                else:
                    lang = ''

                if 'title' in stream['tags']:
                    subtitle = stream['tags']['title']
                else:
                    subtitle = ''
                output(('testingoutputfolder', config['output']), debug)
                output(('basefilename ',basefilename),debug)
                subtitlefile = os.path.join(config['output'],(os.path.basename(filename)+'-'+lang+'-'+subtitle+'-'+str(subtitlecount)+'.srt'))
                output (('output subtitle name is: ',subtitlefile),debug)
                subtitlemap = "0:s:"+str(subtitlecount)
                command = [config['tool']['ffmpeg'],
                           "-i", filename,
                           "-map", subtitlemap,
                           "-y",
                            subtitlefile
                           ]
                output (('extract command: ',command),debug)
                cmd = config['tool']['ffmpeg']+" -i "+filename+" -map "+subtitlemap+" -y "+ subtitlefile
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                for line in process.stdout:
                    output(line,'info')
    #END Subtitle Extractor

    #Does video need scale

    #Does video codec match and have good bitrate

    # Does video codec match and have good bitrate
    #Determine transcode type here

    #Transcode here

    #Move transcode results here

output(("End program"),'debug')
