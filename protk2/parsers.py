"""
protk2.parsers : File parsers
"""

import re,os,sys

from protk2.db.core import DatabaseManager
from protk2.db.types import ProsodyEntry, AudioFile

FOUND_ITEM = -1
FOUND_INTERVAL = -2
FOUND_EOF = -3
MAXEMPTY = 10

class TextGridParser(object):
    
    def __init__(self,filename, audio_file):
        self.filename = filename
        self.audio_file = audio_file
        self.contents = []
        
    def parse(self):
        fh = open(self.filename)
        f = fh.readlines()
        # parse the header
        self._parse_header(f)
        # start parsing items
        self._parse_items(f)
        return self.contents
        
    def _parse_header(self,f):
        line = None
        while True:
            if len(f) > 0: line = f[0]
            
            if line == None: break
            if len(line.strip()) == 0:
                f.pop(0)
                continue
            
            if re.search("ooTextFile",line):
                #print("[parser][txtgrid]> Reading 'ooTextFile'")
                pass
                
            elif re.search("TextGrid",line):
                #print("[parser][txtgrid]> + File is a textgrid. Good.")
                pass
                
            elif re.search("xmin",line):
                self.start = float(line.split('=')[1])
                #print("[parser][txtgrid]> + Start time: %f" % self.start)
                
            elif re.search("xmax",line):
                self.end = float(line.split('=')[1])
                #print("[parser][txtgrid]> + End time: %f" % self.end)
                
            elif re.search("tiers?",line) and re.search("exists",line):
                #print("[parser][txtgrid]> + Has tiers...")
                pass
                
            elif re.search("size",line):
                self.size = int(line.split('=')[1])
                #print("[parser][txtgrid]> + Tier count: %d"%self.size)
                
            elif re.search("item",line) and re.search(r"\[\]",line):
                #print("[parser][txtgrid]> Reached start of items")
                return line
            
            else:
                #print("[parser][txtgrid]> Unkonwn parameter in line '%s'" % line)
                pass
                
            if len(f) > 0: f.pop(0)
                
    def _parse_items(self,f):
        line = None
        found_item = False
        while True:
            if not found_item and len(f) > 0: line = f[0]
            elif len(f) == 0: return False
            
            if line == None: return False
            if len(line.strip()) == 0:
                f.pop(0)
                continue
            
            if re.search("item[ ]*\[\d+\]",line) or found_item:
                #print("[parser][txtgrid]> Found an item...")
                found_item = self._parse_item(f)
                #print("[parser][txtgrid]> Item parsed.")
            else:
                f.pop(0)
                continue
                
            if len(f) > 0: f.pop(0)
                
    def _parse_item(self,f):
        line = None
        found_interval = False
        while True:
            if not found_interval:
                if len(f) > 0:
                    line = f[0]
                else: return False
            
            if len(f) == 0: return False
            if line == None: return False
            if len(line.strip()) == 0:
                f.pop(0)
                continue
            
            if re.search("item[ ]*\[\d+\]",line): return True
            elif re.search("class",line) and re.search("[Ii]nterval[Tt]ier",line):
                #print("[parser][txtgrid][item]> Reading item")
                pass
            elif re.search("name[ ]*=",line):
                item_type = line.split("=")[1].strip().strip('"')
                #print("[parser][txtgrid][item]> + Item type: %s" % item_type)
            elif re.search("xmin",line):
                start = float(line.split('=')[1])
                #print("[parser][txtgrid][item]> + Start time: %f" % self.start)
            elif re.search("xmax",line):
                end = float(line.split('=')[1])
                #print("[parser][txtgrid][item]> + End time: %f" % self.end)
            elif re.search("intervals[ ]*\[\d+][ ]*:",line):
                #print("[parser][txtgrid][item]["+item_type+"]> Found a new "+item_type)
                #if len(f) > 0: f.pop(0) # apparently this line broke stuff. Oops.
                found = self._parse_interval(f,item_type)
                #print("[parser][txtgrid][item]> Parsed item.")
                if found == FOUND_ITEM: return True
                elif found == FOUND_INTERVAL: found_interval = True
                elif found == FOUND_EOF: return False
            else:
                #print("[parser][txtgrid][item]> Unknown line...")
                pass
                
            if len(f) > 0: f.pop(0)
                
    def _parse_interval(self,f,label="interval"):
        line = None
        start = None
        end = None
        text = None
        extdata = {}
        found = -100
        while True:
            if len(f) > 0:
                line = f[0]
            else:
                found = FOUND_EOF
                break
            
            if line.strip() == "": found = FOUND_EOF
            if len(line.strip()) == 0:
                f.pop(0)
                continue
            
            if re.search("item[ ]*\[\d+\]",line): 
                found = FOUND_ITEM
                break
            elif re.search("intervals[ ]*\[\d+][ ]*:",line):
                found = FOUND_INTERVAL
                break
            elif re.search("text[ ]*=",line):
                text = line.split("=")[1].strip().strip('"')
                #print("[parser][txtgrid][item]["+label+"]> + Text: %s" % item_type)
            elif re.search("xmin",line):
                start = float(line.split('=')[1])
                #print("[parser][txtgrid][item]["+label+"]> + Start time: %f" % start)
            elif re.search("xmax",line):
                end = float(line.split('=')[1])
                #print("[parser][txtgrid][item]["+label+"]> + End time: %f" % end)
            elif len(line.split('=')) == 2:
                spl = [i.strip().strip('!"') for i in line.split('=')]
                extdata[spl[0]] = spl[1]
                #print("[parser][txtgrid][item]["+label+"]> + Extra: '%s' = '%s'"%(str(spl[0]),str(spl[1])))
            if len(f) > 0: f.pop(0)
        """    
        if label.lower() == "word" and start != None and end != None and text != None:
            w = Word(self.audio_file, start, end, text, extdata)
            self.contents.append(w)
        elif label.lower() == "phone" and start != None and end != None and text != None:
            p = Phone(self.audio_file, start, end, text, extdata)
            self.contents.append(p)
        """
        if start != None and end != None and text != None:
            w = ProsodyEntry(self.audio_file, start, end, label, text, extdata)
            self.contents.append(w)
        
        return found


