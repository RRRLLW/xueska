from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import Response, HTMLResponse
from doc_generator import generate_student_id, generate_transcript, generate_teacher_badge

app = FastAPI(title="Pro Document Generator API")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>身份凭证生成器 Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex items-center justify-center p-4">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-2xl border border-gray-700">
        <h2 class="text-3xl font-bold mb-6 text-blue-400 text-center">🎓 凭证生成器 Pro</h2>
        
        <form id="genForm" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">文档类型</label>
                    <select id="docType" name="docType" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                        <option value="student_id">学生证 (Student ID)</option>
                        <option value="teacher_badge">教师证 (Teacher Badge)</option>
                        <option value="transcript">成绩单 (Transcript)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">主题颜色</label>
                    <select id="theme" name="theme" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                        <option value="blue">科技蓝 (Blue)</option>
                        <option value="maroon">常春藤红 (Maroon)</option>
                        <option value="green">教育绿 (Green)</option>
                        <option value="navy">海军深蓝 (Navy)</option>
                        <option value="purple">典雅紫 (Purple)</option>
                    </select>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">名字 (First Name)</label>
                    <input type="text" name="first" value="John" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">姓氏 (Last Name)</label>
                    <input type="text" name="last" value="Doe" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">学校名称 (School)</label>
                    <input type="text" name="school" value="Massachusetts Institute of Technology" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">专业/部门 (Major/Dept)</label>
                    <input type="text" name="major" value="Computer Science" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                </div>
            </div>

            <div id="extraFields" class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">证件照片 (可选)</label>
                    <input type="file" name="photo" accept="image/*" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-white">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-1">出生日期 (成绩单专用)</label>
                    <input type="date" name="dob" value="2003-05-15" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white">
                </div>
            </div>

            <div class="flex items-center space-x-3 mt-4 bg-gray-700 p-3 rounded-lg border border-gray-600">
                <input type="checkbox" id="exportPdf" name="exportPdf" value="true" class="w-5 h-5 text-blue-600 bg-gray-800 border-gray-500 rounded focus:ring-blue-500 focus:ring-2">
                <label for="exportPdf" class="text-sm font-medium text-gray-300">导出为 PDF 文件 (默认输出 PNG 图片)</label>
            </div>
            
            <button type="button" onclick="generateDoc()" id="submitBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition duration-200 mt-6 shadow-lg">
                🚀 生成凭证
            </button>
        </form>

        <div class="mt-8 hidden" id="resultContainer">
            <h3 class="text-sm font-medium text-green-400 mb-2 text-center" id="resultMsg">✅ 生成成功！(可右键保存或直接下载)</h3>
            <div class="border-2 border-dashed border-gray-600 rounded-lg p-2 bg-gray-900 flex justify-center flex-col items-center">
                <img id="resultImg" class="max-w-full h-auto rounded hidden" src="" alt="Generated Document">
                <a id="downloadPdfBtn" class="hidden mt-4 bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg transition duration-200" href="" download="Document.pdf">📄 下载 PDF 文件</a>
            </div>
        </div>
    </div>

    <script>
        async function generateDoc() {
            const formElement = document.getElementById('genForm');
            const formData = new FormData(formElement);
            const btn = document.getElementById('submitBtn');
            const isPdf = document.getElementById('exportPdf').checked;
            
            btn.innerText = "生成中...请稍候";
            btn.classList.add('opacity-75', 'cursor-not-allowed');
            document.getElementById('resultContainer').classList.add('hidden');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("生成失败");

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                document.getElementById('resultContainer').classList.remove('hidden');

                if (isPdf) {
                    document.getElementById('resultImg').classList.add('hidden');
                    const pdfBtn = document.getElementById('downloadPdfBtn');
                    pdfBtn.classList.remove('hidden');
                    pdfBtn.href = url;
                } else {
                    document.getElementById('downloadPdfBtn').classList.add('hidden');
                    const img = document.getElementById('resultImg');
                    img.classList.remove('hidden');
                    img.src = url;
                }
            } catch (error) {
                alert(error.message);
            } finally {
                btn.innerText = "🚀 生成凭证";
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return HTML_PAGE

@app.post("/api/generate")
async def generate_document(
    docType: str = Form(...),
    first: str = Form(...),
    last: str = Form(...),
    school: str = Form(...),
    major: str = Form("Computer Science"),
    theme: str = Form("blue"),
    dob: str = Form("2000-01-01"),
    exportPdf: bool = Form(False),
    photo: UploadFile = File(None)
):
    try:
        photo_bytes = await photo.read() if photo and photo.filename else None
        
        if docType == "student_id":
            file_bytes = generate_student_id(first, last, school, major, theme, photo_bytes, exportPdf)
        elif docType == "teacher_badge":
            file_bytes = generate_teacher_badge(first, last, school, major, theme, photo_bytes, exportPdf)
        elif docType == "transcript":
            file_bytes = generate_transcript(first, last, dob, school, major, theme, exportPdf)
        else:
            return Response(content="Invalid Type", status_code=400)
            
        media_type = "application/pdf" if exportPdf else "image/png"
        return Response(content=file_bytes, media_type=media_type)
        
    except Exception as e:
        return Response(content=f"Server Error: {str(e)}", status_code=500)
