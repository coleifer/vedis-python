#!/bin/bash
gcc -DVEDIS_ENABLE_THREADS=1 -Wall -fPIC -c vedis.c
gcc -shared -Wl,-soname,libvedis.so.1 -o libvedis.so.1.0 vedis.o
ctypesgen.py vedis.h -L ./ -l vedis -o _vedis.py
