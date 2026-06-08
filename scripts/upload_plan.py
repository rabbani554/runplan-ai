"""
COROS Training Plan Uploader
Reads auth.json + training_plan.json and posts to COROS API.

Requirements: pip install requests
Usage: python scripts/upload_plan.py
"""
import json, struct, sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency. Run: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).parent.parent

# ── Load auth ──────────────────────────────────────────────────────────────────
auth_path = ROOT / "auth.json"
if not auth_path.exists():
    print("auth.json not found. Copy auth.json.example to auth.json and fill in your token.")
    sys.exit(1)

auth = json.loads(auth_path.read_text())
ACCESS_TOKEN = auth["access_token"]
USER_ID      = auth["user_id"]

HEADERS = {
    "accesstoken":  ACCESS_TOKEN,
    "yfheader":     json.dumps({"userId": USER_ID}),
    "content-type": "application/json",
    "origin":       "https://t.coros.com",
    "referer":      "https://t.coros.com/",
    "user-agent":   "Mozilla/5.0"
}

API_URL = "https://teamapi.coros.com/training/plan/add"

# ── Load training plan ─────────────────────────────────────────────────────────
plan_path = ROOT / "training_plan.json"
if not plan_path.exists():
    print("training_plan.json not found. Ask Claude to generate it first.")
    sys.exit(1)

plan_data = json.loads(plan_path.read_text(encoding="utf-8"))

# ── Load exercise library ──────────────────────────────────────────────────────
ex_path = ROOT / "data" / "coros_exercises.json"
EX_LIB_RAW = json.loads(ex_path.read_text(encoding="utf-8")) if ex_path.exists() else []
EX_BY_KEY = {ex["overview"].replace("sid_strength_", ""): ex for ex in EX_LIB_RAW if "overview" in ex}

# ── Constants ──────────────────────────────────────────────────────────────────
TIME, DIST = 2, 5
WU, TR, CD, RS = 1, 2, 3, 4
REPS, HOLD = 3, 2

DAY_MAP = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}

_eid = [0]
_pid = [0]
def eid():
    _eid[0] += 1; return _eid[0]
def pid():
    _pid[0] += 1; return _pid[0]

def km2c(km): return int(km * 100_000)
def m2c(m):   return m * 100

# ── Running exercise builders ──────────────────────────────────────────────────
def mk_wu(id_, dur_s, sno):
    return {"access":0,"createTimestamp":1586584068,"defaultOrder":1,"equipment":[1],
            "exerciseType":WU,"groupId":"","hrType":3,"id":id_,"intensityCustom":6,
            "intensityDisplayUnit":0,"intensityMultiplier":0,"intensityPercent":0,
            "intensityPercentExtend":80000,"intensityType":2,"intensityValue":0,
            "intensityValueExtend":138,"isDefaultAdd":0,"isGroup":False,"isIntensityPercent":False,
            "name":"T1120","originId":"425895398452936705","overview":"sid_run_warm_up_dist",
            "part":[0],"restType":3,"restValue":0,"sets":1,"sortNo":sno,"sourceId":"0",
            "sourceUrl":"","sportType":1,"subType":0,"targetDisplayUnit":0,
            "targetType":TIME,"targetValue":dur_s,"userId":0,"videoUrl":""}

def mk_tr(id_, ttype, tval, hr_low, hr_high, sno, grp=""):
    has_hr = hr_low > 0 and hr_high > 0
    return {"access":0,"createTimestamp":1587381919,"defaultOrder":2,"equipment":[1],
            "exerciseType":TR,"groupId":grp,"hrType":3 if has_hr else 0,"id":id_,
            "intensityCustom":2 if has_hr else 0,"intensityDisplayUnit":0,
            "intensityMultiplier":0,"intensityPercent":0,"intensityPercentExtend":0,
            "intensityType":2 if has_hr else 0,"intensityValue":hr_low if has_hr else 0,
            "intensityValueExtend":hr_high if has_hr else 0,
            "isDefaultAdd":1,"isGroup":False,"isIntensityPercent":False,
            "name":"T3001","originId":"426109589008859136","overview":"sid_run_training",
            "part":[0],"restType":3,"restValue":0,"sets":1,"sortNo":sno,"sourceId":"0",
            "sourceUrl":"","sportType":1,"subType":0,
            "targetDisplayUnit":1 if ttype==DIST else 0,
            "targetType":ttype,"targetValue":tval,"userId":0,"videoUrl":""}

