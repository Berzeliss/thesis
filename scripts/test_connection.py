import psycopg2
import subprocess

DB_CONFIG = {
    "database": "tpch",
    "user": "postgres",
    "password": "thesis",
    "port": 5432,
}

def get_wsl_host():
    try:
        result = subprocess.check_output(
            "ip route | grep default",
            shell=True
        ).decode()

        return result.split()[2]
    except:
        return None

def try_connect(host):
    try:
        conn = psycopg2.connect(host=host, **DB_CONFIG)
        conn.close()
        return True
    except:
        return False

def main():
    print("=== PostgreSQL Connection Tester ===\n")

    hosts = [
        "localhost",
        "127.0.0.1",
        get_wsl_host()
    ]

    working = None

    for host in hosts:
        if not host:
            continue

        print(f"Trying host: {host}")

        if try_connect(host):
            print(f"✔ Connected successfully via {host}\n")
            working = host
            break
        else:
            print(f"✖ Failed on {host}\n")

    if not working:
        print("❌ No connection possible")
        return

    print("🎯 Final working host:", working)


if __name__ == "__main__":
    main()