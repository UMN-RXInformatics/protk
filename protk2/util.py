"""
protk2.util : ProTK utility functions
"""

import os,sys

def parse_args():
    # pull args from sys.argv
    args = sys.argv
    
    if len(args) > 1:
        args = args[1:]
    else: return {}
    
    ret = {}
    
    for arg in args:
        if arg.find("=") != -1:
            parts = arg.split("=")
        else:
            parts = [arg]
            
        switch = parts[0]
        if switch.startswith("--"):
            if len(parts) > 1: ret[switch[2:]] = parts[1]
            else: ret[switch[2:]] = True
        else:
            print("Invalid option: %s" % switch)
            
    return ret

def merge_options(defaults, overrides):
    
    for k,v in overrides.iteritems():
        defaults[k] = v
        
    return defaults
        
def has_keys(d,keys):
    for k in keys:
        if not d.has_key(k):
            print str(k)
            return False
    return True

import numpy

def moving_average(x,window_length=11):
    s = numpy.r_[x[window_length-1:0:-1],x,x[-1:-window_length:-1]]
    w=numpy.ones(window_length,'d')
    return numpy.convolve(w/w.sum(),s,mode='valid')

def dict2str(d):
    if d == None: return ""
    return ','.join([':'.join([str(k),str(v)]) for k,v in d.iteritems()])

def str2dict(s):
    return dict([j.split(':') for j in s.split(',')])
