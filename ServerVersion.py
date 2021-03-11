# -*- coding: utf-8 -*-
# @Time    : 2020/8/19 09:40
# @Author  : WJRYR
# @FileName: ServerVersion.py
import re

from burp import IBurpExtender
from burp import IHttpListener
from burp import IMessageEditorTab
from burp import IMessageEditorTabFactory

class BurpExtender(IBurpExtender, IHttpListener, IMessageEditorTabFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("ServerVersion")
        callbacks.registerHttpListener(self)
        callbacks.registerMessageEditorTabFactory(self)
        print '[+] ##################################\n' \
              '[+]     ServerVersion\n' \
              '[+]     Author: WJRYR\n' \
              '[+] ##################################\n'

    def createNewInstance(self, controller, editable):
        return SvINFOTab(self, controller, editable)

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if messageIsRequest:
            return
        response = messageInfo.getResponse()
        r = self._helpers.analyzeResponse(response)
        msg = str(r.getHeaders())
        if isSv(msg):
            messageInfo.setHighlight('pink')

class SvINFOTab(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self._extender = extender
        self._helpers = extender._helpers
        self._editable = editable
        self._txtInput = extender._callbacks.createTextEditor()
        self._txtInput.setEditable(editable)
        self.isInfo = False

    def getTabCaption(self):
        return "ServerVersion"

    def getUiComponent(self):
        return self._txtInput.getComponent()

    def isEnabled(self, response, isRequest):
        r = self._helpers.analyzeResponse(response)
        msg = str(r.getHeaders())
        sv = isSv(msg)
        if not isRequest:
            if sv:
                return True

    def setMessage(self, content, isRequest):
        if content:
            if isRequest:
                r = self._helpers.analyzeRequest(content)
            else:
                r = self._helpers.analyzeResponse(content)
            msg = str(r.getHeaders())
            info = ""
            sv = isSv(msg)
            if sv:
                info += '[SV] ' + ','.join(sv) + '\n'
            self._txtInput.setText(info)
        else:
            return False

def isSv(string):
    sv = re.findall(r'Server: [a-z0-9A-Z]{2,20}/[0-9.]{1,15}', string)
    if sv != ['']:
        return sv
    else:
        return False
