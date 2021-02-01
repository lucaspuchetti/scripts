# Helping script to adapt one or many files or folders to unix systems.
# It mainly deals with the inconveniencies of using powershell for managing the
# Windows FS.

# Libraries required.
import sys
import os
import codecs
import argparse
import re
import shutil

# Script Constants
BOM_ORDER = ["utf-8-sig" , "utf-16-be" , "utf-16-le"]
BOMS = {"utf-8-sig" : codecs.BOM_UTF8,
        "utf-16-be" : codecs.BOM_UTF16_BE,
        "utf-16-le" : codecs.BOM_UTF16_LE
}
BUFFER_SIZE = 1024*1024 # 1Mb
LINE_ENDINGS = {"CRLF" : b"\r\n",
                "LF" : b"\n"
}
TEXT_FILES = [  ".txt",
                ".py",
                ".sas",
                ".csv",
                ".json",
                ".md",
                ".diff",
                ".patch"
            ]

def _get_argument_parser():
    parser = argparse.ArgumentParser(
        description="Este script permite adaptar archivos creados en el " + \
        "entorno Windows para que puedan ser interpretados correctamente " + \
        "por un servidor Linux. Uso: unixize [FILE OR DIRECTORY]"
        )
    # Handling output options:
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("--verbose", "-v" ,
                    help="Increase output verbosity. Overrides --quiet",
                    action="store_true")
    verbosity.add_argument("--quiet", "-q" ,
                    help="Run without producing output.",
                    action="store_true")
    # Handling action options:
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--unixize","-u",
                    help="Make compatibility changes to text files.",
                    action="store_true")
    action.add_argument("--decode","-d",
                    help="Return the BOM of a file or all files in a directory.",
                    action="store_true")
    action.add_argument("--recode","-r",
                    help="Only make encoding changes to a file.",
                    action="store_true")
    # Other options
    parser.add_argument("--line-ending","-l",
                    help="Set the line ending to change to.",
                    type=str.lower,
                    choices=["lf", "crlf", "linux", "windows"],
                    default="lf")
    parser.add_argument("--recursive","-R",
                    help="Apply changes to subdirectories.",
                    action="store_true")
    # Positional arguments
    parser.add_argument("paths",
                    nargs="*",
                    help="Paths to be worked on.",
                    type=str)
    return parser

def _replace_line_endings(line_end):
    # Creates a function that returns a corrected chunk and the overall
    # size change to handle parsing.
    if line_end == "CRLF":
        def line_replacer(chunk):
            chunk = re.sub(b"\r",b"",chunk)
            chunk = re.sub(b"\n" , LINE_ENDINGS[line_end] , chunk)
            return chunk
    elif line_end == "LF":
        def line_replacer(chunk):
            chunk = re.sub(b"\r",b"",chunk)
            return chunk
    else:
        def line_replacer(chunk):
            return chunk
    return line_replacer

def decode(chunk , verbose=1):
    # Tries to figure out if the file has BOM
    # Input: A file object
    # Output: A string with the BOM key if true, an empty string if false.
    if verbose == 2:
        print("Checking BOM...")
    for bom in BOM_ORDER:
        if chunk.startswith(BOMS[bom]):
            if verbose == 2:
                print("File starts with %s BOM" % bom)
            return bom
    else:
        if verbose == 2:
            print("No BOM in file.")
        return ""

def recode(inFile, verbose=1):
    # Parses inFile, changing encoding (UTF with BOM to UTF). Changes are made
    # in place.
    
    # Checking if there is BOM in the file
    with open(inFile , "rb" ) as r:
        chunk = r.read(BUFFER_SIZE)
        bom = decode(chunk , verbose)
    if bom:
        # Removing the BOM from file.
        outFile = inFile + ".recoded"
        with open(inFile , "r" , encoding=bom) as r:
            with open(outFile , "w" , encoding="utf-8") as w:
                shutil.copyfileobj(r,w,length=BUFFER_SIZE) 
        os.replace(outFile, inFile)
        # We make a second check, because transcoding from UTF16 seems to
        # result in UTF-8 with BOM regardless.
        recode(inFile,verbose)

def unixize(inFile, line_end="" , verbose=1):
    # Parses file, making changes to encoding (UTF with BOM to UTF) and line
    # endings. Changes are passed into a new file, then replaced into the
    # original.

    # Recoding to UTF-8
    recode(inFile,verbose)
    if verbose == 2:
        print("%s recoded to UTF-8" % inFile)
    # Changing line endings
    # Fetch a function to handle line ending replacement.
    line_replacer = _replace_line_endings(line_end)
    outFile = inFile + ".tmp"
    with open(inFile, "rb") as r:
        with open(outFile, "wb") as w:
            chunk = r.read(BUFFER_SIZE)
            while chunk:
                # Replacing line endings.
                chunk = line_replacer(chunk)
                w.write(chunk)
                chunk = r.read(BUFFER_SIZE)
    if verbose == 2:
        print("Line endings changed to %s" % line_end)
    os.replace(outFile,inFile)

def _file_unixize(path, line_end="LF",verbose=1, action="unixize"):
    # Handles files before proccessing.
    if os.path.splitext(path)[1] in TEXT_FILES:
        if verbose >= 1:
            print("%s is being processed" % path)
        if action == "unixize":
            unixize(path,line_end,verbose)
        elif action == "recode":
            recode(path, verbose)
        else:
            with open(path , "rb") as f:
                bom = decode(f.read(BUFFER_SIZE),verbose)
                if verbose == 0:
                    print(bom or "utf-8")
    else:
        if verbose >= 1:
            print("%s is not a text file." % path)

def main(args):
    # Assert paths:
    for path in args.paths:
        os.stat(path)

    # Resolving verbosity
    if args.verbose:
        verbose = 2
        print("verbosity set to 2")
    elif args.quiet:
        verbose = 0
    else:
        verbose = 1

    # Resolving action
    action = ("recode" * args.recode) or \
             ("decode" * args.decode) or \
             "unixize"

    # Resolving line-ending
    if args.line_ending in ("lf","linux"):
        line_ending="LF"
    else:
        line_ending="CRLF"
    if action == "unixize" and verbose == 2:
        print("The line ending used will be %s." % line_ending)
    
    # Processing Files.
    for path in args.paths:
        if os.path.isfile(path):
            _file_unixize(path,
                          line_end=line_ending,
                          verbose=verbose)
        elif os.path.isdir(path):
            if args.recursive:
                for directory, _ , files in os.walk(path):
                    if verbose >= 1:
                        print("Checking %s/..." % directory)
                    for in_file in files:
                        file_path = os.path.join(directory,in_file)
                        if os.path.isfile(file_path):
                            _file_unixize(file_path,
                                          line_end=line_ending,
                                          verbose=verbose,
                                          action=action)
            else:
                for in_file in os.listdir(path):
                    file_path = os.path.join(path,in_file)
                    if os.path.isfile(file_path):
                        _file_unixize(file_path,
                                      line_end=line_ending,
                                      verbose=verbose,
                                      action=action)


if __name__ == "__main__":
    cmd_parser = _get_argument_parser()
    args = cmd_parser.parse_args()
    main(args)
