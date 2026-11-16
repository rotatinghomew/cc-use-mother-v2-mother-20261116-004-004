import decimal
import unittest
from job_match_market.matching.engine import MatchingEngine

class DomainTests(unittest.TestCase):
    def setUp(self): self.engine=MatchingEngine()

    def candidate(self,**changes):
        value={'id':'person-1','skills':['python','sql'],'minimum_salary':'5000','maximum_commute':45};value.update(changes);return value
    def context(self,**changes):
        value={'required_skills':['python','sql'],'salary':'8000','commute_minutes':30,'prior_exposures':0};value.update(changes);return value
    def test_hard_constraints_pass(self):self.assertTrue(self.engine.evaluate(self.candidate(),self.context()).accepted)
    def test_missing_skill(self):self.assertIn('missing_skills:sql',self.engine.evaluate(self.candidate(skills=['python']),self.context()).reasons)
    def test_salary_floor(self):self.assertIn('salary_below_minimum',self.engine.evaluate(self.candidate(),self.context(salary='4000')).reasons)
    def test_commute_limit(self):self.assertIn('commute_exceeds_limit',self.engine.evaluate(self.candidate(),self.context(commute_minutes=60)).reasons)
    def test_exposure_penalty(self):self.assertLess(self.engine.evaluate(self.candidate(),self.context(prior_exposures=5)).value,self.engine.evaluate(self.candidate(),self.context()).value)
    def test_rank_relevant_first(self):self.assertEqual(self.engine.rank([self.candidate(id='partial',skills=['python']),self.candidate(id='full')],self.context())[0].key,'full')
    def test_compare_context(self):self.assertEqual(self.engine.compare(self.engine.rank([self.candidate()],self.context()),self.engine.rank([self.candidate()],self.context(prior_exposures=2)))['change_count'],1)

