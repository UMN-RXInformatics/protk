#!/bin/bash

DATADIR=/home/pakh0002/ProTK_SALSA/work/

./ingest.py --audio=$DATADIR --textgrid=$DATADIR
./extract.py --audio=$DATADIR --execpraat --formants --shimmer --jitter --pitches --intensities
./aggr.py --config=config

