from flask import Flask, render_template, request, jsonify
import json
import os


app = Flask(__name__)

# ====== 全域快取 ======
STUDENT_DATA = []
COLLEGE_DICT = {}
DEPT_DICT = {}

def cache_all_data():
    global STUDENT_DATA, COLLEGE_DICT, DEPT_DICT
    COLLEGE_DICT = load_college_data()
    DEPT_DICT = load_department_data()
    STUDENT_DATA = load_student_data()
    # 疑似資料標記
    for student in STUDENT_DATA:
        # 只要 error 欄位不是 None/null 就標疑似
        if student.get('error') is not None:
            student['is_suspicious'] = True
            student['suspicious_reasons'] = [student.get('error', '資料格式異常')]
        else:
            student['is_suspicious'] = False
            student['suspicious_reasons'] = []



def load_college_data():
    """載入學院代碼對照表"""
    try:
        with open('../college_data/college_code.json', 'r', encoding='utf-8') as f:
            college_list = json.load(f)
        return {c["code"]: c["name"] for c in college_list}
    except FileNotFoundError:
        return {}

def load_department_data():
    """載入系所代碼對照表"""
    try:
        with open('../college_data/department_code.json', 'r', encoding='utf-8') as f:
            dept_list = json.load(f)
        return {d["code"]: d["name"] for d in dept_list}
    except FileNotFoundError:
        return {}

def is_suspicious_data(student):
    """檢測疑似有問題的資料"""
    student_id = student.get('student_id', '')
    suspicious_reasons = []
    if student_id == '':
        suspicious_reasons.append('學號為空')
    return len(suspicious_reasons) > 0, suspicious_reasons

