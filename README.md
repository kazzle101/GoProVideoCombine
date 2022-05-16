# GoPro Video Combine
Python 3 script to combine GoPro videos into one big file using the creation time in the metadata

The GoPro has a weird file naming system, the numbers can get all over the place and non sequential. This utility combines all the files generated 
during your recording into one big file ordered by the creation_time field in the metadata. You wil need ffmpeg and ffprobe installed and available 
on the path, on Debian/Ubuntu type platforms install with:
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install ffmpeg ffprobe
```

## Usage:
```
$ python gpCombine.py --help
usage: gpCombine.py [-h] -s SOURCE -o OUTPUT [-p] [-m] [--delete]

Utility to combine GoPro video files into one large file using the creation_time field in the metadata

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        source directory containing GoPro .mp4 files
  -o OUTPUT, --output OUTPUT
                        output dir/filename.mp4
  -p, --srcpath         save the output file to the same location as the source directory
  -m, --logmetadata     save the metadata as a readable json file
  --delete              delete the original GoPro source files after combining

As well as the output.mp4, the files list, a log file and opionally one json file is saved with the name 
of the output file but with a different extention: .txt, .log and .json. Pre-existing files on the output 
will be deleted before being written anew. ffmpeg and ffprobe need to be installed and available on 
the path.
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
Combining files, this can take a while
  files list: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown.txt
    log file: ~/Video Recordings/Cycle Rides/Chapeltown/chapeltown.log
```



