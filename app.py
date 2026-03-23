import streamlit as st
import pandas as pd
import os
from pymatgen.io.vasp import Poscar

# =========================
# 页面设置
# =========================
st.set_page_config(page_title="二维晶体数据库", layout="wide")
st.title("二维无机晶体数据库")

# =========================
# 加载 CSV 数据
# =========================
@st.cache_data
def load_data():
    # 第一列 index 作为索引
    df = pd.read_csv('data.csv', index_col=0)
    return df

df = load_data()

# =========================
# 侧边栏功能选择
# =========================
page = st.sidebar.radio("功能", ["📊 浏览数据", "🔍 查看VASP", "📥 下载数据"])

# =========================
# 页面 1: 浏览数据
# =========================
if page == "📊 浏览数据":
    st.subheader("数据表")
    
    # 搜索框
    search = st.text_input("搜索化学式或其他列:")
    if search:
        # 转成字符串，忽略 NaN
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    else:
        df_display = df
    
    st.dataframe(df_display, use_container_width=True)
    st.write(f"共 {len(df_display)} 条数据")

# =========================
# 页面 2: 查看 VASP
# =========================
elif page == "🔍 查看VASP":
    st.subheader("查看 VASP 结构")
    
    # 下拉框显示 "索引 | 化学式"
    options = [f"{idx} | {df.loc[idx, 'formula']}" for idx in df.index]
    selected_display = st.selectbox("选择结构:", options)
    
    if selected_display:
        selected_idx = int(selected_display.split('|')[0].strip())
        formula = df.loc[selected_idx, 'formula']
        
        # 构建 VASP 文件路径
        vasp_path = f"vasp_files/{selected_idx}.vasp"
        
        if os.path.exists(vasp_path):
            # 读取结构
            structure = Poscar.from_file(vasp_path).structure
            st.write(f"### {formula} (索引 {selected_idx})")
            st.write("晶胞参数:")
            st.write(structure.lattice)
            st.write("原子位置:")
            st.write(structure)
        else:
            st.warning("对应 VASP 文件不存在！")

# =========================
# 页面 3: 下载数据
# =========================
elif page == "📥 下载数据":
    st.subheader("下载数据 / VASP 文件")
    
    # 下载 CSV 数据
    csv_bytes = df.to_csv().encode('utf-8')
    st.download_button("下载 CSV 数据", data=csv_bytes, file_name="data.csv", mime="text/csv")
    
    # 下载单个 VASP 文件
    selected_idx = st.selectbox("选择 VASP 文件下载（索引）:", df.index)
    vasp_path = f"vasp_files/{selected_idx}.vasp"
    
    if os.path.exists(vasp_path):
        with open(vasp_path, "rb") as f:
            vasp_bytes = f.read()
        st.download_button(f"下载 VASP 文件 ({selected_idx}.vasp)", data=vasp_bytes, file_name=f"{selected_idx}.vasp")
    else:
        st.warning("对应 VASP 文件不存在！")
