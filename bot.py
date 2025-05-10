import requests
import json
import time
import random
from termcolor import colored

# Banner
def print_banner():
    banner = """
╔══════════════════════════════════════════════╗
║       🌟 TokenTails Bot - Auto Tasks         ║
║   Automate your TokenTails account tasks!    ║
║  Developed by: https://t.me/sentineldiscus   ║
╚══════════════════════════════════════════════╝
"""
    print(colored(banner, 'cyan'))

# メールとパスワードを読み込む
def load_credentials():
    try:
        with open('data.txt', 'r') as file:
            credentials = [line.strip().split('|') for line in file if line.strip() and '|' in line]
            return [(cred[0], cred[1]) for cred in credentials if len(cred) == 2]
    except FileNotFoundError:
        print(colored("data.txtファイルが見つかりません！", 'red'))
        return []
    except Exception as e:
        print(colored(f"data.txtの読み込みエラー：{e}", 'red'))
        return []

# トークンとリフレッシュトークンを取得する
def get_new_token(email, password):
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCfitm6sU-lOunY3JpGdn8D4Ng7Dz5m3yk"
    payload = {
        "returnSecureToken": True,
        "email": email,
        "password": password,
        "clientType": "CLIENT_TYPE_WEB"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            id_token = data.get("idToken")
            refresh_token = data.get("refreshToken")
            if id_token and refresh_token:
                print(colored("トークンの更新に成功しました", 'green'))
                return id_token, refresh_token
            else:
                print(colored("トークンの取得に失敗：idTokenまたはrefreshTokenがありません", 'red'))
                return None, None
        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "不明")
            print(colored(f"トークンの取得に失敗：ステータス {response.status_code} - {error_message}", 'red'))
            return None, None
    except requests.exceptions.RequestException as e:
        print(colored(f"新しいトークンの取得エラー：{e}", 'red'))
        return None, None

# idTokenをリフレッシュする
def refresh_id_token(refresh_token):
    url = "https://securetoken.googleapis.com/v1/token?key=AIzaSyCfitm6sU-lOunY3JpGdn8D4Ng7Dz5m3yk"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            new_id_token = data.get("id_token")
            new_refresh_token = data.get("refresh_token")
            if new_id_token:
                print(colored("トークンのリフレッシュに成功しました", 'green'))
                return new_id_token, new_refresh_token
            else:
                print(colored("トークンのリフレッシュに失敗：id_tokenがありません", 'red'))
                return None, None
        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "不明")
            print(colored(f"トークンのリフレッシュに失敗：ステータス {response.status_code} - {error_message}", 'red'))
            return None, None
    except requests.exceptions.RequestException as e:
        print(colored(f"トークンのリフレッシュエラー：{e}", 'red'))
        return None, None

# URL
live_url = "https://api.tokentails.com/user/catbassadors/live"
daily_checkin_url = "https://api.tokentails.com/user/catbassadors/lives/redeem"
profile_url = "https://api.tokentails.com/user/profile"
task_urls = [
    "https://api.tokentails.com/quest/complete/FOLLOW_TG_CHANNEL",
    "https://api.tokentails.com/quest/complete/FOLLOW_X",
    "https://api.tokentails.com/quest/complete/FOLLOW_TG_GROUP",
    "https://api.tokentails.com/quest/complete/FOLLOW_DISCORD",
    "https://api.tokentails.com/quest/complete/FOLLOW_LINKEDIN",
    "https://api.tokentails.com/quest/complete/FOLLOW_IG",
    "https://api.tokentails.com/quest/complete/FOLLOW_TIKTOK"
]

# 'fb'プレフィックス付きのヘッダー
def get_headers(id_token):
    accesstoken = f"fb{id_token}"  # 'fb'プレフィックス
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "accesstoken": accesstoken,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "origin": "https://tokentails.com",
        "referer": "https://tokentails.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