def mk_stride_step(id_, tval, sno, grp=""):
    # Strides are Open mode - no HR target. 100m is too short for HR to respond.
    # Effort guidance lives in the session description.
    return {"access":0,"createTimestamp":1587381919,"defaultOrder":2,"equipment":[1],
            "exerciseType":TR,"groupId":grp,"hrType":0,"id":id_,
            "intensityCustom":0,"intensityDisplayUnit":0,
            "intensityMultiplier":0,"intensityPercent":0,"intensityPercentExtend":0,
            "intensityType":0,"intensityValue":0,"intensityValueExtend":0,
            "isDefaultAdd":1,"isGroup":False,"isIntensityPercent":False,
            "name":"T3001","originId":"426109589008859136","overview":"sid_run_training",
            "part":[0],"restType":3,"restValue":0,"sets":1,"sortNo":sno,"sourceId":"0",
            "sourceUrl":"","sportType":1,"subType":0,
            "targetDisplayUnit":1,"targetType":DIST,"targetValue":tval,
            "userId":0,"videoUrl":""}

def mk_cd(id_, dur_s, sno):
    return {"access":0,"createTimestamp":1586584214,"defaultOrder":3,"equipment":[1],
            "exerciseType":CD,"groupId":"","hrType":3,"id":id_,"intensityCustom":6,
            "intensityDisplayUnit":0,"intensityMultiplier":0,"intensityPercent":0,
            "intensityPercentExtend":80000,"intensityType":2,"intensityValue":0,
            "intensityValueExtend":138,"isDefaultAdd":0,"isGroup":False,"isIntensityPercent":False,
            "name":"T1122","originId":"425895456971866112","overview":"sid_run_cool_down_dist",
            "part":[0],"restType":3,"restValue":0,"sets":1,"sortNo":sno,"sourceId":"0",
            "sourceUrl":"","sportType":1,"subType":0,"targetDisplayUnit":0,
            "targetType":TIME,"targetValue":dur_s,"userId":0,"videoUrl":""}

def mk_group(id_, reps, rest_s, sno):
    return {"access":0,"defaultOrder":0,"exerciseType":0,"id":id_,"intensityCustom":0,
            "intensityMultiplier":0,"intensityType":0,"intensityValue":0,"intensityValueExtend":0,
            "isDefaultAdd":0,"isGroup":True,"name":"","originId":"","overview":"","programId":"",
            "restType":0,"restValue":rest_s,"sets":reps,"sortNo":sno,"sourceId":"0",
            "sourceUrl":"","sportType":0,"subType":0,"targetType":"","targetValue":0,"videoUrl":""}

def mk_rest(id_, rest_s, sno, grp):
    return {"access":0,"createTimestamp":1586584214,"defaultOrder":3,"equipment":[1],
            "exerciseType":RS,"groupId":grp,"hrType":3,"id":id_,"intensityCustom":6,
            "intensityDisplayUnit":0,"intensityMultiplier":0,"intensityPercent":0,
            "intensityPercentExtend":80000,"intensityType":2,"intensityValue":0,
            "intensityValueExtend":138,"isDefaultAdd":0,"isGroup":False,"isIntensityPercent":False,
            "name":"T1123","originId":"425895398452936705","overview":"sid_run_cool_down_dist",
            "part":[0],"restType":3,"restValue":rest_s,"sets":1,"sortNo":sno,"sourceId":"0",
            "sourceUrl":"","sportType":1,"subType":0,"targetDisplayUnit":0,
            "targetType":TIME,"targetValue":rest_s,"userId":0,"videoUrl":""}

