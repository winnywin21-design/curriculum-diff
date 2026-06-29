# -*- coding: utf-8 -*-
"""사용법: python3 validate.py <추출JSON>
스키마 v1의 검증 규칙으로 추출 결과를 점검한다."""
import json, sys
ROLE_OK={"BIG_IDEA","CORE_CONCEPT","GENERALIZED_KNOWLEDGE","KNOWLEDGE","PROCESS","VALUE"}
RG_OK={"FRAMING","KNOWLEDGE","PROCESS","VALUE"}
CANON_OK={"NUMBER_OPERATION","CHANGE_RELATION","GEOMETRY_MEASURE","DATA_POSSIBILITY",None}

def validate(doc):
    e=[]; d=doc["document"]; ft=d["framework_type"]
    for lvl in d["school_levels"]:
        bands=set(lvl["grade_bands"])
        for a in lvl["areas"]:
            roles=[x["role"] for x in a["framing"]]+[x["role"] for x in a["content"]]
            if ft=="FIVE_ELEMENT" and ({"VALUE","BIG_IDEA"}&set(roles)):
                e.append(f"{a['name']}: FIVE_ELEMENT인데 VALUE/BIG_IDEA 존재")
            if ft=="BIG_IDEA_THREE_CATEGORY" and ({"CORE_CONCEPT","GENERALIZED_KNOWLEDGE"}&set(roles)):
                e.append(f"{a['name']}: 3범주 체계인데 CORE_CONCEPT/일반화된지식 존재")
            if a["canonical_area"] not in CANON_OK:
                e.append(f"{a['name']}: canonical_area 통제어휘 위반")
            for b in a["content"]:
                if b["grade_band"] not in bands: e.append(f"{a['name']}: grade_band '{b['grade_band']}' 미정의")
                if b["role"] not in ROLE_OK or b["role_group"] not in RG_OK: e.append(f"{a['name']}: role 통제어휘 위반")
    return e

if __name__=="__main__":
    if len(sys.argv)<2: print("사용법: python3 validate.py <추출JSON>"); sys.exit(2)
    doc=json.load(open(sys.argv[1],encoding="utf-8")); errs=validate(doc)
    d=doc["document"]; n=sum(len(a["areas"]) for a in d["school_levels"])
    print(f"[{d['id']}] framework={d['framework_type']} · 영역 {n}개")
    print("✅ 검증 통과 (위반 0건)" if not errs else "❌ 위반:\n  - "+"\n  - ".join(errs))
    sys.exit(0 if not errs else 1)
