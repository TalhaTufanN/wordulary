import io, os, shutil
os.environ["WORDULARY_REQUIRE_USER_KEY"]=""
from fastapi.testclient import TestClient
import importlib, app as appmod
importlib.reload(appmod)
c=TestClient(appmod.app)

print("=== BOZUK DOSYA (artık 400, net mesaj) ===")
for fn in ["bozuk.pdf","bozuk.docx"]:
    r=c.post("/api/process", data={"question_count":"10"},
             files={"file":(fn, io.BytesIO(b"bu gecerli bir dosya degil"),"application/octet-stream")})
    print(f"  {fn}: {r.status_code} -> {r.json().get('detail','')[:55]}")

print("\n=== GERÇEK PDF: Oxford (küçük alt-küme, çeviri süresini sınırla) ===")
# Oxford'dan sadece ilk sayfayi al -> kucuk PDF
from pypdf import PdfReader, PdfWriter
r=PdfReader("sources/The_Oxford_5000_by_CEFR_level.pdf")
w=PdfWriter(); w.add_page(r.pages[0])
with open("_ox1.pdf","wb") as f: w.write(f)

with open("_ox1.pdf","rb") as f: data=f.read()
resp=c.post("/api/process", data={"question_count":"15"},
            files={"file":("oxford.pdf", io.BytesIO(data),"application/pdf")})
print(f"  HTTP {resp.status_code}")
if resp.status_code==200:
    from pypdf import PdfReader as PR
    j=resp.json()
    for key,typ,ad in [("word_list_url","words","kelime listesi"),("quiz_url","quizzes","quiz")]:
        fn=j[key].split("/")[-1].split("?")[0]
        d=c.get(f"/api/download/{fn}", params={"type":typ})
        open("_o.pdf","wb").write(d.content)
        rr=PR("_o.pdf")
        t=rr.pages[0].extract_text()
        print(f"  {ad}: {len(rr.pages)} sayfa, ilk satırlar:")
        for l in [x for x in t.split(chr(10)) if x.strip()][:4]: print(f"      {l}")
    os.remove("_o.pdf")
else:
    print("  ", resp.json())
os.remove("_ox1.pdf")
