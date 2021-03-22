import numpy as numpy
import pyphen
import re
import json 

class CefrCalculator:

    def __init__(self):

        with open('application/python_scripts/common_words.json', encoding="utf-8") as f:
            data = json.load(f)
        
        data = {self._preprocess(k): v for k, v in data.items()}
        todel = []
        toadd = []
        for i in data: 
            if " " in i:
                temp = i.split()
                # print(temp)
                todel.append(i)
                for j in temp: 
                    if j not in data:
                        toadd.append(j)
                
        for i in todel:
            del data[i]
        for i in toadd:
            data[i] = "unknown"
        
        
        data = {re.sub("[!?.]", "", k): v for k, v in data.items()}
    
        self.words = data


    def _num_sentences(self, text):
        """ Returns total number of sentences in a text. """
        text = text.strip()
        sens = len(re.findall("\w+[^.!?]*[.!?]", text))
        if text[-1] not in [".", "?", "!"]:
            sens += 1
        return sens

    def _num_syllables(self, text):
        """ Returns number of syllables in text. """

        syl = pyphen.Pyphen(lang="fr")
        return len(syl.inserted(text).split("-"))

    def _avg_sent_len(self, text):
        """ Returns average number of words per sentence. """
        try:
            return (len(self._rm_punc(text).split()) / self._num_sentences(text))
        except ZeroDivisionError as e:
            print(f"Division error")
            return 0.0

    def _avg_word_len(self, text):
        """ Returns the average number of syllables per word. """
        try:
            return self._num_syllables(text) / len(text.split())
        except ZeroDivisionError as e:
            print(f"Division error")
            return 0.0
    
    def _avg_char_word(self, text):
        """ Returns the average number of chars per word. """

        chars = text.replace(" ", "")
        awl = len(chars) / len(text.split())
        return awl

    def _difficult_words(self, text):
        """ Returns number of difficult words in text"""

        num = 0 
        dif_words = []

        for i in set(text.split()):
            if i not in self.words.keys():
                num += 1 
                dif_words.append(i)

        return num

    def _rm_punc(self, text): 
        """ Removes end of sentence punctuation (!.?) """

        clean_text = re.sub('[!?.]', '', text)

        return clean_text

    def _preprocess(self, text):
        """ Returns pre-processed text. """

        clean_text = text.lower() # makes lowercase 
        clean_text = re.sub('\w*\d\w*', '', clean_text) # removes digits 
        # clean_text = re.sub("’", "' ", clean_text) 
        clean_text = re.sub("'", "' ", clean_text) # adds space after any '
        clean_text = re.sub('\n', '', clean_text) # removes any carriage returns
        clean_text = clean_text.replace("l'", "l' ") # adds space after any l' 
        punctuation = "\#$%&()*+…-,/:;<=>@[\\]^_«»{|}~\n“”€—–"
        clean_text = re.sub('[%s]' % re.escape(punctuation), ' ', clean_text) # removes punctuation
        
        return clean_text

    def _dale_chall(self, text):
        asl = self._avg_sent_len(text)
        text = self._rm_punc(text)
        pdw = self._difficult_words(text) / len(text.split()) * 100
        score = (0.1579 * pdw) + (0.0496 * asl)
        if pdw > 4:
            score = score + 3.6356
        return score 

    def _flesch_score(self, text):
        return 207 - (1.015 * self._avg_sent_len(text)) - (73.6 * self._avg_word_len(self._rm_punc(text)))
        # return 206.835 - (1.015 * self._avg_sent_len(text)) - (84.6 * self._avg_word_len(self._rm_punc(text)))

    def _flesch_kincaid_score(self,text):
        return (0.39 * self._avg_sent_len(text)) + (11.8 * self._avg_word_len(self._rm_punc(text))) - 15.59

    def _flesch_cefr(self, text):
        flesch = self._flesch_score(text)
        cefr = "Unknown"
        if flesch >= 90:
            cefr = "A1"
        elif flesch >= 80:
            cefr = "A2"
        elif flesch >= 70:
            cefr = "B1"
        elif flesch >= 60:
            cefr = "B2"
        elif flesch >= 50:
            cefr = "C1"
        elif flesch >= 0:
            cefr = "C2" 
        
        return cefr
    
    def _fk_cefr(self, text):
        fk = self._flesch_kincaid_score(text)
        cefr = "Unknown"  
        if fk >= 13:
            cefr = "C2"
        elif fk >= 10:
            cefr = "C1"
        elif fk >= 9:
            cefr = "B2"
        elif fk >= 7:
            cefr = "B1"
        elif fk >= 5:
            cefr = "A2"
        elif fk >= 0:
            cefr = "A1" 
        
        return cefr
    
    def _dc_cefr(self, text):
        dc = self._dale_chall(text)
        cefr = "Unknown" 
        if dc >= 9:
            cefr = "C2"
        elif dc >= 8:
            cefr = "C1"
        elif dc >= 7:
            cefr = "B2"
        elif dc >= 6:
            cefr = "B1"
        elif dc >= 5:
            cefr = "A2"
        elif dc >= 0:
            cefr = "A1" 
        
        return cefr

    def cefr_score(self, text):
        text = self._preprocess(text)
        dc_cefr = self._dc_cefr(text)
        f_cefr = self._flesch_cefr(text)
        fk_cefr = self._fk_cefr(text)

        lst = [f_cefr, fk_cefr, dc_cefr]
        lst = sorted(lst)
        # return max(lst, key=lst.count)
        return lst[1]

# c = CefrCalculator()

# with open("../experimentation/cefr_texts.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# texts = [ data[str(i)]['text'] for i in range(len(data)) ]
# cefrs = [ data[str(i)]['cefr'] for i in range(len(data)) ]

# calc_cefrs = [c.cefr_score(i) for i in texts]


# final_cefrs = []
# for i in calc_cefrs:
#     final_cefrs.append(max(i, key=i.count))

# f_correct = 0
# fk_correct = 0
# dc_correct = 0
# final_correct = 0
# for i in range(len(cefrs)): 
#     if cefrs[i] == calc_cefrs[i][0]:
#         f_correct += 1 
#     if cefrs[i] == calc_cefrs[i][1]:
#         fk_correct += 1 
#     if cefrs[i] == calc_cefrs[i][2]:
#         dc_correct += 1
#     if cefrs[i] == final_cefrs[i]:
#         final_correct += 1

# print(f"Flesch => Number correct: {f_correct}       Percentage correct: {f_correct/len(cefrs) * 100} ")  
# print(f"Flesch Kincaid => Number correct: {fk_correct}      Percentage correct: {fk_correct/len(cefrs) * 100} ") 
# print(f"Dale-chall => Number correct: {dc_correct}      Percentage correct: {dc_correct/len(cefrs) * 100} ") 
# print(f"Final=> Number correct: {final_correct}      Percentage correct: {final_correct/len(cefrs) * 100} ") 


    