# ユーザープロフィールを取得する（リトライ付き）
def get_user_profile(id_token, refresh_token, email, password):
    headers = get_headers(id_token)
    for attempt in range(3):
        try:
            response = requests.get(profile_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                name = data.get("name", "見つかりません")
                print(colored(f"ユーザー名：{name}", 'green'))
                return name
            elif response.status_code == 401:
                print(colored("トークンが期限切れです。トークンをリフレッシュします...", 'yellow'))
                new_id_token, new_refresh_token = refresh_id_token(refresh_token)
                if new_id_token:
                    headers = get_headers(new_id_token)
                    response = requests.get(profile_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        name = data.get("name", "見つかりません")
                        print(colored(f"ユーザー名：{name}", 'green'))
                        return name
                    else:
                        print(colored(f"トークンリフレッシュ後のプロフィール取得に失敗：ステータス {response.status_code}", 'red'))
                        return None
                else:
                    print(colored("プロフィールのトークンリフレッシュに失敗。再ログインを試みます...", 'yellow'))
                    new_id_token, new_refresh_token = get_new_token(email, password)
                    if new_id_token:
                        headers = get_headers(new_id_token)
                        response = requests.get(profile_url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            name = data.get("name", "見つかりません")
                            print(colored(f"ユーザー名：{name}", 'green'))
                            return name
                        else:
                            print(colored(f"再ログイン後のプロフィール取得に失敗：ステータス {response.status_code}", 'red'))
                            return None
                    else:
                        print(colored("プロフィールの再ログインに失敗", 'red'))
                        return None
            elif response.status_code == 504:
                print(colored(f"プロフィール取得に失敗：ステータス504（試行 {attempt + 1}/3）", 'red'))
                if attempt < 2:
                    time.sleep(2)
                    continue
                print(colored("サーバーが応答しません（504）。TokenTailsのサーバー状態を確認してください。", 'red'))
                return None
            else:
                print(colored(f"プロフィール取得に失敗：ステータス {response.status_code}", 'red'))
                return None
        except requests.exceptions.RequestException as e:
            print(colored(f"プロフィール取得エラー：{e}", 'red'))
            if attempt < 2:
                time.sleep(2)
                continue
            print(colored("3回の試行後に失敗。接続またはサーバーの状態を確認してください。", 'red'))
            return None
    return None

# liveエンドポイントにPOSTリクエストを送信する（リトライ付き）
def send_live_request(id_token, points, refresh_token, email, password):
    headers = get_headers(id_token)
    payload = {
        "points": points,
        "time": 50,
        "type": "CATBASSADORS"
    }
    for attempt in range(3):
        try:
            response = requests.post(live_url, headers=headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 201:
                print(colored(f"Catbassadorsをプレイ成功（{points}ポイント）", 'green'))
                return response.json()
            elif response.status_code == 400:
                print(colored("チケットがありません", 'red'))
                return "ticket_habis"
            elif response.status_code == 401:
                print(colored("トークンが期限切れです。トークンをリフレッシュします...", 'yellow'))
                new_id_token, new_refresh_token = refresh_id_token(refresh_token)
                if new_id_token:
                    headers = get_headers(new_id_token)
                    response = requests.post(live_url, headers=headers, data=json.dumps(payload), timeout=10)
                    if response.status_code == 201:
                        print(colored(f"Catbassadorsをプレイ成功（{points}ポイント）", 'green'))
                        return response.json()
                    elif response.status_code == 400:
                        print(colored("チケットがありません", 'red'))
                        return "ticket_habis"
                    else:
                        print(colored(f"トークンリフレッシュ後のCatbassadorsプレイに失敗：ステータス {response.status_code}", 'red'))
                        return None
                else:
                    print(colored("Catbassadorsのトークンリフレッシュに失敗。再ログインを試みます...", 'yellow'))
                    new_id_token, new_refresh_token = get_new_token(email, password)
                    if new_id_token:
                        headers = get_headers(new_id_token)
                        response = requests.post(live_url, headers=headers, data=json.dumps(payload), timeout=10)
                        if response.status_code == 201:
                            print(colored(f"Catbassadorsをプレイ成功（{points}ポイント）", 'green'))
                            return response.json()
                        elif response.status_code == 400:
                            print(colored("チケットがありません", 'red'))
                            return "ticket_habis"
                        else:
                            print(colored(f"再ログイン後のCatbassadorsプレイに失敗：ステータス {response.status_code}", 'red'))
                            return None
                    else:
                        print(colored("Catbassadorsの再ログインに失敗", 'red'))
                        return None
            elif response.status_code == 504:
                print(colored(f"Catbassadorsプレイに失敗：ステータス504（試行 {attempt + 1}/3）", 'red'))
                if attempt < 2:
                    time.sleep(2)
                    continue
                print(colored("サーバーが応答しません（504）。TokenTailsのサーバー状態を確認してください。", 'red'))
                return None
            else:
                print(colored(f"Catbassadorsプレイに失敗：ステータス {response.status_code}", 'red'))
                return None
        except requests.exceptions.RequestException as e:
            print(colored(f"Catbassadorsプレイエラー：{e}", 'red'))
            if attempt < 2:
                time.sleep(2)
                continue
            print(colored("3回の試行後に失敗。接続またはサーバーの状態を確認してください。", 'red'))
            return None
    return None

# デイリーチェックインのGETリクエストを送信する（リトライ付き）
def send_daily_checkin_request(id_token, refresh_token, email, password):
    headers = get_headers(id_token)
    for attempt in range(3):
        try:
            response = requests.get(daily_checkin_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(colored("デイリーチェックインに成功しました", 'green'))
                return True
            elif response.status_code == 401:
                print(colored("トークンが期限切れです。トークンをリフレッシュします...", 'yellow'))
                new_id_token, new_refresh_token = refresh_id_token(refresh_token)
                if new_id_token:
                    headers = get_headers(new_id_token)
                    response = requests.get(daily_checkin_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        print(colored("デイリーチェックインに成功しました", 'green'))
                        return True
                    else:
                        print(colored(f"トークンリフレッシュ後のデイリーチェックインに失敗：ステータス {response.status_code}", 'red'))
                        return False
                else:
                    print(colored("デイリーチェックインのトークンリフレッシュに失敗。再ログインを試みます...", 'yellow'))
                    new_id_token, new_refresh_token = get_new_token(email, password)
                    if new_id_token:
                        headers = get_headers(new_id_token)
                        response = requests.get(daily_checkin_url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            print(colored("デイリーチェックインに成功しました", 'green'))
                            return True
                        else:
                            print(colored(f"再ログイン後のデイリーチェックインに失敗：ステータス {response.status_code}", 'red'))
                            return False
                    else:
                        print(colored("デイリーチェックインの再ログインに失敗", 'red'))
                        return False
            elif response.status_code == 504:
                print(colored(f"デイリーチェックインに失敗：ステータス504（試行 {attempt + 1}/3）", 'red'))
                if attempt < 2:
                    time.sleep(2)
                    continue
                print(colored("サーバーが応答しません（504）。TokenTailsのサーバー状態を確認してください。", 'red'))
                return False
            else:
                print(colored(f"デイリーチェックインに失敗：ステータス {response.status_code}", 'red'))
                return False
        except requests.exceptions.RequestException as e:
            print(colored(f"デイリーチェックインエラー：{e}", 'red'))
            if attempt < 2:
                time.sleep(2)
                continue
            print(colored("3回の試行後に失敗。接続またはサーバーの状態を確認してください。", 'red'))
            return False
    return False

# タスクのGETリクエストを送信する（リトライ付き）
def send_task_requests(id_token, refresh_token, email, password):
    headers = get_headers(id_token)
    for url in task_urls:
        task_name = url.split('/')[-1]
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    print(colored(f"タスク {task_name} を完了しました", 'green'))
                    break
                elif response.status_code == 401:
                    print(colored("トークンが期限切れです。トークンをリフレッシュします...", 'yellow'))
                    new_id_token, new_refresh_token = refresh_id_token(refresh_token)
                    if new_id_token:
                        headers = get_headers(new_id_token)
                        response = requests.get(url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            print(colored(f"タスク {task_name} を完了しました", 'green'))
                            break
                        else:
                            print(colored(f"トークンリフレッシュ後のタスク {task_name} に失敗：ステータス {response.status_code}", 'red'))
                            break
                    else:
                        print(colored(f"タスク {task_name} のトークンリフレッシュに失敗。再ログインを試みます...", 'yellow'))
                        new_id_token, new_refresh_token = get_new_token(email, password)
                        if new_id_token:
                            headers = get_headers(new_id_token)
                            response = requests.get(url, headers=headers, timeout=10)
                            if response.status_code == 200:
                                print(colored(f"タスク {task_name} を完了しました", 'green'))
                                break
                            else:
                                print(colored(f"再ログイン後のタスク {task_name} に失敗：ステータス {response.status_code}", 'red'))
                                break
                        else:
                            print(colored(f"タスク {task_name} の再ログインに失敗", 'red'))
                            break
                elif response.status_code == 504:
                    print(colored(f"タスク {task_name} に失敗：ステータス504（試行 {attempt + 1}/3）", 'red'))
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    print(colored("サーバーが応答しません（504）。TokenTailsのサーバー状態を確認してください。", 'red'))
                    break
                else:
                    print(colored(f"タスク {task_name} に失敗：ステータス {response.status_code}", 'red'))
                    break
            except requests.exceptions.RequestException as e:
                print(colored(f"タスク {task_name} エラー：{e}", 'red'))
                if attempt < 2:
                    time.sleep(2)
                    continue
                print(colored("3回の試行後に失敗。接続またはサーバーの状態を確認してください。", 'red'))
                break

# 1つのアカウントのメイン処理
def process_account(email, password):
    # トークンを取得
    id_token, refresh_token = get_new_token(email, password)
    if not id_token or not refresh_token:
        print(colored(f"アカウント {email} の処理に失敗：トークンを取得できません", 'red'))
        return

    # ユーザープロフィールを取得
    print(colored("プロフィールデータを取得中...", 'blue'))
    get_user_profile(id_token, refresh_token, email, password)

    # タスクを送信
    print(colored("\nタスクを完了中...", 'blue'))
    send_task_requests(id_token, refresh_token, email, password)

    # デイリーチェックインを送信
    print(colored("\nデイリーチェックインを実行中...", 'blue'))
    send_daily_checkin_request(id_token, refresh_token, email, password)

    # liveリクエストを継続的に送信
    print(colored("\nCatbassadorsをプレイ中...", 'blue'))
    while True:
        points = random.randint(2500, 5000)
        response_data = send_live_request(id_token, points, refresh_token, email, password)
        if response_data == "ticket_habis":
            print(colored("アカウントの処理に成功しました", 'green'))
            break
        elif response_data is None:
            print(colored("サーバーエラーのためCatbassadorsの処理に失敗。次のアカウントに進みます。", 'red'))
            break
        time.sleep(50)

# メイン関数
def main():
    print_banner()
    credentials = load_credentials()
    if not credentials:
        print(colored("data.txtに有効な認証情報がありません。終了します。", 'red'))
        return

    for i, (email, password) in enumerate(credentials, 1):
        print(colored(f"\n=== アカウント {i} ===", 'cyan'))
        process_account(email, password)

if __name__ == "__main__":
    main()
