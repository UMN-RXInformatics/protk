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
    print("""``ingest_relabel.py`` is used to ingest all relevant data for a fileset (textgrids and audio files). It will parse the textgrids and then generate and run Praat analysis scripts for the audio files. It will also run feature extraction for the desired units of analysis (UOAs) (e.g. phonemes, words, speech segments, etc.) extracted from the text grids. 


    Options
    -------
    General options:

    **WARNING:** directory paths **must** be absolute, otherwise Praat will not properly find files.

    * ``--audio=<directory>``: **required** -- directory containing audio files
    * ``--textgrid=<directory>``: directory containing textgrid files
    * ``--recs=<directory>'': directory containing HTK rec files
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
    audio_dir = AUDIO_PATH
else:
    audio_dir = normalize_dir_path(opts["audio"])
load_audio(db_session, audio_dir)


if opts.has_key("framesize"):
    window_size = None
    frame_size = float(opts["framesize"])
    if opts.has_key("windowsize"): window_size = float(opts["windowsize"])
    
    afs = db_session.query(AudioFile)
    
    for af in afs:
        generate_framing(frame_size, window_size, db_session, af)

NVOWELS = []
for v in VOWELS:
    for i in range(10):
        NVOWELS.append(v+str(i))
        
if opts.has_key("textgrid"):
    txtgrd_dir = opts["textgrid"]
    rec_dir = opts["recs"]
    if dir_exists(txtgrd_dir) and dir_exists(rec_dir):
    
        files = list_file_paths(txtgrd_dir, include=".TextGrid")
        afs = []
        for f in files:
            tmp = db_session.query(AudioFile).filter(AudioFile.basename==noext_name(f))
            if tmp.count() != 0: afs.append(tmp[0])
        for af in afs:
            f = normalize_dir_path(txtgrd_dir)+af.basename+".TextGrid"
            tg_words = [i for i in TextGridParser(f,af).parse()]
            for w in tg_words:
                if w.ptype == "phone":
                    w.centroid = (w.start + w.end) / 2
                else: continue
            
            rec_words = parse_rec(af, normalize_dir_path(rec_dir)+af.basename+".rec")
            for w in rec_words: w.centroid = (w.start + w.end) / 2
            rec_words = [i for i in rec_words if i.data.lower() in FILLED_PAUSE]

            nw = []
            for w in tg_words:
                if w.ptype != "phone":
                    nw.append(w)
                    continue
                if w.data.lower() not in NVOWELS:
                    nw.append(w)
                    continue
                for p in rec_words:
                    if abs(p.centroid - w.centroid) < 0.2:
                        print w.data, "-->", p.data
                        w.data = p.data
                    nw.append(w)


            db_session.add_all(nw)
            db_session.commit()

print("> Relabeled data ingest completed.")
