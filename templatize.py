import pandas as pd
import numpy as np
import re
import configparser
import json
import transformers

def read_json(json_file='templates.json'):
    jsonf = json.load(open(json_file,'r'))
    return jsonf

def read_in_df(txtfile='anes_timeseries_2016/anes_timeseries_2016_rawdata.txt'):
    df = pd.read_csv(txtfile, sep="|")
    return df

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
        self.templates=read_json(json_file='templates.json')

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

    def target(self, ix, tsep = True):
        
        sep = "\t" if tsep else ""
        instance = self.df.iloc[ix]
        dv = self.templates['variables'][self.dv]
        c = dv['c']
        t = dv['dvt']
        choices = dv['opts']
        choicesstrlist = [f"({key}) {value}\n" for key, value in zip(choices.keys(), choices.values())]
        choicesstr = "".join(choicesstrlist)
        answer = instance[c]
        t = t.replace('ANSWER', sep + str(answer)).replace('CHOICES', choicesstr)
        return t

    def genstories(self, ixs = None, randomly=False, n = None):
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
            story = self.backstory(ix) + self.target(ix)
            stories.append(story.split('\t'))
        return stories

    def predict(self, model, stories):
        """
        Given a model and a list of stories (each one is a list where the 
        first entry is a backstory and the second entry is a target answer for
        that story), predict the answer for the story given the model.
        """




class Sampler():

    """
    This class takes a df and samples according to provided criteria. 
    There are also methods to calculate statistics for subdfs, like "What 
    percentage of white men who believe that the bible is the word of God
    voted for Donald Trump in 2016?"
    """

    def __init__(self, df):
        """
        Take a df you're interested in sampling from and calculating statistics
        for.
        """
        self.df = df 

    def narrow(self, keep):
        """
        Pass in a dict, keep, for vars you want to narrow on, for example:

        ivs = {"2012vote": ['1', '2']}

        Would narrow the df down to individuals who voted 1 or 2 in the 2012
        presidential election (Mitt Romney or Barack Obama)
        """
        for key, value in keep.items():
            self.df = self.df[self.df[key].isin(value)]
        return df
        
def Stats():
    """
    Calculate stats about a dataframe, like of a dataframe, how many voted for 
    Donald Trump.
    """
    def __init__(self, df):
        self.df = df
        self.templates=read_json(json_file='templates.json')

    def proportion(self, var):
        """
        Calculate what proportion of each of the values of the random variable
        var takes in the dataframe.
        e.g. with the dataframe 

          2012vote  gender
        0   Barack    male
        1     Mitt  female
        2   Barack  female
        3     evan    male

        if we did self.proportion('2012vote') we would get 


        Barack    50.0
        evan      25.0
        Mitt      25.0
        Name: 2012vote, dtype: float64
        """
        var = self.templates('var')

        props = df[var['c']].value_counts(normalize=True) * 100
        return props









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
    stories = template.genstories(ixs = [0, 15, 40])
    for story in stories:
        print( story )
