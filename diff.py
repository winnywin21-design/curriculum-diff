# -*- coding: utf-8 -*-
"""사용법: python3 diff.py <이전JSON> <이후JSON> [항목크로스워크JSON] [출력JSON]
canonical_area·role_group 기준으로 두 문서를 대조해 유지/통합/명칭변경/재구성/매핑/신설/삭제를 산출한다."""
import json, sys
from collections import defaultdict

def areas(doc): return [a for lvl in doc["document"]["school_levels"] for a in lvl["areas"]]
def norm(s): return s.replace(" ","").replace("그그래프","그래프")
def collect(al,role): return [it for a in al for b in a["content"] if b["role"]==role for it in b["items"]]
def relation(a15,a22):
    if [a["name"] for a in a15]==[a["name"] for a in a22]: return "유지"
    if len(a15)>1: return "통합"
    if len(a22)>1: return "분리"
    return "명칭변경"

def run(prev, cur, xw=None):
    G=defaultdict(lambda:{"p":[],"c":[]})
    for a in areas(prev): G[a["canonical_area"]]["p"].append(a)
    for a in areas(cur):  G[a["canonical_area"]]["c"].append(a)
    out={"pair":f'{prev["document"]["id"]} ↔ {cur["document"]["id"]}',
         "crosswalk_applied":bool(xw),"areas":[]}
    for canon,g in G.items():
        ap,ac=g["p"],g["c"]
        kp,kc=collect(ap,"KNOWLEDGE"),collect(ac,"KNOWLEDGE")
        np={norm(x):x for x in kp}; nc={norm(x):x for x in kc}
        kept=[nc[k] for k in nc if k in np]
        rem=[np[k] for k in np if k not in nc]; add=[nc[k] for k in nc if k not in np]
        reorg=[]
        for r in list(rem):
            pcs=[x for x in list(add) if norm(x) in norm(r)]
            if len(pcs)>=2:
                reorg.append({"from":[r],"to":pcs}); rem.remove(r)
                for p in pcs: add.remove(p)
        mapped=[]
        for m in (xw or {}).get(canon,[]):
            if all(x in rem for x in m["from"]) and all(y in add for y in m["to"]):
                mapped.append(m)
                for x in m["from"]: rem.remove(x)
                for y in m["to"]: add.remove(y)
        out["areas"].append({"canonical_area":canon,
            "label":[a["name"] for a in ac][0] if ac else None,
            "areas_prev":[a["name"] for a in ap],"relation":relation(ap,ac),
            "knowledge":{"kept":kept,"reorganized":reorg,"mapped":mapped,"added":add,"removed":rem},
            "value_new":collect(ac,"VALUE"),"review_needed":bool(rem or add)})
    return out

if __name__=="__main__":
    if len(sys.argv)<3: print(__doc__); sys.exit(2)
    prev=json.load(open(sys.argv[1],encoding="utf-8")); cur=json.load(open(sys.argv[2],encoding="utf-8"))
    xw=json.load(open(sys.argv[3],encoding="utf-8")) if len(sys.argv)>3 and sys.argv[3].endswith(".json") else None
    outp=sys.argv[4] if len(sys.argv)>4 else "diff.out.json"
    res=run(prev,cur,xw); json.dump(res,open(outp,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    clean=sum(1 for a in res["areas"] if not a["review_needed"])
    print(f"비교: {res['pair']}  (크로스워크 {'적용' if xw else '미적용'})")
    print(f"정합: {clean}/{len(res['areas'])} 영역 · 검토 필요 {len(res['areas'])-clean}")
    for a in res["areas"]:
        k=a["knowledge"]
        print(f"  ▶ {a['label']} [{a['relation']}] ← {' + '.join(a['areas_prev'])}  "
              f"유지{len(k['kept'])}/재구성{len(k['reorganized'])}/매핑{len(k['mapped'])}/신설{len(k['added'])}/삭제{len(k['removed'])}"
              +("  ⚠검토" if a['review_needed'] else ""))
    print(f"→ {outp}")
