import io, traceback
from app import app

app.testing = True
client = app.test_client()

jd = open("jd.txt", encoding="utf-8").read()   # paste your long JD into jd.txt first

for name in ["Archit-Mahajan-Resume-final.pdf"]:
    import glob
    path = glob.glob(f"uploads/*{name}")[0]
    with open(path, "rb") as f:
        data = {"resume": (io.BytesIO(f.read()), name), "job_description": jd}
    try:
        r = client.post("/upload", data=data, content_type="multipart/form-data")
        print(name, "->", r.status_code)
    except Exception:
        traceback.print_exc()