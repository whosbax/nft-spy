from spies.jpgstoreapis.jpgstoreapis import JpgStoreApi
import time

while True:
    spy_jpg_store = JpgStoreApi()
    spy_jpg_store.process()
    time.sleep(JpgStoreApi.SLEEP_PROCESS_API)
