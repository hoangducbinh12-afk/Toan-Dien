import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ Thống Soi Cầu 9 Biến Siêu Cấp", layout="wide")

st.markdown("""
    <style>
    .stTable td, .stTable th { font-size: 13px !important; font-weight: bold !important; text-align: center !important; }
    .main-title { text-align: center; color: #1E3A8A; font-weight: bold; }
    .history-container { overflow-x: auto; white-space: nowrap; border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- DỮ LIỆU ĐỊNH NGHĨA CỐ ĐỊNH ---
BO_MAP = {
    "00": [0, 5, 50, 55], "01": [1, 10, 6, 60, 51, 15, 56, 65], "02": [2, 20, 7, 70, 52, 25, 57, 75],
    "03": [3, 30, 8, 80, 53, 35, 58, 85], "04": [4, 40, 9, 90, 54, 45, 59, 95], "11": [11, 16, 61, 66],
    "12": [12, 21, 17, 71, 62, 26, 67, 76], "13": [13, 31, 18, 81, 63, 36, 68, 86], "14": [14, 41, 19, 91, 64, 46, 69, 96],
    "22": [22, 27, 72, 77], "23": [23, 32, 28, 82, 73, 37, 78, 87], "24": [24, 42, 29, 92, 74, 47, 79, 97],
    "33": [33, 38, 83, 88], "34": [34, 43, 39, 93, 84, 48, 89, 98], "44": [44, 49, 94, 99]
}
CON_GIAP_MAP = {
    "Tý": [0, 12, 24, 36, 48, 60, 72, 84, 96], "Sửu": [1, 13, 25, 37, 49, 61, 73, 85, 97],
    "Dần": [2, 14, 26, 38, 50, 62, 74, 86, 98], "Mão": [3, 15, 27, 39, 51, 63, 75, 87, 99],
    "Thìn": [4, 16, 28, 40, 52, 64, 76, 88], "Tỵ": [5, 17, 29, 41, 53, 65, 77, 89],
    "Ngọ": [6, 18, 30, 42, 54, 66, 78, 90], "Mùi": [7, 19, 31, 43, 55, 67, 79, 91],
    "Thân": [8, 20, 32, 44, 56, 68, 80, 92], "Dậu": [9, 21, 33, 45, 57, 69, 81, 93],
    "Tuất": [10, 22, 34, 46, 58, 70, 82, 94], "Hợi": [11, 23, 35, 47, 59, 71, 83, 95]
}

def get_mapping_index(val, mapping):
    for idx, (name, lst) in enumerate(mapping.items()):
        if val in lst: return idx
    return -1

def get_chan_le_idx(n):
    d, du = n // 10, n % 10
    if d % 2 == 0 and du % 2 == 0: return 0 # Chẵn Chẵn
    if d % 2 == 0 and du % 2 != 0: return 1 # Chẵn Lẻ
    if d % 2 != 0 and du % 2 != 0: return 2 # Lẻ Lẻ
    return 3 # Lẻ Chẵn

def get_be_to_idx(n):
    d, du = n // 10, n % 10
    if d <= 4 and du <= 4: return 0 # Bé Bé
    if d <= 4 and du >= 5: return 1 # Bé To
    if d >= 5 and du <= 4: return 2 # To Bé
    return 3 # To To

# --- KHỞI TẠO STATE ---
keys_10 = ['dau', 'duoi', 'tong', 'hieu', 'cham']
if 'dau' not in st.session_state:
    for k in keys_10: st.session_state[k] = [0] * 10
    st.session_state['bo'] = [0] * 15
    st.session_state['chanle'] = [0] * 4
    st.session_state['beto'] = [0] * 4
    st.session_state['giap'] = [0] * 12
    st.session_state.lich_su_full = []
    st.session_state.cloud_db = {}
    st.session_state.da_kich_hoat_pt = False

# --- HÀM XỬ LÝ ---
def cap_nhat_logic():
    n = st.session_state.so_moi_ve
    # Xác định các chỉ số của số vừa về
    d_v, du_v = n // 10, n % 10
    t_v, h_v = (d_v + du_v) % 10, (d_v - du_v + 10) % 10
    bo_v = get_mapping_index(n, BO_MAP)
    cl_v = get_chan_le_idx(n)
    bt_v = get_be_to_idx(n)
    gp_v = get_mapping_index(n, CON_GIAP_MAP)

    # 1. Tính hạng (Backtest)
    h_list = []
    for i in range(100):
        d, du = i // 10, i % 10
        score = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
                st.session_state.hieu[(d-du+10)%10] + \
                ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
                st.session_state.bo[get_mapping_index(i, BO_MAP)] + \
                st.session_state.chanle[get_chan_le_idx(i)] + \
                st.session_state.beto[get_be_to_idx(i)] + \
                st.session_state.giap[get_mapping_index(i, CON_GIAP_MAP)]
        h_list.append({"So": f"{d}{du}", "Diem": score})
    
    df_rank = pd.DataFrame(h_list).sort_values(by=["Diem", "So"]).reset_index(drop=True)
    vi_tri = df_rank[df_rank['So'] == f"{n:02d}"].index[0] + 1
    diem_ve = df_rank[df_rank['So'] == f"{n:02d}"].iloc[0]['Diem']

    # 2. Cập nhật điểm
    for i in range(10):
        st.session_state.dau[i] = 0 if i == d_v else st.session_state.dau[i] + 1
        st.session_state.duoi[i] = 0 if i == du_v else st.session_state.duoi[i] + 1
        st.session_state.tong[i] = 0 if i == t_v else st.session_state.tong[i] + 1
        st.session_state.hieu[i] = 0 if i == h_v else st.session_state.hieu[i] + 1
        if i == d_v or i == du_v: st.session_state.cham[i] = 0
        else: st.session_state.cham[i] += 1
    
    for i in range(15): st.session_state.bo[i] = 0 if i == bo_v else st.session_state.bo[i] + 1
    for i in range(4): 
        st.session_state.chanle[i] = 0 if i == cl_v else st.session_state.chanle[i] + 1
        st.session_state.beto[i] = 0 if i == bt_v else st.session_state.beto[i] + 1
    for i in range(12): st.session_state.giap[i] = 0 if i == gp_v else st.session_state.giap[i] + 1

    st.session_state.lich_su_full.insert(0, {"Số": f"{n:02d}", "Hạng": vi_tri, "Điểm": diem_ve})

# --- GIAO DIỆN ---
st.markdown("<h2 class='main-title'>💎 SIÊU APP SOI CẦU 9 BIẾN</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.header("☁️ CLOUD")
    if st.button("💾 LƯU DỮ LIỆU"):
        now = datetime.now().strftime("%H:%M:%S")
        st.session_state.cloud_db[now] = {k: list(st.session_state[k]) for k in ['dau','duoi','tong','hieu','cham','bo','chanle','beto','giap']}
        st.session_state.cloud_db[now]['ls'] = list(st.session_state.lich_su_full)
        st.toast("Đã lưu!")
    if st.session_state.cloud_db:
        sel = st.selectbox("Bản lưu:", list(st.session_state.cloud_db.keys())[::-1])
        if st.button("🔄 NẠP"):
            d = st.session_state.cloud_db[sel]
            for k in ['dau','duoi','tong','hieu','cham','bo','chanle','beto','giap']: st.session_state[k] = d[k]
            st.session_state.lich_su_full = d['ls']
            st.rerun()
    if st.button("🗑️ RESET"): st.session_state.clear(); st.rerun()

c1, c2, c3 = st.columns([2, 1, 1])
with c1: st.number_input("Số về:", 0, 99, step=1, format="%02d", key="so_moi_ve")
with c2: st.write("##"); st.button("CẬP NHẬT", on_click=cap_nhat_logic, type="primary")

st.divider()
t1, t2, t3, t4 = st.tabs(["⚡ Lọc Dàn", "📊 Bảng A", "🔢 Ma Trận B", "🛠️ Sửa Tay"])

with t1:
    l100 = []
    for i in range(100):
        d, du = i // 10, i % 10
        s = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
            st.session_state.hieu[(d-du+10)%10] + \
            ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
            st.session_state.bo[get_mapping_index(i, BO_MAP)] + \
            st.session_state.chanle[get_chan_le_idx(i)] + \
            st.session_state.beto[get_be_to_idx(i)] + \
            st.session_state.giap[get_mapping_index(i, CON_GIAP_MAP)]
        l100.append({"Số": f"{d}{du}", "Điểm": s})
    df_s = pd.DataFrame(l100).sort_values(by=["Điểm", "Số"])
    st.success(", ".join(df_s.head(10)["Số"].tolist()))
    st.info(", ".join(df_s.head(36)["Số"].tolist()))

with t2:
    for lbl, k, cols in [("ĐẦU", "dau", 10), ("ĐUÔI", "duoi", 10), ("TỔNG", "tong", 10), ("HIỆU", "hieu", 10), ("CHẠM", "cham", 10), 
                        ("BỘ", "bo", 15), ("CHẴN LẺ", "chanle", 4), ("BÉ TO", "beto", 4), ("12 GIÁP", "giap", 12)]:
        st.write(f"**{lbl}**")
        st.table(pd.DataFrame([st.session_state[k]], columns=[(list(BO_MAP.keys())[i] if k=='bo' else list(CON_GIAP_MAP.keys())[i] if k=='giap' else i) for i in range(cols)], index=[""]))

with t3:
    m = []
    for d in range(10):
        r = []
        for du in range(10):
            i = d*10 + du
            val = st.session_state.dau[d] + st.session_state.duoi[du] + st.session_state.tong[(d+du)%10] + \
                  st.session_state.hieu[(d-du+10)%10] + \
                  ((st.session_state.cham[d]*2) if d==du else (st.session_state.cham[d]+st.session_state.cham[du])) + \
                  st.session_state.bo[get_mapping_index(i, BO_MAP)] + \
                  st.session_state.chanle[get_chan_le_idx(i)] + \
                  st.session_state.beto[get_be_to_idx(i)] + \
                  st.session_state.giap[get_mapping_index(i, CON_GIAP_MAP)]
            r.append(val)
        m.append(r)
    st.dataframe(pd.DataFrame(m, columns=[str(i) for i in range(10)], index=[str(i) for i in range(10)]), use_container_width=True)

with t4:
    if st.button("💾 LƯU SỬA TAY"):
        for k in ['dau','duoi','tong','hieu','cham','bo','chanle','beto','giap']:
            for i in range(len(st.session_state[k])): st.session_state[k][i] = st.session_state[f"edit_{k}_{i}"]
        st.rerun()
    for k, lbl in [('dau','Đầu'),('duoi','Đuôi'),('tong','Tổng'),('hieu','Hiệu'),('cham','Chạm'),('bo','Bộ'),('chanle','Chẵn Lẻ'),('beto','Bé To'),('giap','12 Giáp')]:
        st.write(f"Sửa {lbl}")
        cols = st.columns(len(st.session_state[k]))
        for i in range(len(st.session_state[k])):
            with cols[i]: st.number_input(f"{i}", value=st.session_state[k][i], key=f"edit_{k}_{i}", label_visibility="collapsed")

st.divider()
if not st.session_state.da_kich_hoat_pt:
    if st.button("🚀 BẮT ĐẦU PHÂN TÍCH"): st.session_state.da_kich_hoat_pt = True; st.rerun()
else:
    if st.button("⏹️ TẮT PHÂN TÍCH"): st.session_state.da_kich_hoat_pt = False; st.rerun()
    if st.session_state.lich_su_full:
        rks = [x["Hạng"] for x in st.session_state.lich_su_full]
        gs = [sum(1 for r in rks if 1<=r<=10), sum(1 for r in rks if 11<=r<=39), sum(1 for r in rks if 40<=r<=59), sum(1 for r in rks if 60<=r<=75), sum(1 for r in rks if 76<=r<=100)]
        st.table(pd.DataFrame({"Nhóm": ["1-10","11-39","40-59","60-75","76-100"], "Số lần": gs, "Tỷ lệ": [f"{(x/len(rks))*100:.1f}%" for x in gs]}))
        st.line_chart(pd.DataFrame(st.session_state.lich_su_full[::-1])['Hạng'])
        st.markdown('<div class="history-container">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.lich_su_full).T)
        st.markdown('</div>', unsafe_allow_html=True)