import requests
import bs4 as BeautifulSoup
import json     

# 方法1：使用字典格式的 cookies

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

cookie_string = input("請輸入 cookies : ")

cookies = {
    'MoodleSession': cookie_string,
}

# 載入現有的資料
stu_id_list = load_from_json("../stu_data/student_ori_data.json")
error_id_list = load_from_json("../stu_data/error_id_list.json")

print(f"載入 {len(stu_id_list)} 筆學生資料")
print(f"載入 {len(error_id_list)} 筆錯誤 ID")
print("-" * 50)

# 處理 error_id_list 中的 ID
successful_ids = []  # 記錄成功處理的 ID

for id in error_id_list.copy():  # 使用 copy() 避免修改過程中出現問題
    try:
        print(f"重新請求 ID: {id}")
        res = requests.get(f'https://moodle3.ntnu.edu.tw/user/profile.php?id={id}', cookies=cookies)
        soup = BeautifulSoup.BeautifulSoup(res.text, 'html.parser')

        # 找到 div class="profilepic"
        profilepic_div = soup.find('div', class_='profilepic')
        if not profilepic_div:
            print(f"ID {id}: 仍然找不到 profilepic div")
            continue

        # 找到其中的 img 元素
        img = profilepic_div.find('img')
        if not img:
            print(f"ID {id}: 找不到 img 元素")
            continue

        img_src = img.get('src')
        img_alt = img.get('alt')
        
        # 解析 alt 屬性中的姓名和學號
        if img_alt:
            parts = img_alt.split(' ')
            if len(parts) == 2:
                name, student_id = parts
            else:
                name = img_alt
                student_id = ""
        else:
            name = ""
            student_id = ""
        
        print('-' * 20)
        print(f"✅ 成功！id: {id}")
        print(f"姓名: {name}")
        print(f"學號: {student_id}")
        print(f"頭像 URL: {img_src}")

        student = {
            'id': id,
            'name': name,
            'student_id': student_id,
            'avatar_url': img_src
        }
        
        # 附加到 student_data 最後面
        stu_id_list.append(student)
        successful_ids.append(id)
        
    except Exception as e:
        print(f"ID {id} 發生錯誤: {e}")
        continue

# 從 error_id_list 中移除成功處理的 ID
for success_id in successful_ids:
    if success_id in error_id_list:
        error_id_list.remove(success_id)

print("-" * 50)

# 儲存結果到 JSON 檔案
save_to_json(stu_id_list, "../stu_data/student_ori_data.json")
save_to_json(error_id_list, "../stu_data/error_id_list.json")
print(f"完成！")
print(f"成功處理 {len(successful_ids)} 筆錯誤 ID")
print(f"總共 {len(stu_id_list)} 筆學生資料")
print(f"剩餘 {len(error_id_list)} 筆錯誤 ID")



