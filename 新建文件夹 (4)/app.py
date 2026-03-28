from fastapi import FastAPI, Query
from fastapi.responses import Response, HTMLResponse
from doc_generator import generate_student_id, generate_transcript, generate_teacher_badge

app = FastAPI(title="Document Generator API")

# 这里是我们自己写的前端页面，使用了 Tailwind CSS 保证美观
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>身份凭证生成器</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex items-center justify-center p-4">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-gray-700">
        <h2 class="text-2xl font-bold mb-6 text-blue-400 text-center">🎓 身份凭证生成器</h2>
        
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">文档类型</label>
                <select id="docType" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-blue-500 focus:border-blue-500">
                    <option value="student_id">学生证 (Student ID)</option>
                    <option value="transcript">成绩单 (Transcript)</option>
                    <option value="teacher_badge">教师证 (Teacher Badge)</option>
                </select>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">名字 (First Name)</label>
                    <input type="text" id="firstName" value="John" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-blue-500 focus:border-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">姓氏 (Last Name)</label>
                    <input type="text" id="lastName" value="Doe" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-blue-500 focus:border-blue-500">
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">学校名称 (School Name)</label>
                <input type="text" id="school" value="Massachusetts Institute of Technology" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div id="dobContainer" class="hidden">
                <label class="block text-sm font-medium text-gray-400 mb-1">出生日期 (用于成绩单)</label>
                <input type="date" id="dob" value="2003-05-15" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-blue-500 focus:border-blue-500">
            </div>
            
            <button onclick="generateDoc()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition duration-200 mt-4">
                生成图片
            </button>
        </div>

        <div class="mt-8 hidden" id="resultContainer">
            <h3 class="text-sm font-medium text-gray-400 mb-2 text-center">生成结果 (可右键保存)</h3>
            <div class="border-2 border-dashed border-gray-600 rounded-lg p-2 bg-gray-900 flex justify-center">
                <img id="resultImg" class="max-w-full h-auto rounded" src="" alt="Generated Document">
            </div>
        </div>
    </div>

    <script>
        // 监听下拉菜单，如果是成绩单则显示生日输入框
        document.getElementById('docType').addEventListener('change', function(e) {
            const dobContainer = document.getElementById('dobContainer');
            if (e.target.value === 'transcript') {
                dobContainer.classList.remove('hidden');
            } else {
                dobContainer.classList.add('hidden');
            }
        });

        function generateDoc() {
            const type = document.getElementById('docType').value;
            const first = encodeURIComponent(document.getElementById('firstName').value);
            const last = encodeURIComponent(document.getElementById('lastName').value);
            const school = encodeURIComponent(document.getElementById('school').value);
            const dob = encodeURIComponent(document.getElementById('dob').value);
            
            const btn = document.querySelector('button');
            btn.innerText = "生成中...";
            btn.classList.add('opacity-75', 'cursor-not-allowed');

            // 拼接 API URL
            const url = `/api/generate?doc_type=${type}&first=${first}&last=${last}&school=${school}&dob=${dob}`;
            
            // 直接将 img 的 src 指向接口，浏览器会自动请求并渲染图片
            const img = document.getElementById('resultImg');
            img.onload = () => {
                document.getElementById('resultContainer').classList.remove('hidden');
                btn.innerText = "生成图片";
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            };
            img.onerror = () => {
                alert("生成失败，请检查服务器终端日志。");
                btn.innerText = "生成图片";
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            };
            // 添加时间戳防止浏览器缓存
            img.src = url + "&t=" + new Date().getTime();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """返回我们编写的前端 HTML 页面"""
    return HTML_PAGE

@app.get("/api/generate")
def generate_document(
    doc_type: str = Query(..., description="文档类型"),
    first: str = Query(..., description="名字"),
    last: str = Query(..., description="姓氏"),
    school: str = Query(..., description="学校名称"),
    dob: str = Query("2000-01-01", description="出生日期")
):
    """处理前端发来的图片生成请求"""
    try:
        if doc_type == "student_id":
            img_bytes = generate_student_id(first, last, school, add_noise=True)
        elif doc_type == "transcript":
            img_bytes = generate_transcript(first, last, dob, school, add_noise=True)
        elif doc_type == "teacher_badge":
            img_bytes = generate_teacher_badge(first, last, school, add_noise=True)
        else:
            return Response(content="Invalid document type", status_code=400)
            
        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        return Response(content=str(e), status_code=500)