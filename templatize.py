import pandas as pd
import numpy as np
import re
import configparser
import json

def read_json(json_file='templates.json'):
    jsonf = json.load(open(json_file,'r'))
    return jsonf

def read_in_df(txtfile='anes_timeseries_2016/anes_timeseries_2016_rawdata.txt'):
    df = pd.read_csv(txtfile, sep="|")
    return df

def read_code_labels(txtfile='codelabels.txt'):
    f = open(txtfile,'r',encoding = 'Latin1')
    return f.read()

def parse_code_labels(code_labels):
    """
    Takes a list of code labels parsed by read_code_labels and
    parses them so that the key of the dictionary this function returns
    a dictionary with the integer codes as keys and the substitution
    answers as values
    """
    cldic = {}
    cls = code_labels.split('\n ;\n ')
    for cl in cls:
        try:
            cl_split = cl.split('\t')
            key = re.search('V\d+[^_\n]',cl_split[0]).group(0)
            value_dic = {k:re.search('[^"].+?(?=")',v).group(0) for k,v in [kv.split(' = ') for kv in cl_split[1:]]}
            cldic[key] = value_dic
        except:
            print(f"Didn't work in this case: {cl}")

    return cldic


class Template():
    """
    This class stores all the templates for all the codes and has methods
    for filling out a template, checking if a template is valid given the
    individual's data.


    """
    def __init__(self, df, ivs, dv, tabsepfordv = True):
        self.df = df
        self.dv = dv
        self.ivs = ivs
        self.tabsepfordv = "\t" if tabsepfordv else ""
        code_labels = read_code_labels()
        self.templates=read_json(json_file='templates.json')
#    def check_if_valid(self, code, data):
#        acceptable = {
#                "V161342": np.arange(1,3),
#                "V161006": np.arange(1,3),
#                "V161009": np.arange(1,6),
#                "V161021": np.arange(1,3),
#                "V161027": np.arange(1,5),
#                "V161126": np.arange(1,8),
#                "V161158x": np.arange(1,8),
#                "V161244": np.arange(1,3),
#                "V161270": np.arange(1,17),
#                "V161310x": np.arange(1,6),
#                "V161361x": [1,21,11,17,15,23,24,13,22,12,25,14,26,27,7,\
#                    9,28,19,3],
#                "V161511": np.arange(1,4),
#                }
#        if data in acceptable[code]:
#            return True
#        else:
#            return False
#
#
#        pass

    def backstory(self, ix):
        """
        Generate story for respondent indexed by ix
        """
        instance = self.df.iloc[ix]
        story = []
        for iv in self.ivs:
            iv = self.templates['variables'][iv]
            c = iv['c']
            t = iv['ivt']
            answer = instance[c]
            try:
                answer = iv['opts'][str(answer)]
                t = t.replace('ANSWER', str(answer))
                story.append(t)
            except:
                pass
        return " ".join(story)







#            acceptable = self.check_if_valid(code, data)
#            if acceptable:
#                try:
#                    data = self.customcldic[code][str(data)]
#                except:
#                    replace_data = self.cldic[code][str(data)]
#                    data = re.search("(?<=\d\. ).*",replace_data).group(0)
##                print(data)
#                template = self.fill_template(code,data)#This needs to insert the data from the survey into a 
#                story.append(template)
#            else:
#                pass
##            print(" ")
#
#        return " ".join(story)

    def target(self, ix):
        
        instance = self.df.iloc[ix]
        dv = self.templates['variables'][self.dv]
        c = dv['c']
        t = dv['dvt']
        choices = dv['opts']
        choicesstrlist = [f"({key}) {value}\n" for key, value in zip(choices.keys(), choices.values())]
        choicesstr = "".join(choicesstrlist)
        answer = instance[c]
        t = t.replace('ANSWER', str(answer)).replace('CHOICES', choicesstr)
        return t







    def generate_stories(self, ixs = None, randomly=False, n = None):
        """
        Iterate through ixs and generate stories for all the respondents
        """
        #Choose indices
        if ixs is not None:
            if n:
                n = np.min((len(ixs), n))
            if randomly:
                ixs = np.random.choice(ixs, n)
            else:
                ixs = ixs[:n]
        else:
            n = np.min((len(self.df.index), n))
            if randomly:
                ixs = np.random.choice(self.df.index, n)
            else:
                ixs = np.arange(n)

        stories = []
        for ix in ixs:
            ivstory = self.backstory(ix, self.ivs)
            print( ivstory )
            
            dvstory = self.backstory(ix, [self.dv])
            print( dvstory )
            if ivstory != "" and dvstory != "":
                stories.append(ivstory+dvstory)
                input()

        return stories






if __name__=="__main__":
    df = read_in_df()
    ivs = [
        "gender",             
        #"primaryvote",             
        "2016vote",             
        "ideology",             
        "party",             
        "church",             
        "education",             
        "race",             
        "sexuality",             
    ]
    dv = "2012vote"
    
    template = Template(df, ivs, dv)
    #ixs=np.arange(50)
    backstory = template.backstory(1) 
    target = template.target(1) 
    print( backstory, target )
    
    

