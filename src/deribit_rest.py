import time, hashlib, requests, base64, sys, hmac
from collections import OrderedDict
import datetime
import json as jsonparser

class RestClient(object):
    def __init__(self, key, secret, url):
        self.key = key
        self.secret = secret
        self.session = requests.Session()
        self.url = url

    def request(self, action, data):
        response = None
        if action.startswith("/api/v2/private/"):           #if private need AUTH
            if self.key is None or self.secret is None:
                raise Exception("Key or secret empty")
        
            tstamp = int(time.time()* 1000)
            nonce = str(datetime.datetime.now())
            
            def converter(data):
                key = data[0]
                value = data[1]
                if isinstance(value, list):
                    return '='.join([str(key), ''.join(value)])
                else:
                    return '='.join([str(key), str(value)])

            items = map(converter, data.items())
            signature_string = '&'.join(items)
            if len(signature_string)>0:
                signature_string ='?'+signature_string;

            sig=self.generatesignature(action+signature_string,tstamp,nonce);   
            
            Authorization="deri-hmac-sha256 id=%s,ts=%s,sig=%s,nonce=%s" %(self.key,tstamp,sig,nonce);
            response = self.session.get(self.url + action, params=data, headers={'Authorization': Authorization}, verify=True)
        else:                                               #if public , no need AUTH
            response = self.session.get(self.url + action, params=data, verify=True)
        
        if response.status_code != 200:
            print(response)
            return "Wrong response code: {0}".format(response.status_code)

        json = response.json()

        if "error" in json:
            print(json["error"])
            return "Failed: " + json["error"]

        if "result" in json:
            return json["result"]
        elif "message" in json:
            return json["message"]
        else:
            return "Ok"

    def generatesignature(self,url,tstamp,nonce):
        """
        To generate signature
        input:
            url: string [eg: [eg: /api/v2/private/xxxx]
            tstamp: int 
            nonce: string [any string for encryption]
        return:
            string [signature]
            
        """
        RequestData = 'GET' + "\n" + url + "\n" + "" + "\n";
        StringToSign = str(tstamp) + "\n" + nonce + "\n" + RequestData;

        signature = hmac.new(
            bytes(self.secret, "latin-1"),
            msg=bytes(StringToSign, "latin-1"),
            digestmod=hashlib.sha256
        ).hexdigest().lower()
        return signature;

    def getinstruments(self,currency, kind):
        '''
        to get available trading instruments
        input:
            currency: string ['BTC', 'ETH']
            kind:string [eg: 'future' or 'option']
        '''
        assert kind in ['future','option']
        
        options = {
            'currency': currency,
            'kind':kind
        }

        return self.request("/api/v2/public/get_instruments", options)
    
    def getportfoliomargin(self, curr, instrs):
        
        options = {
             'currency':curr, 
             'simulated_positions': jsonparser.dumps(instrs),
             'add_positions': False
        }

        return self.request("/api/v2/public/get_portfolio_margins", options)
    

    def getinstrument(self, instr):
        options = {
            'instrument_name': instr,
        }

        return self.request("/api/v2/public/get_instrument", options)
    

    def getindex(self, currency):
        options = {
            "currency":currency,
            }

        response=self.request("/api/v2/public/get_index", options);
        return response
    
    def getopenorders(self, currency, kind):
        '''
        to retrieve pending orders [order not yet settled]
        input:
            currency: string in 'BTC' or 'ETH'
        output:
            [ID1, ID2...]
        '''
        options = {
            "currency":currency,
            "kind": kind
            }

        response=self.request("/api/v2/private/get_open_orders_by_currency", options);
        return response

    def getpositions(self, currency, kind):
        '''
        to retrieve position by currency
        input:
            currency: string in 'BTC' or 'ETH'
        return: 
            int [size of position. positive for 'buy' and negative for 'sell'
            
        '''

        options = {
            "currency":currency,
            "kind": kind
            }
        response=self.request("/api/v2/private/get_positions", options);
        return response
    

    def buy(self, instrument, quantity, price, postOnly=None, time_in_force="fill_or_kill"):
        options = {
            "instrument_name": instrument,
            "amount": quantity,
            "price": price,
            "time_in_force": time_in_force
        }
  
        if postOnly:
            options["postOnly"] = postOnly

        return self.request("/api/v2/private/buy", options)


    def sell(self, instrument, quantity, price, postOnly=None, time_in_force="fill_or_kill"):
        options = {
            "instrument_name": instrument,
            "amount": quantity,
            "price": price,
            "time_in_force": time_in_force
        }

        if postOnly:
            options["postOnly"] = postOnly

        return self.request("/api/v2/private/sell", options)
