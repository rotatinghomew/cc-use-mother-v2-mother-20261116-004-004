来沈青年岗位匹配与曝光公平交易台
测试：python3 -m unittest discover -s tests -v
构建：python3 -m compileall -q job_match_market tests
验收：python3 -m job_match_market --database /tmp/job_match_market.sqlite3 run --fixture fixtures/acceptance.json --output /tmp/job_match_market-output.json
单测：python3 -m unittest tests.test_domain -v
