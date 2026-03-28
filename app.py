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
    <title>身份凭证生成器 Pro Max</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1f2937; }
        ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }
        
        /* 针对不同比例证件的预览框自适应 */
        .preview-container {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #111827;
            background-image: linear-gradient(45deg, #1f2937 25%, transparent 25%, transparent 75%, #1f2937 75%, #1f2937),
                              linear-gradient(45deg, #1f2937 25%, transparent 25%, transparent 75%, #1f2937 75%, #1f2937);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen p-4 md:p-8 font-sans">
    
    <div class="max-w-7xl mx-auto">
        <div class="mb-8 text-center relative">
            <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 inline-block">
                🎓 身份凭证生成器 Pro Max
            </h1>
            <p class="text-gray-400 mt-2 text-sm">内置北美高校库 & AI 随机真实身份注入</p>
        </div>

        <div class="flex flex-col lg:flex-row gap-8">
            
            <div class="lg:w-5/12 bg-gray-800 p-6 rounded-2xl shadow-2xl border border-gray-700 h-fit">
                <div class="flex justify-between items-center mb-6">
                    <div class="flex items-center">
                        <span class="text-xl">🛠️</span>
                        <h2 class="text-xl font-bold ml-2 text-gray-100">参数配置</h2>
                    </div>
                    <button type="button" onclick="randomizeIdentity()" id="randomizeBtn" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-1.5 px-3 rounded shadow-lg transition-all flex items-center gap-1">
                        <span>🎲</span> 一键生成真实身份
                    </button>
                </div>
                
                <form id="genForm" class="space-y-5">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">文档类型</label>
                            <select id="docType" name="docType" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all">
                                <option value="student_id">竖版学生证 (Student ID)</option>
                                <option value="transcript">官方成绩单 (Transcript)</option>
                                <option value="teacher_badge">教师证 (Teacher Badge)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">主题颜色</label>
                            <select id="theme" name="theme" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all">
                                <option value="blue">科技蓝 (Blue)</option>
                                <option value="maroon">常春藤红 (Maroon)</option>
                                <option value="navy">海军深蓝 (Navy)</option>
                                <option value="green">教育绿 (Green)</option>
                                <option value="purple">典雅紫 (Purple)</option>
                            </select>
                        </div>
                    </div>

                    <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-700/50 space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">名字 (First Name)</label>
                                <input type="text" id="firstName" name="first" value="John" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">姓氏 (Last Name)</label>
                                <input type="text" id="lastName" name="last" value="Doe" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">证件照片 (点骰子可自动获取真实头像)</label>
                            <input type="file" id="photoInput" name="photo" accept="image/*" class="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer">
                        </div>
                    </div>

                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">学校名称 (选择或手动输入)</label>
                            <input list="school-list" name="school" id="school" value="Massachusetts Institute of Technology" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            <datalist id="school-list">
                                <option value="Massachusetts Institute of Technology">
                                <option value="Harvard University">
                                <option value="Stanford University">
                                <option value="University of California, Los Angeles">
                                <option value="New York University (NYU)">
                                <option value="University of Southern California">
                                <option value="Columbia University">
                                <option value="Cornell University">
                                <option value="University of Washington">
                                <option value="University of Michigan">
                                <option value="Yale University">
                                <option value="Princeton University">
                            </datalist>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">专业/部门 (Major)</label>
                                <input type="text" name="major" value="Computer Science" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">自定义编号 (留空随机)</label>
                                <input type="text" name="customId" placeholder="如: 20230912" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">有效期/签发日 (留空默认)</label>
                                <input type="text" name="validDate" placeholder="如: EXP: 08/2028" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">出生日期 (成绩单专用)</label>
                                <input type="date" id="dobInput" name="dob" value="2003-05-15" class="w-full bg-gray-700 border border-gray-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center space-x-3 bg-gray-900/50 p-3 rounded-lg border border-gray-700/50">
                        <input type="checkbox" id="exportPdf" name="exportPdf" value="true" class="w-5 h-5 text-purple-600 bg-gray-800 border-gray-500 rounded focus:ring-purple-500 focus:ring-2 cursor-pointer">
                        <label for="exportPdf" class="text-sm font-medium text-gray-300 cursor-pointer">直接导出为 PDF 文档扫描件</label>
                    </div>
                    
                    <button type="button" onclick="generateDoc()" id="submitBtn" class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white font-bold py-3.5 rounded-xl transition-all duration-300 shadow-lg transform hover:-translate-y-0.5">
                        🚀 立即生成真实凭证
                    </button>
                </form>
            </div>

            <div class="lg:w-7/12 bg-gray-800 p-6 rounded-2xl shadow-2xl border border-gray-700 flex flex-col">
                <div class="flex justify-between items-center mb-4">
                    <div class="flex items-center">
                        <span class="text-xl">👁️</span>
                        <h2 class="text-xl font-bold ml-2 text-gray-100">生成结果预览</h2>
                    </div>
                    <div id="actionButtons" class="hidden space-x-2">
                        <a id="downloadBtn" class="bg-gray-700 hover:bg-gray-600 text-white text-sm font-semibold py-1.5 px-4 rounded-lg transition duration-200" href="" download>
                            💾 保存到本地
                        </a>
                    </div>
                </div>

                <div class="flex-grow border-2 border-dashed border-gray-600 rounded-xl preview-container relative overflow-hidden h-[600px] lg:h-[750px] p-4">
                    <div id="placeholderText" class="text-center text-gray-500">
                        <svg class="mx-auto h-12 w-12 text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p>调整左侧参数，点击“生成”即可在此无损预览</p>
                    </div>
                    
                    <img id="resultImg" class="w-full h-full object-contain rounded shadow-2xl hidden" src="" alt="Document Preview">
                    
                    <div id="pdfReadyText" class="hidden text-center z-10 bg-gray-900/80 p-6 rounded-xl border border-gray-700">
                        <svg class="mx-auto h-16 w-16 text-red-500 mb-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                        </svg>
                        <p class="text-xl font-bold text-white mb-2">PDF 文档已生成就绪</p>
                        <p class="text-gray-400 text-sm">此格式不支持网页直连预览<br>请点击右上角按钮下载原文件</p>
                    </div>
                </div>
            </div>
            
        </div>
    </div>

    <script>
        // 一键生成真实欧美身份与照片的魔法逻辑
        async function randomizeIdentity() {
            const btn = document.getElementById('randomizeBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '⏳ 正在抓取真实数据...';
            btn.classList.add('opacity-75', 'cursor-not-allowed', 'animate-pulse');

            try {
                // 请求随机生成 API (限定欧美地区以符合常春藤预设)
                const res = await fetch('https://randomuser.me/api/?nat=us,gb,ca,au');
                const data = await res.json();
                const user = data.results[0];
                
                // 填入姓名和生日
                document.getElementById('firstName').value = user.name.first;
                document.getElementById('lastName').value = user.name.last;
                const dob = user.dob.date.split('T')[0];
                document.getElementById('dobInput').value = dob;
                
                // 抓取并转换 AI 人脸照片为 File 对象填入表单
                const imgRes = await fetch(user.picture.large);
                const imgBlob = await imgRes.blob();
                const file = new File([imgBlob], "ai_face.jpg", { type: "image/jpeg" });
                
                // 使用 DataTransfer 将文件对象挂载到 input[type="file"] 上
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                document.getElementById('photoInput').files = dataTransfer.files;

                // 稍微给点提示
                btn.innerHTML = '✅ 身份注入成功！';
                setTimeout(() => { btn.innerHTML = originalText; }, 2000);

            } catch (err) {
                alert('自动获取身份失败，请检查网络连接或稍后重试。');
                btn.innerHTML = originalText;
            } finally {
                btn.classList.remove('opacity-75', 'cursor-not-allowed', 'animate-pulse');
            }
        }

        // 提交表单生成文档逻辑
        async function generateDoc() {
            const formElement = document.getElementById('genForm');
            const formData = new FormData(formElement);
            const btn = document.getElementById('submitBtn');
            const isPdf = document.getElementById('exportPdf').checked;
            
            btn.innerHTML = `
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg> 渲染高精度凭证中...
            `;
            btn.classList.add('opacity-75', 'cursor-not-allowed');
            document.getElementById('placeholderText').classList.add('hidden');
            document.getElementById('resultImg').classList.add('hidden');
            document.getElementById('pdfReadyText').classList.add('hidden');
            document.getElementById('actionButtons').classList.add('hidden');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("生成失败，请检查服务器日志");

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                document.getElementById('actionButtons').classList.remove('hidden');
                const downloadBtn = document.getElementById('downloadBtn');
                downloadBtn.href = url;

                if (isPdf) {
                    document.getElementById('pdfReadyText').classList.remove('hidden');
                    downloadBtn.download = "SheerID_Official_Document.pdf";
                    downloadBtn.innerText = "📄 下载完整 PDF";
                } else {
                    const img = document.getElementById('resultImg');
                    img.classList.remove('hidden');
                    img.src = url;
                    downloadBtn.download = "SheerID_Verification_ID.png";
                    downloadBtn.innerText = "🖼️ 下载高清大图";
                }
            } catch (error) {
                alert(error.message);
                document.getElementById('placeholderText').classList.remove('hidden');
            } finally {
                btn.innerHTML = "🚀 立即生成真实凭证";
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
    customId: str = Form(""),
    validDate: str = Form(""),
    dob: str = Form("2000-01-01"),
    exportPdf: bool = Form(False),
    photo: UploadFile = File(None)
):
    try:
        photo_bytes = await photo.read() if photo and photo.filename else None
        
        if docType == "student_id":
            file_bytes = generate_student_id(first, last, school, major, theme, photo_bytes, exportPdf, customId, validDate)
        elif docType == "teacher_badge":
            file_bytes = generate_teacher_badge(first, last, school, major, theme, photo_bytes, exportPdf, customId, validDate)
        elif docType == "transcript":
            file_bytes = generate_transcript(first, last, dob, school, major, theme, exportPdf, customId, validDate)
        else:
            return Response(content="Invalid Type", status_code=400)
            
        media_type = "application/pdf" if exportPdf else "image/png"
        return Response(content=file_bytes, media_type=media_type)
        
    except Exception as e:
        return Response(content=f"Server Error: {str(e)}", status_code=500)
