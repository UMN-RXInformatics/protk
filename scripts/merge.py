#!/usr/bin/env python
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

   * ``--base``: the base TextGrid to append the relabeled data to
   * ``--tier``: the tier to select relabels from (i.e., words, phones, etc.)
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

afs = db_session.query(AudioFile)
af = afs[0]

tier = "word"
if opts.has_key("tier"): tier = opts["tier"]
entries = list(db_session.query(ProsodyEntry).filter(ProsodyEntry.ptype==tier).filter(ProsodyEntry.audio_file==af.id))

if not opts.has_key("base"):
    print "> ERROR: Need a TextGrid to merge with"
    exit(2)
f = open(opts["base"])
fl = f.readlines()
fl2 = []
started = False
for l in fl:
    if l.find("[]") != -1: started = True
    if l.find("size") != -1 and l.find("=") != -1 and not started:
        pts = l.split('=')
        count = int(pts[-1])+1
        fl2.append("size = %d" % count)
    else: fl2.append(l[:-1])

hdr = """    item [count]:
		class = "IntervalTier"
		name = "word"
		xmin = 0
		xmax = %f
		intervals: size = %d"""
itm = '''        intervals [%d]:
            xmin = %.2f
            xmax = %.2f
            text = "%s\"'''
emx = max([i.end for i in entries])
fl2.append(hdr % (emx, len(entries)))
i = 0
for e in entries:
    fl2.append(itm % (i, e.start, e.end, e.data))
    i += 1

for l in fl2: print l
