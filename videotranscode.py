#requires https://pymediainfo.readthedocs.io/en/latest/  pip install pymediainfo
#requires pyYAML:   pip install PyYAML
debug = 1
# Imports
import yaml #Required to process yaml
import argparse #required to process arguments
import os #Required to be cross platform
from os import walk #required to get files.. odd it didnt come in with import os
import sys #Required for sys.exit() calls
#from pymediainfo import MediaInfo  #https://pymediainfo.readthedocs.io/en/latest/#
  #I didnt like it, so i'll write my own.

### Functions

def videofoldercheck( str ):
   print("checking folder ", str)
   if os.path.isdir(str):
       print("folder exists")
   else:
       if os.path.isfile (str):
           sys.exit("ERROR: path specified is a folder, not a file: ",str)
       os.makedirs(str)
   return;

def absolutepath( base, path ):
    if os.path.isabs(path):
        abspath = path
    else:
        abspath = os.path.join (base, path)
    return(abspath);


## Configs
with open('config.yaml') as f:
    # use safe_load instead load
    config = yaml.safe_load(f)
    #example print data['Person'].name
if debug ==  1:
    print ("after yaml load")
    print (config)
    print ("config.mode", config['mode'])

#Get Arguments
parser = argparse.ArgumentParser(description='This is a video transcoding script')
parser.add_argument('-m', '--mode', help='Processing mode', choices=set(['crf','2pass']) )
parser.add_argument('-s', '--scale', help='Scaling', choices=set(['off','480p','720p','1080p','uhd']))
parser.add_argument('-v', '--vcodec', help='Output video codec', choices=set(['AVC','HEVC','VP9']))
parser.add_argument('-i', '--inputfolder', help='Input video folder')
parser.add_argument('-o', '--outputfolder', help='Output video folder')
args = parser.parse_args()

if args.mode:
    print ("mode argument provided", args.mode)
    config['mode']=args.mode
if args.scale:
    print ("scale argument provided ",args.scale)
    config['scale']=args.scale
if args.vcodec:
    print("vcodec argument provided ",args.vcodec)
    config['vcodec']=args.vcodec
if args.inputfolder:
    print ("input folder specified ",args.inputfolder)
    if os.path.isdir(args.inputfolder):
        print ("folder exists")
        config['input']=args.inputfolder
    else:
        print ("folder does not exist, using path in config file")
if args.outputfolder:
    print ("output folder specified ",args.outputfolder)
    if os.path.isdir(args.outputfolder):
        print ("folder exists")
        config['output']=args.outputfolder
    else:
        print ("folder does not exist, using path in config file")

print ("final config after arguments",config)

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

#Initial Verify processing directories exist, if not create them
videofoldercheck(config['input'])
videofoldercheck(config['output'])
videofoldercheck(config['unknown'])
videofoldercheck(config['bad'])
videofoldercheck(config['multiaudio'])

#intiail verify of existance of required tools
if os.path.isfile (config['tool']['mediainfo']):
    print ("mediainfo exec found")
else:
    exitmessage = "MediaInfo exe not found at ",config['tool']['mediainfo']
    sys.exit(exitmessage)
if os.path.isfile (config['tool']['mediainfotemplate']):
    print("mediainfo template found")
else:
    exitmessage = "MediaInfo template not found at ", config['tool']['mediainfotemplate']
    sys.exit(exitmessage)

############  Enter processor/encoder loop

while True:
    #Get list of files from input path, recursive
    f = []
    for (dirpath, dirnames, filenames) in walk(config['input']):
        f.extend(filenames)
        break
    print (filenames)

    #find a good video file
        # good = a supportable container
        # a good codec
        # not with a lock file

    for (filename) in filenames:
        basefilename, extension = os.path.splitext(filename)
        # check for media container
        if extension not in config['SupportedInputContainers']:
            print ("extension not on supported container list",filename)
            continue
        #check for lock file
        lockfile = absolutepath(config['input'],(basefilename+".LOCK"))
        if os.path.isfile(lockfile):
            print ("found lockfile, moving on ", lockfile)


        #end of all files
print("End program")