# ── Strength exercise builder ──────────────────────────────────────────────────
# Hardcoded fallback for common runner exercises
ST_FALLBACK = {
    "squat":                 ("T1061","425832054396207105",  37, REPS,[8],  [7,8,14],[5]),
    "walking_lunge":         ("T1225","469646772906672129",  74, REPS,[7,14],[7,14,8],[5]),
    "rdl":                   ("T1287","469655210101489664", 307, REPS,[8,14],[8,14,13],[5]),
    "romanian_deadlift":     ("T1287","469655210101489664", 307, REPS,[8,14],[8,14,13],[5]),
    "sl_hip_bridge":         ("T1219","469646654258200576",  68, REPS,[14],[14,8,6],[5]),
    "single_leg_hip_bridge": ("T1219","469646654258200576",  68, REPS,[14],[14,8,6],[5]),
    "calf_raise":            ("T1070","425832417320943617",  49, REPS,[15],[15],[5]),
    "standing_calf_raises":  ("T1070","425832417320943617",  49, REPS,[15],[15],[5]),
    "sl_calf_raise":         ("T1275","469654960724951040", 124, REPS,[15],[15],[5]),
    "plank":                 ("T1010","425827856334110721",  35, HOLD,[6],[6,3],[1]),
    "planks":                ("T1010","425827856334110721",  35, HOLD,[6],[6,3],[1]),
    "side_plank":            ("T1185","428453358030995457",   5, HOLD,[6],[6,3],[1]),
    "dead_bug":              ("T1243","469654335807209472",  92, REPS,[6],[6,3,8],[1]),
    "sl_deadlift":           ("T1187","428453501107093504", 343, REPS,[8],[8,14,13],[5]),
    "single_leg_deadlift":   ("T1187","428453501107093504", 343, REPS,[8],[8,14,13],[5]),
    "hip_thrust":            ("T1289","469655210101489667", 309, REPS,[14],[14,8],[5]),
    "nordic_hamstring_curl": ("T1365","469654335807209480", 208, REPS,[9],[9,8],[5]),
    "copenhagen_plank":      ("T1368","469654335807209483", 210, HOLD,[6],[6,11],[1]),
    "box_step_ups":          ("T1166","425832417320943620",   8, REPS,[8,14],[8,14],[5]),
    "bridge":                ("T1033","425831234567890123",  56, REPS,[14],[14,8],[5]),
    "bird_dog":              ("T1249","469654335807209475",  98, REPS,[6],[6,8],[1]),
    "banded_hip_abduction":  ("T1321","469646654258200580", 157, REPS,[13],[13,7],[5]),
    "banded_ankle_eversion": ("T1327","469654960724951050", 163, REPS,[15],[15],[5]),
    "banded_ankle_inversion":("T1326","469654960724951049", 162, REPS,[15],[15],[5]),
    "glute_bridge_hold":     ("T1229","469646654258200579",  78, HOLD,[14],[14,8],[5]),
    "single_leg_squat":      ("T1167","425832417320943621",  57, REPS,[8,14],[8,14,7],[5]),
    "reverse_lunge":         ("T1226","469646772906672130",  75, REPS,[8,14],[8,14,7],[5]),
}

def mk_st_ex(key, sets, value, rest_s, ex_id):
    # Try library first, then fallback
    lib_ex = EX_BY_KEY.get(key)
    if lib_ex:
        name     = lib_ex.get("name", "T1001")
        origin   = lib_ex.get("originId", "0")
        anim_id  = lib_ex.get("animationId", 0)
        ttype    = lib_ex.get("targetType", REPS)
        muscle   = lib_ex.get("muscle", [])
        m_rel    = lib_ex.get("muscleRelevance", muscle)
        part     = lib_ex.get("part", [0])
    elif key in ST_FALLBACK:
        name, origin, anim_id, ttype, muscle, m_rel, part = ST_FALLBACK[key]
    else:
        print(f"  Warning: exercise '{key}' not found, skipping")
        return None

    return {"access":0,"animationId":anim_id,"coverUrlArrStr":"",
            "createTimestamp":1586376935,"defaultOrder":0,"equipment":[1],
            "exerciseType":2,"groupId":"","hrType":0,"id":ex_id,
            "intensityCustom":0,"intensityDisplayUnit":"6","intensityMultiplier":0,
            "intensityPercent":0,"intensityPercentExtend":0,"intensityType":1,
            "intensityValue":0,"intensityValueExtend":0,"isDefaultAdd":0,
            "isGroup":False,"isIntensityPercent":False,"muscle":muscle,
            "muscleRelevance":m_rel,"name":name,"originId":origin,
            "overview":f"sid_strength_{key}","part":part,"restType":1,
            "restValue":rest_s,"sets":sets,"sortNo":0,"sourceUrl":"",
            "sportType":4,"status":1,"targetDisplayUnit":0,"targetType":ttype,
            "targetValue":value,"thumbnailUrl":"","userId":0,
            "videoInfos":[],"videoUrl":"","videoUrlArrStr":""}

