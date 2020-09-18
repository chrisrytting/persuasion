import pandas as pd
import numpy as np
import re


def labels_txt_to_dic(txtfile='varlabels.txt'):

    """
    Read the varlabels.txt file, of the form

    'code = "label"'

    and create a dictionary where, for each item, code is the key and 
    label is the item.
    """
    varlabelstxt = None
    with open('varlabels.txt','r', encoding='Latin1') as f:
        varlabelstxt = [vl.strip() for vl in f.readlines()]

    varlabelsdic = {}
    for vl in varlabelstxt:
        key, val = vl.split(' = ')
        varlabelsdic[key] = val[1:-1]
    return varlabelsdic

def read_in_df(txtfile='anes_timeseries_2016/anes_timeseries_2016_rawdata.txt'):
    df = pd.read_csv(txtfile, sep="|")
    return df

def label_df(df):
    """
    Take the raw text file and get it into a df, with descriptive names instead
    of codes.

    (In this directory, the file varlabels.txt has replacement names for the 
    codes that, in the raw data file, index the columns. We want to replace
    the codes with their more descriptive names)
    """
    labels_txt = get_labels_txt()
    labels_dic = labels_txt_to_dic(labels_txt)
    df.rename(labels_dic, axis = 1, inplace=True)
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


def generate_story(df, ix):
    """
    Given a dataframe and an index, generate a natural language story for a 
    person given the data in the dataframe

    TODO: Add an ability to indicate which fields you want described in that
    story, e.g. who they voted for in the presidential election, how they 
    feel about their own party, how they feel about the other party, how old
    they are, etc.
    """

    label_dic = labels_txt_to_dic()
    code_labels = read_code_labels()
    cldic = parse_code_labels(code_labels)
    #print(cldic)

    story_list = ["name", 'vote2012'] 
    code_dic = {
            'name':'V161342',
            'vote2012':'V161006',
            }
    story_nl = ""
    for story in story_list:
        code = code_dic[story]
        answer = df.iloc[ix][code]
        converted_answer = re.search("(?<=\d\. ).*",cldic[code][str(answer)]).group(0)
        story_bit = f"I am a {converted_answer}."
        story_nl += story_bit

    parts_of_story = []

class Template():
    """
    This class stores all the templates for all the codes and has methods
    for filling out a template, checking if a template is valid given the
    individual's data.


    """
    def __init__(self, df, alltoinclude):
        self.df = df

        code_labels = read_code_labels()
        self.cldic = parse_code_labels(code_labels)
        self.customcldic = {
                "V161009":{"1": "a great deal of",
                    "2": "a lot of",
                    "3": "a moderate amount of",
                    "4": "a little"
                    "5": "no"
                    },
                "V161021":{"1": "voted",
                    "2": "didn't vote",
                    }
                }

        #Pass in as a list "alltoinclude" those keys here which you want to 
        #include in the story

        namelabeldic = {
                "name": "V161342",
                "2012vote": "V161006",
                "medianews": "V161009",
                "primaryvote": "V161021",
                "2016vote": "V161027",
                }

        self.codestoinclude=[]
        for toinclude in alltoinclude:
            self.codestoinclude.append(namelabeldic[toinclude])

    def fill_template(self, code, data):
        self.codetemplatedic = {
                "V161342":f"I am a {'woman' if data.lower() == 'man' else 'woman'}.", #Gender
                "V161006":f"In 2012, I voted for {data}.", #Pres vote in 2012
                "V161009":f"I watch {data} news.", #News consumption
                "V161021":f"I {data} in the primary.", #Pres primary vote this year
                "V161027":f"I voted for {data} in 2016.", #Pres primary vote this year
                }
        filled_template=self.codetemplatedic[code]
        return filled_template



    def check_if_valid(self, code, data):
        acceptable = {
                "V161342": np.arange(1,3),
                "V161006": np.arange(1,3),
                "V161009": np.arange(1,6),
                "V161021": np.arange(1,3),
                "V161027": np.arange(1,5),
                }
        if data in acceptable[code]:
            return True
        else:
            return False


        pass

    def generate_story(self, ix):
        story = []
        for code in self.codestoinclude:
            data = self.df.iloc[ix][code] #This needs to get the data from the survey
            acceptable = self.check_if_valid(code, data)
            if acceptable:
                data = re.search("(?<=\d\. ).*",self.cldic[code][str(data)]).group(0)
                template = self.fill_template(code,data)#This needs to insert the data from the survey into a 
                story.append(template)
            else:
                pass

        return " ".join(story)


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
            story = self.generate_story(ix)
            if story != "":
                stories.append(story)
        return stories






if __name__=="__main__":
    df = read_in_df()
    template = Template(df, 'name 2012vote'.split())
    ixs=[0]
    ixs=np.arange(50)
    story = template.generate_stories( randomly =True, n=100)
    print(story)




































