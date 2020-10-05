import pandas as pd
import numpy as np
import re
import configparser

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

        self.tabsepfordv = "\t" if tabsepfordv else ""
        code_labels = read_code_labels()
        self.cldic = parse_code_labels(code_labels)
        self.customcldic = {
                "V161009":{"1": "a great deal of",
                    "2": "a lot of",
                    "3": "a moderate amount of",
                    "4": "a little",
                    "5": "no",
                    },
                "V161021":{"1": "voted",
                    "2": "didn't vote",
                    },
                "V161342":{"1": "man",
                    "2": "woman",
                    },
                "V161126":{"1": "extremely liberal",
                    "2": "liberal",
                    "3": "slightly liberal",
                    "4": "moderate",
                    "5": "slightly conservative",
                    "6": "conservative",
                    "7": "extremely conservative",
                    },
                "V161158x":{"1": "a strong Democrat",
                    "2": "a moderate Democrat",
                    "3": "an independent who leans left",
                    "4": "an independent",
                    "5": "an independent who leans right",
                    "6": "a moderate Republican",
                    "7": "a strong Republican",
                    },
                "V161244":{"1": "do",
                    "2": "don't",
                    },
                "V161270":{"1": "I didn't graduate high school",
                    "2": "I didn't graduate high school",
                    "3": "I didn't graduate high school",
                    "4": "I didn't graduate high school",
                    "5": "I didn't graduate high school",
                    "6": "I didn't graduate high school",
                    "7": "I didn't graduate high school",
                    "8": "I didn't graduate high school",
                    "9": "I graduated from high school",
                    "10": "I went to some college",
                    "11": "I have an associate's degree",
                    "12": "I have an associate's degree",
                    "13": "I have a bachelor's degree",
                    "14": "I have a master's degree",
                    "15": "I have a professional degree",
                    "16": "I have a doctorate",
                    },
                "V161310x":{"1": "white",
                    "2": "black",
                    "3": "asian",
                    "4": "native american",
                    "5": "hispanic",
                    },
                "V161361x":{"11": "low five figures",
                    "13": "low five figures",
                    "12": "low five figures",
                    "14": "low five figures",
                    "07": "low five figures",
                    "09": "low five figures",
                    "03": "low five figures",
                    "21": "high five figures",
                    "17": "high five figures",
                    "15": "high five figures",
                    "22": "high five figures",
                    "19": "high five figures",
                    "23": "six figures",
                    "24": "six figures",
                    "25": "six figures",
                    "26": "six figures",
                    "27": "six figures",
                    "28": "six figures",
                    },
                "V161511":{"1": "straight",
                    "2": "gay",
                    "3": "bisexual",
                    },
                }

        #Pass in as a list "ivs" those keys here which you want to 
        #include in the story

        namelabeldic = {
                "gender": "V161342",
                "2012vote": "V161006",
                "medianews": "V161009",
                "primaryvote": "V161021",
                "2016vote": "V161027",
                "ideology": "V161126",
                "party": "V161158x",
                "churchgoer": "V161244",
                "educationlevel": "V161270",
                "race": "V161310x",
                "salary": "V161361x",
                "sexualorientation": "V161511",
                }


        self.ivs=[]
        for iv in ivs:
            self.ivs.append(namelabeldic[iv])
        self.dv = namelabeldic[dv]

    def fill_template(self, code, data):
        self.codetemplatedic = {
                "V161342":f"I am a {data}.", #Gender
                "V161006":f"In 2012, I voted for {self.tabsepfordv}{data}.", #Pres vote in 2012
                "V161009":f"I watch {data} news.", #News consumption
                "V161021":f"I {data} in the primary.", #Pres primary vote this year
                "V161027":f"I voted for {data} in 2016.", #Pres primary vote this year
                "V161126":f"I consider myself {data}.", #Ideology
                "V161158x":f"I consider myself {data}.", #Party
                "V161244":f"I {data} go to church.", #Church Attendance
                "V161270":f"{data}.", #Educational attainment
                "V161310x":f"I am {data}.", #Race
                "V161361x":f"I make {data}.", #Salary
                "V161511":f"I am {data}.", #Sexual Orientation
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
                "V161126": np.arange(1,8),
                "V161158x": np.arange(1,8),
                "V161244": np.arange(1,3),
                "V161270": np.arange(1,17),
                "V161310x": np.arange(1,6),
                "V161361x": [1,21,11,17,15,23,24,13,22,12,25,14,26,27,7,\
                    9,28,19,3],
                "V161511": np.arange(1,4),
                }
        if data in acceptable[code]:
            return True
        else:
            return False


        pass

    def generate_story(self, ix, codes):
        """
        Generate story for respondent indexed by ix
        """
        story = []
        for code in codes:
#            print(code)
            data = self.df.iloc[ix][code] #This needs to get the data from the survey
#            print(data)
            acceptable = self.check_if_valid(code, data)
#            print(acceptable)
            if acceptable:
                try:
                    data = self.customcldic[code][str(data)]
                except:
                    replace_data = self.cldic[code][str(data)]
                    data = re.search("(?<=\d\. ).*",replace_data).group(0)
#                print(data)
                template = self.fill_template(code,data)#This needs to insert the data from the survey into a 
                story.append(template)
            else:
                pass
#            print(" ")

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
            ivstory = self.generate_story(ix, self.ivs)
            dvstory = self.generate_story(ix, [self.dv])
            if ivstory != "" and dvstory != "":
                stories.append(ivstory+dvstory)

        return stories






if __name__=="__main__":
    df = read_in_df()
#"gender",             
#"2012vote",             
#"medianews",             
#"primaryvote",             
#"2016vote",             
#"ideology",             
#"party",             
#"churchgoer",             
#"educationlevel",             
#"race",             
#"salary",             
#"sexualorientation",             
    varnames = 'gender 2012vote medianews primaryvote 2016vote'.split()




    ivs = [
        "gender",             
        #"2012vote",             
        "medianews",             
        "primaryvote",             
        "2016vote",             
        "ideology",             
        "party",             
        "churchgoer",             
        "educationlevel",             
        "race",             
        "salary",             
        "sexualorientation",             
    ]
    dv = "2012vote"
    
    template = Template(df, ivs, dv)
    #ixs=np.arange(50)
    story = template.generate_stories( randomly=True, n=20)
    print( story )
    

