#requires https://pymediainfo.readthedocs.io/en/latest/
#requires pyYAML:   pip install PyYAML
debug = 1
# Imports
import yaml #Required to process yaml
import argparse #required to process arguments
import os #Required to be cross platform

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

print (config)







print("End program")
