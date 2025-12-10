import os
import pwd
import time

def list_pids():
    return [int(p) for p in os.listdir("/proc") if p.isdigit()]

def get_uid(pid: int) -> int | None:
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("Uid:"):
                    return int(line.split()[1])  # Real UID
    except FileNotFoundError:
        return None  # Process ended
    except PermissionError:
        return None  # Uncommon but safe

def get_cpu_ticks(pid: int) -> int | None:
    try:
        with open(f"/proc/{pid}/stat") as f:
            data = f.read().split()
            utime = int(data[13])
            stime = int(data[14])
            return utime + stime
    except FileNotFoundError:
        return None
    except PermissionError:
        return None

def count_user_processes(uid: int) -> int:
    count = 0
    for pid in list_pids():
        p_uid = get_uid(pid)
        if p_uid == uid:
            count += 1
    return count

def user_is_active(uid: int) -> bool:
    return count_user_processes(uid) > 0

def user_cpu_usage(uid: int) -> int:
    total = 0
    for pid in list_pids():
        p_uid = get_uid(pid)
        if p_uid == uid:
            ticks = get_cpu_ticks(pid)
            if ticks is not None:
                total += ticks
    return total


def username_from_uid(uid: int) -> str:
    return pwd.getpwuid(uid).pw_name

def is_human_uid(uid: int) -> bool:
    return uid >= 1000

def is_human_user_ldap(uid: int) -> bool:
    try:
        entry = pwd.getpwuid(uid)
    except KeyError:
        return False

    shell = entry.pw_shell
    return shell not in ("/usr/sbin/nologin", "/usr/bin/nologin", "/bin/false")

def list_human_users():
    human = []
    for entry in pwd.getpwall():
        uid = entry.pw_uid
        shell = entry.pw_shell

        # filter out system accounts
        if uid < 1000:
            continue

        # filter out non-login shells
        if shell in ("/usr/sbin/nologin", "/usr/bin/nologin", "/bin/false", ""):
            continue

        human.append({
            "uid": uid,
            "username": entry.pw_name,
            "home": entry.pw_dir,
            "shell": shell
        })
    return human



def read_cpu_times():
    with open("/proc/stat") as f:
        fields = f.readline().split()[1:]
        return list(map(int, fields))

num_cores = os.cpu_count()
# cpu_usage = min(cpu_usage / num_cores, 100.0)

def cpu_percent(interval=1.0):
    t1 = read_cpu_times()
    time.sleep(interval)
    t2 = read_cpu_times()

    idle1 = t1[3] + t1[4]
    idle2 = t2[3] + t2[4]

    non_idle1 = sum(t1[:3] + t1[5:8])
    non_idle2 = sum(t2[:3] + t2[5:8])

    total1 = idle1 + non_idle1
    total2 = idle2 + non_idle2

    totald = total2 - total1
    idled = idle2 - idle1
    nonidled = non_idle2 - non_idle1

    cpu_usage = (nonidled / totald) * 100.0
    return cpu_usage

