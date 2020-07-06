# WySCHC

## Overview

This is a basic implementation of the SCHC F/R protocol for large packets and an integration with the Google Cloud
Platform (GCP) framework, using Cloud Functions and Cloud Storage.
It is intended for use in the Sigfox network, but the ultimate goal is to use it under *any*
LPWAN techology. You can read more about SCHC and its parameters for the Sigfox network
in these links:

* https://www.rfc-editor.org/rfc/rfc8724.html
* https://tools.ietf.org/html/draft-ietf-lpwan-schc-over-sigfox-00

## Structure

The code makes use of Python classes for easier message manipulation. The SCHC messages carry lots of different
parameters inside their headers depending on their types. The classes are grouped inside the "Messages" and the
"Entities" folders. I'm currently working in the codes found inside the "WIP" folder, so they shall be ignored for the time being.

This code also uses GCP methods (more on this soon...)

### Messages

This directory contains the ACK, Fragment and Header classes. ACK and Fragments are the two main types of messages
used in the SCHC F/R protocol. The Header is used in the Fragment class to distinguish the header of the fragment.

### Entities

This directory contains the Fragmenter, Protocol, Reassembler and Sigfox classes. The Fragmenter and Reassembler
are the two main fragment processors in use for this project. Protocol is a class that shall act as a superclass for
every SCHC profile. So far, the Sigfox class inherits from Protocol.

## Getting started

First of all, clone the repo using the `git clone` command.

```
git clone github.com/wituwitu/WySCHC.git
```

The fundamentals of SCHC F/R have been implemented using purely offline testing. The integration with the Sigfox
network comes within the ATOM code execution.

### Offline testing

The two main scripts are the sender and receiver. For offline testing, the reccomended values are:

```
IP: 127.0.0.1
PORT: 8889
FILENAME: your_file.extension
UPLINK LOSS RATE: Any integer between 0 and 99
```

These scripts work using bytes: you can use text or image files (it should work with *any* file, but this has not
been put to the test). To try these, open two terminals and first execute the receiver. The uplink loss rate is an integer between 0 and 99
and probability of the loss of a SCHC packet. Inside the code you will find that this only applies for non-SCHC-ACK-Request packages. This shall be corrected
as the project keeps progressing.

```
python receiver.py [PORT] [UPLINK LOSS RATE]
```

Then execute the sender. [FILENAME] was tested with many kinds of files, but now the restriction of the maximum number of windows
was added, so `example.txt` is the optimal file to be treated with this implementation.

```
python sender.py [IP] [PORT] [FILENAME] [-hv]
```

As it's an offline testing, the communication shall be completed in no time. Many directories and subdirectories will
be created. The log of both scripts will be printed on the terminals, so you can see how they work. The receiver will 
write a text file, but this is easily 
changed manually modifying the extension of the output file in the code. Then, the sender will compare the original 
file with the output. If everything has gone
according to plan, it will print "True" as its last words.

## Online testing

This project is currently being tested within the GCP framework. More on this soon.

## Author

* Diego S. Wistuba La Torre (wistuba at niclabs dot com)