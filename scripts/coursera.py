#
# Testing solutions for Coursera
#
#
#
try:
  from urllib import urlencode
  from urllib2 import urlopen
except Exception:
  from urllib.parse import urlencode
  from urllib.request import urlopen
import hashlib
import base64

class CourseraException(Exception):
    pass

class WeekTestCase:
    def __init__(self, week):
        self.testsuite = week
        self.name = "Name not set"
        self.test_id = "XXXYYYZZZ"

class WeekTest:
    coursera_challenge_url = "http://class.coursera.org/conrob-002/assignment/challenge"
    coursera_submit_url = "http://class.coursera.org/conrob-002/assignment/submit"

    def __init__(self, gui):
        self.gui = gui
        self.week = 0
        # Test is a tuple - 'title','id',function
        self.tests = []
        self.login = None
        self.password = None
        
        self.callback = None
        self.submit = True
        
        self.testname = 'Name not set'
    
    def setuser(self, login, password):
        self.login = str(login)
        self.password = str(password)
    
    def run_tests(self,tests = None):
        if tests is None:
            tests = list(range(len(self.tests)))
        for i in tests:
            self.test(self.tests[i])
    
    def test(self,testcase,callback):
        
        if isinstance(testcase,int):
            testcase = self.tests[testcase]
        
        self.callback = callback
        self.testcase = testcase

        params = urlencode({
            'email_address' : self.login,
            'assignment_part_sid' : testcase.test_id,
            'response_encoding' : 'delim'
            }).encode('utf-8')
        response = urlopen(url=WeekTest.coursera_challenge_url, data = params)

        string = response.read().decode('utf-8').split('|')[1:]

        self.c_response = {}
        for i in range(len(string)//2):
            try:
                self.c_response[string[2*i]] = string[2*i+1]
            except Exception:
                pass
            
        if 'email_address' not in self.c_response or not self.c_response['email_address']:
            raise CourseraException("Communication with server failed")
        elif 'challenge_key' not in self.c_response or not self.c_response['challenge_key'] \
                or 'state' not in self.c_response or not self.c_response['state']:
            # Error occured, error string in email_address
            print(self.c_response)
            raise CourseraException(self.c_response['email_address'])
        
        testcase.start_test()

    def respond(self,fn_output):

        if self.callback is None:
            return

        ch_resp = hashlib.sha1((self.c_response['challenge_key'] + self.password).encode('utf-8')).hexdigest()

        params = urlencode(
        {'assignment_part_sid': self.testcase.test_id,
            'email_address': self.c_response['email_address'],
            'submission': base64.standard_b64encode(fn_output.encode('utf-8')),
            'submission_aux': b'',
            'challenge_response': ch_resp,
            'state': self.c_response['state']}).encode('utf-8');
        
        self.callback(urlopen(url=self.coursera_submit_url, data = params).read().decode('utf-8'))
        
        self.testcase = None
        self.callback = None
        
