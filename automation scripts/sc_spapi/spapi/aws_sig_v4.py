import hashlib
import hmac
import logging
import urllib

from collections import OrderedDict
from datetime import datetime
from requests.compat import urlparse

class AWSSigV4:
    def __init__(self, service:str, aws_access_key_id:str, aws_secret_access_key:str, region:str, aws_session_token) -> None:
        logging.info("\"===========================AWSSignV4===========================\"")
        t = datetime.utcnow()
        self.amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        self.datestamp = t.strftime('%Y%m%d')
        self.service = service
        self.access_key = aws_access_key_id
        self.secret_key = aws_secret_access_key
        self.region = region
        self.aws_session_token = aws_session_token

    @staticmethod
    def _sign_msg(key, msg):
        """ Sign message using key """
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def __call__(self, req):
        logging.info(f"Setting the signed authorization header of the request: {req}")
        self.method = req.method
        self.body = req.body
        req_url = urlparse(req.url)
        host = req_url.hostname
        uri = urllib.parse.quote(req_url.path)
        canonical_request, credential_scope, signed_headers = self.__set_string_to_sign(req_url, host, uri)
        string_to_sign = '\n'.join(['AWS4-HMAC-SHA256', self.amzdate, credential_scope, hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()])
        authorization_header = self.__set_authorization_header(credential_scope, signed_headers, string_to_sign)
        logging.debug(f"AWSSIGNv4 headers: {authorization_header}")
        return self.__update_request_headers(req, host, authorization_header)

    def __update_request_headers(self, req, host, authorization_header):
        logging.info("Updating the request header...")
        req.headers.update({
            'host': host,
            'x-amz-date': self.amzdate,
            'Authorization': authorization_header,
            'x-amz-security-token': self.aws_session_token
        })
        return req

    def __set_authorization_header(self, credential_scope, signed_headers, string_to_sign):
        logging.info("Setting the authorization header...")
        kDate = self._sign_msg(('AWS4' + self.secret_key).encode('utf-8'), self.datestamp)
        kRegion = self._sign_msg(kDate, self.region)
        kService = self._sign_msg(kRegion,  self.service)
        kSigning = self._sign_msg(kService, 'aws4_request')
        signature = hmac.new(kSigning, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"AWS4-HMAC-SHA256 Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

    def __set_string_to_sign(self, req_url, host, uri):
        logging.info("Setting the string to sign...")
        canonical_query_string = self.__set_canonical_query_string(req_url)
        headers_to_sign = self.__set_headers_to_sign(host)
        ordered_headers = OrderedDict(sorted(headers_to_sign.items(), key=lambda t: t[0]))
        signed_headers = ';'.join(ordered_headers.keys())
        canonical_headers = ''.join(map(lambda h: ":".join(h) + '\n', ordered_headers.items()))
        payload_hash = self.__set_payload_hash()
        canonical_request = '\n'.join([self.method, uri, canonical_query_string, canonical_headers, signed_headers, payload_hash])
        credential_scope = '/'.join([self.datestamp, self.region, self.service, 'aws4_request'])
        return canonical_request,credential_scope, signed_headers


    def __set_payload_hash(self):
        logging.info("Setting the payload hash...")
        if self.method == 'GET':
            return hashlib.sha256(''.encode('utf-8')).hexdigest()
        else:
            if self.body:
                return hashlib.sha256(self.body.encode('utf-8')).hexdigest()
            else:
                return hashlib.sha256(''.encode('utf-8')).hexdigest()

    def __set_headers_to_sign(self, host):
        logging.info("Setting request headers to sign...")
        headers_to_sign = {'host': host, 'x-amz-date': self.amzdate}
        return headers_to_sign

    def __set_canonical_query_string(self, req_url):
        logging.info("Setting the canonical query string...")
        ordered_query_parameters = self.__extract_query_parameter(req_url)
        return "&".join(map(lambda param: "=".join(param), ordered_query_parameters))
    
    @staticmethod
    def __extract_query_parameter(req_url):
        logging.info(f"Extracting and sorting alphabetically query parameters...")
        if len(req_url.query) > 0:
            split_query_parameters = list(map(lambda param: param.split('='), req_url.query.split('&')))
            return sorted(split_query_parameters, key=lambda param: (param[0], param[1]))
        else:
            logging.info(f"No parameters in the request url: {req_url}")
            return list()