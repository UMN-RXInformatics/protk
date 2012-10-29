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
    * ``--execpraat``: run praat analysis
    * ``--scriptdir=<directory>``: directory to output generated Praat scripts to
    * ``--outputdir=<directory>``: directory to output Praat analysis results to

    Feature extraction options:

    **WARNING:** feature extraction will only work if you have already imported or generated speech events using ``ingest.py``.

    * ``--pitches``: load pitch features for all prosodic events
    * ``--intensities``: load intensity features for all prosodic events
    * ``--formants``: load formant features for all prosodic events
    * ``--shimmer``: load shimmer features for all prosodic events
    * ``--jitter``: load jitter features for all prosodic events
    * ``--framesize=<float>``: generate frames of specified size (in seconds) as
      prosodic events for analysis. You must specify the size when using this option.
      * ``--windowsize=<float>``: overlap the frames by the specified size (in seconds). You must specify the size when using this option.""")
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
print audio_dir

script_dir = audio_dir+"script/"
output_dir = audio_dir+"output/"

make_dirs(script_dir)
make_dirs(output_dir)

if opts.has_key("scriptdir"):
    script_dir = normalize_dir_path(opts["scriptdir"])
if opts.has_key("outputdir"):
    output_dir = normalize_dir_path(opts["outputdir"])

normalize = opts.has_key("normalize")

if opts.has_key("execpraat"):
    psr = PraatScriptRunner(audio_dir, script_dir, output_dir)
    psr.generate_scripts()
    psr.run_scripts()
    
if opts.has_key("formants"):
    load_formant_sl(db_session, output_dir, normalize=normalize)
    
if opts.has_key("shimmer"):
    load_shimmers(db_session, output_dir)
    
if opts.has_key("jitter"):
    load_jitters(db_session, output_dir)
    
if opts.has_key("intensities"):
    load_intensities(db_session, output_dir,normalize=normalize)
    
if opts.has_key("pitches"):
    load_pitches(db_session, output_dir,normalize=normalize)
