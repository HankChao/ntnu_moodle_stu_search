import requests
import bs4 as BeautifulSoup
import json     

# 方法1：使用字典格式的 cookies

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

cookie_string = input("請輸入 cookies : ")

cookies = {
    'MoodleSession': cookie_string,
}

id = 21327
end = 21327
stu_id_list = []
error_id_list = []

while True:
    try:
        if id > end:
            break

        res = requests.get(f'https://moodle3.ntnu.edu.tw/user/profile.php?id={id}', cookies=cookies)
        soup = BeautifulSoup.BeautifulSoup(res.text, 'html.parser')

        # 找到 div class="profilepic"

        profilepic_div = soup.find('div', class_='profilepic')
        if not profilepic_div:
            print(f"ID {id}: 找不到 profilepic div")
            id += 1
            error_id_list.append(id)
            continue

        # 找到其中的 img 元素
        img = profilepic_div.find('img')

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
        
        print('-' * 20)
        print(f"id: {id}")
        print(f"姓名: {name}")
        print(f"學號: {student_id}")
        print(f"頭像 URL: {img_src}")

        student = {
            'id': id,
            'name': name,
            'student_id': student_id,
            'avatar_url': img_src
        }
        stu_id_list.append(student)
    
    except Exception as e:
        print(f"發生錯誤: {e}")
        print(f"ID {id} 出現異常問題")
        error_id_list.append(id)
    
    id += 1

# 儲存結果到 JSON 檔案
save_to_json(stu_id_list, "../stu_data/student_ori_data.json")
save_to_json(error_id_list, "../stu_data/error_id_list.json")
print(f"完成！共找到 {len(stu_id_list)} 筆學生資料，{len(error_id_list)} 筆錯誤")



