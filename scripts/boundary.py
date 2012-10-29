#!/usr/bin/env python
"""
arff.py : ARFF output script for ProTK 2
"""

import os,sys,os.path
from numpy.ctypeslib import ct
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from protk2.db.core import *
from protk2.db.types import *
from protk2.loaders import *
from protk2.parsers import *
from protk2.fs import *
from protk2.praat import *
from protk2.util import *
from protk2.arff import *
from protk2.config import *
import pickle

opts = parse_args()

if len(sys.argv) == 1 or opts.has_key("help"):
    print("""``boundary.py`` is a helper script for generating boundaries for use with the high-performance frame feature extractor.
    
    * ``--config``: specify a configuration file to use
    """)
    exit()

CONFIG = None
if opts.has_key("config"):
    if os.path.exists(opts["config"]):
        execfile(opts["config"])

if opts.has_key("outname"):
    outname = opts["outname"]

# Create a database connection (and possibly the database itself)
db = DatabaseManager(DATABASE)
create_tables(db.engine)
db_session = db.get_session()

targets = ["filledpause_um","filledpause_ah","++um++","++uh++","++ah++"]
if opts.has_key("targets"):
    targets = opts["targets"].lower().split(",")

afs = db_session.query(AudioFile)

if not opts.has_key("test"): f = open("train.arff","w")
else: f = open("test.arff","w")
f.write("""@RELATION filledpause
@ATTRIBUTE f1_mean NUMERIC
@ATTRIBUTE f1_stdev NUMERIC
@ATTRIBUTE f1_median NUMERIC
@ATTRIBUTE f2_mean NUMERIC
@ATTRIBUTE f2_stdev NUMERIC
@ATTRIBUTE f2_median NUMERIC
@ATTRIBUTE f1_f2_mean NUMERIC
@ATTRIBUTE f1_f2_stdev NUMERIC
@ATTRIBUTE f1_f2_median NUMERIC
@ATTRIBUTE word_duration NUMERIC
@ATTRIBUTE word_pred_sil {YES,NO}
@ATTRIBUTE word_succ_sil {YES,NO}
@ATTRIBUTE truth {YES,NO}
@DATA\n""")

for af in afs:
    
    #print """
    #AUDIO FILE: ID #%d, in %s
    #""" % (af.id,af.filename)

    entries = list(db_session.query(ProsodyEntry).filter(ProsodyEntry.audio_file == af.id).filter(ProsodyEntry.ptype == "word"))
    
    target_entries = []

    idx = 0
    sil = 0
    for e in entries:
        if e.data.lower() in SILENCE:
            idx += 1
            sil += 1
            continue
        if e.data.lower() not in targets:
            truth = 0
        else: truth = 1
        pred = 1
        succ = 1
        if idx != 0:
            if entries[idx - 1].data.lower() in SILENCE: pred = 0
            else: pred = 1
        else: pred = 1
        idx += 1
        if idx < len(entries):
            if entries[idx].data.lower() in SILENCE: succ = 0
            else: succ = 1
        else: pred = 1

        duration = e.end - e.start

        target_entries.append([e.start, e.end, duration, pred, succ, truth])
    with open("boundaries","w") as f:
        f.write('%d\n'%len(target_entries))
        for t in target_entries:
            f.write("%f %f %f %d %d %d\n"%(t[0], t[1], t[2], t[3], t[4], t[5]))
    fmtfile = os.path.dirname(af.filename)+"/output/"+af.basename+".FormantSL"
    print fmtfile
    if not opts.has_key("test"):
        os.system("./formantsl %s boundaries >> train.arff" % fmtfile)
    else:
        os.system("./formantsl-test %s boundaries >> test.arff" % fmtfile)
