# -*- coding: utf-8 -*-
import os, sys
path = os.path.join(os.path.dirname(__file__), '../lib/')
sys.path.append(path)
import json, requests, rsa
import tanys

from thrift.transport import THttpClient
from thrift.protocol import TCompactProtocol

from Gen import LineService
from Gen.ttypes import *

class Talk:
  client = None
  _session = requests.session()

  auth_query_path = "/api/v4/TalkService.do";
  http_query_path = "/S4";
  wait_for_mobile_path = "/Q";
  host = "gd2.line.naver.jp";
  port = 443;#80
  UA = "Line/7.4.7 iPad3,6 7.0.2"
  LA = "IOSIPAD 7.4.7 iPhone OS 7.0.2"

  authToken = None
  cert = None

  def __init__(self):
    self.transport = THttpClient.THttpClient("https://"+self.host,None, self.http_query_path)
    self.transport.setCustomHeaders({
      "X-Line-Application" : self.LA,"User-Agent" : self.UA})
    self.transport.open()
    #self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport);
    self.protocol = TCompactProtocol.TCompactProtocol(self.transport);
    self.client = LineService.Client(self.protocol)

  def login(self, mail, passwd, cert=None, callback=None):
    tanys.Login(sid=mail,password=passwd,callback=callback,uke=self.ready)
    
  def ready(self,moji):
    r = moji.split(",")
    self.cert = r[0]
    self.authToken = r[1]
    self.transport.setCustomHeaders({
      "X-Line-Application" : self.LA,
      "User-Agent" : self.UA,
      "X-Line-Access" : r[1]
      })
    self.transport.path = self.http_query_path
  def TokenLogin(self, authToken):
    self.transport.setCustomHeaders({"X-Line-Application" : self.LA,"User-Agent" : self.UA,"X-Line-Access" : authToken,})
    self.authToken = authToken
    self.transport.path = self.http_query_path

  def qrLogin(self, callback):
    self.transport.path = self.auth_query_path

    qr = self.client.getAuthQrcode(True,"UGSBot")
    callback("line://au/q/" + qr.verifier)
    self.headers = {'X-Line-Application': self.LA, 'X-Line-Access': qr.verifier}
    r = requests.get("https://gd2.line.naver.jp/Q", headers=self.headers)
    vr = r.json()["result"]["verifier"]
    lr = self.client.loginWithVerifierForCerificate(vr)
    self.transport.setCustomHeaders({"X-Line-Application" : self.LA,"User-Agent" : self.UA,"X-Line-Access": lr.authToken})
    self.authToken = lr.authToken
    self.cert = lr.certificate
    self.transport.path = self.http_query_path
    

  def __crypt(self, mail, passwd, RSA):
    message = (chr(len(RSA.sessionKey)) + RSA.sessionKey +
                   chr(len(mail)) + mail +
                   chr(len(passwd)) + passwd).encode('utf-8')

    pub_key = rsa.PublicKey(int(RSA.nvalue, 16), int(RSA.evalue, 16))
    crypto = rsa.encrypt(message, pub_key).encode('hex')

    return crypto
