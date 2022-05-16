#!/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
import subprocess
import json
from datetime import datetime
import shutil
import sys

_logMetadata = False

# check to see we can do all that we want
def checkDirectoriesAreOK(sourceDir, outputFile):

    if not os.path.exists(sourceDir):
        print (f"Source directory not found: {sourceDir}")
        return False
    if not os.path.isdir(sourceDir):
        print (f"Source location not a directory?: {sourceDir}")
        return False

    if not os.access(sourceDir, os.R_OK):
        print(f"Cannot read from directory: {sourceDir}")
        return False

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("ffmpeg and/or ffprobe is not installed or not on the path")
        return False

    outExt = os.path.splitext(outputFile)[1]
    if not outExt or outExt.lower() != ".mp4":
        outFile = os.path.basename(outputFile)
        print(f"Output file must have the .mp4 extention: {outFile}")
        return False

    fpath = os.path.dirname(outputFile)
    if not fpath or fpath == outputFile:
        fpath = os.getcwd()

    if not os.access(fpath, os.W_OK):
        print(f"Cannot write to directory: {fpath}")
        return False

    if os.path.exists(outputFile):
        os.remove(outputFile)

    ext = [".txt", ".log", ".json", "_numbers.json", "_dates.json"]
    outFile = os.path.splitext(outputFile)[0]
    for e in ext:
        f = outFile+e
        if os.path.exists(f):
            os.remove(f)

    return True

## -p option - saves having to type an output path for the output file
def setOutputPathSameAsSource(sourceDir, outputFile):
    output = os.path.basename(outputFile)    
    return  os.path.join(sourceDir, output)

