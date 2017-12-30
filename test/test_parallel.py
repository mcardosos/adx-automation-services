import requests
from concurrent.futures import ThreadPoolExecutor

# logging.basicConfig(level=logging.DEBUG)

host = 'http://localhost:5000'

# reset all the status
for task in requests.get(f'{host}/run/5/tasks').json():
    task_id = task['id']
    requests.patch(f'{host}/task/{task_id}', json={'status': 'initialized'}).raise_for_status()


def checkout_task(run_id):
    while True:
        resp = requests.post(f'{host}/run/{run_id}/checkout')
        resp.raise_for_status()
        print(resp.json()['id'])
        if resp.status_code == 204:
            break


with ThreadPoolExecutor() as pool:
    futures = [pool.submit(checkout_task, 5) for _ in range(3)]
    for f in futures:
        f.done()