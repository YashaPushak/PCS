#Author: Yasha Pushak
#Created: Some time in 2016
#Last updated: February 21st, 2018

#A collection of functions for parsing and writing the parameter configuration space (.pcs) files. 

import re
import random
import copy
import helper


#Handy things to remember for later, possibly I should just make them into functions themselves:
#Sort by length of name in reverse order
#sorted(paramList, key=lambda k: len(k['name']), reverse=True)
#Sort by name in alphabetical order
#sorted(paramList, key=lambda k: k['name'])

#How I plan to store things:
#paramList = [{'default': 50, 'values': [10, 500], 'type': 'integer', 'name': 'ASCENT_CANDIDATES', 'log': True}, {'default': 0, 'values': [0, 5], 'type': 'integer', 'name': 'BACKBONE_TRIALS', 'log': False}, {'default': 'NO', 'values': ['YES', 'NO'], 'type': 'categorical', 'name': 'BACKTRACKING', 'log': False}]


class PCS:
    "A parameter configuration space object"

    lineEnd = '(( *$)|( *#.*$))'
    nextID = 0
    idPrefix = '@#'

    def __init__(self, infile)
    #Create the "memory" object. 
    self.mem = {}
    #Create lists for each group of "objects"
    self.paramList = []
    self.conditionList = []
    self.forbiddenList = []
    self.valueList = []
    self.commentList = []

    parseDoc(infile)



    def parseDoc(self,nfile):
        #Author: Yasha Pushak
        #Last Updated: October 27th, 2016
        #
        #This function parses a parameter configuration space file of the format
        #typically used by SMAC, and then returns three data structures
        #that represent this information. 
        #Note: I am almost certainly going to require that parameter values
        #may not contain parameter names as a substring. 
        #
        #Input:
        #    infile - a parameter configuration space file
        #Output:
        #    doc - A document "object" that represents the parameter configuration 
        #          space document
        #    paramList - A datastructure that represents all of the parameters. 
        #    conditionList - A datastructure that represents all of the condition statements
        #    forbiddenList - A datastructure that represents all of the forbidden parameter combinations. 
      
        #An array of IDs that represents the parameter configuration space document.
        self.doc = newObject()
        #Set the type of the document "object"
        self.doc['type'] = 'document'
        #initialize the contents of the document
        self.doc['content'] = []
    
        with open(infile) as f_in:
            #Pass through the document once to tag each line, and parse the
            #lines that contain parameters.
            for line in f_in:
                line = line.strip()
                if(re.search('^' + lineEnd,line)):
                    #We have a comment line or an empty line
                    #f_out.write(line + '#Empty line or comment\n')
                    #object = parseComment(line)
                    self.doc['content'].append(['comment',line])
                elif(re.search('^.+? real *\[-?([0-9]|\.|(e-?\+?))+?, *-?([0-9]|\.|(e-?\+?))+?\] *\[-?([0-9]|\.|(e-?\+?))+\] *(log)?' + lineEnd,line)):
                    #We have a real parameter
                    #Note: this does not completely validate the string, since
                    #we may still have something like 10.0.0 as a value,
                    #Or, the default value may not be in the specified range. 
                    #f_out.write(line + '#Real parameter\n')
                    obj = parseReal(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? integer *\[-?([0-9])+?, *-?([0-9])+?\] *\[-?([0-9])+\] *(log)?' + lineEnd,line)):
                    #We have an integer parameter
                    #f_out.write(line + '#integer parameter\n')
                    obj = parseInteger(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? categorical *{.+?} *\[.+?\]' + lineEnd,line)):
                    #We have a categorical parameter
                    #f_out.write(line + '#categorical parameter\n')
                    obj = parseCategorical(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? ordinal *{.+?} *\[.+?\]' + lineEnd,line)):
                    #we have an ordinal parameter
                    #f_out.write(line + '#ordinal parameter\n')
                    obj = parseOrdinal(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? *\[-?([0-9]|\.|(e-?))+?, *-?([0-9]|\.|(e-?))+?\] *\[-?([0-9]|\.|(e-?))+\] *l?' + lineEnd,line)):
                    #We have a real parameter in the old syntax
                    obj = parseRealOldSyntax(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? *\[-?([0-9])+?, *-?([0-9])+?\] *\[-?([0-9])+\] *l?il?' + lineEnd,line)):
                    #We have an integer parameter in the old syntax
                    obj = parseIntegerOldSyntax(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? *{.+?} *\[.+?\]' + lineEnd,line)):
                    #We have a categorical parameter in the old syntax
                    obj = parseCategoricalOldSyntax(line)
                    self.doc['content'].append(obj['id'])
                elif(re.search('^.+? \| .+? ((==)|((!=)|((in)|(<|>)))) .+?( (((&&)|(\|\|)) .+? ((==)|((!=)|((in)|(<|>)))) .+?))*' + lineEnd,line)):
                    #We have a conditional statement
                    #f_out.write(line + '#conditional statement\n')
                    #object = parseConditional(line)
                    self.doc['content'].append(['conditional',line])
                elif(re.search('^ *{.+?}' + lineEnd,line)):
                    #We have a forbidden clause
                    #f_out.write(line + '#Forbidden clause\n')
                    #object = parseForbidden(line)
                    self.doc['content'].append(['forbidden',line])
                else:
                    #f_out.write(line + '#Unknown line\n')
                    print('[Warning]: The following unrecognized line in the parameter configuration space file "' + infile + '" is being converted to a comment and we are attempting to continue.')
                    print(line)
                    #object = parseComment('#' + line)
                    self.doc['content'].append(['comment','#' + line])

        for i in range(0,len(self.doc['content'])):
            line = self.doc['content'][i]
            if(isinstance(line,list)):
                #This line has not yet been parsed.
                if(line[0] == 'comment'):
                    obj = parseComment(line[1])
                elif(line[0] == 'conditional'):
                    obj = parseConditional(line[1])
                elif(line[0] == 'forbidden'):
                    obj = parseForbidden(line[1])
                else:
                    print('[Error] The following line has an unknown type.')
                    print(line)
                    raise Exception('Unknown line type.')
                #Replace the line with the now parsed object id. 
                self.doc['content'][i] = obj['id']


        #Do some (non-exhaustive) checks to see if this is a valid document
        testDocumentCorrectness(self.doc)
 

    def parseIntegerOldSyntax(self,line):
        #Author: Yasha Pushal
        #Create: February 21st, 2018
        #Last udpated: F2019-03-06
        #parses and returns a dict object containing the information about the integer parameter
        #stored in the line in the old syntax.

        #Create the object
        param = newObject()
        #set the type
        param['type'] = 'integer'
        #get the paramter name
        param['name'] = line.split(' ')[0].split('[')[0].strip()
        #Get the range of values
        values = line.split('[')[1].split(']')[0].split(',')
        try:
            param['values'] = [int(values[0]), int(values[1])]
        except:
            print('[Error]: Failed to parse the range of values for:')
            print(line)
            raise
        #Grab the default value
        try:
            param['default'] = int(line.split('[')[2].split(']')[0])
        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        #Check if the default value is within the specified range. 
        if(not (param['default'] >= param['values'][0] and param['default'] <= param['values'][1])):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified range:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified range.')
        #Check for a log scale
        if(re.search('^.+? *\[-?([0-9])+?, *-?([0-9])+?\] *\[-?([0-9])+\] *il' + lineEnd,line) or re.search('^.+? *\[-?([0-9])+?, *-?([0-9])+?\] *\[-?([0-9])+\] *li' + lineEnd,line)):
            param['log'] = True
        else:
            param['log'] = False
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''
        #Store the parameter in the parameter list
        self.paramList.append(param)

        return param



    def parseRealOldSyntax(self,line):
        #Author: Yasha Pushal
        #Create: February 21st, 2018
        #Last udpated: 2019-03-06
        #parses and returns a dict object containing the information about the real parameter
        #stored in the line in the old syntax.
 
        #Create the object
        param = newObject()
        #set the type
        param['type'] = 'real'
        #get the paramter name
        param['name'] = line.split(' ')[0].split('[')[0].strip()
        #Get the range of values
        values = line.split('[')[1].split(']')[0].split(',')
        try:
            param['values'] = [float(values[0]), float(values[1])]
        except:
            print('[Error]: Failed to parse the range of values for:')
            print(line)
            raise
        #Grab the default value
        try:
            param['default'] = float(line.split('[')[2].split(']')[0])
        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        #Check if the default value is within the specified range. 
        if(not (param['default'] >= param['values'][0] and param['default'] <= param['values'][1])):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified range:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified range.')
        #Check for a log scale
        if(re.search('^.+? *\[-?([0-9]|\.|(e-?))+?, *-?([0-9]|\.|(e-?))+?\] *\[-?([0-9]|\.|(e-?))+\] *l' + lineEnd,line)):
            param['log'] = True
        else:
            param['log'] = False
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''
        #Store the parameter in the parameter list
        self.paramList.append(param)

        return param



    def parseCategoricalOldSyntax(self,line):
        #Author: Yasha Pushak
        #Created: February 21st, 2018
        #Last updated: February 21st, 2018
        #Parses and returns a dict object containing the information about the 
        #categorical parameter stored in the line in the old syntax
        param = {}
        #Create an ID for the parameter
        param['id'] = getID()
        #get the parameter name
        param['name'] = line.split(' ')[0].split('{')[0].strip()
        #get the parameter type
        param['type'] = 'categorical'
        #Get the range of values
        values = line.split('{')[1].split('}')[0].split(',')
        #Remove any whitespace and create value objects.
        keyValuePair = {}
        for i in range(0,len(values)):
            keyValuePair[values[i].strip()] = parseValue(values[i])
            values[i] = keyValuePair[values[i].strip()]['id']
        param['values'] = values
        #Grab the default value
        try:
            param['default'] = keyValuePair[line.split('[')[1].split(']')[0].strip()]['id']

        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        if(param['default'] not in param['values']):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified set of values:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified set of values.')
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''

        #Add the new object to memory.
        self.mem[param['id']] = param
        #store the parameter in the parameter list
        self.paramList.append(param)

        return param



    def parseReal(self,line):
        #Author: Yasha Pushak
        #Last updated: 2019-03-06
        #Parses and returns a dict object containing the information about the real
        #parameter stored in the line.
        param = {}
        #Create an ID for the parameter
        param['id'] = getID()
        #get the parameter name
        param['name'] = line.split(' ')[0].strip()
        #get the parameter type
        param['type'] = line.split(' ')[1].split('[')[0].strip()
        if(not param['type'] == 'real'):
            print('[Error]: Called parseReal() on non-real parameter:')
            print(line.strip())
            raise Exception('Called parseReal() on non-real parameter.')
        #Get the range of values
        values = line.split('[')[1].split(']')[0].split(',')
        try:
            param['values'] = [float(values[0]), float(values[1])]
        except:
            print('[Error]: Failed to parse the range of values for:')
            print(line)
            raise
        #Grab the default value
        try: 
            param['default'] = float(line.split('[')[2].split(']')[0])
        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        #Check if the default value is within the specified range. 
        if(not (param['default'] >= param['values'][0] and param['default'] <= param['values'][1])):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified range:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified range.')
        #check if this parameter should be searched on a log scale.
        if(re.search('^.+? .+? *\[([0-9]|\.)+?, *([0-9]|\.)+?\] *\[([0-9]|\.)+\] *log' + lineEnd,line)):
            param['log'] = True
        else:
            param['log'] = False
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''

        #Add the new object to memory
        self.mem[param['id']] = param
        #Store the parameter in the parameter list
        self.paramList.append(param)

        return param
 

    def parseInteger(self,line):
        #Author: Yasha Pushak
        #Last updated: 2019-03-06
        #Parses and returns a dict object containing the information about the real
        #parameter stored in the line.
        param = {}
        #Create an ID for the parameter
        param['id'] = getID()
        #get the parameter name
        param['name'] = line.split(' ')[0].strip()
        #get the parameter type
        param['type'] = line.split(' ')[1].split('[')[0].strip()
        if(not param['type'] == 'integer'):
            print('[Error]: called parseInteger() on non-integer parameter:')
            print(line.strip())
            raise Exception('Called parseInteger() on a non-integer parameter.')
        #Get the range of values
        values = line.split('[')[1].split(']')[0].split(',')
        try:
            param['values'] = [int(values[0]), int(values[1])]
        except:
            print('[Error]: Failed to parse the range of values for:')
            print(line)
            raise
        #Grab the default value
        try:
            param['default'] = int(line.split('[')[2].split(']')[0])
        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        #check that the default value is within the specifeid range. 
        if(not (param['default'] >= param['values'][0] and param['default'] <= param['values'][1])):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified range:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified range.')
        #check if this parameter should be searched on a log scale.
        if(re.search('^.+? .+? *\[([0-9]|\.)+?, *([0-9]|\.)+?\] *\[([0-9]|\.)+\] *log' + lineEnd,line)):
            param['log'] = True
        else:
            param['log'] = False
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''

        #Add the new object to memory.
        self.mem[param['id']] = param
        #Store the parameter in the parameter list
        self.paramList.append(param)

        return param


    def parseCategorical(self,line):
        #Author: Yasha Pushak
        #Last updated: 2019-03-06
        #Parses and returns a dict object containing the information about the 
        #categorical parameter stored in the line.
        param = {}
        #Create an ID for the parameter
        param['id'] = getID()
        #get the parameter name
        param['name'] = line.split(' ')[0].strip()
        #get the parameter type
        param['type'] = line.split(' ')[1].split('[')[0].strip()
        if(not param['type'] == 'categorical'):
            print('[Error]: called parseCategorical() on non-categorical parameter:')
            print(line.strip())
            raise exception('Called parseCategorical() on a non-categorical parameter.')
        #Get the range of values
        values = line.split('{')[1].split('}')[0].split(',')
        #Remove any whitespace and create value objects.
        keyValuePair = {}
        for i in range(0,len(values)):
            keyValuePair[values[i].strip()] = parseValue(values[i])
            values[i] = keyValuePair[values[i].strip()]['id']
        param['values'] = values
        #Grab the default value
        try:
            param['default'] = keyValuePair[line.split('[')[1].split(']')[0].strip()]['id']

        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        if(param['default'] not in param['values']):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified set of values:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified set of values.')
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''

        #Add the new object to memory.
        self.mem[param['id']] = param
        #store the parameter in the parameter list
        self.paramList.append(param)

        return param


    def parseOrdinal(self,line):
        #Author: Yasha Pushak
        #Last updated: October 24th, 2016
        #Parses and returns a dict object containing the information about the 
        #ordinal parameter stored in the line.
        param = {}
        #Create an iD for the parameter
        param['id'] = getID()
        #get the parameter name
        param['name'] = line.split(' ')[0].strip()
        #get the parameter type
        param['type'] = line.split(' ')[1].split('[')[0].strip()
        if(not param['type'] == 'ordinal'):
            print('[Error]: called parseOrdinal() on non-ordinal parameter:')
            print(line.strip())
            raise exception('Called parseOrdinal() on a non-ordinal parameter.')
         #Get the range of values
        values = line.split('{')[1].split('}')[0].split(',')
        #Remove any whitespace and create value objects.
        keyValuePair = {}
        for i in range(0,len(values)):
            keyValuePair[values[i].strip()] = parseValue(values[i])
            values[i] = keyValuePair[values[i].strip()]['id']
        param['values'] = values
        #Grab the default value
        try:
            param['default'] = keyValuePair[line.split('[')[1].split(']')[0].strip()]['id']
        except:
            print('[Error]: Failed to parse the default value for:')
            print(line)
            raise
        if(param['default'] not in param['values']):
            print('[Error]: The default value for ' + param['name'] + ' does not fall within the specified set of values:')
            print(line.strip())
            raise Exception('The default value for ' + param['name'] + ' does not fall within the specified set of values.')
        #Grab any trailing comments
        if(len(line.split('#'))>1):
            comment = parseComment(line.split('#')[1].strip())
            param['comment'] = comment['id']
        else:
            param['comment'] = ''

        #Add the new object to memory
        self.mem[param['id']] = param
        #Store the parameter in the parameter list
        self.paramList.append(param)

        return param


    def parseValue(self,term):
        #Author: Yasha Pushak
        #Last updated: O2019-03-06
        #Creates and returns a dict "object" representing the value in term.
    
        value = {}
        #Create an ID for the value
        value['id'] = getID()
        #Add the new "object" to memory
        self.mem[value['id']] = value
        #Store the type of this object
        value['type'] = 'value'
        #Store the text of the value
        value['text'] = term.strip()
        #Store the value in the value list.
        self.valueList.append(value)
     
        return value


    def parseComment(self,line):
        #Author: Yasha Pushak
        #Last updated: 2019-03-06
        #Creates and returns a dict representing the comment in line.
        comment = {}
        #Create an ID for the comment
        comment['id'] = getID()
        #Store the type of this object
        comment['type'] = 'comment'
        #Store the text of the comment
        if(len(line) > 0 and line[0] == '#'):
            line = line[1:]
        comment['text'] = line
 
        #Add the new object to memory
        self.mem[comment['id']] = comment
        #store the comment in the comment list
        self.commentList.append(comment)
  
        return comment


    def parseConditional(self,line):
        #Author: Yasha Pushak
        #Last updated: December 8th, 2016
        #Parses the conditional statement represented in the line. 

        #Store the line in case we need to print it in an error message
        linecp = line
    
        condition = {}
        #Get and store an ID for the condition.
        condition['id'] = getID()
        #Store the new object in memory.
        self.mem[condition['id']] = condition
        #Store the conditional in the condition list
        self.conditionList.append(condition)
        #Store the type of the object
        condition['type'] = 'conditional'   
 
        if(len(line.split('#')) > 1):
            condition['comment'] = parseComment('#'.join(line.split('#')[1]))['id']
        else:
            condition['comment'] = ''
  
        line = line.split('#')[0].strip()

        try:
            child = line.split('|')[0].strip()
            condition['child'] = lookupParamID(child)
    
            #remove the part of the line containing the child parameter
            line = re.sub('^.+? \|','',line).strip()
 
            clauses = []

            condition['clauses'] = parseConditionalClause(line,linecp)

            return condition
        except:
            print('[Error]: Something went wrong while parsing the following conditional statement.')
            print(linecp)
            raise


    def parseForbidden(self,line):
        #Author: Yasha Pushak
        #Created before: December 8th, 2016
        #Last updated: 2019-03-06
        #Parses and returns an "object" that corresponds to the forbidden statement 
        #stored in the line.
 
        #Create a new object
        forbidden = {} 
        #Create an ID
        forbidden['id'] = getID()
        #Set its type
        forbidden['type'] = 'forbidden'
        #store the forbidden "object" in "memory"
        self.mem[forbidden['id']] = forbidden
        #store the forbidden clause in the forbidden list
        self.forbiddenList.append(forbidden)
    
        linecp = line
   
        #Check for comments
        items = re.split('^ *{.+?} *?#',line)
        if(len(items) > 1):
            forbidden['comment'] = parseComment(items[1])['id']
        else:
            forbidden['comment'] = ''

        #Get just the forbidden clause and remove the braces at either end.
        line = re.search('^{.+?}',line).group(0)[1:-1].strip()
        clause = [line]


        #Assume that we have the classic syntax until we cannot
        try:
            forbidden['syntax'] = 'classic'
            forbidden['clause'] = parseClassicClause(line)

            return forbidden
        except Exception:
            forbidden['syntax'] = 'advanced' 
            forbidden['clause'] = parseAdvancedClause(line,linecp)

            return forbidden


    def parseClassicClause(self,string):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-06
        #a helper function that parses a forbidden statement string formatted in
        #the classic syntax.

        if(',' in string):
            A = string.split(',')[0]
            B = ','.join(string.split(',')[1:])
            #create a new, top-level clause, and recursively parse the units.
            return newClause(parseClassicClause(A),parseClassicClause(B),'&&')
        else:
            #find the parent parameter
            A = re.split(' *=',string)[0].strip()
            AID = lookupParamID(A)
            #remove the parent
            #print(line)
            string = string.strip()[len(A):].strip()
            #print(string)
            #Find the operator
            operator = re.search('^=',string).group(0)
            #Remove the operator
            string = string[len(operator):].strip()
            #Replace the operator with it's actual counterpart. 
            operator = '=='
            #Find the value
            value = re.split(',',string)[0].strip()
            #check if we have a categorical or ordinal parameter
            if(self.mem[AID]['type'] in ['ordinal', 'categorical']):
                #Find the corresponding ID of the value
                found = False
                for valueID in getAttr(AID,'values'):
                    if (getAttr(valueID,'text') == value):
                        B = valueID
                        found = True
                        break
                if(not found):
                    raise Exception('Forbidden statement specifies a parameter value that does not exist for the parameter.')
            else:
                B = value
    
            return newClause(AID,B,operator)
 

    def parseConditionalClause(self,string,linecp):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-06
        #A helper functison that parses a conditional statement condition clause.

        #The ordering here for splitting on logical or and logical and is important,
        #as it enforces the order of operations.
        if('||' in string):
            A = string.split('||')[0].strip()
            B = '||'.join(string.split('||')[1:]).strip()
            #create a new, top-level clause, and recursively parse the units.
            return newClause(parseConditionalClause(A,linecp),parseConditionalClause(B,linecp),'||')
        elif('&&' in string):
            A = string.split('&&')[0].strip()
            B = '&&'.join(string.split('&&')[1:]).strip()
            #create a new, top-level clause, and recursively parse the units.
            return newClause(parseConditionalClause(A,linecp),parseConditionalClause(B,linecp),'&&')
        else:
            #find the parent parameter
            parent = re.split(' |(( in )|((==)|((!=)|(>|<))))',string)[0]

            parentID = lookupParamID(parent)
            A = parentID
            #remove the parent
            string = string[len(parent):].strip()
            #Find the operator
            operator = re.search('(in )|((==)|((!=)|(>|<)))',string).group(0)
            #Remove the operator
            string = string[len(operator):].strip()
            operator = operator.strip()
            #Find the value
            value = re.split('(' + lineEnd + ')|((&&)|(\|\|))',string)[0].strip()
            #check if we have a categorical or ordinal parameter
            if(self.mem[parentID]['type'] in ['ordinal', 'categorical']):
                #check if we have a set of values
                if(operator == 'in'):
                    #Remove the braces and create an array of values
                    B = parseValueArray(value[1:-1],A)
                else:
                    #Create an array of values with only one value
                    for valueID in self.mem[A]['values']:
                        if (self.mem[valueID]['text'] == value):
                            B = valueID
                            found = True
                            break
                    if(not found):
                        print('[Error]: Conditional statement specifies a parameter value that does not exist for the parameter.')
                        print(linecp)
                        raise Exception('Conditional statement specifies a parameter value that does not exist for the parameter.')
            else:
                B = value
 
            return newClause(A,B,operator)



    def parseAdvancedClause(self,string,linecp):
        #Author: Yasha Pushak
        #Created Before: December 8th, 2016
        #Last updated: 2019-03-06
        #A helper function that parses a forbidden statement written in the 
        #advanced syntax.
 
        string = string.strip()

        if('(' in string):
            print("'" + string + "'")
            print(len(string))
            #We have some brackets to handle first.
            tokens = splitBraces(string)
            print(tokens)    
  
            if(len(tokens) == 1 and tokens[0][0] == 0 and tokens[0][1] == (len(string) - 1)):
                #The entire statement has brackets around it.
                #So we remove them and start again.
                clause = parseAdvancedClause(string[1:-1].strip(),linecp)
                clause['brackets'] = True
                return clause

            #Recursively handle each top-level unit.
            #move backwards, so that we don't mess up the indices of the string.
            for i in range(len(tokens)-1,-1,-1):
                token = tokens[i]
                #Replace the top-level brackets in the string with the ID of the 
                #newly created clause.
                string = string[:token[0]] + parseAdvancedClause(string[token[0]:token[1]+1].strip(),linecp)['id'] + string[token[1]+1:]
                #print(string)
        #At this point, any brackets have been removed, so we can now begin handling
        #operators.
        #The ordering here for splitting on logical or and logical and is important,
        #as it enforces the order of operations.
        if('||' in string):
            A = string.split('||')[0].strip()
            B = '||'.join(string.split('||')[1:]).strip()
            #create a new, top-level clause, and recursively parse the units.
            return newClause(parseAdvancedClause(A,linecp),parseAdvancedClause(B,linecp),'||')
        elif('&&' in string):
            A = string.split('&&')[0].strip()
            B = '&&'.join(string.split('&&')[1:]).strip()
            #create a new, top-level clause, and recursively parse the units.
            return newClause(parseAdvancedClause(A,linecp),parseAdvancedClause(B,linecp),'&&')
        elif(isID(string)):
            #At this point, we may encounter a string that is the ID of an already-
            #parsed clause that was originally contained in brackets. If so, we 
            #need to simply return the object corresponding to that ID.
            return self.mem[string]
        else:
            #It is possible that they may be trying to use one of the arithmetic
            #operators or functions. Currently we do not support these. Currently,
            #we only support the logical operators used in the advanced syntax.
            try:
                #find A
                A = re.split(' |(( in )|((==)|((!=)|(>|(<|((>=)|(<=)))))))',string)[0]
                #Remove A
                string = string[len(A):].strip()
                A = A.strip()
                #Find the operator
                operator = re.search('(in )|((==)|((!=)|(>|(<|((>=)|(<=))))))',string).group(0)
                #Remove the operator
                string = string[len(operator):].strip()
                operator = operator.strip()
                #Find the value
                B = re.split('(' + lineEnd + ')|((&&)|(\|\|))',string)[0].strip()
            
                foundA = False
                foundB = False
                #Check if A is a parameter
                try:
                    AID = lookupParamID(A)
                    A = self.mem[AID]
                    foundA = True
                    #Since A is a parameter, we check if B is a value of A.
                    if(A['type'] in ['ordinal','categorical']):
                        for valueID in A['values']:
                            if(getAttr(valueID,'text') == B):
                                BID = valueID
                                B = self.mem[valueID]
                                foundB = True
                                break
                    
                except:
                    #This is expected to fail if A is not a parameter.
                    pass
                #If we didn't find that B was a value of A, check if B is a parameter.
                if(not foundB):
                    try:
                        BID = lookupParamID(B)
                        B = self.mem[BID]
                        foundB = True
                        #Since B is a parameter, if A is not found check if it is a 
                        #value of B.
                        if(not foundA):
                            if(B['type'] in ['ordinal','categorical']):
                                for valueID in B['values']:
                                    if(getAttr(valueID,'text') == A):
                                        AID = valueID
                                        A = self.mem[valueID]
                                        foundA = True
                                        break
                    except:
                        #This is expected to fail if B is not a parameter
                        pass
                #If we couldn't match either A or B to parameters, then this is not
                #a valid clause.
                if(not foundA and not foundB):
                    print('[Error]: Unable to parse the following forbidden statement because two units could not be matched to parameters.')
                    print(linecp)
                    raise Exception('Unable to parse a forbidden statement because two units could not be matched to parameters.')
                elif(not foundA):
                    #If we didn't find A, but B is a numeric parameter, we'll create
                    #a new value for A to wrap the numeric text.
                    if(isNumeric(B)):
                        A = newValue(A)
                        AID = A['id']
                        foundA = True
                elif(not foundB):
                    #If we didn't find B, but A is a numeric parameter, we'll create
                    #a new value for B to wrap the numeric text.
                    if(isNumeric(A)):
                        B = newValue(B)
                        BID = B['id']
                        foundB = True
                #If we still haven't managed to parse A or B, throw an exception.
                if(not foundA):
                    print('[Error]: Unable to parse the following forbidden statement because the unit "' + A + '" could not be parsed.')
                    print(linecp)
                    raise Exception('Unable to parse the following forbidden statement because the unit "' + A + '" could not be parsed.')
                elif(not foundB):
                    print('[Error]: Unable to parse the following forbidden statement because the unit "' + B + '" could not be parsed.')
                    print(linecp)
                    raise Exception('Unable to parse the following forbidden statement because the unit "' + B + '" could not be parsed.')

                #If we got this far, then we parsed everything.
                return newClause(A,B,operator)
            except:
                print('[Error]: An error occured while parsing the following advanced forbidden statement. Please ensure that no arithmetic operators or functions are being used, as we do not currently support them.')
                print(linecp)
                raise

        


    def parseValueArray(self,string,parentID):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last udpated: 2019-03-06
        #Parses and returns a new array of values for the specified parent parameter
    
        values = []

        for val in string.split(','):
            val = val.strip()
            for valueID in getAttr(parentID,'values'):
                if(getAttr(valueID,'text') == val):
                    values.append(valueID)
  
        return newValueArray(values)



    def splitBraces(self,string):
        #Author: Yasha Pushak
        #Created Before: December 8th, 2016
        #Last upeadted: 2019-03-06
        #A helper function that splits a string into an array based on top-level
        #brackets
 
        numBrackets = 0
        tokens = []
        start = -1
        for i in range(0,len(string)):
            if(string[i] == '('):
                numBrackets += 1
                if(numBrackets == 1):
                    #We have found a top-level opening bracket, record this.
                    start = i
            elif(string[i] == ')'):
                numBrackets -= 1
                if(numBrackets == 0):
                    #We have found a top-level closing bracket, record this.
                    tokens.append([start,i])
                elif(numBrackets < 0):
                     raise Exception("Wrong number of brackets in string: '" + string + "'")

        if(not numBrackets == 0):
            raise Exception("Wrong number of brackets in string: '" + string + "'")

        return tokens


    def getName(self,obj):
        #Author: Yasha Pushak
        #Created Before: October 24th, 2016
        #Last updated: 2019-03-06
        #a minor helper function only intended for use within printForbidden.
        #Returns the name of a parameter or a value, depending on which was input.
        if(obj['type'] == 'value'):
            return obj['text']
        else:
            return obj['name']


    def getID(self):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last Updated: 2019-03-06
        #This function simply returns the next unique ID of the form '@#x' where x
        #is the ID of the object.
        cid = idPrefix + str(self.nextID)
        selfnextID += 1
        return cid


    def lookupParamID(self,name):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Looks up the ID of a parameter by name. Throws an exception if no parameter
        #with such a name is in memory (yet).
        for param in self.paramList:
            if(param['name'] == name):
                return param['id']

        raise Exception('No parameter exists with name: ' + name)


    def printObject(self,obj, printType = ''):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #A generic print method that allows any "object" to be printed, either by ID
        #or passed in directly.
    
        #Check that we have either an instance of an object, or the ID of an object.
        if(isinstance(obj,str)):
            #If we have a string, it may be an ID.
            if(obj not in self.mem):
                print('[Warning]: The following string that was not a valid ID was passed into printObject. We are printing as a string and attempting to continue.')
                print(obj)
                return [obj]
            else:
               #The object passed in was an object ID. Get the corresponding object
               obj = self.mem[obj]
                
       #Check if we have an "object" with a type.
        try:
            ojbType = obj['type']
        except:
            print('[Warning]: The following non-"object" was passed to printObject. We are casting it to a string and attempting to continue.')
            print(obj)
            return([str(obj)])
    
       #Check the type of the object and handle accordingly.
       if(objType == 'document'):
            return printDocument(obj)
        elif(objType == 'comment'):
            return printComment(obj)
        elif(objType == 'integer'):
            return printInteger(obj)
        elif(objType == 'real'):
            return printReal(obj)
        elif(objType == 'categorical'):
            return printCategorical(obj)
        elif(objType == 'ordinal'):
            return printOrdinal(obj)
        elif(objType == 'conditional'):
            return printConditional(obj)
        elif(objType == 'forbidden'):
            return printForbidden(obj)
        elif(objType == 'value'):
            return printValue(obj)
        elif(objType == 'clause'):
            return printClause(obj,printType)
        elif(objType == 'valueArray'):
            return printValueArray(obj)
        else:
            print('[Warning]: Un-implemented print function for type: ' + objType + '. We are casting it to a string and attempting to continue.')
            return [str(obj)]


    def printDocument(self):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints a document by printing each of it's objects. 
        string = ''
        for obj in self.doc['content']:
            for line in printObject(obj):
                string += line + '\n'
        return string

    def printComment(self,comment):
        #Author: Yasha Pushak
        #CReated Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints a comment.
        if(len(comment['text']) == 0):
            return ['']
        else:
            return ['#' + comment['text']]


    def printInteger(self,integer):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints an integer 
        string = ''
        string += integer['name'] + ' '
        string += integer['type'] + ' '
        string += str(integer['values']) + ' ' 
        string += '[' + str(integer['default']) + '] '
        if(integer['log']):
            string += 'log '
        if(len(integer['comment']) > 0):
            string += printObject(integer['comment'])[0]
        return [string]



    def printReal(self,real):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints a real 
        string = ''
        string += real['name'] + ' '
        string += real['type'] + ' '
        string += str(real['values']) + ' '
        string += '[' + str(real['default']) + '] '
        if(real['log']):
            string += 'log '
        if(len(real['comment']) > 0):
            string += printObject(real['comment'])[0]
        return [string]


    def printCategorical(self,param):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints a categorical
        string = ''
        string += param['name'] + ' '
        string += param['type'] + ' '
        string += '{' + printObject(param['values'][0])[0]
        for value in param['values'][1:]:
            string += ', ' + printObject(value)[0]
        string += '} '
        string += '[' + printObject(param['default'])[0] + '] '
        if(len(param['comment']) > 0):
            string += printObject(param['comment'])[0]
        return [string]


    def printOrdinal(self,param):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints an ordinal
        string = ''
        string += param['name'] + ' '
        string += param['type'] + ' '
        string += '{' + printObject(param['values'][0])[0]
        for value in param['values'][1:]:
            string += ', ' + printObject(value)[0]
        string += '} '
        string += '[' + printObject(param['default'])[0] + '] '
        if(len(param['comment']) > 0):
            string += printObject(param['comment'])[0]
        return [string]


    def printValue(self,obj):
        #Author: Yasha Pushak
        #Created Before: October 21st, 2016
        #Last updated: 2019-03-06
        #Prints a value
        return [obj['text']]


    def printConditional(self,obj):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Prints a conditional statement. 
        string = ''
        child = obj['child']
        string += getAttr(child,'name') + ' | '

        string += printObject(obj['clauses'],'conditional')[0]
       
        return [string]

    def printForbidden(self,obj):
        #Author: Yasha Pushak
        #Created Before: December 8th, 2016
        #Last updated: 2019-03-06
        #Prints a forbidden clause.

        return ['{' + printObject(obj['clause'],obj['syntax'])[0] + '}']


    def printClause(self,obj, printType):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-06
        #prints a classic forbidden object

        A = self.mem[obj['A']]
        B = self.mem[obj['B']]
        operator = obj['operator']
    
        if(printType == 'classic'):
            if(isParameter(A)):
                string = getAttr(A,'name')
            else:
                string = printObject(A,printType)[0] 

            if(operator == '&&'):
                string += ', '
            elif(operator == '=='):
                string += '='
            else:
                string += operator
                print('[Warning]: Printed unspecified operator for forbidden statement classic syntax: ' + operator)

            string += printObject(B,printType)[0]

        elif(printType == 'conditional'):
            if(isParameter(A)):
                string = getAttr(A,'name')
            else:
                string = printObject(A,printType)[0]

            string += ' ' + operator + ' '

            string += printObject(B,printType)[0]
        elif(printType == 'advanced'):
            string = ''

            if(obj['brackets']):
                string += '('

            if(isParameter(A)):
                string += getAttr(A,'name')
            else:
                string += printObject(A,printType)[0]

            string += ' ' + operator + ' '

            if(isParameter(B)):
                string += getAttr(B,'name')
            else:
                string += printObject(B,printType)[0]

            if(obj['brackets']):
                string += ')'
    
        return [string]


    def printValueArray(self,obj):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-06
        #Prints a value array.
    
        string = '{'
        for value in obj['values']:
            string += printObject(value)[0] + ', '
        string = string[:-2] + '}'

        return [string]
    

    def getAttr(self,obj,attribute):
        #Author: Yasha Pushak
        #Created Before: October 20th, 2016
        #Last updated: 2019-03-06
        #Returns the attribute of the object (specified directly, or by ID).
    
        #Check that we have either an instance of an object, or the ID of an object.
        if(isinstance(obj,str)):
            #If we have a string, it may be an ID.
            if(obj not in self.mem):
                print('[Error]: The following string that was not a valid ID was passed into getAttr().')
                print(obj)
                raise Exception('A string that was not a valid ID was passed into getAttr().')
            else:
                #The object passed in was an object ID. Get the corresponding object
                obj = self.mem[obj]
    
        try:
            return obj[attribute]
        except:
            print('[Error]: Attribute ' + attribute + ' undefined for the following object:')
            print(obj)
            raise


    def testDocumentCorrectness(self):
        #Author: Yasha Pushak
        #Last updated: October 24th, 2016
        #Performs some simple checks to see if the document is valid.
        #These tests are not exhaustive and should not be considered sufficient
        #for proof of correctness.

        #check that there are no collisions between parameter names and values when
        #using the advanced forbidden syntax.
        collision = False
        for param in self.paramList:
            for value in self.valueList:
                if(param['name'] == value['text']):
                    collision = True
                    break
            if(collision):
                break
        advanced = False
        for forbidden in self.forbiddenList:
            if(forbidden['syntax'] == 'advanced'):
                advanced = True
                break
        if(collision and advanced):
            print('[Error]: Cannot use advanced syntax for forbidden clauses and have parameter names and values that collide. This issue will need to be resolved manually.')



    def newValue(self, text):
        #Author: Yasha Pushak
        #Created Before: October 25th, 2016
        #Last updated: 2019-03-07
        #Creates a new value object with the inputted text.
    
        obj = newObject()
        obj['type'] = 'value'
        obj['text'] = text

        self.valueList.append(obj)
    
        return obj


    def newConditional(self, child,clause):
        #Author: Yasha Pushak
        #Created Before: December 9th, 2016
        #Last updated: 2019-03-06
        #Creates a new conditional object (specifically for hyperparameters)
        #child, parent, and value must be IDs (if applicable) rather than "objects"
   
        obj = newObject()
        obj['type'] = 'conditional'
        obj['child'] = child
        obj['clauses'] = clause

        self.conditionList.append(obj)

        return obj


   def newForbidden(self,clause,syntax):
        #Author: Yasha Pushak
        #Created Before: October 31st, 2016
        #Last updated: 2019-03-07
        #Creates a new forbidden clause with the pre-parsed clause.
    
        obj = newObject()
        obj['type'] = 'forbidden'
        obj['clause'] = clause
        obj['syntax' ] = syntax

        self.forbiddenList.append(obj)

        return obj


    def newComment(self,text):
        #Author: Yasha Pushak
        #Created Before: October 25th, 2016
        #Last updated: 2019-03-06
        #Creates a new comment object
        obj = newObject()
        obj['type'] = 'comment'
        obj['text'] = text
    
        self.commentList.append(obj)
    
        return obj



    def newClause(self,A,B,operator):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-07
        #A clause is made up of either a two units and an operator that
        #acts on them. A unit is either a parameter, a value or another clause.

        clause = newObject()
        clause['type'] = 'clause'
        if(type(A) is dict):
            clause['A'] = A['id']
        else:
            clause['A'] = A
        if(type(B) is dict):
            clause['B'] = B['id']
        else:
            clause['B'] = B
        clause['operator'] = operator
        clause['brackets'] = False
    
        return clause


    def newValueArray(self,values):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-06
        #Creates a new object to store an array of values.
        #Currently only used with the 'in' operator of the conditional statements;
        #however, this definitely could have also been used to specify the list of
        #permissible value for categorical and ordinal parameters.

        valueArray = newObject()
        valueArray['type'] = 'valueArray'
        valueArray['values'] = values

        return valueArray


    def newObject(self):
        #Author: Yasha Pushak
        #Created Before: October 25th, 2016
        #Last updated: 2019-03-07
        #Creates a new object
        obj = {}
        obj['id'] = getID()
        obj['type'] = 'object'
        obj['comment'] = ''
        self.mem[obj['id']] = obj

        return obj



    def isNumeric(self,obj):
        #Author: Yasha Pushak
        #Created Before: October 27th, 2016
        #Last updated: 2019-03-07
        #Returns true of the object is a real or integer parameter.
        #Throws an exception if there is no type accosiated with the "object"
        #Returns false otherwise.
        obj = getObject(obj)

        try:
            return (obj['type'] in ['real','integer'])
        except:
            print('[Error]: Unable to evaluate the type of the following non-"object".')
            print(obj)
            raise



    def isParameter(self,obj):
        #Author: Yasha Pushak
        #created: December 7th, 2016
        #Last updated: 2018-10-22
        #Returns true of the object is a real, integer, categorical, or ordinal 
        #parameter.
        #Throws an exception if there is no type accosiated with the "object"
        #Returns false otherwise.

        obj = getObject(obj)

        try:
            return obj['type'] in ['real','integer','categorical','ordinal']
        except:
            print('[Error]: Unable to evaluate the type of the following non-"object".')
            print(obj)
            raise


    def containsParent(self,condition,param):
        #Author: Yasha Pushak
        #Created Before: December 14th, 2016
        #Last updated: 2019-03-07
        #checks if the specified condition contains the specified parameter as a 
        #parent.
    
        condition = getObject(condition)
        clause = condition['clauses']
    
        return containsParameter(clause,param)


    def containsParameter(self,clause,parameter):
        #Author: Yasha Pushak
        #Created Before: December 14th, 2016
        #Last Updated: 2019-03-07
        #checks if the specified clause contains the specified parameter.
    
        clause = getObject(clause)
        parameter = getObject(parameter)
    
        A = clause['A']
        B = clause['B']

        found = False

        if(isID(A)):
            A = getObject(A)
            if(A['id'] == parameter['id']):
                found = True
            elif(A['type'] == 'clause'):
                found = containsParameter(A,parameter)

        if(found):
            return found
    
        if(isID(B)):
            B = getObject(B)
            if(B['id'] == parameter['id']):
                found = True
            elif(B['type'] == 'clause'):
                found = containsParameter(B,parameter)

        return found
                    
   


    def getObject(self,obj):
        #Author: Yasha Pushak
        #Created Before: December 8th, 2016
        #Last updated: 2019-03-07
        #If the argument passed in is an object ID, then we get the object from 
        #memory with the corresponding ID. If it is already an object, we return it.
        if(type(obj) is str and isID(obj)):
            return self.mem[obj]
        elif(type(obj) is dict):
            return obj
        else:
            raise Exception('Non-object:' + str(obj) + ' passed into getObject.')


    def getNamedValues(self,param):
        #Author: Yasha Pushak
        #Created Before: December 7th, 2016
        #Last updated: 2019-03-07
        #Returns the values of the parameter as strings, rather than IDs or objects.
    
        try:
            if(not isParameter(param)):
                raise Exception('Object passed in is not a parameter.')
            if(not isinstance(param['values'],list)):
                raise Exception('Values field of the object is not a list.')

            output = []
            for value in param['values']:
                if(isID(value)):
                    output.append(self.mem[value]['text'])
                else:
                    output.append(value)
            return output
        except:
            print('[Error]: Something went wrong while getting the named values of the following object:')
            print(param)
            raise 


    def isID(self,string):
        #Author: Yasha Pushak
        #Created Before: December 8th, 2016
        #Last updated: 2019-03-06
        #Checks if the specified string is in the format of an ID, and if the ID is
        #actually stored in memory... Which would probably be sufficient, actually.
        if(len(string) > len(idPrefix) and string[0:len(idPrefix)] == idPrefix):
            try:
                num = int(string[len(idPrefix):])
            except ValueError:
                return False
            return string in self.mem.keys()



    def getParentConditions(self,param):
        #Author: YP
        #Created: 2018-10-22
        #Last updated: 2019-03-07
        #Gets all of the parent clauses for the parameter

        conditions = []
        param = getObject(param)

        for condition in self.conditionList:
            if(condition['child'] == param['id']):
                conditions.append(condition)

        return conditions

    def isActive(self,param,config):
        #Author: YP
        #Created: 2018-10-22
        #Last updated: 2019-03-07
        #Checks to see if all parent conditions are satisfied.
        #for the parameter. param
        #config should be a dict containing parameter names, objects, or ids as 
        #keys with parameter values as text, objects, or ids as values.

        if(type(param) is str and not isID(param)):
            param = lookupParamID(param)
        param = getObject(param)
     
        #Get the relavent conditions
        conds = getParentConditions(param)

        #Convert the configuration dict to ids
        config = convertConfigToIdsAndText(config)

        allTrue = True
        for cond in conds:
            allTrue = allTrue and evalClause(getAttr(cond,'clauses'),config) 

        return allTrue
        

    def convertConfigToIdsAndText(self,config):
        #Author: YP
        #Created: 2018-10-22
        #Last updated: 2019-03-07
        #Converts a configuration as a dict with parameters as names, objects or
        #Ids as keys, and parameter values as objects or ids, or text, as values.

        newConfig = {}

        for p in config.keys():
            #Get p as an ID
            if(type(p) is str and not isID(p)):
                pId = lookupParamID(p)
            else:
                pId = getAttr(getObject(p),'id')
        
            v = config[p]
            #get v as text
            if(type(v) is str and isID(v)):
                v = getAttr(v,'text')
            elif(type(v) is dict):
                v = getAttr(v,'text') 
 
            newConfig[pId] = v

        return newConfig
        
            
    def evalClause(self,obj,config):
        #Author: YP
        #Created: 2018-10-22
        #Last updated: 2019-03-07
        #Evaluates the condition using the configuration specified in config.
        #Config must be a dict with parameters as keys (ids or objects), and 
        #the values must be the parameter values (either as ids or objects)

        obj = getObject(obj)

        if(isParameter(obj)):
            #The object is a parameter, so we return the value
            #for the parameter
            return config[obj['id']]
        elif(getAttr(obj,'type') == 'value'):
            return getAttr(obj,'text')
        elif(obj['type'] == 'clause'):
            #The object is a clause, so we need to evaluate it (possibly 
            #using recursion)
            operator = obj['operator']
            if(operator == '&&'):
                return evalClause(obj['A'],config) and evalClause(obj['B'],config)
            elif(operator == '||'):
                return evalClause(obj['A'],config) or evalClause(obj['B'],config)
            elif(operator in ['<=','>=','<','>']):
                #We don't support ordinals here, so this won't handle them
                #correctly.
                A = float(evalClause(obj['A'],config))
                B = float(evalClause(obj['B'],config))
                if(operator == '<='):
                    return A <= B
                elif(operator == '>='):
                    return A >= B
                elif(operator == '<'):
                    return A < B
                elif(operator == '>'):
                    return A > B
                else:
                    raise Exception("Invalid operator")
            elif(operator in ['==','!=']):
                if(isID(obj['A'])):
                    A = evalClause(obj['A'],config)
                else:
                    A = obj['A']
                if(isID(obj['B'])):
                    B = evalClause(obj['B'],config)
                else:
                    B = obj['B']
                #A and B are now values as strings
                if(operator == '=='):
                    return A == B
                elif(operator == '!='):
                    return not A == B
            elif(operator == 'in'):
                if(isID(obj['A'])):
                    A = evalClause(obj['A'],config)
                else:
                    A = obj['A']
                B = getAttr(obj['B'],'values')
                vals = []
                for v in B:
                    vals.append(getAttr(v,'text'))
                return A in vals
            
        raise Exception("We should never have made it here.")


