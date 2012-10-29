"""
protk2.fs : File system functions
"""

# Directory handling functions
import os, sys, shutil

class PathDoesNotExist(Exception):
    pass
class FileDoesNotExist(Exception):
    pass
class DirDoesNotExist(Exception):
    pass
class DirListError(Exception):
    pass

def get_filenames(directory,filter_by=None):
    try:
        ls = os.listdir(directory)
        new = []
        for entry in ls:
            if entry.startswith('.'):
                continue
            if filter_by != None:
                if entry.find(filter_by) == -1:
                    continue
                else:
                    new.append(entry)
            else:
                new.append(entry)
        return new
    except:
        raise DirListError()
    
def normalize_dir_path(path):
    return path if path[-1] == '/' else path+'/'

def make_empty_dir(path):
    """
    Make an empty directory at the specified path (clears existing dirs)
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            raise OSError("Path exists, but is not a directory")
    else:
        os.makedirs(path)
    return normalize_dir_path(path)

def make_dirs(path):
    """
    Make a directory (if it does not exist) at the specified path
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            return normalize_dir_path(path)
        else:
            raise OSError("Path exists, but is not a directory")
    else:
        os.makedirs(path)
    return normalize_dir_path(path)

def list_files(path,include=None,exclude=None,hidden=False,fullpaths=False):
    """
    Return a list of files in the directory given by path
    """
    
    print include,"derp"
    
    if not os.path.exists(path):
        raise OSError("Nonexistent directory '%s'"%path)
    if not os.path.isdir(path):
        raise OSError("Path exists, but is not a directory")

    ls = [f for f in os.listdir(path) if f[0] != '.' or hidden]
    if include != None:
        if type(include) is str:
            ls = [f for f in ls if f.find(include) != -1]
        elif type(include) is list:
            ls2 = []
            for f in ls:
                has = False
                for inc in include:
                    if f.find(inc) != -1:
                        has = True
                if has: ls2.append(f)
            ls = ls2
        else:
            raise Exception("`list_files` expects `include` to be a string or list")
    elif exclude != None:
        if type(exclude) is str:
            ls = [f for f in ls if f.find(exclude) == -1]
        elif type(exclude) is list:
            ls2 = []
            for f in ls:
                nohas = True
                for ex in exclude:
                    if f.find(ex) != -1:
                        nohas = False
                        break
                if nohas:
                    ls2.append(f)
            ls = ls2
        else:
            raise Exception("`list_files` expects `exclude` to be a string or list")
    
    if fullpaths == True:
        npath =normalize_dir_path(path)
        return [npath+f for f in ls]
    else: return ls

def list_file_paths(path,include=None,exclude=None,hidden=False):
    """
    Return a list of file paths to files in the directory given by path
    """
    return list_files(path,include,exclude,hidden,True)

def dir_exists(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            return True
        else: raise Exception("Path exists but is not a directory")
    else:
        return False
    
def basename(path):
    return path.split('/')[-1]
    
def noext_name(path):
    return '.'.join(basename(path).split('.')[:-1])