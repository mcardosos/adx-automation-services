
import os
import logging
import base64
import datetime
import coloredlogs
import requests
from kubernetes import client as kube_client
from kubernetes import config as kube_config

coloredlogs.install(level=logging.INFO)
logger = logging.getLogger('a01.svc.email.newsletter')  # pylint: disable=invalid-name

INTERNAL_COMMUNICATION_KEY = os.environ['A01_INTERNAL_COMKEY']
# SMTP_SERVER = os.environ['A01_REPORT_SMTP_SERVER']
# SMTP_USER = os.environ['A01_REPORT_SENDER_ADDRESS']
# SMTP_PASS = os.environ['A01_REPORT_SENDER_PASSWORD']
STORE_HOST = os.environ.get('A01_STORE_NAME', 'task-store-web-service-internal')

DEV = os.environ['DEV']
PRODUCTS = os.environ['PRODUCTS'] # products that requirte a runs newsletter
NAMESPACE = 'a01-prod'

class InternalAuth(object):  # pylint: disable=too-few-public-methods
    def __call__(self, req):
        req.headers['Authorization'] = INTERNAL_COMMUNICATION_KEY
        return req


SESSION = requests.Session()
SESSION.auth = InternalAuth()

def get_receivers(product: str) -> str:
    if DEV:
        kube_config.load_kube_config()
    else:
        kube_config.load_incluster_config()

    api = kube_client.CoreV1Api()
    secret = api.read_namespaced_secret(name=product, namespace=NAMESPACE)
    receivers = base64.standard_b64decode(secret.data['owners.weekly']).decode("utf-8")
    logger.info(f'receivers for weekly email for product {product} are {receivers}')

    return receivers

def get_task_store_uri(path: str) -> str:
    # in debug mode, the service is likely run out of a cluster, switch to https schema
    if not DEV:
        return f'https://{STORE_HOST}/api/{path}'
    return f'http://{STORE_HOST}/api/{path}'

def create_report():
    products = PRODUCTS.split(',')
    for product in products:
        receivers = get_receivers(product)

        before = (datetime.datetime.now().date() - datetime.timedelta(days=1))
        after = (before - datetime.timedelta(days=7))
        params = {
            'product': product,
            'before': before.strftime('%m-%d-%Y'),
            'after': after.strftime('%m-%d-%Y')
        }

        runs = SESSION.get(get_task_store_uri(f'runs'), params=params).json()
        logger.info(f'got runs from {after} to {before}')

        for run in runs:
            run_id = run['id']
            tasks = SESSION.get(get_task_store_uri(f'run/{run_id}/tasks')).json()
