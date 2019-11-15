# WySCHC

## Overview

This is a basic implementation of the SCHC F/R protocol for large packets. It is intended for use in the Sigfox network, but the ultimate 
goal is to use it under *any* LPWAN techology. You can read more about SCHC and its parameters for the Sigfox network
in these links:

https://tools.ietf.org/html/draft-ietf-lpwan-ipv6-static-context-hc-21
https://tools.ietf.org/html/draft-ietf-lpwan-schc-over-sigfox-00

## Structure

The code makes use of Python classes for easier message manipulation. The SCHC messages carry lots of different
parameters inside their headers depending on their types. The classes are grouped inside the "Messages" and the
"Entities" folders.

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
```

These scripts work using bytes: you can use text or image files (it should work with *any* file, but this has not
been put to the test). To try these, open two terminals and first execute the receiver.

```
python receiver.py [PORT]
```

Then immediately execute the sender.

```
python sender.py [IP] [PORT] [FILENAME]
```

As it's an offline testing, the communication shall be completed in no time. The log of both scripts will be
printed on the terminals, so you can see how do they work. The receiver will write an image file, but this is easily 
changed manually modifying the extension of the output file in the code (this will be corrected soon, so the user
won't need to modify any code). Then, the sender will compare the original file with the output. If everything has gone
according to plan, it will print "True" as its last words.

### Sigfox backend execution (offline)

This part of the README assumes that you have a Sigfox backend accound, an activated Pycom board with a SiPy module (or any module that
supports Sigfox sockets), and ATOM with the pymakr plugin installed. Ensure that you can see messages sent by your device in your Sigfox backend. So far this project makes use of the Sigfox network.

Important: This project has not been tested online. The project tried to use the Sigfox network using a Pycom board with a SiPy module, but many communication
errors were had. A more recent module will be used for online testing.

To bypass this problem, here are the instructions to run this project in an offline manner, but using the Sigfox backend
to recover messages using the Sigfox API.

#### Getting API access from Sigfox

* Log in to the Sigfox backend
* Follow the instructions from the following link to grant you
API access. Use Read & Write roles.
  * https://support.sigfox.com/docs/api-credential-creation
* Write your API user's **login** and **password** strings.
* Go to the **Device** tab and write the ID of your device.

You now have the essential information for fetching Sigfox messages from your machine using HTTP requests.
Now we need to send a fragmented message to the Sigfox network.

#### Sending fragments using ATOM and pymakr

Choose a small file that you want to transmit using SCHC F/R over the Sigfox network. This part of the process is
**tedious**, so use a really small file (for this tutorial I used a 52 bytes file.). **You will be sending the fragments
manually**.

The reason you have to do this manually is because I've tried doing it in a loop but the pycom board freezes.

Execute the sender script with the verbose flag:

```
python sender.py [IP] [PORT] [FILENAME] -v
```

You will notice that it prints

```
nth fragment:
<fragment>
Sending...
progress, percent
```

Write down **every fragment** in order. Then open ATOM with the pymakr plugin with your board connected
and execute the following lines, replacing `<YOUR_RCZ>`:

```
from network import Sigfox
import socket
import binascii
import time

sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.<YOUR_RCZ>)
s.setblocking(True)
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
s.settimeout(10)
```

Now, for every fragment you wrote, execute the next line:

```
s.send(<fragment>)
```

Check if the Sigfox network has received the fragment using the Sigfox backend messages tab. If it did, continue. If 
the fragment you just sent does not appear in a while, try again. Repeat until the last fragment.

#### Reassembling the files locally

Now you shall see that the Sigfox backend has received all the fragments. So now we need to reassemble them.

The script for doing this is `receiver_backend.py`. Grab your API credentials and execute the script as follows, 
replacing `[LIMIT]` with the number of fragments you just sent:

```
python receiver_backend.py [DEVICE ID] [LIMIT] [USER] [PASS]
```

This shall fetch the fragments from the Sigfox API using HTTP GET requests, print them on the console and
then start reassembling the packet using SCHC F/R rules, then output an extensionless file. Add the extension
manually.

All this work you did will be automated in the future, I promise.

## Future work

All the process of sending the fragments manually to the network will be automated as soon as I get
a board that doesn't freeze when sending many messages. This will allow to test the SCHC F/R mechanism
online.

## Author

* Diego S. Wistuba La Torre