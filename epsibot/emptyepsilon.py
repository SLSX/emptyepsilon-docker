#!/usr/bin/env python3
try:
    import requests
except ImportError:
    import urequests as requests # For micropython.

class EmptyEpsilon:
    def __init__(self, host, port):
        self.slug = 'http://{0}:{1}'.format(host, port)
    def _request(self, endpoint, params):
        uri = [self.slug, endpoint]
        if isinstance(params, dict):
            response = requests.get(''.join(uri), params=params)
        elif isinstance(params, list):
            # EmptyEpsilon HTTP API doesn't conform to URI standard.
            # We need to build our own query.
            uri.append('?')
            uri.append('&'.join(params))
            response = requests.get(''.join(uri))
        data = response.json()
        response.close()
        if 'ERROR' in data:
            raise ValueError(data['ERROR'])
        return data
    def get(self, arg, instance=None):
        """Implements /get.lua API."""
        params = {}
        if instance is not None:
            params['__OBJECT__'] = instance
        if isinstance(arg, dict):
            params.update(arg)
            return self._request('/get.lua', params)
        elif isinstance(arg, list):
            for i, call in enumerate(arg):
                params['v{:04}'.format(i)] = call
            data = self._request('/get.lua', params)
            return [data[key] for key in sorted(data)]
        elif isinstance(arg, str):
            params['value'] = arg
            data = self._request('/get.lua', params)
            return data['value']
        else:
            raise ValueError('arg must must be dict, list or str. <{}> was given.'.format(type(arg)))
    def set(self, arg, instance=None):
        """Implements /set.lua API."""
        params = []
        if instance is not None:
            params.append('__OBJECT__=' + instance)
        if isinstance(arg, list):
            params.extend(arg)
        elif isinstance(arg, str):
            params.append(arg)
        else:
            raise ValueError('Arg must must be list or str. <{}> was given'.format(type(arg)))
        self._request('/set.lua', params=params)
    def exec(self, code, json=False):
        """Implements /exec.lua API."""
        uri = self.slug + '/exec.lua'
        response = requests.post(uri, data=code)
        if json:
            return response.json()
        else:
            return response.text
    def getPlayerShip(self, id=-1, callsign=None):
        """Convinience function to get playerSpaceShip instances."""
        if callsign is not None:
            lua_code = """callsigns = {}
                          function append_callsign(i)
                            callsigns[i] = getPlayerShip(i):getCallSign()
                          end
                          i = 1
                          while(pcall(append_callsign, i))
                          do
                            i = i + 1
                          end
                          return callsigns"""
            callsigns = self.exec(lua_code, json=True)
            for id, clsign in callsigns.items():
                if clsign == callsign:
                    break
        return 'getPlayerShip({})'.format(id)
