# Codding by Tanysyz
from __future__ import unicode_literals
import rsa
import requests
import re

from thrift.transport import THttpClient
from thrift.protocol import TCompactProtocol

from HelloWorld.lib.line import LineService
from HelloWorld.lib.line.ttypes import *

EMAIL_REGEX = re.compile('[^@]+@[^@]+\\.[^@]+')

class Login(object):
    UA = "Line/8.2.1"
    LA = "IOSIPAD\t8.2.1\tTanysyz\t11.2.5"

    auth_query_path = "/api/v4/TalkService.do"
    http_query_path = '/S4'
    login_query_path = "/api/v4p/rs"
    wait_for_mobile_path = "/Q"
    host = "https://gd2.line.naver.jp"
    port = 443
    _session = requests.session()
    _headers = {}
    com_name = ''

    headers = {
        "User-Agent": UA,
        "X-Line-Application": LA,
        "X-LHM": "POST",
        "x-lal": "ja-JP_JP"
    }
    def call(callback):
        print (callback)
        
    def __init__(self, sid = None, password = None, callback = call, uke = None, com_name = 'Library T'):
        UA = "Line/8.2.1"
        LA = "IOSIPAD\t8.2.1\tTanysyz\t11.2.5"
        self._headers['User-Agent'] = UA
        self._headers['X-Line-Application'] = LA
        self.userid = sid
        self.password = password
        self.callback = callback
        self.pcname = com_name
        self.uke = uke
        self.login()

    def login(self):
        self.transport = THttpClient.THttpClient(self.host + ":" + str(self.port) + self.http_query_path)
        self.transport.setCustomHeaders(self.headers)
        self.protocol = TCompactProtocol.TCompactProtocol(self.transport)
        self.client = LineService.Client(self.protocol)
        self.transport.open()
        self.transport.path = self.auth_query_path
        r = self.client.getRSAKeyInfo(IdentityProvider.LINE)

        data = (chr(len(r.sessionKey)) + r.sessionKey
                + chr(len(self.userid)) + self.userid
                + chr(len(self.password)) + self.password)

        pub = rsa.PublicKey(int(r.nvalue, 16), int(r.evalue, 16))
        cipher = rsa.encrypt(data, pub).encode('hex')

        login_request = loginRequest()
        login_request.type = 0
        login_request.identityProvider = IdentityProvider.LINE
        login_request.identifier = r.keynm
        login_request.password = cipher
        login_request.keepLoggedIn = 1
        login_request.accessLocation = "127.0.0,1"
        login_request.systemName = self.pcname
        login_request.e2eeVersion = 1

        self.transport.path = self.login_query_path
        r = self.client.loginZ(login_request)

        if r.type == LoginResultType.SUCCESS:
            self.setAttr(r.authToken, self.certificate)
        elif r.type == LoginResultType.REQUIRE_QRCODE:
            pass

        elif r.type == LoginResultType.REQUIRE_DEVICE_CONFIRM:
            print("Masukin kodenya mamank : {}".format(r.pinCode))
            verifier = \
                requests.get(url=self.host + self.wait_for_mobile_path,
                             headers={"X-Line-Access": r.verifier}).json()["result"]["verifier"].encode("utf-8")

            verifier_request = loginRequest()
            verifier_request.type = 1
            verifier_request.verifier = verifier
            verifier_request.e2eeVersion = 1
            r = self.client.loginZ(verifier_request)
            self.uke('%s,%s' % (r.certificate, r.authToken))

        else:
            print("Eror {}".format(r.type))
