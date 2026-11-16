from __future__ import annotations
from ..market_clearing.fair_match import FairMatchMarket
import datetime as dt
import decimal
import math
import statistics
import ast
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

class DomainError(RuntimeError):
    pass

@dataclass(frozen=True)
class AnalysisResult:
    key: str
    accepted: bool
    value: decimal.Decimal
    reasons: tuple[str,...]
    facts: Mapping[str,Any]=field(default_factory=dict)

class MatchingEngineBase:
    algorithm='matching'
    def normalize(self,rows):
        result=[];seen=set()
        for position,row in enumerate(rows):
            item=dict(row);key=str(item.get('id') or position)
            if key in seen:continue
            seen.add(key);item['_key']=key;item['_position']=position;result.append(item)
        return result
    def rank(self,subjects,context):return sorted([self.evaluate(item,context) for item in self.normalize(subjects)],key=lambda result:(not result.accepted,-result.value,result.key))
    def allocate(self,subjects,context):
        remaining=decimal.Decimal(str(context.get('capacity',100)))-decimal.Decimal(str(context.get('reserved',0)));accepted=[];rejected=[]
        by_key={str(item.get('id')):item for item in self.normalize(subjects)}
        for result in self.rank(subjects,context):
            demand=decimal.Decimal(str(by_key[result.key].get('demand',1)))
            if result.accepted and demand<=remaining:accepted.append(result);remaining-=demand
            else:rejected.append(AnalysisResult(result.key,False,result.value,result.reasons+('allocation_exhausted',),result.facts))
        return accepted,rejected
    def summarize(self,results):
        values=[float(result.value) for result in results];reasons=Counter(reason for result in results for reason in result.reasons)
        return {'count':len(results),'accepted':sum(result.accepted for result in results),'rejected':sum(not result.accepted for result in results),'mean':statistics.fmean(values) if values else 0.0,'median':statistics.median(values) if values else 0.0,'reasons':dict(sorted(reasons.items()))}
    def compare(self,left,right):
        a={item.key:item for item in left};b={item.key:item for item in right};changes=[]
        for key in sorted(set(a)|set(b)):
            old=a.get(key);new=b.get(key)
            if old is None:changes.append({'key':key,'change':'added','accepted':new.accepted})
            elif new is None:changes.append({'key':key,'change':'removed','accepted':old.accepted})
            elif old.accepted!=new.accepted or old.value!=new.value:changes.append({'key':key,'change':'changed','from':str(old.value),'to':str(new.value),'accepted_from':old.accepted,'accepted_to':new.accepted})
        return {'changes':changes,'change_count':len(changes)}

class MatchingEngine(MatchingEngineBase):
    def __init__(self): self.market=FairMatchMarket()
    def evaluate(self,item,context):
        if context.get('vacancy'):
            vacancy=context['vacancy']; ok,reasons=self.market.feasible(item,vacancy); score=self.market.score(item,vacancy,context.get('exposures',{})); return AnalysisResult(str(item.get('id','unknown')),ok,score,reasons,{'vacancy_id':vacancy.get('id'),'fair_score':str(score)})
        key=str(item.get('id','unknown'));skills=set(item.get('skills',[]));required=set(context.get('required_skills',[]));missing=sorted(required-skills);reasons=[]
        if missing:reasons.append('missing_skills:'+','.join(missing))
        salary=decimal.Decimal(str(context.get('salary',0)));minimum=decimal.Decimal(str(item.get('minimum_salary',0)))
        if salary<minimum:reasons.append('salary_below_minimum')
        commute=int(context.get('commute_minutes',0));maximum=int(item.get('maximum_commute',999))
        if commute>maximum:reasons.append('commute_exceeds_limit')
        overlap=len(skills&required);union=len(skills|required);similarity=decimal.Decimal(overlap)/decimal.Decimal(union or 1);exposure=decimal.Decimal(str(context.get('prior_exposures',0)));score=similarity-decimal.Decimal('0.02')*exposure
        return AnalysisResult(key,not reasons,score,tuple(reasons),{'missing_skills':missing,'commute_minutes':commute,'prior_exposures':str(exposure)})
