import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:5000/resort/pamporovo"  

skills = ["beginner", "intermediate", "advanced", "expert"]
styles = ["all-mountain", "dynamic", "speed"]
pistes = ["green", "blue", "red", "black"]

def send_request(i):
    data = {
        "skill": random.choice(skills),
        "style": random.choice(styles),
        "piste_color": random.choice(pistes),
        "height": random.randint(150, 200),
        "weight": random.randint(50, 100),
    }
    try:
        r = requests.post(URL, data=data)
        return f"{i}: {r.status_code}"
    except Exception as e:
        return f"{i}: ERROR {e}"

if __name__ == "__main__":
    start = time.time()
    n_requests = 50  

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(send_request, range(n_requests)))

    end = time.time()
    print("\n".join(results))
    print(f"⏱️ Изпратени {n_requests} заявки за {end - start:.2f} секунди")
