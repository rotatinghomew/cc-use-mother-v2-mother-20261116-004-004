from __future__ import annotations
from collections import defaultdict,deque
from decimal import Decimal
class FairMatchMarket:
    def feasible(self,candidate,vacancy):
        reasons=[];skills=set(candidate.get('skills',()));required=set(vacancy.get('required_skills',()))
        if required-skills:reasons.append('missing_skills')
        if Decimal(str(vacancy.get('salary','0')))<Decimal(str(candidate.get('minimum_salary','0'))):reasons.append('salary_below_minimum')
        if int(vacancy.get('commute_minutes',0))>int(candidate.get('maximum_commute',999)):reasons.append('commute_exceeds_limit')
        if vacancy.get('work_mode') not in set(candidate.get('work_modes',(vacancy.get('work_mode'),))):reasons.append('work_mode_mismatch')
        return not reasons,tuple(reasons)
    def score(self,candidate,vacancy,exposures):
        skills=set(candidate.get('skills',()));required=set(vacancy.get('required_skills',()));overlap=Decimal(len(skills&required))/Decimal(max(1,len(skills|required)));salary=Decimal(str(vacancy.get('salary','0')));minimum=Decimal(str(candidate.get('minimum_salary','0')));salary_gain=(salary-minimum)/max(Decimal('1'),minimum or Decimal('1'));commute=Decimal(str(vacancy.get('commute_minutes',0)))/Decimal('120');penalty=Decimal(str(exposures.get(str(vacancy['id']),0)))*Decimal('0.03');return overlap+min(Decimal('0.5'),salary_gain)-commute-penalty
    def preferences(self,candidates,vacancies,exposures):
        result={}
        for candidate in candidates:
            ranked=[]
            for vacancy in vacancies:
                ok,_=self.feasible(candidate,vacancy)
                if ok:ranked.append((self.score(candidate,vacancy,exposures),str(vacancy['id'])))
            result[str(candidate['id'])]=[vid for _,vid in sorted(ranked,key=lambda x:(-x[0],x[1]))]
        return result
    def clear(self,candidates,vacancies,exposures):
        prefs=self.preferences(candidates,vacancies,exposures);vacancy_by={str(v['id']):v for v in vacancies};candidate_by={str(c['id']):c for c in candidates};queue=deque(sorted(prefs));next_index=defaultdict(int);held=defaultdict(list)
        while queue:
            cid=queue.popleft();choices=prefs[cid]
            if next_index[cid]>=len(choices):continue
            vid=choices[next_index[cid]];next_index[cid]+=1;held[vid].append(cid);capacity=int(vacancy_by[vid].get('capacity',1));held[vid].sort(key=lambda key:(-Decimal(str(candidate_by[key].get('employer_score',0))),key));rejected=held[vid][capacity:];held[vid]=held[vid][:capacity];queue.extend(rejected)
        return {cid:vid for vid,cids in held.items() for cid in cids}
    def exposure_plan(self,vacancies,history,slots):
        groups=defaultdict(list)
        for vacancy in vacancies:groups[str(vacancy.get('industry','other'))].append(vacancy)
        result=[]
        while len(result)<slots and groups:
            for group in sorted(list(groups)):
                choices=sorted(groups[group],key=lambda vacancy:(history.get(str(vacancy['id']),0),str(vacancy['id'])))
                if choices:result.append(str(choices[0]['id']));groups[group]=choices[1:]
                if not groups[group]:groups.pop(group,None)
                if len(result)>=slots:break
        return result
