'''
Created on Mar 19, 2012

@author: jacobokamoto
'''

# relation_name: name of relation parameter in arff output
# attributes: list of two-element tuples representing attribute names and attribute types, i.e. ("intensity", "NUMERIC")
# values: list of lists of values
def generate_arff(relation_name, attributes, values):
    
    output = []
    output.append("@RELATION %s" % relation_name)
    for attr in attributes:
        output.append("@ATTRIBUTE %s %s" % (attr[0], attr[1]))
    
    output.append("@DATA")
    for val in values:
        for x in range(len(val)):
            if val[x] == None:
                val[x] = '?'

        if len(val) != len(attributes):
            print "Ignoring row with only %d values for %d attributes" % (len(val),len(attributes))
            continue
        output.append(','.join([str(i) for i in val]))
        
    return output