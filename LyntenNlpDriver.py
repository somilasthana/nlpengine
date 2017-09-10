import json
import os
import subprocess
import socket
from urlparse import urlparse
import time
import sys
import requests
from PConfig import PConfig
from PConstant import PConstant
import logging
// Most of this code is taken from Lynten/stanford-corenlp 
// But needed a fine control


class LyntenNlpDriver(object):

    def __init__(self, memory = '4g', port=9050, lang='en', kstart=False):

        self.config = PConfig()
        self.corenlp_path = self.config[PConstant.CORENLP_CONFIG.value]
        self.port = port
        self.lang = lang
        self._flogger()
        if kstart:
            self.cmd = self.cmdnativeserver(memory, port, lang)
            self.pid = self.runnativeserver(self.cmd)

        

    def cmdnativeserver(self, memory, port, lang):

        cmd = "java"
        java_args = "-Xmx{}".format(memory)
        java_class = "edu.stanford.nlp.pipeline.StanfordCoreNLPServer"
        path = '"{}*"'.format(self.corenlp_path)
        args = [cmd, java_args, '-cp', path, java_class, '-port', str(port)]
        args = ' '.join(args)
        return args

    def runnativeserver(self,args):

        p = None
        with open(os.devnull, 'w') as null_file:    
            out_file = null_file
            p = subprocess.Popen(args, shell=True, stdout=out_file, stderr=subprocess.STDOUT)

        self.url = 'http://localhost:' + str(self.port)
        self._logger.info("initiating corenlp server '%s'", self.url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = urlparse(self.url).hostname
        while sock.connect_ex((host_name, self.port)):
            time.sleep(1)
        self._logger.info("successful running corenlp server '%s'", self.url)
        return p

    def _request(self, annotators=None, data=None):

        if sys.version_info.major >= 3:
            data = data.encode('utf-8')

        self._logger.info("requesting corenlp server services '%s'", annotators)
        properties = {'annotators': annotators, 'pipelineLanguage': self.lang, 'outputFormat': 'json'}
        r = requests.post(self.url, params={'properties': str(properties)}, data=data,headers={'Connection': 'close'})
        r_dict = json.loads(r.text)
        return r_dict

    def annotate(self, text, properties=None):

        if sys.version_info.major >= 3:
            text = text.encode('utf-8')
        self._logger.info("requesting corenlp server to annotate '%s'", text)
        r = requests.post(self.url, params={'properties': str(properties)}, data=text,
                          headers={'Connection': 'close'})
        return r.text

    def word_tokenize(self, sentence):
        
        r_dict = self._request('ssplit,tokenize', sentence)
        return [token['word'] for s in r_dict['sentences'] for token in s['tokens']]

    def pos_tag(self, sentence):

        r_dict = self._request('pos', sentence)
        words = []
        tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['word'])
                tags.append(token['pos'])
        return list(zip(words, tags))

    def ner(self, sentence):

        r_dict = self._request('ner', sentence)
        words = []
        ner_tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['word'])
                ner_tags.append(token['ner'])
        return list(zip(words, ner_tags))

    def pos_tag_ner(self, sentence):

        r_dict = self._request('pos', sentence)
        r_dict_ner = self._request('ner', sentence)
        words = []
        tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['word'])
                tags.append(token['pos'])
        ner_tags = []
        for s in r_dict_ner['sentences']:
            for token in s['tokens']:
                ner_tags.append(token['ner'])
        return list(zip(zip(words, tags),ner_tags))

    def parse(self, sentence):
        r_dict = self._request('pos,parse', sentence)
        return [s['parse'] for s in r_dict['sentences']][0]

    def dependency_parse(self, sentence):
        r_dict = self._request('depparse', sentence)
        return [(dep['dep'], dep['governor'], dep['dependent']) for s in r_dict['sentences'] for dep in
                s['basicDependencies']]

    def _flogger(self):

        self._logger = logging.getLogger('LyntenNlpDriver')
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

