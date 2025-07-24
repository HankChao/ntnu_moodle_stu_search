from playwright.sync_api import sync_playwright
import requests
import json

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


with sync_playwright() as p:
    #參數設置
    user_account = input("請輸入帳號: ")
    user_password = input("請輸入密碼: ")
    id = 1
    end = -1  # -1 代表無限
    error_id_count = 0
    sduid_list = []
    error_id_list = []

    browser = p.chromium.launch(headless=True)  # headless=True 不顯示瀏覽器
    page = browser.new_page()
    page.goto("https://moodle3.ntnu.edu.tw/")

    page.fill('input[name="username"]', user_account)  # 填入帳號
    page.fill('input[name="password"]', user_password)  # 填入密碼
    page.click('button[type="submit"]')   

    

    while True:
        try:
            page.goto(f"https://moodle3.ntnu.edu.tw/user/profile.php?id={id}")

            if not page.query_selector('div.card-body'):
                error_id_count += 1
                print(f"沒有找到 id 為 {id} 的使用者資料")
                id += 1
                error_id_list.append(id)
                continue

            if "無效的用戶" in page.content():
                print(f"無效的用戶 id: {id}")
                break

            if id == end:
                break

            # 取得 img 元素
            img = page.query_selector('div.profilepic img')
            img_src = img.get_attribute('src')
            img_alt = img.get_attribute('alt')

            parts = img_alt.split(" ")
            if len(parts) == 2:
                name, stu_id = parts
            else:
                name = img_alt
                stu_id = ""

            print('-' * 20)
            print(f"id: {id}, 姓名: {name}, 學號: {stu_id}")
            print(f"頭像 URL: {img_src}")

            student = {
                "id": id,
                "name": name,
                "student_id": stu_id,
                "icon": img_src
            }

            sduid_list.append(student)
            id += 1
        except Exception as e:
            print(f"第 {id} 筆發生錯誤: {e}")

    save_to_json(sduid_list, "student_data.json")
    save_to_json(error_id_list, "error_id_list.json")
    browser.close()