class FormantBurgParser(object):
    
    def __init__(self, f):
        self.file = f
        self.formants = []
    
    def parse(self, af):
        f = open(self.file)
        
        header = []
        for i in range(0,9):
            header.append(f.readline())
        
        x = 0.0
        xstep = 0.00625
        while True:
            intensity = None
            numFormants = None
            formants = []
            try:
                intensity = float(f.readline())
                numFormants = float(f.readline())
            except:
                print "<<EOF>>"
                break
            for i in range(0,int(numFormants*2),2):
                freq = float(f.readline())
                band = float(f.readline())
                formants.append((freq,band))
            
            self.formants.append((x,x+xstep,freq,band))
            x+=xstep
            
        return self.formants

class FormantSLParser(object):
    
    def __init__(self, f, xstep=0.00625):
        self.file = f
        self.xstep = 0.00625
        self.formants = []
        
    def parse(self, af):
        f = open(self.file)
        
        header = []
        for i in range(0,9):
            header.append(f.readline())
            
        x = 0
        xstep = self.xstep
        while True:
            fmts = []
            for i in range(0,6):
                
                try:
                    freq = float(f.readline())
                    band = float(f.readline())
                    fmts.append((x,x+xstep,freq))
                except:
                    return self.formants
            self.formants.append(fmts)

