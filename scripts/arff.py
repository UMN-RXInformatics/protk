#!/usr/bin/env python
"""
arff.py : ARFF output script for ProTK 2
"""

import os,sys
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
    print("""``arff.py`` is ProTK's ARFF generation script. It is configured using either command-line switches or a configuration file specified by the ``--config=<file>`` switch.

    Options
    -------

    * ``--config=<file>``: The configuration file to use to configure the ARFF generator
    * ``--target-tier=<string>``: The type of prosodic event (word, phoneme, frame, etc.) to use for ARFF output
    * ``--context=<integer>``: The number of events ahead and behind to use as context in the ARFF
    * ``--truth-tier=<string>``: The type of prosodic event to search for events matching the ``--truth-targets`` option
    * ``--truth-targets=<comma-separated-list-of-strings>``: The content of prosodic events to use as truth intervals in file generation
    * ``--targets=<comma-separated-list-of-strings>``: The content of prosodic events to look for to determine YES/NO values
    * ``--context=<integer>``: the number of units of analysis (i.e., words or phonemes) before and after the current unit of analysis to output as context
    * ``--exclude=<comma-separated-list-of-strings>``: The content of prosodic events to use as exclusion criteria
    * ``--test=<model-file>``: Set the truth values of all output to YES for creating testing ARFFs and use the model specified by <model-file> as an input to the classifier
    """)
    exit()

CONFIG = None
if opts.has_key("config"):
    if os.path.exists(opts["config"]):
        execfile(opts["config"])

# Create a database connection (and possibly the database itself)
db = DatabaseManager(DATABASE)
create_tables(db.engine)
db_session = db.get_session()

# Check for search options
if opts.has_key("truth-tier") and opts.has_key("truth-targets"):
    sf = opts["truth-targets"].lower().split(',')
    possibles = list(db_session.query(ProsodyEntry).filter(ProsodyEntry.ptype==opts["truth-tier"]))
    search = [i for i in possibles if i.data.lower() in sf]
else:
    search = False

targets = ["filledpause_um","filledpause_ah"]
if opts.has_key("targets"):
    targets = opts["targets"].lower().split(",")

context_size=ARFF_CONTEXT_SIZE
if opts.has_key("context"):
    context_size = int(opts["context"])

excludes = []
if opts.has_key("exclude"):
    excludes = opts["exclude"].lower().split(',')

passthrough = []
if opts.has_key("passthrough"):
    passthrough = [i.split(":") for i in opts["passthrough"].split('+')]
    for pt in passthrough:
        if len(pt) != 2:
            print("ERROR> --passthrough expects parameters in a comma-separated param-name:arff-type format")
            exit(1)
