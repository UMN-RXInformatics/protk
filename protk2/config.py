'''
Created on Mar 17, 2012

@author: jacobokamoto
'''
DATABASE = {'driver':'sqlite3','name':'sqlite.db'}

ARFF_FEATURES = {
                 'pitch':('mean','median','stdev','slope','minval','maxval'),
                 'shimmer':('mean','median','stdev','slope','minval','maxval'),
                 'jitter':('mean','median','stdev','slope','minval','maxval'),
                 'intensity':('mean','median','stdev','slope','minval','maxval'),
                 'f1':('mean','median','stdev','slope','minval','maxval'),
                 'f2':('mean','median','stdev','slope','minval','maxval'),
                 }

ARFF_SHOW_WORD = False
ARFF_CONTEXT_SIZE = 0

#ARFF_CLASSIFY_COMMAND = """java -cp weka.jar weka.classifiers.functions.SMO -l %s -T %s -p 0 > %s"""
ARFF_CLASSIFY_COMMAND = """java -Xmx8000m -cp /Applications/WEKA.app/Contents/Resources/Java/weka.jar weka.classifiers.trees.J48 -l %s.model -T %s.arff -p 0 > %s.classres"""

VOWELS = ['ah','aw','ey','aa','ae','uh','iy','eh','ay','ih','o','ao']
FILLED_PAUSE = ['filledpause_um','filledpause_ah','fpm','fpu','++um++','++ah++','++uh++','fpa']
NONSPEECH = ['t_noise','t_breath','t_lipsmack','t_laugh','t_cough']+FILLED_PAUSE
SILENCE = ['sil','t_sil','<sil>','<eps>','e_sil']
IGNORE = ['<s>','</s>']

FILLED_PAUSE = FILLED_PAUSE + ['<' + i + '>' for i in FILLED_PAUSE]
NONSPEECH = NONSPEECH + ['<' + i + '>' for i in NONSPEECH]

AUDIO_PATH = "/opt/data/testing/wav/"
