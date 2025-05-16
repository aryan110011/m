#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import requests
from datetime import datetime
from threading import Thread

# ---------------------- CONFIG ---------------------- #
PASSWORD = "sarfu123"
TOKENS_FILE = "tokens.txt"
COMMENTS_FILE = "comments.txt"
BACKUP_FILE = "backup_tasks.json"

# ---------------------- DESIGN ---------------------- #
def clear():
    os.system('clear')

def show_logo():
    clear()
    logo = """
\033[1;31m

                  __                    _ _           
                 / _|                  | | |          
  ___  __ _ _ __| |_ _   _   _ __ _   _| | | _____  __
 / __|/ _` | '__|  _| | | | | '__| | | | | |/ _ \ \/ /
 \__ \ (_| | |  | | | |_| | | |  | |_| | | |  __/>  < 
 |___/\__,_|_|  |_|  \__,_| |_|   \__,_|_|_|\___/_/\_\\
                                                      

              MADE BYE =>   ArYan.x3 Don Tool
\033[0m
"""
    print(logo)
    print("\033[1;33m🕒 Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("\033[0m")

def ask_password():
    pw = input("\033[1;33m🔐 Enter Password: \033[0m")
    if pw != PASSWORD:
        print("\033[1;31m❌ Incorrect Password!")
        exit()

# ---------------------- HELPERS ---------------------- #
def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_uptime(start_time):
    now = datetime.now()
    delta = now - start_time
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def validate_token(token):
    try:
        r = requests.get(f"https://graph.facebook.com/me?access_token={token}", timeout=10)
        return r.ok, r.json().get("name", "Unknown")
    except:
        return False, "Unknown"

def post_comment(token, post_id, comment):
    try:
        url = f"https://graph.facebook.com/{post_id}/comments"
        r = requests.post(url, data={'message': comment, 'access_token': token}, timeout=10)
        return r.ok
    except:
        return False

# ---------------------- CORE TOOL ---------------------- #
def main_menu():
    while True:
        show_logo()
        print("\n\033[1;32m[1] Start Auto Comment")
        print("[2] View Backup IDs")
        print("[3] Resume Task")
        print("[4] Exit Tool\033[0m")
        opt = input("\nChoose option: ")
        if opt == "1":
            start_auto_comment()
        elif opt == "2":
            view_backups()
        elif opt == "3":
            resume_task()
        elif opt == "4":
            exit()

def load_ids():
    show_logo()
    print("\n\033[1;36m[+] Login via:\n[1] Single Token\n[2] Single Cookie\n[3] Multi File (tokens.txt/cookies.txt)")
    choice = input("Choose option: ")

    tokens = []
    if choice == '1':
        token = input("Enter Access Token: ").strip()
        tokens = [token]
    elif choice == '2':
        cookie = input("Enter Cookie: ").strip()
        try:
            token = get_token_from_cookie(cookie)
            tokens = [token]
        except:
            print("\033[1;31m[!] Failed to fetch token from cookie.")
            return []
    elif choice == '3':
        filepath = input("Enter file path (tokens.txt / cookies.txt): ").strip()
        if not os.path.exists(filepath):
            print("\033[1;31m[!] File not found.")
            return []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if "EAA" in line:
                    tokens.append(line)
                elif "c_user=" in line:
                    try:
                        token = get_token_from_cookie(line)
                        tokens.append(token)
                    except:
                        continue

    valid_ids = []
    for token in tokens:
        ok, name = validate_token(token)
        if ok:
            valid_ids.append((token, name))

    return valid_ids[:20]

def get_token_from_cookie(cookie):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
    r = requests.get("https://business.facebook.com/business_locations", headers=headers)
    token = r.text.split('EAAG')[1].split('"')[0]
    return "EAAG" + token

def start_auto_comment():
    ids = load_ids()
    if not ids:
        print("\033[1;31m[!] No valid IDs loaded.")
        time.sleep(2)
        return

    print(f"\033[1;32m[+] {len(ids)} IDs loaded. Max 20 used.")

    post_count = int(input("How many post IDs to comment on? "))
    post_ids = [input(f"Post ID {i+1}: ").strip() for i in range(post_count)]

    comment_mode = input("Comment from file? (y/n): ").lower()
    if comment_mode == 'y':
        with open(COMMENTS_FILE, 'r') as f:
            comments = [c.strip() for c in f if c.strip()]
    else:
        comments = [input("Enter single comment: ")]

    hatter_name = input("Enter your name (hatter): ").strip()
    delay = int(input("Delay between comments (seconds): "))
    conlosa = input("Conlosa name for backup: ").strip()

    backup = load_json(BACKUP_FILE)
    backup[conlosa] = {
        "ids": ids,
        "posts": post_ids,
        "comments": comments,
        "name": hatter_name,
        "delay": delay
    }
    save_json(BACKUP_FILE, backup)

    comment_loop(ids, post_ids, comments, hatter_name, delay)

def comment_loop(ids, post_ids, comments, hatter, delay):
    start_time = datetime.now()
    while True:
        for post_id in post_ids:
            for token, name in ids:
                for comment in comments:
                    final_comment = f"{hatter} {comment}"
                    retries = 0
                    while retries < 5:
                        if post_comment(token, post_id, final_comment):
                            uptime = get_uptime(start_time)
                            print(f"\033[1;32m[✓] {name} -> {post_id} | {final_comment} | Uptime: {uptime}")
                            break
                        else:
                            retries += 1
                            print(f"\033[1;31m[!] Retry {retries} {name} | Waiting 5s...")
                            time.sleep(5)
                    time.sleep(delay)

def view_backups():
    show_logo()
    backup = load_json(BACKUP_FILE)
    if not backup:
        print("\033[1;31m[!] No backups found.")
        time.sleep(2)
        return
    for name in backup:
        print(f"\033[1;36m- {name}\033[0m")
    task = input("Enter conlosa name to view: ").strip()
    if task in backup:
        print(json.dumps(backup[task], indent=4))
    else:
        print("\033[1;31m[!] Task not found.")
    input("Press Enter to return...")

def resume_task():
    backup = load_json(BACKUP_FILE)
    if not backup:
        print("\033[1;31m[!] No saved tasks.")
        return
    for name in backup:
        print(f"\033[1;36m- {name}")
    task = input("Enter conlosa name to resume: ").strip()
    data = backup.get(task)
    if not data:
        print("\033[1;31m[!] Task not found.")
        return
    comment_loop(data["ids"], data["posts"], data["comments"], data["name"], data["delay"])

# ---------------------- RUN ---------------------- #
if __name__ == "__main__":
    show_logo()
    ask_password()
    main_menu()
