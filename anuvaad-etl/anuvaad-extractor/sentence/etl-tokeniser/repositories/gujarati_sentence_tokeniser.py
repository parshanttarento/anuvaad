import re
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters, PunktTrainer, PunktLanguageVars
from nltk.tokenize import sent_tokenize


"""
Utility tokenizer class for anuvaad project
"""
class AnuvaadGujaratiTokenizer(object):
    """
    Default abbrevations
    incomplete char range = ([\u0A81-\u0A83,\u0ABC-\u0ACD,\u0AE2-\u0AE5, \u0AF0-\u0AF1])
    complete char range = ([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])    
    (\u09F0-\u09F9) represents character used in different lnguages other than bengali which use bengali script
    number range = ([\u0AE6-\u0AEF])
    arabic abbreviation symbol = ([\u0AFA-\u0AFF])
    source for unicodes : https://unicode.org/charts/PDF/U0A80.pdf
    """
    _abbrevations_with_non_generalize_pattern = []
    _abbrevations_with_non_generalize = []
    _text_abbrevations_pattern_cic = r'((\s)(([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])([\u0A81-\u0A83,\u0ABC-\u0ACD,\u0AE2-\u0AE5, \u0AF0-\u0AF1])?([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])?(\u002e)(\s)?){1,})'
    _text_abbrevations_pattern_cci = r'((\s)(([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])?([\u0A81-\u0A83,\u0ABC-\u0ACD,\u0AE2-\u0AE5, \u0AF0-\u0AF1])?(\u002e)(\s)?){1,})'
    _text_colon_abbreviations_pattern = r'(([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])([\u0A81-\u0A83,\u0ABC-\u0ACD,\u0AE2-\u0AE5, \u0AF0-\u0AF1])?[:](\s)?[\u0A81-\u0AFF|-])'
    _text_abbrevations_without_space_pattern = r'(^(([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])([\u0A81-\u0A83,\u0ABC-\u0ACD,\u0AE2-\u0AE5, \u0AF0-\u0AF1])?([\u0A85-\u0AB9,\u0AD0-\u0AE1,\u0AF9])?([\u0A81-\u0A83,\u0ABC-\u0ACD,\u0AE2-\u0AE5, \u0AF0-\u0AF1])?(\u002e)(\s)?){1,})'
    _text_abbrevations_cic = []
    _text_abbrevations_cci = []
    _text_colon_abbreviations = []
    _text_abbrevations_without_space = []
    _tokenizer = None
    _regex_search_texts = []
    _date_abbrevations  = []
    _table_points_abbrevations = []
    _brackets_abbrevations = []
    _decimal_abbrevations = []
    _url_abbrevations = []
    _dot_with_char_abbrevations = []
    _dot_with_quote_abbrevations = []
    _dot_with_number_abbrevations = []
    _dot_with_beginning_number_abbrevations = []
    
    def __init__(self, abbrevations=None):
        if abbrevations is not None:
            self._abbrevations_without_space.append(abbrevations)
        self._regex_search_texts = []
        self._text_abbrevations_cic =[]
        self._text_abbrevations_cci =[]
        self._text_colon_abbreviations = []
        self._text_abbrevations_without_space = []
        self._dot_abbrevations = []
        self._date_abbrevations = []
        self._time_abbreviations = []
        self._table_points_abbrevations = []
        self._brackets_abbrevations = []
        self._dot_with_char_abbrevations = []
        self._dot_with_quote_abbrevations = []
        self._dot_with_number_abbrevations = []
        self._decimal_abbrevations = []
        self._url_abbrevations = []
        self._dot_with_beginning_number_abbrevations = []
        self._tokenizer = PunktSentenceTokenizer(lang_vars=SentenceEndLangVars())

    def tokenize(self, text):
        print('--------------Process started-------------')
        text = self.serialize_with_abbrevations(text)
        text = self.serialize_colon_abbreviations(text)
        text = self.serialize_dates(text)
        text = self.serialize_time(text)
        text = self.serialize_table_points(text)
        text = self.serialize_url(text)
        text = self.serialize_pattern(text)
        text = self.serialize_dots(text)
        text = self.serialize_brackets(text)
        text = self.serialize_dot_with_number(text)
        text = self.serialize_dot_with_number_beginning(text)
        text = self.serialize_quotes_with_number(text)
        text = self.serialize_bullet_points(text)
        text = self.serialize_decimal(text)
        text = self.add_space_after_sentence_end(text)
        text = self.serialize_end(text)
        sentences = self._tokenizer.tokenize(text)
        output = []
        for se in sentences:
            se = self.deserialize_dates(se)
            se = self.deserialize_time(se)
            se = self.deserialize_pattern(se)
            se = self.deserialize_url(se)
            se = self.deserialize_dots(se)
            se = self.deserialize_decimal(se)
            se = self.deserialize_brackets(se)
            se = self.deserialize_dot_with_number(se)
            se = self.deserialize_dot_with_number_beginning(se)
            se = self.deserialize_quotes_with_number(se)
            se = self.deserialize_colon_abbreviations(se)
            se = self.deserialize_with_abbrevations(se)
            se = self.deserialize_bullet_points(se)
            se = self.deserialize_table_points(se)
            se = self.deserialize_end(se)
            if se != '':
                output.append(se.strip())
        print('--------------Process finished-------------')
        return output

    def serialize_url(self, text):
        patterns = re.findall(r'(?:(?:https?):?:(?:(?://)|(?:\\\\))+(?:(?:[\w\d:#@%/;$()~_?\+-=\\\.&](?:#!)?))*)',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._url_abbrevations.append(pattern)
                text = pattern_obj.sub('URL_'+str(index)+'_URL', text)
                index+=1
        return text

    def deserialize_url(self, text):
        index = 0
        if self._url_abbrevations is not None and isinstance(self._url_abbrevations, list):
            for pattern in self._url_abbrevations:
                pattern_obj = re.compile(re.escape('URL_'+str(index)+'_URL'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def serialize_decimal(self, text):
        patterns = re.findall(r'(?:(?:[ ]|[(]|[-])[0-9]{1,}[.][0-9]{1,}(?:[ ]|[)]|[%]))',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._decimal_abbrevations.append(pattern)
                text = pattern_obj.sub('DE_'+str(index)+'_DE', text)
                index+=1
        return text

    def deserialize_decimal(self, text):
        index = 0
        if self._decimal_abbrevations is not None and isinstance(self._decimal_abbrevations, list):
            for pattern in self._decimal_abbrevations:
                pattern_obj = re.compile(re.escape('DE_'+str(index)+'_DE'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def add_space_after_sentence_end(self, text):
        sentence_ends = ['.','?','!',';',':','।', '॥']
        for sentence_end in sentence_ends:
            pattern = re.compile(r'['+sentence_end+'][ ]') #remove already correct patterns
            text = pattern.sub(sentence_end, text)
            pattern = re.compile(r'['+sentence_end+']')
            text = pattern.sub(sentence_end + ' ', text)
        return text

    def serialize_end(self, text):
        pattern_d = re.compile(r'(\u0965)')
        text = pattern_d.sub(' END_||_END', text)
        pattern = re.compile(r'(\u0964)')
        text = pattern.sub(' END_|_END ', text)
        return text

    def deserialize_end(self, text):
        pattern = re.compile(re.escape(' END_|_END'), re.IGNORECASE)
        text = pattern.sub('।', text)
        pattern = re.compile(re.escape(' END_||_END'), re.IGNORECASE)
        text = pattern.sub('॥', text)
        return text

    def serialize_bullet_points(self, text):
        pattern1 = re.compile(r'(?!^)[•]')
        text = pattern1.sub('TT__TT UU_0_UU', text)
        pattern2 = re.compile(r'(?!^)[▪]')
        text = pattern2.sub('TT__TT UU_1_UU', text)
        pattern3 = re.compile(r'(?!^)[●]')
        text = pattern3.sub('TT__TT UU_2_UU', text)
        return text

    def deserialize_bullet_points(self, text):
        pattern = re.compile(re.escape('TT__TT'), re.IGNORECASE)
        text = pattern.sub('', text)
        pattern = re.compile(re.escape('UU_0_UU'), re.IGNORECASE)
        text = pattern.sub('•', text)
        pattern = re.compile(re.escape('UU_1_UU'), re.IGNORECASE)
        text = pattern.sub('▪', text)
        pattern = re.compile(re.escape('UU_2_UU'), re.IGNORECASE)
        text = pattern.sub('●', text)
        return text

    def serialize_table_points(self, text):
        patterns = re.findall(r'(?:(?:(?:[ ][(]?(?:(?:[0,9]|[i]|[x]|[v]){1,3}|[a-zA-Z\u0980-\u09FE]{1,1})[)])|(?:[ ](?:(?:[0-9]|[i]|[x]|[v]){1,3}|[a-zA-Z\u0980-\u09FE]{1,1})[.][ ])))',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._table_points_abbrevations.append(pattern)
                text = pattern_obj.sub('RR_'+str(index)+'_RR', text)
                index+=1
        return text

    def deserialize_table_points(self, text):
        index = 0
        if self._table_points_abbrevations is not None and isinstance(self._table_points_abbrevations, list):
            for pattern in self._table_points_abbrevations:
                pattern_obj = re.compile(re.escape('RR_'+str(index)+'_RR'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def serialize_brackets(self, text):
        patterns = re.findall(r'(?:[(](?:[0-9\u0980-\u09FEa-zA-Z][.]?|[ ]){1,}[)]?).',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._brackets_abbrevations.append(pattern)
                text = pattern_obj.sub('WW_'+str(index)+'_WW', text)
                index+=1
        return text

    def deserialize_brackets(self, text):
        index = 0
        if self._brackets_abbrevations is not None and isinstance(self._brackets_abbrevations, list):
            for pattern in self._brackets_abbrevations:
                pattern_obj = re.compile(re.escape('WW_'+str(index)+'_WW'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text
    
    def serialize_dates(self, text):
        patterns = re.findall(r'[0-9]{1,4}[.][0-9]{1,2}[.][0-9]{1,4}',text)   # [0-9]{,2}[.][0-9]{,2}[.][0-9]{2,4}   [0-9]{1,4}[.][0-9]{1,2}[.][0-9]{1,4}
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._date_abbrevations.append(pattern)
                text = pattern_obj.sub('DD_'+str(index)+'_DD', text)
                index+=1
        return text

    def deserialize_dates(self, text):
        index = 0
        if self._date_abbrevations is not None and isinstance(self._date_abbrevations, list):
            for pattern in self._date_abbrevations:
                pattern_obj = re.compile(re.escape('DD_'+str(index)+'_DD'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def serialize_time(self, text):
        patterns = re.findall(r'[0-9]{1,2}[:][0-9]{1,2}',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._time_abbreviations.append(pattern)
                text = pattern_obj.sub('TI_'+str(index)+'_ME', text)
                index+=1
        return text

    def deserialize_time(self, text):
        index = 0
        if self._time_abbreviations is not None and isinstance(self._time_abbreviations, list):
            for pattern in self._time_abbreviations:
                pattern_obj = re.compile(re.escape('TI_'+str(index)+'_ME'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text
    
    def serialize_quotes_with_number(self, text):
        patterns = re.findall(r'([ ][“][0-9a-zA-Z\u0980-\u09FE]{1,}[.])',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._dot_with_quote_abbrevations.append(pattern)
                text = pattern_obj.sub(' ZZ_'+str(index)+'_ZZ', text)
                index+=1
        return text

    def deserialize_quotes_with_number(self, text):
        index = 0
        if self._dot_with_quote_abbrevations is not None and isinstance(self._dot_with_quote_abbrevations, list):
            for pattern in self._dot_with_quote_abbrevations:
                pattern_obj = re.compile(re.escape('ZZ_'+str(index)+'_ZZ'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def serialize_dot_with_number_beginning(self, text):
        patterns = re.findall(r'(^[\s]?[0-9]{1,}[-]?[.])',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._dot_with_beginning_number_abbrevations.append(pattern)
                text = pattern_obj.sub('YY_'+str(index)+'_YY', text)
                index+=1
        return text

    def deserialize_dot_with_number_beginning(self, text):
        index = 0
        if self._dot_with_beginning_number_abbrevations is not None and isinstance(self._dot_with_beginning_number_abbrevations, list):
            for pattern in self._dot_with_beginning_number_abbrevations:
                pattern_obj = re.compile(re.escape('YY_'+str(index)+'_YY'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def serialize_dot_with_number(self, text):
        patterns = re.findall(r'(?:[ ][0-9]{,2}[.][ ])',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._dot_with_number_abbrevations.append(pattern)
                text = pattern_obj.sub(' XX_'+str(index)+'_XX', text)
                index+=1
        return text

    def deserialize_dot_with_number(self, text):
        index = 0
        if self._dot_with_number_abbrevations is not None and isinstance(self._dot_with_number_abbrevations, list):
            for pattern in self._dot_with_number_abbrevations:
                pattern_obj = re.compile(re.escape('XX_'+str(index)+'_XX'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text

    def serialize_dots(self, text):
        pattern = re.compile(r'([.]{3,})|[.](\s)([.](\s)?){1,}')
        text = pattern.sub('XX__XX', text)
        return text

    def deserialize_dots(self, text):
        pattern = re.compile(re.escape('XX__XX'), re.IGNORECASE)
        text = pattern.sub('......', text)
        return text

    def serialize_pattern(self, text):
        patterns = re.findall(r'([\u0980-\u09FE][.]){2,}',text)
        index = 0
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._dot_with_char_abbrevations.append(pattern)
                text = pattern_obj.sub('$$_'+str(index)+'_$$', text)
                index+=1
        return text

    def deserialize_pattern(self, text):
        index = 0
        if self._dot_with_char_abbrevations is not None and isinstance(self._dot_with_char_abbrevations, list):
            for pattern in self._dot_with_char_abbrevations:
                pattern_obj = re.compile(re.escape('$$_'+str(index)+'_$$'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text
           
    def serialize_with_abbrevations(self, text):
        index_cic = 0
        index_cci = 0
        index_for_without_space = 0
        index_no_gen = 0
        for abbrev in self._abbrevations_with_non_generalize_pattern:
            pattern_non_gen = re.compile(abbrev, re.IGNORECASE)
            text = pattern_non_gen.sub('#N'+str(index_no_gen)+'G##', text)
            index_no_gen += 1
        patterns_wo = re.findall(self._text_abbrevations_without_space_pattern, text)
        patterns_wo = [tuple(j for j in pattern if j)[0] for pattern in patterns_wo]
        patterns_wo = list(sorted(patterns_wo, key = len))
        patterns_wo = patterns_wo[::-1]
        if patterns_wo is not None and isinstance(patterns_wo, list):
            for pattern in patterns_wo:
                pattern_obj = re.compile(re.escape(pattern))
                self._text_abbrevations_without_space.append(pattern)
                text = pattern_obj.sub('#W'+str(index_for_without_space)+'S#', text)
                index_for_without_space+=1
        patterns_cic = re.findall(self._text_abbrevations_pattern_cic, text)
        patterns_cic = [tuple(j for j in pattern if j)[0] for pattern in patterns_cic]
        patterns_cic = list(sorted(patterns_cic, key = len))
        patterns_cic = patterns_wo[::-1]
        if patterns_cic is not None and isinstance(patterns_cic, list):
            for pattern in patterns_cic:
                pattern_obj = re.compile(re.escape(pattern))
                self._text_abbrevations_cic.append(pattern)
                text = pattern_obj.sub('#CI'+str(index_cic)+'C#', text)
                index_cic+=1
        patterns_cci = re.findall(self._text_abbrevations_pattern_cci, text)
        patterns_cci = [tuple(j for j in pattern if j)[0] for pattern in patterns_cci]
        patterns_cci = list(sorted(patterns_cci, key = len))
        patterns_cci = patterns_cci[::-1]
        if patterns_cci is not None and isinstance(patterns_cci, list):
            for pattern in patterns_cci:
                pattern_obj = re.compile(re.escape(pattern))
                self._text_abbrevations_cci.append(pattern)
                text = pattern_obj.sub('##C'+str(index_cci)+'CI##', text)
                index_cci+=1        
        return text

    def deserialize_with_abbrevations(self, text):
        index_cic = 0
        index_cci = 0
        index_for_without_space = 0
        index_no_gen = 0
        for abbrev in self._abbrevations_with_non_generalize:
            pattern = re.compile(re.escape('#N'+str(index_no_gen)+'G##'), re.IGNORECASE)
            text = pattern.sub(abbrev, text)
            index_no_gen += 1
        if self._text_abbrevations_without_space is not None and isinstance(self._text_abbrevations_without_space, list):
            for pattern in self._text_abbrevations_without_space:
                pattern_obj = re.compile(re.escape('#W'+str(index_for_without_space)+'S#'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index_for_without_space+=1
        if self._text_abbrevations_cic is not None and isinstance(self._text_abbrevations_cic, list):
            for pattern in self._text_abbrevations_cic:
                pattern_obj = re.compile(re.escape('#CI'+str(index_cic)+'C#'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index_cic+=1
        if self._text_abbrevations_cci is not None and isinstance(self._text_abbrevations_cci, list):
            for pattern in self._text_abbrevations_cci:
                pattern_obj = re.compile(re.escape('##C'+str(index_cci)+'CI##'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index_cci+=1
        return text

    def serialize_colon_abbreviations(self, text):
        index = 0
        patterns = re.findall(self._text_colon_abbreviations_pattern, text)
        patterns = [tuple(j for j in pattern if j)[0] for pattern in patterns]
        patterns = list(sorted(patterns, key = len))
        patterns = patterns[::-1]
        if patterns is not None and isinstance(patterns, list):
            for pattern in patterns:
                pattern_obj = re.compile(re.escape(pattern))
                self._text_colon_abbreviations.append(pattern)
                text = pattern_obj.sub('#C'+str(index)+'C#', text)
                index+=1
        return text

    def deserialize_colon_abbreviations(self, text):
        index = 0
        if self._text_colon_abbreviations is not None and isinstance(self._text_colon_abbreviations, list):
            for pattern in self._text_colon_abbreviations:
                pattern_obj = re.compile(re.escape('#C'+str(index)+'C#'), re.IGNORECASE)
                text = pattern_obj.sub(pattern, text)
                index+=1
        return text


class SentenceEndLangVars(PunktLanguageVars):
    text = []
    with open('repositories/tokenizer_data/end.txt', encoding='utf8') as f:
        text = f.read()
    sent_end_chars = text.split('\n')
    sent_end_chars.remove('TT__TT')