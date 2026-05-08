import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH MOBILE ---
st.set_page_config(page_title="9 BIEN PRO", layout="centered")

st.markdown("""
    <style>
    .stTable td, .stTable th { font-size: 12px !important; padding: 2px !important; text-align: center !important; font-weight: bold !important; }
    .main-title { text-align: center; color: #1E3A8A; font-size: 20px; font-weight: bold; }
    .history-container { overflow-x: auto; white-space: nowrap; border: 1px solid #ddd; padding: 5px; background-color: #f8f9fa; border-radius: 5px; }
    div[data-testid="stExpander"] div { padding: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MAP DATA KHÔNG DẤU ---
BO_MAP = {
    "00": [0, 5, 50, 55], "01": [1, 10, 6, 60, 51, 15, 56, 65], "02": [2, 20, 7, 70, 52, 25, 57, 75],
    "03": [3, 30, 8, 80, 53, 35, 58, 85], "04": [4, 40, 9, 90, 54, 45, 59, 95], "11": [11, 16, 61, 66],
    "12": [12, 21, 17, 71, 62, 26, 67, 76], "13": [13, 31, 18, 81, 63, 36, 68, 86], "14": [14, 41, 19, 91, 64, 46, 69, 96],
    "22": [22, 27, 72, 77], "23": [23, 32, 28, 82, 73, 37, 78, 87], "24": [24, 42, 29, 92, 74, 47, 79, 97],
    "33": [33, 38, 83, 88], "34": [34, 43, 39, 93, 84, 48, 89, 98], "44": [44, 49, 94, 99]
}
CHAN_LE_LABELS = ["chan chan", "chan le", "le le", "le chan"]
BE_TO_LABELS = ["be be", "be to", "to be", "to to"]
GIAP_MAP = {
    "Ty": [0, 12, 24, 36, 48, 60, 72, 84, 96], "Suu": [1, 13, 25, 37, 49, 61, 73, 85, 97],
    "Dan": [2, 14, 26, 38, 50, 62, 74, 86, 98], "Mao": [3, 15, 27, 39, 51, 63, 75, 87, 99],
    "Thin": [4, 16, 28, 40, 52, 64, 76, 88], "Ty.": [5, 17, 29, 41, 53, 65, 77, 89],
    "Ngo": [6, 18, 30, 42, 54, 66, 78, 90], "Mui": [7, 19, 31, 43, 55, 67, 79, 91],
    "Than": [8, 20, 32, 44, 56, 68, 80, 92], "Dau": [9, 21, 33, 45, 57, 69, 81, 93],
    "Tuat": [10, 22, 34, 46, 58, 70, 82, 94], "Hoi": [11, 23, 35, 47, 59, 71, 83, 95]
}

def get_mapping_idx(val, mapping):
    for idx, lst in enumerate(mapping.values()):
        if val in lst: return idx
    return 0

def get_cl_idx(n):
    d, du = n // 10, n % 10
    if d % 2 == 0 and du % 2 == 0: return 0
    if d % 2 == 0 and du % 2 != 0: return 1
    if d % 2 != 0 and du % 2 != 0: return 2
    return 3

def get_bt_idx(n):
    d, du = n // 10, n % 10
    if d <= 4 and du <= 4: return 0
    if d <= 4 and du >= 5: return 1
    if d >= 5 and du <= 4: return 2
    return 3

# --- KHOI TAO STATE ---
if 'dau' not in st.session_state:
    for k in ['dau','duoi','tong','hieu','cham']: st.session_state[k] = [0]*10
    st.session_state['bo'] = [0]*15
    st.session_state['chanle'] = [0]*4
    st.session_state['beto'] = [0]*4
    st.session_state['giap'] = [0]*12
    st.session_state.ls = []
    st.session_state.db = {}
    st.session_state.pt = False

def cap_nhat():
    n = st.session_state.so_ve
    dv, duv = n//10, n%10
    tv, hv = (dv+duv)%10, (dv-duv+10)%10
    bv, clv, btv, gv = get_mapping_idx(n, BO_MAP), get_cl_idx(n), get_bt_idx(n), get_mapping_idx(n, GIAP_MAP)

    # Tinh Hang
    tmp = []
    for i in range(100):
        d, du = i//10, i%10
        s = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
            st.session_state.hieu[(d-du+10)%10] + \
            ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
            st.session_state.bo[get_mapping_idx(i, BO_MAP)] + st.session_state.chanle[get_cl_idx(i)] + \
            st.session_state.beto[get_bt_idx(i)] + st.session_state.giap[get_mapping_idx(i, GIAP_MAP)]
        tmp.append({"s": f"{d}{du}", "d": s})
    df = pd.DataFrame(tmp).sort_values(by=["d","s"]).reset_index(drop=True)
    h = df[df['s'] == f"{n:02d}"].index[0] + 1
    
    # Cap nhat diem
    for i in range(10):
        st.session_state.dau[i] = 0 if i==dv else st.session_state.dau[i]+1
        st.session_state.duoi[i] = 0 if i==duv else st.session_state.duoi[i]+1
        st.session_state.tong[i] = 0 if i==tv else st.session_state.tong[i]+1
        st.session_state.hieu[i] = 0 if i==hv else st.session_state.hieu[i]+1
        st.session_state.cham[i] = 0 if (i==dv or i==duv) else st.session_state.cham[i]+1
    for i in range(15): st.session_state.bo[i] = 0 if i==bv else st.session_state.bo[i]+1
    for i in range(4):
        st.session_state.chanle[i] = 0 if i==clv else st.session_state.chanle[i]+1
        st.session_state.beto[i] = 0 if i==btv else st.session_state.beto[i]+1
    for i in range(12): st.session_state.giap[i] = 0 if i==gv else st.session_state.giap[i]+1
    st.session_state.ls.insert(0, {"Số": f"{n:02d}", "Hạng": h})

# --- GIAO DIEN ---
st.markdown("<div class='main-title'>💎 THONG KE 9 BIEN PRO</div>", unsafe_allow_html=True)

with st.sidebar:
    if st.button("💾 LUU CLOUD"):
        st.session_state.db[datetime.now().strftime("%H:%M")] = {k: list(st.session_state[k]) for k in ['dau','duoi','tong','hieu','cham','bo','chanle','beto','giap','ls']}
    if st.session_state.db:
        if st.button("🔄 NAP DU LIEU"):
            d = st.session_state.db[list(st.session_state.db.keys())[-1]]
            for k in d: st.session_state[k] = d[k]
            st.rerun()
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

# NHAP LIEU NHANH
c1, c2 = st.columns([3, 2])
with c1: st.number_input("So vua ve:", 0, 99, step=1, format="%02d", key="so_ve")
with c2: st.write("##"); st.button("CAP NHAT", on_click=cap_nhat, type="primary", use_container_width=True)

st.divider()

t1, t2, t3, t4 = st.tabs(["⚡ Dan", "📊 Bang A", "🔢 Ma Tran B", "🛠️ Sua"])

with t1:
    l_tmp = []
    for i in range(100):
        d, du = i//10, i%10
        score = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
                st.session_state.hieu[(d-du+10)%10] + \
                ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
                st.session_state.bo[get_mapping_idx(i, BO_MAP)] + st.session_state.chanle[get_cl_idx(i)] + \
                st.session_state.beto[get_bt_idx(i)] + st.session_state.giap[get_mapping_idx(i, GIAP_MAP)]
        l_tmp.append({"s": f"{d}{du}", "d": score})
    df_s = pd.DataFrame(l_tmp).sort_values(by=["d","s"])
    st.success(", ".join(df_s.head(10)["s"].tolist()))
    st.info(", ".join(df_s.head(36)["s"].tolist()))

with t2:
    # HIEN THI BANG A RUT GON CHO MOBILE
    for lbl, k, names in [
        ("DAU", "dau", range(10)), ("DUOI", "duoi", range(10)), ("TONG", "tong", range(10)),
        ("HIEU", "hieu", range(10)), ("CHAM", "cham", range(10)), ("BO", "bo", list(BO_MAP.keys())),
        ("CHAN LE", "chanle", CHAN_LE_LABELS), ("BE TO", "beto", BE_TO_LABELS), ("12 GIAP", "giap", list(GIAP_MAP.keys()))
    ]:
        st.write(f"**{lbl}**")
        st.markdown('<div class="history-container">', unsafe_allow_html=True)
        st.table(pd.DataFrame([st.session_state[k]], columns=names, index=[""]))
        st.markdown('</div>', unsafe_allow_html=True)

with t3:
    mt = []
    for d in range(10):
        r = []
        for du in range(10):
            i = d*10+du
            v = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
                st.session_state.hieu[(d-du+10)%10] + \
                ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
                st.session_state.bo[get_mapping_idx(i, BO_MAP)] + st.session_state.chanle[get_cl_idx(i)] + \
                st.session_state.beto[get_bt_idx(i)] + st.session_state.giap[get_mapping_idx(i, GIAP_MAP)]
            r.append(v)
        mt.append(r)
    st.dataframe(pd.DataFrame(mt, columns=[str(i) for i in range(10)], index=[str(i) for i in range(10)]), use_container_width=True)

with t4:
    if st.button("💾 LUU SUA TAY"):
        for k in ['dau','duoi','tong','hieu','cham','bo','chanle','beto','giap']:
            for i in range(len(st.session_state[k])): st.session_state[k][i] = st.session_state[f"e_{k}_{i}"]
        st.rerun()
    for k, lbl in [('dau','Dau'),('duoi','Duoi'),('tong','Tong'),('hieu','Hieu'),('cham','Cham'),('bo','Bo'),('chanle','Chan Le'),('beto','Be To'),('giap','12 Giap')]:
        with st.expander(f"Sua {lbl}"):
            cols = st.columns(5)
            for i in range(len(st.session_state[k])):
                with cols[i % 5]: st.number_input(f"{i}", value=st.session_state[k][i], key=f"e_{k}_{i}")

st.divider()
if not st.session_state.pt:
    if st.button("🚀 BAT DAU PHAN TICH", use_container_width=True): st.session_state.pt = True; st.rerun()
else:
    if st.button("⏹️ TAT PHAN TICH", use_container_width=True): st.session_state.pt = False; st.rerun()
    if st.session_state.ls:
        rks = [x["Hạng"] for x in st.session_state.ls]
        gs = [sum(1 for r in rks if 1<=r<=10), sum(1 for r in rks if 11<=r<=39), sum(1 for r in rks if 40<=r<=59), sum(1 for r in rks if 60<=r<=75), sum(1 for r in rks if 76<=r<=100)]
        st.table(pd.DataFrame({"Nhom": ["1-10","11-39","40-59","60-75","76-100"], "Lan": gs, "%": [f"{(x/len(rks))*100:.1f}%" for x in gs]}))
        st.line_chart(pd.DataFrame(st.session_state.ls[::-1])['Hạng'])
        st.markdown('<div class="history-container">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.ls).T)
        st.markdown('</div>', unsafe_allow_html=True)
