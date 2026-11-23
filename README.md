# SANA AI + ERIX + Storm Break — Compact v4

ही मूळ `SANA_AI_ERIX_STORM_ULTIMATE_V4` प्रोजेक्टची कमी फाईल्समधील आवृत्ती आहे. Next.js frontend आणि वेगळे backend folders एकाच FastAPI app मध्ये एकत्र केले आहेत. त्यामुळे Render वर एकच Web Service deploy करायची आहे.

## ठेवलेली फीचर्स

- SANA AI Chat — Gemini API key दिल्यास खरे Gemini उत्तर; key नसल्यास local task-routing उत्तर
- ERIX Agent Catalog — मूळ 220 task templates आणि specialist routing
- RAG Knowledge — Text Ingest आणि Keyword Search
- Storm Break — Training Simulator
- Cyber Pink / Desi Grace — 3D Avatar, फिरवण्यासाठी drag support
- API: `/health`, `/api/agents`, `/api/chat`, `/api/rag/ingest`, `/api/rag/search`, `/api/storm/simulate`
- API docs: `/docs`

## महत्त्वाच्या मर्यादा

- 220 या Task Templates आहेत; 220 स्वतंत्र AI मॉडेल्स नाहीत.
- Gemini API key दिली तरच chat मध्ये Gemini LLM वापरले जाते. API key नसताना local routing demo चालतो.
- RAG सध्या in-memory आहे. Render restart/redeploy झाल्यावर त्यात टाकलेला मजकूर पुसला जाईल.
- Voice cloning या मूळ आवृत्तीतही जोडलेले नाही.
- Storm Break हा फक्त training simulator आहे. खऱ्या आपत्तीमध्ये सरकारी/अधिकृत सूचनाच पाळा.
- 3D Avatar साठी browser मध्ये internet आवश्यक आहे; Three.js सार्वजनिक CDN वरून load होते.

## Windows PC वर चालवा

ZIP extract करून त्या folder मध्ये CMD उघडा:

```bat
py -3.12 -m venv venv
venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Browser मध्ये `http://127.0.0.1:8000` उघडा.

Gemini चालू करायचा असल्यास project मधील `.env` फाईल उघडून तुमची स्वतःची key द्या:

```env
GEMINI_API_KEY=your_own_key
GEMINI_MODEL=gemini-2.5-flash
```

`.env` किंवा API key GitHub वर upload करू नका. `.gitignore` मध्ये `.env` वगळलेली आहे.

## GitHub वर Upload

1. GitHub वर नवीन रिकामी repository तयार करा.
2. ZIP extract करा.
3. Extract केलेल्या project folder मधील या 6 फाईल्स upload करा: `main.py`, `requirements.txt`, `render.yaml`, `README.md`, `.gitignore`, `.env.example`.
4. Git वापरत असल्यास project folder मधून CMD मध्ये:

```bat
git init
git add .
git commit -m "SANA AI ERIX compact v4"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

`YOUR-USERNAME` आणि `YOUR-REPOSITORY` ऐवजी तुमची GitHub माहिती वापरा.

## Render वर Deploy

1. Render Dashboard उघडा.
2. **New + → Blueprint** निवडा.
3. GitHub repository निवडा.
4. Render मधील `render.yaml` एकच Python Web Service तयार करेल.
5. Gemini वापरायचा असल्यास त्या Render service → **Environment** मध्ये `GEMINI_API_KEY` नावाची Secret variable जोडा. Value मध्ये तुमची key द्या; ती कोणालाही पाठवू नका.
6. Deploy पूर्ण झाल्यावर Render ने दिलेली URL उघडा.

Render commands आधीच `render.yaml` मध्ये आहेत:

- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

तपासणी:
- Website: तुमची Render URL
- Health: तुमची Render URL + `/health`
- API Docs: तुमची Render URL + `/docs`

Frontend आणि API एकाच URL वर असल्याने वेगळे frontend/backend Render services किंवा CORS URL सेट करण्याची गरज नाही. Render Free service idle असताना sleep होऊ शकते. Gemini वापरावर provider चे quota आणि pricing लागू होऊ शकतात.
