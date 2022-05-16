# GoPro Video Combine
Python 3 script to combine multiple GoPro videos into one big file.

The GoPro has a weird file naming system, the numbers are in a unfortunate format that needs manipulating to make them sequential, typically 
on the GoPro Hero 6 and above they are:
```
Gezzxxxx.MP4
e = encoding, using: H for AVC encoding and X for HEVC encoding
zz = chapter number,  xxxx = file number
```
To sort the files into the order they were recorded in we need to swap the file number with the chapter number - xxxxzz

An alternative method is also available, to sort by the date and times in the metadata. This is taken from the format.tags.creation_time 
and streams.0.tags.timecode fields, the creation_time has the date and appears to be set when the recording first starts, and the timecode 
is the time when that particular file was created. The problem with this is that the time gets lost if the batter goes flat and you start recording 
again befre it has been picked up from the GPS, or your recording rolls over midnight as the date for all the clips is set when the recording starts.

You will need ffmpeg and ffprobe installed and available on the path, on Debian/Ubuntu type platforms install with:
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install ffmpeg ffprobe
```

## Usage:
```
$python gpCombine.py --help
usage: gpCombine.py [-h] -s SOURCE -o OUTPUT [-p] [-d] [-m] [--delete]

Utility to combine GoPro video files into one large file using their odd file naming convention

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        source directory containing GoPro .mp4 files
  -o OUTPUT, --output OUTPUT
                        output dir/filename.mp4
  -p, --srcpath         save the output file to the same location as the source directory
  -d, --sortbydate      sorts the combined files by dates in the metadata instead of by filename
  -m, --logmetadata     save the metadata as a readable .json file
  --delete              delete the original GoPro source files after combining

As well as the output.mp4, text, log files and opionally a couple of json files are saved with the name of 
the output file but with different extentions: .txt, .log and .json. Pre-exitsing files on the output will 
be deleted before being written anew. ffmpeg and ffprobe need to be installed and available on the path
```
## Example:
```
$ python gpCombine.py -s ~/Video\ Recordings/Cycle\ Rides/Chapeltown/ -o chapeltown.mp4 -p -m
```
### Output:
```
  source dir: ~/Video Recordings/Cycle Rides/Chapeltown/
 output file: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown.mp4
    metadata: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown.json
     numbers: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown_numbers.json
  files list: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown.txt
Combining 23 files, this can take a while...
    log file: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown.log
```



