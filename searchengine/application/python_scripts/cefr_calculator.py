import numpy as numpy
import pyphen
import re
from textstat.textstat import textstatistics
import json 

text = "Le gouvernement va pouvoir continuer de mettre en place des restrictions pour faire face à la deuxième vague de coronavirus. Dans une ambiance souvent tendue, l’Assemblée nationale a voté samedi la prorogation de l’état d’urgence sanitaire jusqu’au 16 février. Le projet de loi, voté par 71 voix contre 35 en première lecture, est attendu au Sénat mercredi et devrait être adopté définitivement début novembre."

text2 = "Les appels au boycott de produits français se sont multipliés samedi dans plusieurs pays du Moyen-Orient. L’Organisation de coopération islamique, qui réunit les pays musulmans, a déploré « les propos de certains responsable français susceptibles de nuire aux relations franco-musulmanes ». L’émoi a été suscité par les propos du président Emmanuel Macron, qui a promis de ne pas « renoncer aux caricatures » de Mahomet, interdites dans la religion musulmane. vague"

text3 = "Cette année, Joe Biden a renvoyé Donald Trump dans son golf privé en prenant bientôt sa place à la Maison Blanche. L’Argentine est proche de légaliser l’avortement et Adèle Haenel s’est levée contre les violences faites aux femmes. Pour la première fois dans l’Union européenne, les énergies renouvelables ont produit plus d’électricité que les combustibles fossiles lors du premier semestre 2020. Tom Moor, un ancien capitaine de l'armée britannique centenaire a collecté près de 40 millions de livres pour le système hospitalier du Royaume-Uni, en marchant avec son déambulateur "

class CefrCalculator:

    words = open("application/python_scripts/vocab_list.txt", "r", encoding="utf-8").readlines()
    words = [i.split(":")[0].strip() for i in words]

    def _num_sentences(self, text):
        return len(re.findall("\w+[^.!?]*[.!?]", text))

    def _num_syllables(self, text):
        syl = pyphen.Pyphen(lang="fr")
        return len(syl.inserted(text).split("-"))
        # text_stat = textstatistics()
        # text_stat.set_lang("fr")
        # return text_stat.syllable_count(self.text)

    def _avg_sent_len(self, text):
        # print(f"num words: {len(text.split())}")
        # print(f"Num sents: {self._num_sentences(text)}")
        try:
            return round((len(text.split()) / self._num_sentences(text)), 1)
        except ZeroDivisionError as e:
            print(f"Division error")
            return 0.0

    def _avg_word_len(self, text):
        # print(f"sylls: {self._num_syllables(text)}")
        try:
            return round((self._num_syllables(text) / len(text.split())), 1)
        except ZeroDivisionError as e:
            print(f"Division error")
            return 0.0


    def _flesch_score(self, text):
        return 207 - (1.015 * self._avg_sent_len(text)) - (73.6 * self._avg_word_len(text))

    def _flesch_kincaid_score(self,text):
        return round(((0.39 * self._avg_sent_len(text)) + (11.8 * self._avg_word_len(text)) - 15.59), 1)

    def _difficult_words(self, text):
        pass

    def _dale_chall(self, text):
        pass

    def cefr_score(self, text):
        flesch = self._flesch_score(text)
        flesch = self._flesch_kincaid_score(text)
        cefr = "unknown"
        # if flesch >= 90:
        #     cefr = "A1"
        # elif flesch >= 80:
        #     cefr = "A2"
        # elif flesch >= 70:
        #     cefr = "B1"
        # elif flesch >= 60:
        #     cefr = "B2"
        # elif flesch >= 50:
        #     cefr = "C1"
        # elif flesch >= 0:
        #     cefr = "C2"   
        if flesch >= 13:
            cefr = "C2"
        elif flesch >= 10:
            cefr = "C1"
        elif flesch >= 8:
            cefr = "B2"
        elif flesch >= 7:
            cefr = "B1"
        elif flesch >= 6:
            cefr = "A2"
        elif flesch >= 0:
            cefr = "A1" 
        
        return cefr

text4 =  """Qu’est-ce qui vous a donné le goût du football ?

Le football, c’est la principale passion de ma famille italienne. La première fois que mon père m’a emmenée au stade pour voir un match de football, j’avais 4 ans. Chez nous, tous les dimanches, la famille se retrouvait au stade ou à regarder les émissions de foot à la télé avec mes oncles et mes cousins. 

Avez-vous pratiqué le football ?

Pas vraiment. Quand j’étais jeune, le football féminin n’était pas encore si développé. Et mon père n’était pas vraiment favorable. Je lui disais « Apprends-moi à jouer au foot ! » Mais non, il était concentré uniquement sur mon frère. Pour moi, il ne voulait rien entendre : « Le foot, ce n’est pas pour les filles ». Plus je lui disais de m’initier, plus il m’achetait des jouets de fille. Aujourd’hui, le football féminin s’est super bien développé et j’ai moi-même poussé ma fille à en faire.

Votre papa vous a tout de même laissé devenir arbitre ?

A l’époque, il n’y avait pas la possibilité pour les femmes d’être arbitre et surtout pas dans le foot. Dans ma famille, mon oncle était arbitre et mon cousin aussi. Et l’année de l’ouverture de l’arbitrage aux femmes, ce sont eux qui m’ont proposé d’essayer car ils savaient que j'étais passionnée. Là, mon père a dit Pourquoi pas !  J’ai commencé à 15 ans. J’ai suivi les cours pour apprendre toutes les règles du jeu et pour moi c’était un super défi. J’ai pu démontrer qu’une femme était capable d’arbitrer comme les hommes."""

# t = textstatistics()
# t.set_lang("fr")
c = CefrCalculator()
# c1, f1 = c.cefr_score(text)
# c2, f2 = c.cefr_score(text2)
# c3, f3 = c.cefr_score(text3)
# c4, f4 = c.cefr_score(text4)
# print(f"{c1} {f1}")
# print(f"{c2} {f2}")
# print(f"{c3} {f3}")
# print(f"{c4} {f4}")
# print(f"FK from c: {c._flesch_kincaid_score(text)}")
# print(f"FK from t: {t.flesch_kincaid_grade(text)}")

# with open("../experimentation/cefr_texts.json", "r") as f:
#     data = json.load(f)

# texts = [ data[str(i)]['text'] for i in range(len(data)) ]
# cefrs = [ data[str(i)]['cefr'] for i in range(len(data)) ]

# calc_cefrs = [c.cefr_score(i) for i in texts]

# correct = 0
# for i in range(len(cefrs)): 
#     if cefrs[i] == calc_cefrs[i]:
#         correct += 1 

# print(f"Number correct: {correct} \nPercentage correct: {correct/len(cefrs) * 100} ")    

# with open("application/python_scripts/vocab_list.txt", "r", encoding="utf-8") as f:
#     words = f.readlines()

words = open("application/python_scripts/vocab_list.txt", "r", encoding="utf-8").readlines()
words = [i.split(":")[0].strip() for i in words]