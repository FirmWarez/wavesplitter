import getopt, sys

headeroffset = 36       #additional size for full chunk size, wave/riff header minus first four bytes

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
def usage():
    # print sys.argv[0] + " (version: " + str(__version__) + ")"
    # print sys.argv[0] + " (-m s -p <port> | -m b -p <port> -n <name> | -m p -n <name> | -m a -p <port>]) (-a <apdu> | -s <file> | -f <file>) [-c <count> -v] " 
    print ("")
    print ("This script reads a wave file, splits it in to chunks, and saves each chunk as a wave file.")
    print ("")
    print ("  -h, --help      print this help")
    print ("  -v, --verbose   print verbose output")
    print ("  -f, --file      APDU input data file")
    print ("  -c, --count     loop count, default=1, 0=>unlimited")
    print ("")
    print ("")
    exit(1)

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
def print_riff_header(riffheader):
    riff = bytearray(riffheader[0:4])
    chunksize = bytearray(riffheader[4:8])
    fileformat = bytearray(riffheader[8:12])
    subchunk1id = bytearray(riffheader[12:16])
    subchunk1size = bytearray(riffheader[16:20])
    audioformat = bytearray(riffheader[20:22])
    numchannels = bytearray(riffheader[22:24])
    samplerate = bytearray(riffheader[24:28])
    byterate = bytearray(riffheader[28:32])
    blockalign = bytearray(riffheader[32:34])
    bitspersample = bytearray(riffheader[34:36])
    subchunk2id = bytearray(riffheader[36:40])
    subchunk2size = bytearray(riffheader[40:44])

    print ("Chunk ID: ", riff)
    print ("Chunk Size: ", int.from_bytes(chunksize, byteorder='little'))
    print ("Format: ", fileformat)
    print ("Subchunk 1 ID: ", subchunk1id)
    print ("Subchunk 1 size: ", int.from_bytes(subchunk1size, byteorder='little'))
    print ("Audio format: ", int.from_bytes(audioformat, byteorder='little'))
    print ("Number of channels: ", int.from_bytes(numchannels, byteorder='little'))
    print ("Sample rate: ", int.from_bytes(samplerate, byteorder='little'))
    print ("Byte rate: ", int.from_bytes(byterate, byteorder='little'))
    print ("Block align: ", int.from_bytes(blockalign, byteorder='little'))
    print ("Subchun2 ID: ", subchunk2id)
    print ("Subchunk 2 size: ", int.from_bytes(subchunk2size, byteorder='little'))

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
def main():
    print("Hey yo hey")

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hvf:c:",["help", "verbose", "file=", "count="])
    except getopt.GetoptError as err:
        print (err)
        usage()
        
    verbose = False
    inputfilename = None
    numberchunks = 0

    print(opts)
    print (args)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-f", "--file"):
            inputfilename = arg
        elif opt in ("-c", "--count"):
            print(arg)
            numberchunks = int(arg)
        else:
            print("Unknown opt")
            usage()

    if inputfilename == "":
        print ("Must have an input file name")
        usage()

    if numberchunks == 0:
        print ("Must specify number of output chunks")
        usage()

    if verbose:
        print ("Attempting to open ", inputfilename)

    try:
        wavefile = open(inputfilename, "rb")
    except:
        print ("Can not open file")
        usage()

    waveheader = wavefile.read(44)

    if verbose:
        print ("Wave file to parse: ", wavefile.name)
        print ("")
        print ("Input file RIFF/WAVE header information:")
        print_riff_header(waveheader)

    riff = bytearray(waveheader[0:4])
    chunksize = bytearray(waveheader[4:8])
    fileformat = bytearray(waveheader[8:12])
    subchunk1id = bytearray(waveheader[12:16])
    subchunk1size = bytearray(waveheader[16:20])
    audioformat = bytearray(waveheader[20:22])
    numchannels = bytearray(waveheader[22:24])
    samplerate = bytearray(waveheader[24:28])
    byterate = bytearray(waveheader[28:32])
    blockalign = bytearray(waveheader[32:34])
    bitspersample = bytearray(waveheader[34:36])
    subchunk2id = bytearray(waveheader[36:40])
    subchunk2size = bytearray(waveheader[40:44])

    fullwavedatasize = int.from_bytes(subchunk2size, byteorder='little')
    choppedwavesize = int(fullwavedatasize/numberchunks)

    if verbose:
        print ("")
        print ("Full wave data size: ", fullwavedatasize)
        print ("Section size:", choppedwavesize )
        print ("")

    outputheader = waveheader
    outputchunksize = choppedwavesize + headeroffset
    outputchunkbytes = bytearray(outputchunksize.to_bytes(4, byteorder="little"))
    outputwavebytes = bytearray(choppedwavesize.to_bytes(4, byteorder="little"))

    outputheader = riff + outputchunkbytes + fileformat + subchunk1id + subchunk1size + audioformat + numchannels + samplerate + byterate + blockalign + bitspersample  + subchunk2id + outputwavebytes

    if verbose:
        print ("Output file RIFF/WAVE header information:")
        print_riff_header(outputheader)


    for x in range(numberchunks):    
        filename = "chunk" + str(x) + ".wav"
        if verbose:
            print("Creating output file ", filename)
        outputfile = open(filename, "wb")
        outputfile.write(outputheader)
        outputchunk = wavefile.read(choppedwavesize)
        outputfile.write(outputchunk)
        outputfile.close

    wavefile.close


#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
if __name__ == '__main__':
    main()
