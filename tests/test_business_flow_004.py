import unittest
from job_match_market.market_clearing.fair_match import FairMatchMarket
class FairMarketTests(unittest.TestCase):
 def setUp(self):self.market=FairMatchMarket();self.c={'id':'c1','skills':['python','sql'],'minimum_salary':'10000','maximum_commute':45,'work_modes':['onsite'],'employer_score':5};self.v={'id':'v1','required_skills':['python'],'salary':'12000','commute_minutes':30,'work_mode':'onsite','industry':'software','capacity':1}
 def test_hard_constraints(self):self.assertTrue(self.market.feasible(self.c,self.v)[0])
 def test_missing_skill(self):self.assertIn('missing_skills',self.market.feasible(self.c,{**self.v,'required_skills':['go']})[1])
 def test_salary_floor(self):self.assertIn('salary_below_minimum',self.market.feasible(self.c,{**self.v,'salary':'9000'})[1])
 def test_exposure_penalty(self):self.assertGreater(self.market.score(self.c,self.v,{}),self.market.score(self.c,self.v,{'v1':10}))
 def test_capacity_clearing(self):self.assertEqual(self.market.clear([self.c,{**self.c,'id':'c2','employer_score':2}],[self.v],{}),{'c1':'v1'})
 def test_industry_rotation(self):self.assertEqual(self.market.exposure_plan([self.v,{**self.v,'id':'v2','industry':'manufacturing'},{**self.v,'id':'v3','industry':'software'}],{'v1':4,'v2':0,'v3':0},2),['v2','v3'])