def load_student_data():
    """載入學生資料"""
    try:
        # 載入學生資料
        with open('../stu_data/student_info.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 檢查第一筆有效資料（跳過錯誤資料）
        first_valid_student = None
        for student in data:
            if 'error' not in student or student.get('error') is None:
                first_valid_student = student
                break
        
        # 如果找到有效學生且沒有education欄位，表示是原始資料
        if first_valid_student and 'education' not in first_valid_student:
            print("檢測到未處理的原始資料，正在進行學號分析...")
            return process_raw_student_data(data)
        
        print("載入已處理的學生資料")
        return data
    except FileNotFoundError:
        return []

def process_raw_student_data(raw_students):
    """處理原始學生資料，加入學號分析"""
    college_dict = load_college_data()
    dept_dict = load_department_data()
    processed_students = []
    
    for student in raw_students:
        # 如果已有錯誤標記，直接加入
        if 'error' in student:
            processed_students.append(student)
            continue
            
        student_id = student.get('student_id', '')
        
        # 檢查是否為有效學號格式
        if student_id and len(student_id) == 9 and student_id[:8].isdigit() and student_id[-1].isalpha():
            # 學制分析
            if student_id[0] == '4':
                education = "大學部"
            elif student_id[0] == '6':
                education = "碩士"
            elif student_id[0] == '8':
                education = "博士"
            else:
                education = "未知"
            
            # 入學年度
            admission_year = "1" + student_id[1:3]
            
            # 科系
            department_code = student_id[3:5]
            department_name = department_code + '/' + dept_dict.get(department_code, "未知科系")
            
            # 班級
            class_code = student_id[5]
            if class_code == '0':
                class_code = "0/不分班"
            
            # 座號
            seat_number = student_id[6:8]
            
            # 學院
            college_code = student_id[8].upper()
            college_name = college_code + '/' + college_dict.get(college_code, "未知學院")
            
            processed_student = {
                "id": student.get('id'),
                "avatar_url": student.get('avatar_url'),
                "name": student.get('name'),
                "student_id": student_id,
                "education": education,
                "admission_year": admission_year,
                "department_name": department_name,
                "class_code": class_code,
                "seat_number": seat_number,
                "college_name": college_name
            }
        else:
            # 非師大學號格式
            processed_student = {
                "id": student.get('id'),
                "avatar_url": student.get('avatar_url'),
                "name": student.get('name'),
                "student_id": student_id,
                "error": "非師大學號"
            }
        
        processed_students.append(processed_student)
    
    return processed_students

def get_filter_options(students):
    """取得篩選選項（學院/科系直接來自json，其他仍從學生資料）"""
    college_dict = load_college_data()
    dept_dict = load_department_data()

    # 學院、科系直接用json所有內容，排除 "未知系所"
    colleges = [name for code, name in college_dict.items()]
    departments = [name for code, name in dept_dict.items() if name != "未知系所"]

    # 其他選項仍從學生資料
    educations = set()
    for student in students:
        if 'error' not in student:
            if student.get('education'):
                educations.add(student['education'])

    # 固定選項補齊與排序：大學部、碩班、博班，其餘依字母順序
    fixed_order = ["大學部", "碩班", "博班"]
    all_educations = set(fixed_order) | educations
    # 依指定順序排序
    def edu_sort_key(e):
        try:
            return (fixed_order.index(e), '')
        except ValueError:
            return (len(fixed_order), e)
    sorted_educations = sorted(all_educations, key=edu_sort_key)

    return {
        'departments': sorted(departments),
        'colleges': sorted(colleges),
        'educations': sorted_educations,
        'admission_year_placeholder': '例如：113、112、111（民國年）'
    }

@app.route('/')
def index():
    """首頁（只渲染空列表，資料由 JS 拉取）"""
    students = []  # 首頁不直接渲染學生資料
    filter_options = get_filter_options(STUDENT_DATA)
    return render_template('index.html', 
                         students=students,
                         filter_options=filter_options,
                         total_count=len(STUDENT_DATA))



# ====== 分頁 API ======
def filter_students(data, search_term='', admission_year='', department='', college='', education=''):
    filtered = []
    for student in data:
        # 不要過濾 error
        if admission_year and student.get('admission_year') != admission_year:
            continue
        if department:
            student_dept = student.get('department_name', '')
            dept_name = student_dept.split('/')[1] if '/' in student_dept else student_dept
            if dept_name != department:
                continue
        if college:
            student_college = student.get('college_name', '')
            college_name = student_college.split('/')[1] if '/' in student_college else student_college
            if college_name != college:
                continue
        if education:
            stu_edu = student.get('education', '')
            if stu_edu != education:
                continue
        if search_term:
            name_match = search_term in str(student.get('name', ''))
            student_id_match = search_term in str(student.get('student_id', ''))
            if not (name_match or student_id_match):
                continue
        filtered.append(student)
    return filtered

@app.route('/api/students')
def api_students():
    """分頁 API，回傳學生資料 (json)"""
    # 參數
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 50))
    search_term = request.args.get('search_term', '').strip()
    admission_year = request.args.get('admission_year', '')
    department = request.args.get('department', '')
    college = request.args.get('college', '')
    education = request.args.get('education', '')

    filtered = filter_students(
        STUDENT_DATA,
        search_term=search_term,
        admission_year=admission_year,
        department=department,
        college=college,
        education=education
    )
    # 排序
    def stu_sort_key(stu):
        sid = stu.get('student_id')
        return (0, sid) if sid else (1, '')
    filtered_sorted = sorted(filtered, key=stu_sort_key)
    # 分頁
    start = (page - 1) * size
    end = start + size
    page_data = filtered_sorted[start:end]
    return jsonify({
        'students': page_data,
        'total_count': len(filtered_sorted)
    })

# 保留原本搜尋頁（可選，或改成回傳 404）
@app.route('/search', methods=['POST'])
def search():
    return '請使用首頁搜尋功能', 404

if __name__ == '__main__':
    print('快取所有資料...')
    cache_all_data()
    app.run(debug=True, host='0.0.0.0', port=5001)
