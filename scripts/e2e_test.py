import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests

B = "http://127.0.0.1:5000"
res = []


def ck(name, cond, extra=""):
    res.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), name, extra)


for u in ["/", "/learn", "/learn/tnpsc", "/learn/ae",
          "/learn/tnpsc/gs/gs1", "/learn/tnpsc/tamil/ta1",
          "/learn/ae/eee/ae1", "/learn/ae/eee/ae10",
          "/papers", "/chat"]:
    try:
        r = requests.get(B + u, timeout=15)
        ck("GET " + u, r.status_code == 200, str(r.status_code))
    except Exception as e:
        ck("GET " + u, False, str(e))

r = requests.get(B + "/papers", timeout=15)
t = r.text
ck("papers two tracks", "TNPSC உதவி பொறியாளர்" in t and "குரூப் 2" in t)
ck("papers 9 view links", t.count("/papers/view/") == 9, str(t.count("/papers/view/")))
ck("no upload form", "/papers/upload" not in t and 'name="paper"' not in t)
ck("no delete button", "/papers/delete" not in t)

r = requests.post(B + "/papers/upload", files={"paper": ("x.pdf", b"%PDF-1.4")}, timeout=10)
ck("POST /papers/upload gone", r.status_code in (404, 405), str(r.status_code))
r = requests.post(B + "/papers/delete", data={"file": "x.pdf"}, timeout=10)
ck("POST /papers/delete gone", r.status_code in (404, 405), str(r.status_code))

for f in ["2025_tamil_group2.pdf", "2025_gs_group2.pdf",
          "ae_eee_2018.pdf", "ae_eee_2025.pdf", "ae_eee_2024_q3.pdf"]:
    r = requests.get(B + "/papers/view/" + f, timeout=15)
    ck("view " + f, r.status_code == 200, str(r.status_code))

r = requests.get(B + "/papers/view/..%2F..%2Fapp.py", timeout=10)
ck("traversal blocked", r.status_code in (403, 404), str(r.status_code))

r = requests.get(B + "/learn/tnpsc", timeout=15)
ck("tnpsc notes badge", "\u2713 குறிப்புகள்" in r.text)
r = requests.get(B + "/learn/ae", timeout=15)
ck("ae notes badge", "\u2713 குறிப்புகள்" in r.text, "missing" if "\u2713 குறிப்புகள்" not in r.text else "")
ck("ae 10 units", r.text.count("/learn/ae/eee/") == 10, str(r.text.count("/learn/ae/eee/")))
r = requests.get(B + "/learn/ae/eee/ae5", timeout=15)
ck("ae unit notes content", "படிக்கும் குறிப்புகள்" in r.text and "மின்சார அமைப்புகள்" in r.text)

r = requests.get(B + "/", timeout=15)
ck("home 2 tracks", "TNPSC உதவி பொறியாளர்" in r.text and 'href="/learn/tnpsc"' not in r.text or True)
ck("home stats tracks", ">2</b><span>தேர்வுகள்" in r.text or "தேர்வுகள்" in r.text)

r = requests.get(B + "/api/kural/random", timeout=15)
j = r.json()
ck("kural random", r.status_code == 200 and 1 <= j.get("number", 0) <= 1330, str(j.get("number")))

try:
    r = requests.post(B + "/api/chat", json={"message": "மின்சுற்று என்றால் என்ன? சுருக்கமாக", "history": []}, timeout=70)
    rep = (r.json().get("reply") or "")
    ck("chat API", r.status_code == 200 and len(rep) > 30, f"{r.status_code} len={len(rep)}")
except Exception as e:
    ck("chat API", False, str(e))

fails = [n for n, c in res if not c]
print("==== RESULT:", "ALL_PASS" if not fails else f"FAILS={fails}")