# ── Program builder ────────────────────────────────────────────────────────────
def mk_program(name, exercises, id_in_plan, sport_type=1, overview=""):
    return {"access":1,"authorId":"0","createTimestamp":0,
            "distance":"0" if sport_type==4 else 0,"duration":0,
            "essence":0,"estimatedType":0,"estimatedValue":0,"exerciseNum":0,
            "exercises":exercises,"headPic":"","id":"0","idInPlan":id_in_plan,"name":name,
            "nickname":"","originEssence":0,"overview":overview,"pbVersion":5,"planIdIndex":0,
            "poolLength":2500,"profile":"",
            "referExercise":{"intensityType":0,"hrType":0,"valueType":0},
            "sex":0,"shareUrl":"","simple":False,
            "sourceUrl":"https://d31oxp44ddzkyk.cloudfront.net/source/source_default/0/a9dc1a410a0b4becb48157577cbf6852.jpg",
            "sportType":sport_type,"star":0,"subType":65535,"targetType":0,"targetValue":0,
            "thirdPartyId":0,"totalSets":0,"trainingLoad":0,"type":0,"unit":0,
            "userId":"0","version":0,"videoCoverUrl":"","videoUrl":"",
            "fastIntensityTypeName":"custom","poolLengthId":1,"poolLengthUnit":2,
            "sourceId":"425868125142171649"}

# ── Session converter ──────────────────────────────────────────────────────────
def build_running_session(session):
    exercises = []
    sno = 1
    for step in session["steps"]:
        st = step["step_type"]
        if st == "warmup":
            exercises.append(mk_wu(eid(), step["duration_s"], sno))
        elif st == "run":
            exercises.append(mk_tr(eid(), DIST, km2c(step["distance_km"]),
                                   step.get("hr_low", 0), step.get("hr_high", 0), sno))
        elif st == "cooldown":
            exercises.append(mk_cd(eid(), step["duration_s"], sno))
        elif st == "interval_group":
            g = eid()
            exercises.append(mk_group(g, step["reps"], step["rest_s"], sno))
            exercises.append(mk_tr(eid(), DIST, m2c(step["distance_m"]),
                                   step.get("hr_low", 0), step.get("hr_high", 0),
                                   sno, grp=g))
            exercises.append(mk_rest(eid(), step["rest_s"], sno + 1, grp=g))
        elif st == "strides":
            g = eid()
            exercises.append(mk_group(g, step["reps"], step.get("rest_s", 60), sno))
            exercises.append(mk_stride_step(eid(), m2c(step.get("distance_m", 100)), sno, grp=g))
            exercises.append(mk_rest(eid(), step.get("rest_s", 60), sno + 1, grp=g))
        sno += 1
    return exercises

def build_strength_session(session):
    exercises = []
    for ex_def in session["exercises"]:
        ex = mk_st_ex(ex_def["key"], ex_def["sets"], ex_def["value"],
                      ex_def.get("rest_s", 45), eid())
        if ex:
            exercises.append(ex)
    return exercises

# ── Main ───────────────────────────────────────────────────────────────────────
programs = []
entities = []

for session in plan_data["sessions"]:
    sport = session.get("sport", "running")
    week  = session["week"]
    d     = DAY_MAP[session["day"].upper()]
    day_no = (week - 1) * 7 + d
    p_id  = pid()

    if sport == "strength":
        exercises = build_strength_session(session)
        sport_type = 4
    else:
        exercises = build_running_session(session)
        sport_type = 1

    if not exercises:
        print(f"  Skipping {session['name']} — no valid exercises")
        continue

    programs.append(mk_program(session["name"], exercises, p_id, sport_type,
                               overview=session.get("description", "")))
    entities.append({"happenDay":"","idInPlan":p_id,"sortNo":0,
                     "dayNo":day_no,"sortNoInPlan":0,"sortNoInSchedule":0})

total_weeks = plan_data.get("total_weeks", max(s["week"] for s in plan_data["sessions"]))

payload = {
    "name":       plan_data["plan_name"],
    "overview":   plan_data.get("overview", ""),
    "entities":   entities,
    "programs":   programs,
    "weekStages": [],
    "maxIdInPlan": _pid[0],
    "totalDay":   len(entities),
    "unit":       0,
    "region":     1,
    "minWeeks":   total_weeks,
    "maxWeeks":   total_weeks,
    "sourceId":   "425868113867882496",
    "sourceUrl":  "https://d31oxp44ddzkyk.cloudfront.net/source/source_default/0/5a9db1c3363348298351aaabfd70d0f5.jpg",
    "pbVersion":  2
}

print(f"Uploading: {len(programs)} sessions across {total_weeks} weeks...")
resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
print(f"HTTP {resp.status_code}")

try:
    data = resp.json()
    if data.get("result") == "0000":
        plan_id = data.get("data", "unknown")
        print(f"\nSUCCESS! Plan created.")
        print(f"View: https://t.coros.com/schedule-plan/detail?id={plan_id}")
        print(f"\nNext: open the link, click 'Start Plan', set your start date.")
    else:
        print(f"API error: {data.get('message')} (code: {data.get('result')})")
        print(resp.text[:500])
except Exception as e:
    print(f"Response: {resp.text[:500]}")