## get the metadata from the file, return it as json data
def ffprobeFile(file):

    ffprobe = ['ffprobe', '-v', 'quiet', '-print_format', 
               'json', '-show_format', '-show_streams', f'{file}'] 

    p = subprocess.Popen(ffprobe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
    out, err =  p.communicate()
    if len(out)>0:
        result = json.loads(out)
    else:
        result = {}
    if err:
        print("========= error ========")
        print(err)
    return result

def pInfo(a, b):
    print("{:>12}: {}".format(a, b))

def saveMetadataLogFile(type, outputFile, jsonData, listOfFiles):

    if not _logMetadata:
        return

    outFile = os.path.splitext(outputFile)[0]
    outJson = outFile+".json"
    pInfo("metadata",outJson)
    with open(outJson, mode='wt', encoding='utf-8') as file:
        file.write(json.dumps(jsonData, indent=4))

    if not listOfFiles:
        return

    outFileNo = outFile+"_"+type+".json"
    pInfo(type,outFileNo)
    with open(outFileNo, mode='wt', encoding='utf-8') as file:
        file.write(json.dumps(listOfFiles, indent=4, sort_keys=True, default=str))

    return

## returns the list of files, sorted by file name 
def makeListOfFilesByFileName(sourceDir, outputFile):
    ## GoPros unfortunate file naming convention:
    ## https://community.gopro.com/s/article/GoPro-Camera-File-Naming-Convention?language=en_US
    # GHzzxxxx.mp4 or GXzzxxxx.mp4
    # H = AVC encoding, X = HEVC encoding, 
    # P,F,B = other models using chaptered video (see link above)
    # zz = chapter number, xxxx = file number

    jsonData = []
    listOfFiles = []
    onlyThese = ["GX", "GH", "GP", "GF", "GB"]

    for fn in os.listdir(sourceDir):
        if re.search(r'\.mp4$', fn, re.IGNORECASE):
            source = os.path.join(sourceDir, fn)
            gpfile = os.path.splitext(fn)[0]
            enc = gpfile[0:2]
            if enc.upper() not in onlyThese:
                continue                
            if not gpfile[2:].isdigit():
                continue
            metadata = ffprobeFile(source)
            if metadata:
                jsonData.append(metadata)
                # swap the chapter and file numbers to get a sequential number
                id = int(gpfile[4:] + gpfile[2:4]) 
                data = {"file": source, "number": id}
                listOfFiles.append(data)

    listOfFiles = sorted(listOfFiles, key=lambda d: d['number']) 

    saveMetadataLogFile("numbers", outputFile, jsonData, listOfFiles)

    return  listOfFiles

## returns the list of files, sorted by creation date and time in the metadata.
# this has problems - if the time gets reset because of a flat battery and hasn't been picked up again by the 
# GPS on restart, or the recording rolls over midnight (as the metadata["format"]["tags"]["creation_time"] 
# is only set at the start of the recording), then the combined file will be out of sequence.
def makeListOfFilesByDate(sourceDir, outputFile):

    jsonData = []
    listOfFiles = []
    for fn in os.listdir(sourceDir):
        if re.search(r'\.mp4$', fn, re.IGNORECASE):
            source = os.path.join(sourceDir, fn)
           #print(source)
            
            metadata = ffprobeFile(source)
            if metadata:                
                # print(json.dumps(metadata, indent=4))
                try:
                    creationDate = metadata["format"]["tags"]["creation_time"]
                    creationDate = creationDate.split(".")[0]  ## remove the .00000Z from the end
                    dt = datetime.fromisoformat(creationDate)

                    timeCode = metadata["streams"][0]["tags"]["timecode"]
                    h, m, s, ms = map(int, timeCode.split(":"))
                    dt = dt.replace(hour=h, minute=m, second=s, microsecond=ms)

                    data = {"file": source, "date": dt}
                    listOfFiles.append(data)
                    jsonData.append(metadata)
                except:
                    print(f"cannot find creation date for: {source}")
            else:
                print(f"cannot read metadata for: {source}")

    if not listOfFiles:
        return False

    listOfFiles = sorted(listOfFiles, key=lambda d: d['date']) 

    saveMetadataLogFile("dates", outputFile, jsonData, listOfFiles)

    return listOfFiles


# make the log file show nice when viewed
# this is the output from ffmpeg
def fixLogFile(logText):

    logfix = open(logText, "r").read()
    logfix = logfix.replace("\\r","\n")
    logfix = logfix.replace("\\n","\n")
    logfix = logfix.splitlines()
    logList = [s.strip() for s in logfix]

    with open(logText, mode='wt', encoding='utf-8') as file:
        file.write('\r\n'.join(logList))
        file.write('\r\n')

    return

## combine the files
def combineFiles(fileList, outputFile):

    outFile = os.path.splitext(outputFile)[0]
    outList = outFile+".txt"
    logText = outFile+".log"

    pInfo("files list",outList)

    fc = 0
    fl = f"# files list for output: {outputFile}\n"
    for f in fileList:
        fl += "file '"+f["file"]+"'\n"
        fc += 1

    with open(outList, mode="w", encoding='utf-8') as text:
        text.write(fl)        

    print(f"Combining {fc} files, this can take a while...")

    concat = ['ffmpeg', '-f', 'concat','-safe', '0', '-i', f'{outList}', 
              '-c', 'copy', '-map', '0:v', '-map', '0:a', f'{outputFile}']

    p = subprocess.Popen(concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    if len(out) > 0:
        result = True
        with open(logText, mode="ab") as text:
            text.write(out)
    else:
        result = False
    if err:
        with open(logText, mode="ab") as text:
            text.write(err)

    fixLogFile(logText)
    pInfo("log file", logText)

    return result

def deleteSourceFiles(fileList):

    for f in fileList:
        fn = f["file"]
        try:
            os.remove(fn)
        except:
            print(f"Unable to delete: {fn}")

    return

def main():
    global _logMetadata

    desc = """Utility to combine GoPro video files into one large file
              using their odd file naming convention"""

    epil = """As well as the output.mp4, text, log files and opionally a couple of json files 
              are saved with the name of the output file but with different extentions: 
              .txt, .log and .json.
              
              Pre-exitsing files on the output will be deleted before being written anew.

              ffmpeg and ffprobe need to be installed and available on the path."""

    parser = argparse.ArgumentParser(description=desc, epilog=epil)
    parser.add_argument("-s", "--source", type=str,
                    help="source directory containing GoPro .mp4 files", required=True)
    parser.add_argument("-o", "--output", type=str,
                    help="output dir/filename.mp4", required=True)
    parser.add_argument("-p", "--srcpath", action='store_true',
                    help="save the output file to the same location as the source directory")     
    parser.add_argument("-d", "--sortbydate", action='store_true',
                    help="sorts the combined files by dates in the metadata instead of by filename")                    
    parser.add_argument("-m", "--logmetadata", action='store_true',
                    help="save the metadata as a readable .json file")
    parser.add_argument("--delete", action='store_true',
                    help="delete the original GoPro source files after combining")

    args = parser.parse_args()

    sourceDir = str(args.source)
    outputFile = str(args.output)

    if args.srcpath:
        outputFile = setOutputPathSameAsSource(sourceDir, outputFile)

    if args.logmetadata:
        _logMetadata = True

    if not checkDirectoriesAreOK(sourceDir, outputFile):
        return

    pInfo("source dir", sourceDir)
    pInfo("output file",outputFile)        

    if args.sortbydate:
        mp4Files = makeListOfFilesByDate(sourceDir, outputFile)
    else:
        mp4Files = makeListOfFilesByFileName(sourceDir, outputFile)
    if not mp4Files:
        return        

    if not combineFiles(mp4Files, outputFile):
        return

    if args.delete:
        deleteSourceFiles(mp4Files)

    return

if __name__ == "__main__":
    main()
