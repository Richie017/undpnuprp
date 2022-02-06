from multiprocessing.synchronize import Lock
from threading import Thread

__author__ = 'Sohel'

def import_completed_handler(sender, items=[], user=None, organization=None,**kwargs):
    lock = Lock(ctx=None)
    lock.acquire(True)
    process = Thread(target=sender.run_post_processing_import, args=(items, user, organization,))
    process.start()
    lock.release()
