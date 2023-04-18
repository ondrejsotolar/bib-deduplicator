# bib-deduplicator

This is a Python script for merging multiple bibliography files into one. The merged .bib file has unique keys. Found duplicates are stored alongside in a separate file, so no records are lost. The files are parsed using a simple **pyparsing** grammar. I have tried the bibtexparser lib, which parses the records completely, and it fails on multiple counts with the ACL anthology bibtex file. So, I replaced it with simpler pyparsing code which works. Note that processing a big file such as the ACL anthology (42MB) takes a couple of minutes.

Usage:

    python main.py 
        "dir to search for .bib files" 
        "output path"
