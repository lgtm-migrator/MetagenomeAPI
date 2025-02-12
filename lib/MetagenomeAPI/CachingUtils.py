import json
import requests
import logging

class CachingUtils:
    # looks here for CachingService docs: https://github.com/kbase/cachingservice
    def __init__(self, config):
        if config.get('caching_service_url'):
            self.caching_service_url = config['caching_service_url']
        else:
            self.caching_service_url = config.get('kbase-endpoint') + '/cache/v1'

    def remove_cache(self, token, cache_id):
        """Removed/delete Cache"""
        logging.info(f"Deleting Cache with id {cache_id}")
        endpoint = self.caching_service_url + "/cache/" + cache_id
        resp = requests.delete(endpoint, headers={"Authorization": token})
        logging.debug(f'Response of {resp.ok} from deleting cache_id {cache_id}')
        return resp.ok

    def upload_to_cache(self, token, cache_id, data):
        """Save string content to a cache."""
        logging.info('uploading string to cache', cache_id)
        logging.debug('data is', data)
        endpoint = self.caching_service_url + '/cache/' + cache_id
        bytestring = str.encode(json.dumps(data))
        resp = requests.post(
            endpoint,
            files={'file': ('data.txt', bytestring)},
            headers={'Authorization': token}
        )
        resp_json = resp.json()
        logging.debug(f"status is {resp_json['status']}\n")
        if resp_json['status'] == 'error':
            raise Exception(resp_json['error'])

    def get_cache_id(self, token, data):
        # Generate the cache_id
        logging.debug('generating a cache_id')
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        endpoint = self.caching_service_url + '/cache_id'
        resp_json = requests.post(endpoint, data=json.dumps(data), headers=headers).json()
        if resp_json.get('error'):
            raise Exception(resp_json['error'])
        logging.debug('generated cache', resp_json)
        return resp_json['cache_id']

    def download_cache_string(self, token, cache_id):
        """
        Fetch cached data as string. Returns none if the cache does not exist.
        """
        endpoint = self.caching_service_url + '/cache/' + cache_id
        logging.info('attempting to download cache', cache_id)
        resp = requests.get(endpoint, headers={'Authorization': token})
        if resp.status_code == 200:
            logging.debug('returning cached data')
            return resp.text
        else:
            logging.debug('cache does not exist')
