import streamlit as st
import pandas as pd
from datetime import datetime

# --- CAU HINH GIAO DIEN MOBILE ---
st.set_page_config(page_title="10 BIEN PRO - UPDATE", layout="centered")

st.markdown("""
    <style>
    .stTable td, .stTable th { font-size: 12px !important; padding: 2px !important; text-align: center !important; font-weight: bold !important; }
    .main-title { text-align: center; color: #1E3A8A; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .history-container { overflow-x: auto; white-space: nowrap; border: 1px solid #ddd; padding: 5px; background-color: #f8f9fa; border-radius: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- DINH NGHIA DU LIEU CHUAN (KHONG DAU) ---
BO_MAP = {
    "bo 00": [0, 5, 50, 55], "bo 01": [1, 10, 6, 60, 51, 15, 56, 65], "bo 02": [2, 20, 7, 70, 52, 25, 57, 75],
    "bo 03": [3, 30, 8, 80, 53, 35, 58, 85], "bo 04": [4, 40, 9, 90, 54, 45, 59, 95], "bo 11": [11, 16, 61, 66],
    "bo 12": [12, 21, 17, 71, 62, 26, 67, 76], "bo 13": [13, 31, 18, 81, 63, 36, 68, 86], "bo 14": [14, 41, 19, 91, 64, 46, 69, 96],
    "bo 22": [22, 27, 72, 77], "bo 23": [23, 32, 28, 82, 73, 37, 78, 87], "bo 24": [24, 42, 29, 92, 74, 47, 79, 97],
    "bo 33": [33, 38, 83, 88], "bo 34": [34, 43, 39, 93, 84, 48, 89, 98], "bo 44": [44, 49, 94, 99]
}

CHAN_LE_MAP = {
    "chan chan": [0, 22, 44, 66, 88, 2, 20, 4, 40, 6, 60, 8, 80, 24, 42, 26, 62, 28, 82, 46, 64, 48, 84, 68, 86],
    "chan le": [1, 3, 5, 7, 9, 21, 23, 25, 27, 29, 41, 43, 45, 47, 49, 61, 63, 65, 67, 69, 81, 83, 85, 87, 89],
    "le le": [11, 33, 55, 77, 99, 13, 31, 15, 51, 17, 71, 19, 91, 35, 53, 37, 73, 39, 93, 57, 75, 59, 95, 79, 97],
    "le chan": [10, 12, 14, 16, 18, 30, 32, 34, 36, 38, 50, 52, 54, 56, 58, 70, 72, 74, 76, 78, 90, 92, 94, 96, 98]
}

BE_TO_MAP = {
    "be be": [0, 11, 22, 33, 44, 1, 10, 2, 20, 3, 30, 4, 40, 12, 21, 13, 31, 14, 41, 23, 32, 24, 42, 34, 43],
    "be to": [5, 6, 7, 8, 9, 15, 16, 17, 18, 19, 25, 26, 27, 28, 29, 35, 36, 37, 38, 39, 45, 46, 47, 48, 49],
    "to be": [90, 91, 92, 93, 94, 80, 81, 82, 83, 84, 70, 71, 72, 73, 74, 60, 61, 62, 63, 64, 50, 51, 52, 53, 54],
    "to to": [55, 66, 77, 88, 99, 56, 65, 57, 75, 58, 85, 59, 95, 67, 76, 68, 86, 69, 96, 78, 87, 79, 97, 89, 98]
}

GIAP_MAP = {
    "Ty": [0, 12, 24, 36, 48, 60, 72, 84, 96], "Suu": [1, 13, 25, 37, 49, 61, 73, 85, 97],
    "Dan": [2, 14, 26, 38, 50, 62, 74, 86, 98], "Mao": [3, 15, 27, 39, 51, 63, 75, 87, 99],
    "Thin": [4, 16, 28, 40, 52, 64, 76, 88], "Ty.": [5, 17, 29, 41, 53, 65, 77, 89],
    "Ngo": [6, 18, 30, 42, 54, 66, 78, 90], "Mui": [7, 19, 31, 43, 55, 67, 79, 91],
    "Than": [8, 20, 32, 44, 56, 68, 80, 92], "Dau": [9, 21, 33, 45, 57, 69, 81, 93],
    "Tuat": [10, 22, 34, 46, 58, 70, 82, 94], "Hoi": [11, 23, 35, 47, 59, 71, 83, 95]
}

DANG_MAP = {
    "kep": [0, 55, 11, 66, 22, 77, 33, 88, 44, 99, 5, 50, 16, 61, 27, 72, 38, 83, 49, 94],
    "sat kep": [1, 10, 12, 21, 23, 32, 34, 43, 45, 54, 56, 65, 67, 76, 78, 87, 89, 98, 9, 90],
    "cach 1": [2, 20, 8, 80, 13, 31, 19, 91, 24, 42, 35, 53, 46, 64, 57, 75, 79, 97, 68, 86],
    "cach 2": [3, 30, 18, 81, 25, 52, 47, 74, 69, 96, 7, 70, 14, 41, 29, 92, 36, 63, 58, 85],
    "cach 3": [4, 40, 6, 60, 15, 51, 17, 71, 28, 82, 26, 62, 37, 73, 39, 93, 48, 84, 59, 95]
}

# --- TRO GIUP ---
def find_idx(n, mapping):
    for i, (name, nums) in enumerate(mapping.items()):
        if n in nums: return i
    return -1

# --- KHOI TAO STATE ---
# Su dung session_state de giu du lieu khi load lai trang
if 'dau' not in st.session_state:
    for k in ['dau','duoi','tong','hieu','cham']: st.session_state[k] = [0]*10
    st.session_state['bo'] = [0]*15
    st.session_state['chanle'] = [0]*4
    st.session_state['beto'] = [0]*4
    st.session_state['giap'] = [0]*12
    st.session_state['dang'] = [0]*5
    st.session_state.ls = []
    st.session_state.db_cloud = {} # Kho luu tru ban sao
    st.session_state.pt = False

# --- LOGIC ---
def cap_nhat_diem():
    n = st.session_state.so_moi_ve
    dv, duv = n // 10, n % 10
    tv, hv = (dv + duv) % 10, (dv - duv + 10) % 10
    bo_v, cl_v, bt_v, gp_v, dg_v = find_idx(n, BO_MAP), find_idx(n, CHAN_LE_MAP), find_idx(n, BE_TO_MAP), find_idx(n, GIAP_MAP), find_idx(n, DANG_MAP)

    results = []
    for i in range(100):
        d, du = i // 10, i % 10
        score = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
                st.session_state.hieu[(d-du+10)%10] + \
                ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
                st.session_state.bo[find_idx(i, BO_MAP)] + st.session_state.chanle[find_idx(i, CHAN_LE_MAP)] + \
                st.session_state.beto[find_idx(i, BE_TO_MAP)] + st.session_state.giap[find_idx(i, GIAP_MAP)] + \
                st.session_state.dang[find_idx(i, DANG_MAP)]
        results.append({"s": f"{d}{du}", "d": score})
    
    df = pd.DataFrame(results).sort_values(by=["d", "s"]).reset_index(drop=True)
    h = df[df['s'] == f"{n:02d}"].index[0] + 1

    for i in range(10):
        st.session_state.dau[i] = 0 if i == dv else st.session_state.dau[i] + 1
        st.session_state.duoi[i] = 0 if i == duv else st.session_state.duoi[i] + 1
        st.session_state.tong[i] = 0 if i == tv else st.session_state.tong[i] + 1
        st.session_state.hieu[i] = 0 if i == hv else st.session_state.hieu[i] + 1
        st.session_state.cham[i] = 0 if (i == dv or i == duv) else st.session_state.cham[i] + 1
    for i in range(15): st.session_state.bo[i] = 0 if i == bo_v else st.session_state.bo[i] + 1
    for i in range(4):
        st.session_state.chanle[i] = 0 if i == cl_v else st.session_state.chanle[i] + 1
        st.session_state.beto[i] = 0 if i == bt_v else st.session_state.beto[i] + 1
    for i in range(12): st.session_state.giap[i] = 0 if i == gp_v else st.session_state.giap[i] + 1
    for i in range(5): st.session_state.dang[i] = 0 if i == dg_v else st.session_state.dang[i] + 1
    
    st.session_state.ls.insert(0, {"Số": f"{n:02d}", "Hạng": h})

# --- UI ---
st.markdown("<div class='main-title'>💎 THONG KE 10 BIEN PRO</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ QUAN LY DU LIEU")
    
    # Nut Luu
    if st.button("💾 LUU CLOUD (BACKUP)", use_container_width=True):
        now_str = datetime.now().strftime("%H:%M:%S")
        # Sao chep sau de tranh tham chieu
        st.session_state.db_cloud[now_str] = {
            'dau': list(st.session_state.dau), 'duoi': list(st.session_state.duoi),
            'tong': list(st.session_state.tong), 'hieu': list(st.session_state.hieu),
            'cham': list(st.session_state.cham), 'bo': list(st.session_state.bo),
            'chanle': list(st.session_state.chanle), 'beto': list(st.session_state.beto),
            'giap': list(st.session_state.giap), 'dang': list(st.session_state.dang),
            'ls': list(st.session_state.ls)
        }
        st.success(f"Da luu luc {now_str}!")

    st.divider()

    # Phan Nap du lieu (Chi hien khi co ban luu)
    if st.session_state.db_cloud:
        st.subheader("🔄 NAP DU LIEU DA LUU")
        selected_backup = st.selectbox("Chon ban ghi:", list(st.session_state.db_cloud.keys())[::-1])
        if st.button("🚀 NAP BAN NAY", type="primary", use_container_width=True):
            data = st.session_state.db_cloud[selected_backup]
            st.session_state.dau = list(data['dau'])
            st.session_state.duoi = list(data['duoi'])
            st.session_state.tong = list(data['tong'])
            st.session_state.hieu = list(data['hieu'])
            st.session_state.cham = list(data['cham'])
            st.session_state.bo = list(data['bo'])
            st.session_state.chanle = list(data['chanle'])
            st.session_state.beto = list(data['beto'])
            st.session_state.giap = list(data['giap'])
            st.session_state.dang = list(data['dang'])
            st.session_state.ls = list(data['ls'])
            st.toast(f"Da khoi phuc ban {selected_backup}")
            st.rerun()
    else:
        st.info("Chua co ban sao luu nao.")

    st.divider()
    if st.button("🗑️ RESET TOAN BO", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# NHAP SO
c1, c2 = st.columns([3, 2])
with c1: st.number_input("So vua ve:", 0, 99, step=1, format="%02d", key="so_moi_ve")
with c2: st.write("##"); st.button("CAP NHAT", on_click=cap_nhat_diem, type="primary", use_container_width=True)

st.divider()

t1, t2, t3, t4 = st.tabs(["⚡ Dan", "📊 Bang A", "🔢 Ma Tran B", "🛠️ Sua"])

with t1:
    l_calc = []
    for i in range(100):
        d, du = i // 10, i % 10
        sc = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
             st.session_state.hieu[(d-du+10)%10] + \
             ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
             st.session_state.bo[find_idx(i, BO_MAP)] + st.session_state.chanle[find_idx(i, CHAN_LE_MAP)] + \
             st.session_state.beto[find_idx(i, BE_TO_MAP)] + st.session_state.giap[find_idx(i, GIAP_MAP)] + \
             st.session_state.dang[find_idx(i, DANG_MAP)]
        l_calc.append({"s": f"{d}{du}", "d": sc})
    df_s = pd.DataFrame(l_calc).sort_values(by=["d", "s"])
    ca, cb = st.columns(2)
    with ca:
        n1 = st.number_input("Dan 1:", 1, 100, 10, key="n1")
        st.success(", ".join(df_s.head(int(n1))["s"].tolist()))
    with cb:
        n2 = st.number_input("Dan 2:", 1, 100, 36, key="n2")
        st.info(", ".join(df_s.head(int(n2))["s"].tolist()))

with t2:
    for lbl, k, names in [
        ("DAU", "dau", range(10)), ("DUOI", "duoi", range(10)), ("TONG", "tong", range(10)),
        ("HIEU", "hieu", range(10)), ("CHAM", "cham", range(10)), 
        ("BO", "bo", [x.split()[1] for x in BO_MAP.keys()]),
        ("CHAN LE", "chanle", list(CHAN_LE_MAP.keys())), 
        ("BE TO", "beto", list(BE_TO_MAP.keys())), 
        ("12 GIAP", "giap", list(GIAP_MAP.keys())),
        ("DANG SO", "dang", list(DANG_MAP.keys()))
    ]:
        st.write(f"**{lbl}**")
        st.markdown('<div class="history-container">', unsafe_allow_html=True)
        st.table(pd.DataFrame([st.session_state[k]], columns=names, index=[""]))
        st.markdown('</div>', unsafe_allow_html=True)

with t3:
    m_data = []
    for d in range(10):
        row = []
        for du in range(10):
            idx = d * 10 + du
            val = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
                  st.session_state.hieu[(d-du+10)%10] + \
                  ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
                  st.session_state.bo[find_idx(idx, BO_MAP)] + st.session_state.chanle[find_idx(idx, CHAN_LE_MAP)] + \
                  st.session_state.beto[find_idx(idx, BE_TO_MAP)] + st.session_state.giap[find_idx(idx, GIAP_MAP)] + \
                  st.session_state.dang[find_idx(idx, DANG_MAP)]
            row.append(val)
        m_data.append(row)
    st.dataframe(pd.DataFrame(m_data, columns=[str(i) for i in range(10)], index=[str(i) for i in range(10)]), use_container_width=True)

with t4:
    if st.button("💾 LUU SUA TAY"):
        for k in ['dau','duoi','tong','hieu','cham','bo','chanle','beto','giap','dang']:
            for i in range(len(st.session_state[k])): st.session_state[k][i] = st.session_state[f"e_{k}_{i}"]
        st.rerun()
    for k, lbl in [('dau','Dau'),('duoi','Duoi'),('tong','Tong'),('hieu','Hiệu'),('cham','Cham'),('bo','Bo'),('chanle','Chan Le'),('beto','Be To'),('giap','12 Giap'),('dang','Dang')]:
        with st.expander(f"Sua {lbl}"):
            cols = st.columns(5)
            for i in range(len(st.session_state[k])):
                with cols[i % 5]: st.number_input(f"{i}", value=st.session_state[k][i], key=f"e_{k}_{i}")

st.divider()
if not st.session_state.pt:
    if st.button("🚀 BAT DAU PHAN TICH"): st.session_state.pt = True; st.rerun()
else:
    if st.button("⏹️ TAT PHAN TICH"): st.session_state.pt = False; st.rerun()
    if st.session_state.ls:
        rks = [x["Hạng"] for x in st.session_state.ls]
        gs = [sum(1 for r in rks if 1<=r<=10), sum(1 for r in rks if 11<=r<=39), sum(1 for r in rks if 40<=r<=59), sum(1 for r in rks if 60<=r<=75), sum(1 for r in rks if 76<=r<=100)]
        st.table(pd.DataFrame({"Nhom": ["1-10","11-39","40-59","60-75","76-100"], "Lan": gs, "%": [f"{(x/len(rks))*100:.1f}%" for x in gs]}))
        st.line_chart(pd.DataFrame(st.session_state.ls[::-1])['Hạng'])
        st.markdown('<div class="history-container">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.ls).T)
        st.markdown('</div>', unsafe_allow_html=True)
