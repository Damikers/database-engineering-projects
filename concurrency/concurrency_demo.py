import psycopg2
import threading
import time
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "lab2_db"),
    "user": os.getenv("DB_USER", "lab2_user"),
    "password": os.getenv("DB_PASSWORD", "change_me"),
}

THREADS = 10
ITERATIONS = 10_000


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def reset_counter():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE user_counter SET counter = 0, version = 0 WHERE user_id = 1")
    conn.commit()
    cur.close()
    conn.close()


def get_counter():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT counter FROM user_counter WHERE user_id = 1")
    value = cur.fetchone()[0]
    cur.close()
    conn.close()
    return value


def lost_update_worker():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(ITERATIONS):
        cur.execute("SELECT counter FROM user_counter WHERE user_id = 1")
        counter = cur.fetchone()[0]
        counter += 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = 1", (counter,))
        conn.commit()
    cur.close()
    conn.close()


def inplace_update_worker():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(ITERATIONS):
        cur.execute("UPDATE user_counter SET counter = counter + 1 WHERE user_id = 1")
        conn.commit()
    cur.close()
    conn.close()


def row_lock_worker():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(ITERATIONS):
        cur.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE")
        counter = cur.fetchone()[0]
        counter += 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = 1", (counter,))
        conn.commit()
    cur.close()
    conn.close()


def optimistic_worker():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(ITERATIONS):
        while True:
            cur.execute("SELECT counter, version FROM user_counter WHERE user_id = 1")
            counter, version = cur.fetchone()
            counter += 1
            cur.execute(
                "UPDATE user_counter SET counter = %s, version = %s WHERE user_id = %s AND version = %s",
                (counter, version + 1, 1, version)
            )
            conn.commit()
            if cur.rowcount > 0:
                break
    cur.close()
    conn.close()


def run_scenario(name, worker_fn):
    reset_counter()
    threads = [threading.Thread(target=worker_fn) for _ in range(THREADS)]
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start
    final = get_counter()
    print("--------------------------------+---------------+-------------------")
    print(f"{name:<30}  | {elapsed:<13.2f} | {final}")


def main():
    print("Варіант                         | Час виконання |  Фінальний counter")
    run_scenario("Lost Update", lost_update_worker)
    run_scenario("In-place Update", inplace_update_worker)
    run_scenario("Row-level Locking", row_lock_worker)
    run_scenario("Optimistic Concurrency Control", optimistic_worker)


if __name__ == "__main__":
    main()