afs = db_session.query(AudioFile)
all_arff_rows = []
for af in afs:
    
    print """\nAUDIO FILE: ID #%d, in %s""" % (af.id,af.filename)

    if opts.has_key("target-tier"):
        entries = list(db_session.query(ProsodyEntry).filter(ProsodyEntry.ptype==opts["target-tier"]).filter(ProsodyEntry.audio_file==af.id))
    else:
        entries = list(db_session.query(ProsodyEntry))
        

    for entry in entries:
        entry.features = {}
        fs = db_session.query(AnalysisEntry).filter(AnalysisEntry.prosody_entry==entry.id)
        for f in fs:
            entry.features[f.atype] = f

    entry_rows = []

    idx = 0
    for i in range(len(entries)):

        ctx_entries = [None]*(context_size*2+1)
        if i < context_size:
            for z in range((context_size-i)):
                ctx_entries[i+z] = entries[0]
        for z in range(context_size):
            z=z+1
            l = -z
            r = z
            if l <= 0:
                ctx_entries[context_size+l] = entries[i-z]
            if i+r < len(entries):
                ctx_entries[context_size+r] = entries[i+z]
                
        ctx_entries[context_size] = entries[i]        
        entry_rows.append(ctx_entries)
        
    def build_element(element,conf):
        output = []
        for feature_type,attributes in conf.iteritems():
            if element.features.has_key(feature_type):
                feat = element.features[feature_type]
                for a in attributes:
                    if hasattr(feat,a) and feat.undefined != 1:
                        output.append(eval("feat."+a))
            else:
                output = output+(["?"]*len(attributes))
        return output
        
    arff_rows = []

    import base64
        
    for r in range(len(entry_rows)):
        row = []
        for ele in entry_rows[r]:
            if ele != None:
                row = row + build_element(ele,ARFF_FEATURES)
        
        if ARFF_SHOW_WORD and entries[r] != None: row.append(entries[r].data.strip(""" \t"',.""").replace("'","_") if entries[r].data != "" else "BLANK")

        if len(passthrough) != 0:
            for pt in passthrough:
                pt = pt[0]
                if entries[r].extdata != None and entries[r].extdata != "":
                    ex = str2dict(entries[r].extdata)
                    if ex.has_key(pt):
                        row.append(ex[pt])
                    else:
                        row.append("?")
                else:
                    row.append("?")
        
        if entries[r] != None:
            if opts.has_key("test"):
                row.append("YES")
            elif not search:
                y = False
                for t in targets:
                    if t.lower() == entries[r].data.lower():
                        y = True
                        break
                if y: row.append("YES")
                else: row.append("NO")
            else:
                middle = (entries[r].start+entries[r].end)/2
                y = False
                sf = [i for i in search if i.audio_file == af.id]
                for s in sf: 
                    y = False
                    if middle >= s.start and middle <= s.end:
                        print "> Match found:",s.start,middle,s.end
                        y = True
                        break
                if y: row.append("YES")
                else: row.append("NO")
        
        if entries[r].data.lower() not in excludes:
            arff_rows.append(row)

    if len(excludes) != 0:
        print("> Excluded %d items from ARFF out of total %d items (%f%%)"%(len(entries)-len(arff_rows),len(entries),1.0-float(len(arff_rows))/float(len(entries))))

    all_arff_rows = all_arff_rows+arff_rows

arff_rows=all_arff_rows

# Build attribute list
attributes = []
for i in range(context_size*2+1):
    for feat,attrs in ARFF_FEATURES.iteritems():
        for attr in attrs:
            attributes.append(("ctx%d_%s_%s"%(i,feat,attr),"NUMERIC"))
            
if ARFF_SHOW_WORD: attributes.append(("word","STRING"))
if len(passthrough) != 0:
    for pt in passthrough:
        attributes.append((pt[0],pt[1]))

attributes.append(("truth","{YES,NO}"))

#al = len(attributes)
#for r in arff_rows:
#    if len(r) != al:
#        print len(r)

output = generate_arff("langmodel", attributes, arff_rows)

fname = "output.arff"
if opts.has_key("outfile"): fname = opts["outfile"]

f = open(fname,"w")
    
f.writelines([i+"\n" for i in output]+["\n"])
f.close()

if opts.has_key("test"):
    cmd = ARFF_CLASSIFY_COMMAND%(opts["test"],fname,opts["test"])
    print cmd
    os.system(cmd)

    f = open(opts["test"]+".test.classres")
    cr = f.readlines()[5:]
    cr = [i.split()[2] for i in cr if i.strip() != ""]
    af = afs[0]
    entries = list(db_session.query(ProsodyEntry).filter(ProsodyEntry.ptype==opts["target-tier"]).filter(ProsodyEntry.audio_file==af.id))
    i = 0
    rl = []
    for c in cr:
        if c.lower().find("yes") != -1:
            e = entries[i]
            e2 = ProsodyEntry(af, e.start, e.end, 'relabel', "++FILLEDPAUSE++", None)
            rl.append(e2)
        i += 1

    db_session.add_all(rl)
    db_session.commit()