class IntensityParser(object):
    def __init__(self, f):
        self.file = f
        self.intensities = []
    
    def parse(self):
        f = open(self.file)
        ls = f.readlines()
        
        # Get xmin/xmax, number of entries, and step size
        xmin = float(ls[3])
        xmax = float(ls[4])
        num_entries = int(ls[5])
        step = (xmax - xmin) / num_entries
        
        print("[parser][pitch]> Parsing %d intensity entries from '%s'" % (num_entries, self.file))
        
        # chop header info
        ls2 = ls[13:]
        # step through data 2 lines at a time
        for val in ls2:
            # append step start/end and pitch to list
            self.intensities.append(float(val))
        return self.intensities

class PitchParser(object):
    def __init__(self, f):
        self.file = f
        self.pitches = []
    
    def parse(self):
        f = open(self.file)
        ls = f.readlines()
        
        # Get xmin/xmax, number of entries, and step size
        xmin = float(ls[3])
        xmax = float(ls[4])
        num_entries = int(ls[5])
        step = (xmax - xmin) / num_entries
        
        print("[parser][pitch]> Parsing %d pitch entries from '%s'" % (num_entries, self.file))
        
        # chop header info
        ls2 = ls[6:]
        # step through data 2 lines at a time
        for i in range(0,len(ls2),2):
            # append step start/end and pitch to list
            self.pitches.append((float(ls2[i]),float(ls2[i+1])))
        return self.pitches

"""
ShimmerParser : Parses shimmer files
"""
class ShimmerParser(object):
    def __init__(self, f):
        self.file = f
        self.shimmers = []
    
    def parse(self):
        f = open(self.file)
        ls = f.readlines()
        
        # Get xmin/xmax, number of entries, and step size
        xmin = float(ls[0].split(":")[1])
        xmax = float(ls[1].split(":")[1])
        num_entries = int(float(ls[2].split(":")[1]))
        step = (xmax - xmin) / num_entries
        
        print("[parser][shimmer]> Parsing %d shimmer entries from '%s'" % (num_entries, self.file))
        
        # chop header info
        ls2 = ls[6:]
        # step through data 2 lines at a time
        for val in ls2:
            # append step start/end and pitch to list
            a = val.split(',')
            aval = a[2]
            try:
                aval = float(aval)
            except:
                continue
            self.shimmers.append((float(a[0]),aval))
        return self.shimmers

class SilenceParser(object):
    def __init__(self, f):
        self.file = f
        self.silences = []
        self.soundings = []
        
    def parse(self):
        f = open(self.file)
        ls = f.readlines()
        
        num_parts = int(ls[11])
        ls2 = ls[12:]
        for i in range(0,len(ls2),3):
            s = float(ls2[i])
            e = float(ls2[i+1])
            t = ls2[i+2]
            if t == "silent": self.silences.append((s,e))
            else: self.soundings.append((s,e))
            
        return {'silences': self.silences, 'soundings': self.soundings}

def lolmerge(lol):
    out = []
    for l in lol:
        out = out + l 
    return out 
"""
def parse_htk(filename):
    f = open(filename)
    words = []
    phones = []
    
    lines = f.readlines()

    cword = None
    wstart = -1

    for line in lines:
        parts = line.split()
        syl = lolmerge([i.split("+") for i in parts[2].split("-")])
        if len(syl) == 3:
            syl = syl[1]
        else: syl = syl[0]
        phones.append((parts[0],parts[1],syl))
        if len(parts) > 4:
            if cword != None:
                words.append((wstart,parts[0],cword))
                cword = parts[4]
                wstart = parts[0]
            else:
                cword = parts[4]
                wstart = parts[0]

    return (words,phones,)
"""
def parse_rec(audio_file, filename):
    try: f = open(filename)
    except:
        print filename
        return None
    words = []
    
    lines = f.readlines()

    for line in lines:
        parts = line.split()
        start = float(int(parts[0]))/10000000.0
        end = float(int(parts[1]))/10000000.0
        word = parts[-1].strip()
        words.append(ProsodyEntry(audio_file, start, end, "word", word, None))

    return words
