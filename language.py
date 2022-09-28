from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.classes.tokenizer import SocialTokenizer
from diff_match_patch import diff_match_patch
import os
import spacy
import emotions
import re

class Language:
    stopwords_folder = "resources/stopwords"

    def __init__(self, name, section):
        self.name = name
        self.section = section
        self.models_loaded = False
        self.use_aliases = False

        self.convert_hashtags = section.getboolean('convert_hashtags')
        self.convert_emoji = section.getboolean('convert_emoji')
        self.lemma = section.getboolean('lemma')
        self.emotions = section.getboolean('emotions')
        self.restore_case = section.getboolean('restore_case')
        self.use_stopwords = section.getboolean('use_stopwords')
        self.remove_ending_elongated = section.getboolean('remove_ending_elongated')

    def loadModels(self):
        if self.convert_hashtags:
            self.text_processor = TextPreProcessor(
                normalize=['url', 'email', 'percent', 'money', 'phone', 'user', 'time', 'url', 'date', 'number'],
                fix_html=True,
                segmenter=self.name,
                corrector=self.name,
                unpack_hashtags=True,
                unpack_contractions=False,
                spell_correct_elong=False,
                spell_correction=False,
                tokenizer=SocialTokenizer(lowercase=True).tokenize,
                )

        if self.convert_emoji:
            exec("from resources.emojiTranscriptions import unicode_codes_%s" % self.name)
            emojis = sorted(eval('unicode_codes_%s.EMOJI_UNICODE.values' % self.name)(), key=len, reverse=True)
            pattern = u'(' + u'|'.join(re.escape(u) for u in emojis) + u')'
            self.emoji_regexp = re.compile(pattern)
            self.codes_dict = (
                eval('unicode_codes_%s.UNICODE_EMOJI_ALIAS' % self.name)
                if self.use_aliases
                else eval('unicode_codes_%s.UNICODE_EMOJI' % self.name)
                )

        if self.lemma:
            self.lemmatizer = spacy.load(self.section['spacy_model'] % self.name, disable=['parser', 'ner'])

        if self.use_stopwords:
            self.stopwordsDict = set()
            with open(os.path.join(self.stopwords_folder, self.name), 'r') as file:
                for line in file:
                    line = line.strip()
                    self.stopwordsDict.add(line)

        if self.emotions:
            self.emotionscorer = emotions.EmotionScorer(self.name)
            self.emotionscorer.loadModels()

        models_loaded = True

    def removeEndingElongated(self, text):
        text = re.sub(r'[a][a]+([^A-Za-z])', 'a\g<1>', text)
        text = re.sub(r'[a][a]+$', 'a', text)
        text = re.sub(r'[e][e]+([^A-Za-z])', 'e\g<1>', text)
        text = re.sub(r'[e][e]+$', 'e', text)
        text = re.sub(r'[i][i]+([^A-Za-z])', 'i\g<1>', text)
        text = re.sub(r'[i][i]+$', 'i', text)
        text = re.sub(r'[o][o]+([^A-Za-z])', 'o\g<1>', text)
        text = re.sub(r'[o][o]+$', 'o', text)
        text = re.sub(r'[u][u]+([^A-Za-z])', 'u\g<1>', text)
        text = re.sub(r'[u][u]+$', 'u', text)
        return text

    def replaceEmoji(self, match):
        delimiters = (' ', ' ')
        val = self.codes_dict.get(match.group(0), match.group(0))
        return delimiters[0] + val[1:-1] + delimiters[1]

    def emojiSubstitution(self, text):
        res = re.sub(self.emoji_regexp, self.replaceEmoji, text)
        text = re.sub(u'\ufe0f', '', res)
        return text

    def removeStopwords(self, spacyTokens):
        lexiconList = []
        for token in spacyTokens:
            if str(token.lemma_) in self.stopwordsDict:
                continue
            lexiconList.append(token)
        return lexiconList

    def removeBlacklist(self, spacyTokens, blacklist):
        lexiconList = []
        for token in spacyTokens:
            if str(token.lemma_) in blacklist:
                continue
            lexiconList.append(token)
        return lexiconList

    def cleanString(self, text):
        regex = re.compile('[^A-Za-z ]')
        return regex.sub('', text)


    def checkUpperCase(self, inputarray):
        
        fistString = str(inputarray[0][1])
        fistString = self.cleanString(fistString)

        if len(inputarray) > 1:
            secondString = str(inputarray[1][1])
            returnString = ""
            
            if inputarray[0][0] == -1 and inputarray[1][0] == 1:

                if re.match(r'\s', secondString):
                    addSpace = True
                    returnString = returnString + " "
                    secondString = secondString.lstrip()

                if len(fistString) == 1 and len(secondString) == 1:
                    if fistString.lower() == secondString.lower():
                        returnString = returnString + fistString
                        return(returnString)
                else:
                    returnString = returnString + secondString
                    return(returnString)
        else:
            if inputarray[0][0] == 1:
                return(fistString)
            else:
                return("")

    def restoreUpperCase(self, text1, text2):

        dmp = diff_match_patch()
        diff = dmp.diff_main(text1, text2)
        dmp.diff_cleanupSemantic(diff)
        # print(diff)

        betweenzerolist = []
        restoredString = ""
        if len(diff) == 1:
            restoredString = diff[0][1]

        else:   
            for d in diff:
                if d[0] is not 0:
                    betweenzerolist.append(d)

                else:
                    if len(betweenzerolist) > 0:
                        stringToPrint = self.checkUpperCase(betweenzerolist)
                        restoredString = restoredString + stringToPrint
                        betweenzerolist = []
                        restoredString = restoredString + str(d[1])
                    else:
                        restoredString = restoredString + d[1]


            if len(betweenzerolist) > 0:
                stringToPrint = self.checkUpperCase(betweenzerolist)
                restoredString = restoredString + stringToPrint

        return(restoredString)

    def parseText(self, text, blacklist=[]):
        retData = dict()
        retData['originalText'] = text

        if self.remove_ending_elongated:
            text = self.removeEndingElongated(text)

        if self.convert_emoji:
            text = self.emojiSubstitution(text)

        if self.convert_hashtags:
            text = re.sub('#', ' #', text)
            text = text.lower()
            text = ' '.join(self.text_processor.pre_process_doc(text))
        
        text = re.sub(r'\s+', ' ', text)

        if self.restore_case:
            retData['lowerText'] = text
            text = self.restoreUpperCase(retData['originalText'], text)

        text = text.strip()
        retData['preprocessedText'] = text
        if self.lemma:
            spacyTokens = self.lemmatizer(text)
            if self.use_stopwords:
                spacyTokens = self.removeStopwords(spacyTokens)
            if len(blacklist) > 0:
                spacyTokens = self.removeBlacklist(spacyTokens, blacklist)
            lemmatizedTweet = ''
            for l in spacyTokens:
                lemmatizedTweet += l.lemma_ + ' '
            retData['lemmatizedTweet'] = lemmatizedTweet
            text = lemmatizedTweet.strip()

        if self.emotions:
            res = self.emotionscorer.extractEmotions(text)
            retData["preprocessEmotions"] = text
            retData["emotions"] = res

        return retData
        
