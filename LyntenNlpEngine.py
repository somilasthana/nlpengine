import LyntenNlpDriver
from PConstant import PConstant
import logging 


class LyntenNlpEngine(object):

    def __init__(self):
        
        self.nlphandle = LyntenNlpDriver.LyntenNlpDriver() 
        self._flogger()

    def discovery(self, wcontent):

        self._logger.info("web request to discover '%d'", len(wcontent))
        self.wcontent = wcontent
        ner = self.nlphandle.ner(self.wcontent)
        entity = []
        nermap = {} 
        for nv in ner:
            nermap.setdefault(nv[1], [])
            nermap[nv[1]].append(nv[0])

        for kn in nermap:
            if not kn == 'O': 
                nmap = {}
                nmap.setdefault("entityname", kn)
                nmap.setdefault("tags", list(set(nermap[kn])))                
                entity.append(nmap)

        pos = self.nlphandle.pos_tag(self.wcontent)

        posmap = {}
        for pv in pos:
            if not pv[1] in ['$', ':' ,',', '.', 'CC', 'DT', 'IN', 'MD', 'PRP', 'PRP$', 'RB', 'TO', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ' ]:
                posmap.setdefault(pv[1], [])
                posmap[pv[1]].append(pv[0])

        ninterest = posmap['NN']
        
        summarylist = self._posanalysis(pos)
        summarymap = { 'len' : len(summarylist) }
        for cnt,slist in enumerate(summarylist):
            summarymap['summary '+str(cnt)] = slist

        discoverymap = { 'entity' : entity, 'interesting points': ninterest, 'summarylist' : summarymap}
        return discoverymap 

    def _posanalysis(self,pos):
        statemachine = {}
        statemachine['START'] = {'NNP':('NNP', '+')}
        statemachine['END'] =   {'NNP': ('NNP', '*') }
        statemachine['NNP'] = {'NNP': ('NNP', '+'), 'JJ': ('JJ', '+'), 'NN':('NNP', '+'), 'CD':('NNP', '?')}
        statemachine['JJ'] =  {'JJ': ('JJ', '+'), 'NNS':('NNS', '+'), 'NN':('JJ', '+'), 'NNP':('END', '+')}
        statemachine['NNS'] = {'NNS': ('NNS', '+'), 'NN': ('NNS', '?'), 'CD':('NNS', '?'), 'NNP': ('END', '+'), 'JJ':('END', '?') }

        cstate = pstate = 'START'
        contentparts = []
        part = []
        for pv in pos:
            pstate = cstate
            if pv[1] in statemachine[cstate]:
                (cstate,ops) = statemachine[cstate][pv[1]]
                if ops == '+':
                    part.append((pv[0],pv[1]))
                if ops == '*':
                    contentparts.append(part + [(pv[0],pv[1])])
                    part = [(pv[0],pv[1])]

        supermasterparts = []
        for cpitem in contentparts:
            masterparts = []
            posval = None
            for cp in cpitem:
                if posval is None:
                    posval = cp[1]
                    word = [cp[0]]
                elif posval == cp[1]:
                    word.append(cp[0])
                else:
                    masterparts.append(' '.join(word))
                    word = [cp[0]]
                    posval= cp[1] 
            supermasterparts.append(masterparts)
        return supermasterparts

    def _flogger(self):

        self._logger = logging.getLogger('LyntenNlpEngine')
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
