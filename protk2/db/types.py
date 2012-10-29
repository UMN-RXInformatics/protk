"""
protk2.db.types : Database types for ProTK 2
"""

from sqlalchemy.ext.declarative import declarative_base
import pickle
from sqlalchemy import Column,Float,Integer,String,ForeignKey,Text
from protk2.fs import noext_name
from protk2.util import moving_average,dict2str,str2dict
import base64

Base = declarative_base()

class AudioFile(Base):
    __tablename__ = "audio_file"
    
    id = Column(Integer,primary_key=True)
    
    filename = Column(String(255))
    basename = Column(String(255))
    
    extdata = Column(Text)
    
    def __init__(self, filename, extdata=None):
        self.filename = filename
        self.basename = noext_name(filename)
        self.extdata = pickle.dumps(extdata) if extdata != None else None

"""
ProsodyEntry: Holds information about a specific prosodic event (i.e., word, phoneme, phrase)
"""
class ProsodyEntry(Base):
    
    __tablename__ = "prosody_entries"
    
    id = Column(Integer,primary_key=True)
    
    audio_file = Column(Integer,ForeignKey("audio_file.id"))
    
    ptype = Column(String(255))
    
    start = Column(Float)
    end = Column(Float)
    
    data = Column(String(255))
    
    extdata = Column(Text)
    
    def __init__(self, audio_file, start, end, ptype, data, extdata):
        self.audio_file = audio_file.id
        self.start = start
        self.end = end
        self.data = str(data)
        self.extdata = dict2str(extdata)
        self.ptype = ptype.lower()
        
    def __str__(self):
        return "<word:%s>" % self.word

import numpy
import numpy.linalg

"""
AnalysisEntry: Holds analysis results for a specific prosodic event
"""
class AnalysisEntry(Base):
    __tablename__ = "analysis_entries"
    
    id = Column(Integer,primary_key=True)
    
    prosody_entry = Column(Integer, ForeignKey("prosody_entries.id"))
    
    atype = Column(String(255))
    
    median = Column(Float)
    mean = Column(Float)
    stdev = Column(Float)
    slope = Column(Float)
    maxval = Column(Float)
    minval = Column(Float)
    
    undefined = Column(Integer)
    
    def __init__(self, values, xmin, xmax, atype, prosody_entry, times=None, normalize=False, smooth=False, undefined=False):
        if not undefined:
            valarr = numpy.array(values)
            rngarr = numpy.arange(len(valarr))
            
            if smooth:
                valarr = moving_average(valarr)
                rngarr = numpy.arange(len(valarr))
            
            if normalize:
                #self.slope = (float(numpy.mean(numpy.array(values[-11:-1]))) - float(numpy.mean(numpy.array(values[0:10])))) / (xmax-xmin)
                zmean = float(numpy.mean(valarr))
                zstdev = float(numpy.std(valarr))
                print ">>> ZSTDEV=%f"%zstdev
                # you can do this with numpy arrays. It's frickin' awesome.
                valarr = (valarr-zmean)/zstdev
            
            self.mean = float(numpy.mean(valarr))
            self.median = float(numpy.median(valarr))
            self.stdev = float(numpy.std(valarr))
            self.minval = float(numpy.nanmin(valarr))
            self.maxval = float(numpy.nanmax(valarr))
            
            slp = numpy.polyfit(rngarr, valarr, 1, full=False)
            self.slope = float(slp[0])
            self.prosody_entry = prosody_entry.id
            self.atype = atype
            self.undefined = 0
        else:
            self.prosody_entry = prosody_entry.id
            self.atype = atype
            self.undefined = 1
        
    def get_dict(self):
        return {'mean':self.mean,'median':self.median,'stdev':self.stdev,'slope':self.slope,'maxval':self.maxval,'minval':self.minval} if self.undefined == 0 else {'mean':"?",'median':"?",'stdev':"?",'slope':"?",'maxval':"?",'minval':"?"}
        
def create_tables(engine):
    Base.metadata.create_all(engine)

def generate_framing(frame_size, window_size, db_session, audio_file):
    
    import wave
    import contextlib
    fname=audio_file.filename
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames=f.getnframes()
        rate=f.getframerate()
        duration=frames/float(rate)
        print duration

    if window_size == None: window_size = 0
    
    x = 0.0
    while x < duration:
        # set xmin/xmax
        xmin = x
        xmax = x + frame_size
        
        # add entry to database
        db_session.add(ProsodyEntry(audio_file, xmin, xmax, "frame", "", None))
        
        # advance x pointer
        x = x + frame_size - window_size
