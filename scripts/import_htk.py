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
    exit(1)

if opts.has_key("config"):
    if os.path.exists(opts["config"]):
        execfile(opts["config"])

db = DatabaseManager(DATABASE)
create_tables(db.engine)
db_session = db.get_session()

if not opts.has_key("audio"):
    print("ERROR> Audio directory does not exist")
    exit(2)

audio_dir = normalize_dir_path(opts["audio"])
load_audio(db_session, audio_dir)


