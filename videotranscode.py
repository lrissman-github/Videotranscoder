#requires https://pymediainfo.readthedocs.io/en/latest/  pip install pymediainfo
#requires pyYAML:   pip install PyYAML
debug = 1
# Imports
import yaml #Required to process yaml
import argparse #required to process arguments
import os #Required to be cross platform
import time #Only required for debugging
import sys #Required for sys.exit() calls
#from pymediainfo import MediaInfo https://pymediainfo.readthedocs.io/en/latest/
#I didnt like it, so i'll write my own.
import fnmatch
from datetime import datetime
import logging

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
config['tool']['mkvextract'] = absolutepath(config['base'], config['tool']['mkvextract'])
config['tool']['mkvmerge'] = absolutepath(config['base'], config['tool']['mkvmerge'])
config['tool']['mediainfo'] = absolutepath(config['base'], config['tool']['mediainfo'])
config['tool']['mediainfotemplate'] = absolutepath(config['base'], config['tool']['mediainfotemplate'])
# ffmpeg: 'tools\ffmpeg.exe'
# mkvextract: 'tools\mkvtoolnix\mkvextract.exe'
# mkvmerge: 'tools\mkvtoolnix\mkvmerge.exe'
# mediainfo: 'tools\mediaInfo_cli\Mediainfo.exe'
# mediainfotemplate: 'tools\mediaInfo_cli\Transcode.csv'

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
if os.path.isfile (config['tool']['mediainfo']):
    output(("mediainfo exec found"),'debug')
else:
    exitmessage = "MediaInfo exe not found at ",config['tool']['mediainfo']
    output(exitmessage,'info')
    sys.exit(exitmessage)
if os.path.isfile (config['tool']['mediainfotemplate']):
    output(("mediainfo template found"),'debug')
else:
    exitmessage = "MediaInfo template not found at ", config['tool']['mediainfotemplate']
    output(exitmessage,'info')
    sys.exit(exitmessage)

filematches = []
for root, dirnames, filenames in os.walk(config['input']):
    for filename in fnmatch.filter(filenames, '*.mp4'):
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
    #Check for subtitles and extract to complete dir

    #Get mediainfo

    #Does video need scale

    #Does video codec match and have good bitrate

    # Does video codec match and have good bitrate
    #Determine transcode type here

    #Transcode here

    #Move transcode results here

output(("End program"),'debug')
