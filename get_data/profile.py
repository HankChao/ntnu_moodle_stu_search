import json 

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


with open("../stu_data/student_ori_data.json", "r", encoding="utf-8") as f:
    student_data = json.load(f)



with open("../college_data/department_code.json", "r", encoding="utf-8") as f:
    dept_list = json.load(f)
dept_dict = {d["code"]: d["name"] for d in dept_list}

with open("../college_data/college_code.json", "r", encoding="utf-8") as f:
    college_list = json.load(f)
college_dict = {c["code"]: c["name"] for c in college_list}


# 顯示載入的資料
print(f"總共載入 {len(student_data)} 筆學生資料")
print("-" * 50)

stu_final = []

# 遍歷並顯示每個學生的資料
for i, student in enumerate(student_data, 1):
    print(f"第 {i} 筆:")

    #學號分析
    student_id = student.get('student_id')

    #確實是學號
    if student_id and len(student_id) == 9 and student_id[:8].isdigit() and student_id[-1].isalpha():
        
        #學制
        if student_id[0] == '4':
            education = "大學部"
        elif student_id[0] == '6':
            education = "碩班"
        elif student_id[0] == '8':
            education = "博班"
        else:
            education = "未知"

        #入學年
        admission_year = "1" + student_id[1:3]
        
        #科系
        department_code = student_id[3:5]
        department_name = department_code + '/' + dept_dict.get(department_code, "未知科系")

        #班級
        class_code = student_id[5]
        if class_code == '0':
            class_code = "0" + "/" + "不分班"

        #座號
        seat_number = student_id[6:8]

        #學院(英文)
        college_code = student_id[8].upper()
        college_name = college_code + '/' + college_dict.get(college_code, "未知學院")

        student_info = {
            "id": student.get('id'),
            "avatar_url": student.get('avatar_url'),
            "name": student.get('name'),
            "student_id": student_id,
            "education": education,
            "admission_year": admission_year,
            "department_name": department_name,
            "class_code": class_code,
            "seat_number": seat_number,
            "college_name": college_name,
            "error": None
        }
        stu_final.append(student_info)

    elif not student_id:
        student_info = {
            "id": student.get('id'),
            "avatar_url": student.get('avatar_url'),
            "name": student.get('name'),
            "error": "帳戶名稱格式錯誤"
        }
        stu_final.append(student_info)

    else:
        student_info = {
            "id": student.get('id'),
            "avatar_url": student.get('avatar_url'),
            "name": student.get('name'),
            "student_id": student_id,
            "error": "帳號非師大學號"
        }
        stu_final.append(student_info)

    print("-" * 30)

save_to_json(stu_final, "../stu_data/student_info.json")
print(f"完成！共處理 {len(stu_final)} 筆學生資料")
print("結果已儲存到 student_info.json")

