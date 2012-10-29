#!/usr/bin/env python
"""
ingest.py : Data ingest script for ProTK 2
"""

import os,sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from protk2.db.core import *
from protk2.db.types import *
from protk2.loaders import *
from protk2.parsers import *
from protk2.fs import *
from protk2.praat import *
from protk2.util import *
from protk2.config import *

opts = parse_args()

if len(sys.argv) == 1 or opts.has_key("help"):
    print("""``ingest.py`` is used to ingest all relevant data for a fileset (textgrids and audio files). It will parse the textgrids and then generate and run Praat analysis scripts for the audio files. It will also run feature extraction for the desired units of analysis (UOAs) (e.g. phonemes, words, speech segments, etc.) extracted from the text grids. 


    Options
    -------
    General options:

    **WARNING:** directory paths **must** be absolute, otherwise Praat will not properly find files.

    * ``--audio=<directory>``: **required** -- directory containing audio files
    * ``--textgrid=<directory>``: directory containing textgrid files
    * ``--framesize=<float>``: generate speech event frames that are <float> seconds long
    * ``--windowsize=<float>``: use with ``--framesize`` to overlap the frames by <float> seconds""")
    exit(1)

if opts.has_key("config"):
    if os.path.exists(opts["config"]):
        execfile(opts["config"])

db = DatabaseManager(DATABASE)
create_tables(db.engine)
db_session = db.get_session()

if not opts.has_key("audio"):
    audio_dir = normalize_dir_path(AUDIO_PATH)
else:
    audio_dir = normalize_dir_path(opts["audio"])
print audio_dir
load_audio(db_session, audio_dir)

if opts.has_key("framesize"):
    window_size = None
    frame_size = float(opts["framesize"])
    if opts.has_key("windowsize"): window_size = float(opts["windowsize"])
    
    afs = db_session.query(AudioFile)
    
    for af in afs:
        generate_framing(frame_size, window_size, db_session, af)
        
if opts.has_key("textgrid"):
    txtgrd_dir = opts["textgrid"]
    load_textgrids(db_session, txtgrd_dir)
