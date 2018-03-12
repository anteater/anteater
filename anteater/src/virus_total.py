import json
import logging
import os
import re
import requests
import redis
import sys
import time
import urllib
import uuid
from pylimit import PyRateLimit
import six.moves.configparser

class VirusTotal():
    def __init__(self, *args):
        self.logger = logging.getLogger(__name__)
        self.base_url = 'https://www.virustotal.com/vtapi/v2/'
        self.HTTP_OK = 200
        self.HTTP_BAD = 400
        self.HTTP_FORBIDDEN = 403
        self.HTTP_RATE_EXCEEDED = 204
        self.public_api_sleep_time = 20
        self.logger = logging.getLogger(__name__)
        self.uuid = uuid.uuid4()
        self.config = six.moves.configparser.SafeConfigParser()
        self.config.read('anteater.conf')

        try: # might be better to move this to its own class
            conn = redis.StrictRedis(
                host='localhost',
                port=6379,
                password='')
            conn.ping()
            PyRateLimit.init(redis_host="localhost", redis_port=6379)
        except Exception as ex:
            self.logger.error('Error: %s', ex)
            exit('Failed to connect, terminating.')
        
        self.limit = PyRateLimit()

        try:
            vt_rate_type = self.config.get('config', 'vt_rate_type')
        except six.moves.configparser.NoSectionError:
            self.logger.error("A config section is required for vt_rate_type with a public | private option ")
            sys.exit(1)

        patten = re.compile(r'\bpublic\b|\bprivate\b')
        if not patten.match(vt_rate_type):
            self.logger.error("Unrecognized %s option for vt_rate_type", vt_rate_type)
            sys.exit(1)

        if vt_rate_type == 'public':
            self.limit.create(21,1)
        elif vt_rate_type == 'private':
            self.limit.create(1,1)

    def rate_limit(self):
        """
        Simple rate limit function using redis
        """
        rate_limited_msg = False

        while True:
            is_rate_limited = self.limit.is_rate_limited(uuid)
            if is_rate_limited:
                time.sleep(0.3) # save hammering the shit out of redis
                if not rate_limited_msg:
                    self.logger.info('Rate limit active..please wait...')
                    rate_limited_msg = True
                    
            
            if not is_rate_limited:
                self.logger.info('Rate limit clear.')
                self.limit.attempt(uuid)
                return True

    def scan_file(self, filename, apikey):
        """
        Sends a file to virus total for assessment
        """
        url = self.base_url + "file/scan"
        params = {'apikey': apikey}
        scanfile = {"file": open(filename, 'rb')}
        response = requests.post(url, files=scanfile, params=params)
        rate_limit_clear = self.rate_limit()
        if rate_limit_clear:
            if response.status_code == self.HTTP_OK:
                json_response = response.json()
                return json_response
            elif response.status_code == self.HTTP_RATE_EXCEEDED:
                time.sleep(20)
            else:
                self.logger.error("sent: %s, HTTP: %d", filename, response.status_code)

    def rescan_file(self, filename, sha256hash, apikey):
        """
        just send the hash, check the date
        """
        url = self.base_url + "file/rescan"
        params = {
            'apikey': apikey,
            'resource': sha256hash
        }
        
        headers = {
            "Accept-Encoding": "gzip, deflate",
            "User-Agent" : "gzip,  lhinds" # set this to a config value!
        }
        rate_limit_clear = self.rate_limit()
        if rate_limit_clear:
            response = requests.post(url, params=params)
            if response.status_code == self.HTTP_OK:
                self.logger.info("sent: %s, HTTP: %d, content: %s", os.path.basename(filename), response.status_code, response.text)
            elif response.status_code == self.HTTP_RATE_EXCEEDED:
                    time.sleep(20)
            else:
                self.logger.error("sent: %s, HTTP: %d", os.path.basename(filename), response.status_code)
            return response

    def binary_report(self, sha256sum, apikey):
        """
        retrieve report from file scan
        """
        url = self.base_url + "file/report"
        params = {"apikey": apikey, "resource": sha256sum}
        rate_limit_clear = self.rate_limit()

        if rate_limit_clear:
            response = requests.post(url, data=params)
            
            if response.status_code == self.HTTP_OK:
                json_response = response.json()
                response_code = json_response['response_code']
                return json_response
            elif response.status_code == self.HTTP_RATE_EXCEEDED:
                time.sleep(20)
            else:
                self.logger.warning("retrieve report: %s, HTTP code: %d", os.path.basename(filename), response.status_code)
        

    def send_ip(self, ipaddr, apikey):
        """
        Send IP address for list of past malicous domain associations
        """
        url = self.base_url + "ip-address/report"
        parameters = {"ip": ipaddr, "apikey": apikey}
        rate_limit_clear = self.rate_limit()
        if rate_limit_clear:
            response = requests.get(url, params=parameters)
            if response.status_code == self.HTTP_OK:
                json_response = response.json()
                return json_response
            elif response.status_code == self.HTTP_RATE_EXCEEDED:
                    time.sleep(20)
            else:
                self.logger.error("sent: %s, HTTP: %d", ipaddr, response.status_code)
            time.sleep(self.public_api_sleep_time)

    def url_report(self, scan_url, apikey):
        """
        Send URLS for list of past malicous associations
        """
        headers = {
            "Accept-Encoding": "gzip, deflate",
            "User-Agent" : "gzip,  My Python requests library example client or username"
            }
        url = self.base_url + "url/report"
        params = {"apikey": apikey, 'resource':scan_url}
        rate_limit_clear = self.rate_limit()
        if rate_limit_clear:
            response = requests.post(url, params=params, headers=headers)
            if response.status_code == self.HTTP_OK:
                json_response = response.json()
                return json_response
            elif response.status_code == self.HTTP_RATE_EXCEEDED:
                time.sleep(20)    
            else:
                self.logger.error("sent: %s, HTTP: %d", scan_url, response.status_code)
            time.sleep(self.public_api_sleep_time)
