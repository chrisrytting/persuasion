import pandas as pd
import pickle
import re
import os
from collections import Counter

def load_pickle(pkl):
    return  pickle.load(open(pkl,'rb'))


def split_response_dic_gpt3(response_dic):
    ideo_responses  = {}
    print (",".join(response_dic.keys()))
    bin_response_dic = {}

    conservative_keys = 'slightly conservative.conservative.extremely conservative'.split('.')
    bin_response_dic['conservative'] = []
    for key in conservative_keys:
        bin_response_dic['conservative'] += response_dic[key] 

    liberal_keys = 'slightly liberal.liberal.extremely liberal'.split('.')
    bin_response_dic['liberal'] = []
    for key in liberal_keys:
        bin_response_dic['liberal'] += response_dic[key] 

    response_dic = bin_response_dic

    for key in response_dic.keys():
        ideo_responses[key] = {}
        ideo = response_dic[key]
        responses = []
        for response in ideo:
            splits = re.compile('\d+\.\s').split(response)[1:5]
            #answers = []
            for split in splits:
                split = split.split('\n')[0]
                split = split.lower()
                split = re.sub('^\s+', '', split)
                split = re.sub('\s+$', '', split)
                split = re.sub('\.+$', '', split)
                split = re.sub('\,+$', '', split)
                split = re.sub('"', '', split)
                responses.append(split)
            #responses.append(answers)
        ideo_responses[key]['responses']=responses
#        for resp,count in sorted(Counter(responses).items(), key = lambda x: x[1]):
#            print(resp,count)
        ideo_responses = add_count(ideo_responses)
    return ideo_responses

def ppdf_to_response_dic(ppdf, party):
    """
    party can either be 'GenD' or 'GenR'
    """
    ideo_responses  = {}
    for key in ppdf['Ideo'].unique():
        ideo_responses[key] = {}
        ideo_df = ppdf[ppdf['Ideo'] == key]
        responses = "|".join(ideo_df[party])
        responses = responses.split('|')
        ideo_responses[key]['responses']=responses
        ideo_responses = add_count(ideo_responses)
    return ideo_responses

def add_count(ideo_responses, n=5):
    for key in ideo_responses:
        responses = ideo_responses[key]['responses']
        c = Counter(responses)
        try:
            c.pop("")
        except:
            pass
        ideo_responses[key]['resp_counts'] = sorted(c.items(), key = lambda x: x[1])
        ideo_responses[key]['resp_counts'] = ideo_responses[key]['resp_counts'][-n:]
    return ideo_responses

    

def make_df():
    return pd.read_csv('./ppchris.csv')

def get_ideologies():
    df = pd.read_csv('./Pigeonholing Partisans.csv')
    df = df[['ID','Ideo']]
    df['Ideo'] = df['Ideo'].str.lower()
    df['Ideo'] = df['Ideo'].str.replace("/haven't thought about it","")
    conservative_keys = 'slightly conservative.conservative.extremely conservative'.split('.')
    liberal_keys = 'slightly liberal.liberal.extremely liberal'.split('.')
    bin_ideo_dic = {key:"conservative" for key in conservative_keys}
    bin_ideo_dic.update({key:"liberal" for key in liberal_keys})
    df = df[df['Ideo'] != 'moderate']
    df['Ideo'] = df['Ideo'].map(bin_ideo_dic)
    df = df.dropna()
    return df

def mcresp(partyresp, ideo):
    return partyresp[ideo]['resp_counts'].keys()
    

if __name__=="__main__":
    #GPT-3
    repgpt3 = load_pickle('/Users/chrisrytting/Downloads/Republican.pkl')
    demgpt3 = load_pickle('/Users/chrisrytting/Downloads/Democratic.pkl')
    demrespgpt3 = split_response_dic_gpt3(demgpt3)
    represpgpt3 = split_response_dic_gpt3(repgpt3)
    #print out response frequencies for gpt3 responses for both parties
    for key in represpgpt3:
        print(key, represpgpt3[key]['resp_counts'])
    for key in demrespgpt3:
        print(key, demrespgpt3[key]['resp_counts'])

    #Pigeonholing partisans
    ideo_df = get_ideologies()
    df = make_df()
    ppdf = df.merge(ideo_df, on='ID')


    demresp = ppdf_to_response_dic(ppdf, "GenD")
    represp = ppdf_to_response_dic(ppdf, "GenR")
    ##print out response frequencies for gpt3 responses for both parties
    for key in represp:
        print(key, represp[key]['resp_counts'])
    for key in demresp:
        print(key, demresp[key]['resp_counts'])

    
    humanresp = (demresp, represp)
    gpt3resp = (demrespgpt3, represpgpt3)
    f = open('gpt3vshuman2ideo.txt','w')
    for i, party in enumerate('Democratic Republican'.split()):
        f.write(f"Regarding the {party} party:")
        for key in represp:
            hcounts = humanresp[i][key]['resp_counts']
            hwords = [x for x,y in hcounts][::-1]
            hwordsn = '\n'.join(hwords)
            gpt3counts = gpt3resp[i][key]['resp_counts']
            gpt3words = [x for x,y in gpt3counts][::-1]
            gpt3wordsn = '\\\\'.join(gpt3words)

            template = f"""
A {key} human uses the words: 
{hwordsn}
A {key} GPT3 uses the words: 
{gpt3wordsn}
"""
            f.write(template)
    f.close()
    

