import random
from random import SystemRandom
import secrets
from bit import *
from bit.format import bytes_to_wif
from binascii import hexlify
import multiprocessing
from multiprocessing import Process, Value
import atexit
import time
from datetime import timedelta, datetime

keys_per_second = Value('i', 0)  # Shared variable to store keys per second
total_keys_generated = Value('i', 0)  # Shared variable to store total keys generated
generated_keys = []  # List to store all generated keys

def seconds_to_str(elapsed=None):
    if elapsed is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        return str(timedelta(seconds=elapsed))

def log(txt, elapsed=None):
    colour_cyan = '\033[36m'
    colour_reset = '\033[0;0;39m'
    colour_red = '\033[31m'
    print('\n ' + colour_cyan + '  [TIMING]> [' + seconds_to_str() + '] ----> ' +
          txt + '\n' + colour_reset)
    if elapsed:
        print("\n " + colour_red + " [TIMING]> Elapsed time ==> " + elapsed +
              "\n" + colour_reset)

def end_log():
    end = time.time()  # Use time.time() instead of time()
    elapsed = end - start
    log("End Program", seconds_to_str(elapsed))
    print("\nGenerated Keys:")
    for key in generated_keys:
        print(key)
    keys_per_sec = keys_per_second.value / elapsed
    print(f"\nKeys per second: {keys_per_sec:.2f}")
    print(f"Total Keys Generated: {total_keys_generated.value}")

start = time.time()  # Use time.time() instead of time()
atexit.register(end_log)
log("Start Program")

print("Loading Puzzle TXT Please Wait and Good Luck...")
with open("puzzle.txt", "r") as m:
    add = m.read().split()
add = set(add)

cores = 6  # CPU Control Set Cores

def seek(r, keys_per_second, total_keys_generated):
    while True:
        ran = secrets.SystemRandom().randrange(
            36893488147419103232,
            73786976294838206464)
        key1 = Key.from_int(ran)
        wif = bytes_to_wif(key1.to_bytes(), compressed=False)
        wif2 = bytes_to_wif(key1.to_bytes(), compressed=True)
        key2 = Key(wif)
        caddr = key1.address
        uaddr = key2.address
        myhex = "%064x" % ran
        private_key = myhex[:64]
        generated_keys.append((ran, caddr, wif2, private_key))  # Store the generated keys
        total_keys_generated.value += 1  # Increment total_keys_generated
        if caddr in add:
            print("Nice One Found!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", ran, caddr, wif2,
                  private_key)
            s1 = str(ran)
            s2 = caddr
            s3 = wif2
            s4 = private_key
            f = open(u"CompressedWinner.txt", "a")
            f.write(s1 + ":" + s2 + ":" + s3 + ":" + s4)
            f.write("\n")
            f.close()
            break
        keys_per_second.value += 1  # Increment keys_per_second

if __name__ == '__main__':
    jobs = []
    for r in range(cores):
        p = Process(target=seek, args=(r, keys_per_second, total_keys_generated))
        jobs.append(p)
        p.start()

    # Monitor and display the keys per second
    while True:
        time_elapsed = time.time() - start  # Use time.time() instead of time()
        if time_elapsed > 0:
            keys_per_sec = keys_per_second.value / time_elapsed
            print(f"\rKeys per second: {keys_per_sec:.2f}", end='', flush=True)
        total_keys = total_keys_generated.value
        print(f"\tTotal Keys Generated: {total_keys}", end='', flush=True)
        time.sleep(1)  # Update every 1 second
