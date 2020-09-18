

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

        #Pass in as a list "alltoinclude" those keys here which you want to 
        #include in the story

        namelabeldic = {
                "name": "V161342",
                "2012vote": "V161006",
                }

        self.codestoinclude=[]
        for toinclude in alltoinclude:
            self.codestoinclude.append(namelabeldic[toinclude])

    def fill_template(self, code, data):
        self.codetemplatedic = {
                "V161342":f"I am a {data}", #Gender
                "V161006":f"In 2012, I voted for f{data}", #Pres vote in 2012
                }
        filled_template=self.codetemplatedic[code]
        return filled_template



    def check_if_valid():
        pass

    def generate_story(self, ix):
        story = []
        for code in self.codestoinclude:
            data = self.df.iloc[ix][code] #This needs to get the data from the survey
            data = re.search("(?<=\d\. ).*",cldic[code][str(data)]).group(0)
            template = self.fill_template(code,data)#This needs to insert the data from the survey into a 
            story.append(template)

        return " ".join(story)


    def generate_stories(self, ixs):
        """
        Iterate through ixs and generate stories for all the respondents
        """
        pass


