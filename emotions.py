import os
import re

class EmotionScorer:

    emotions_folder = "resources/emotionDictionaries"

    feat_dicts = {
        "nrc": {"values": dict(), "labels": ['Anger','Anticipation','Disgust','Fear','Joy','Sadness','Surprise','Trust']},
        "nrcPosNeg": {"values": dict(), "labels": ['Positive', 'Negative']},
        "nrcVad": {"values": dict(), "labels": ['Valence', 'Arousal', 'Dominance']}
    }

    def __init__(self, lang):
        self.lang = lang

    def initializeFeatures(self):
        finalFeats = dict()
        for k in self.feat_dicts:
            l = self.feat_dicts[k]['values']
            feats = l[list(l.keys())[0]]
            for i in range(0, len(feats)):
                myFeat = k + '_' + self.feat_dicts[k]['labels'][i]
                finalFeats[myFeat] = 0
        return finalFeats

    def loadModels(self):
        with open(os.path.join(self.emotions_folder, 'nrc_emotions', self.lang), 'r') as file:
            for line in file:
                line = line.replace('\n', '').strip()
                if line.startswith('NO TRANSLATION'):
                    continue
                parts = line.split('\t')
                self.feat_dicts['nrc']['values'][parts[0].lower()] = parts[3:]
                self.feat_dicts['nrcPosNeg']['values'][parts[0].lower()] = parts[1:3]
        with open(os.path.join(self.emotions_folder, 'nrc_valence', self.lang), 'r') as file:
            for line in file:
                line = line.replace('\n', '').strip()
                if line.startswith('NO TRANSLATION'):
                    continue
                parts = line.split('\t')
                self.feat_dicts['nrcVad']['values'][parts[0].lower()] = parts[1:]
        # self.initializeFeatures()

    def addToFeatures(self, myDict, myTag, myFeaturesArray):
        for i in range(0, len(myFeaturesArray)):
            myFeat = myTag + '_' + self.feat_dicts[myTag]['labels'][i]
            if myFeat in myDict:
                myDict[myFeat] = myDict[myFeat] + float(myFeaturesArray[i])
            else:
                myDict[myFeat] = +float(myFeaturesArray[i])

    def countWordsFound(self, myDict, myLexDict):
        if myLexDict in myDict:
            myDict[myLexDict] = myDict[myLexDict] + 1
        else:
            myDict[myLexDict] = 1

    def removeDuplicateToken(self, tokens):
        wordsToProcessList = list(dict.fromkeys(tokens))
        return wordsToProcessList

    def extractEmotions(self, text):
        tokens = re.split(r"\s+", text.lower().strip())
        featuresDict = self.initializeFeatures()
        numberOfWordsFoundDict = dict()
        wordsToProcessList = self.removeDuplicateToken(tokens)

        for token in wordsToProcessList:
            for k in self.feat_dicts:
                if token in self.feat_dicts[k]['values']:
                    if len(token) < 2:
                        continue
                    self.countWordsFound(numberOfWordsFoundDict, k)
                    feats = self.feat_dicts[k]['values'][token]
                    self.addToFeatures(featuresDict, k, feats)

        return featuresDict
