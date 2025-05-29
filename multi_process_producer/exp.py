import time
import sys
import signal
from multiprocessing import Process, Value, Lock
from helpers import generate_user_event

def gen_data(counter, lock):
        while True:
            try:
                event = generate_user_event()
                with lock:
                    counter.value += 1
            except KeyboardInterrupt as e:
                print("Exiting gracefully.....")
        
        
def exit_gracefully(counter, start):
    end = time.time()
    total_time = end - start
    print(f"Total run time: {total_time:.2f} seconds")
    print(f"Total events generated: {counter.value}")
    sys.exit(0)

if __name__ == "__main__":
    counter = Value('i', 0)
    lock = Lock()
    processes = []
    start= time.time()

    def signal_handler(sig, frame):
        exit_gracefully(counter, start)

    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

    for _ in range(5):
        p = Process(target=gen_data, args=(counter, lock))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
    end= time.time()

    total_time = end - start
    print(f"total run time in seconds: {total_time}")
    print(f"Total events fired: {counter}")









