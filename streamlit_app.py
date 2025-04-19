import copy
import json
import numpy as np
import sympy as sp
import pandas as pd
import plotly.express as px

import streamlit as st

import streamlit_plus as stp
import concave_lens_focus
from concave_lens_focus import get_p_q_f

 # 層級：
 # experients
 #  -> experient = objects (+answer)
 #  -> object = values = coordinate
 #  -> value

 # Set 一維資料 iterable, subscriptable
 # Objects, Coordinate, Value各繼承Set
class Set:
    def __init__(self, keys, values=None):
        self.keys, self.dict_ = keys, {}

        if values is None:
            for key in keys:
                self.dict_[key] = None

        elif len(keys) == len(values):
            for key, value in zip(keys, values):
                self.dict_[key] = value

    def __iter__(self):
        return iter(self.dict_[key] for key in self.keys)

    def __setitem__(self, i, value):
        if isinstance(i, int):
            if 0 <= i < len(self.keys):
                self.dict_[self.keys[i]] = value
                return

        self.dict_[i] = value

    def __getitem__(self, i):
        if isinstance(i, slice):
            return list(self.dict_[key] for key in self.keys[i])
        else:
            if isinstance(i, int):
                if 0 <= i < len(self.keys):
                    return self.dict_[self.keys[i]]
        return self.dict_[i]

objects_keys = ["鏡", "後針", "前針1", "前針2"]
objects_lens = [3, 2, 2, 2]
coordinate_keys = ["x", "y", "orientation"]

class Objects(Set):
    def __init__(self):
        super().__init__(objects_keys, [Coordinate(True), Coordinate(), Coordinate(), Coordinate()])

class Coordinate(Set):
    def __init__(self, have_orientation=False):
        if have_orientation:
            super().__init__(coordinate_keys, [Value(), Value(), Value()])

        else:
            super().__init__(coordinate_keys[:2], [Value(), Value()])

class Value(Set):
    def __init__(self, value=0):
        super().__init__([""], [value])

class P_Q_F(Set):
    def __init__(self, values=[0, 0, 0]):
        super().__init__(['p', 'q', 'f'], values)

def objects_to_p_q_f(func, objects):
    mirror_coordinate = np.array(list(value[0] for value in objects[0][:2]))
    mirror_axis_orientation = objects[0][2][0]
    back_pin = np.array(list(value[0] for value in objects[1]))
    front_pin_1 = np.array(list(value[0] for value in objects[2]))
    front_pin_2 = np.array(list(value[0] for value in objects[3]))
    ans = func(mirror_coordinate, mirror_axis_orientation/180*np.pi, back_pin, front_pin_1, front_pin_2)
    if ans is None:
        p = q = f = None
    else:
        p, q, f = ans
    return P_Q_F([p, q, f])

stp.init("experients", [])

 # 標題
st.markdown("# 插針法求凹透鏡焦距計算機")
st.markdown("#### 註：")
stp.layout([1, 50, 1], st.markdown, body="##### \t數據：二維座標")
stp.layout2(5)

p_values, q_values, f_values = [], [], []

for experient in st.session_state["experients"]:
    p, q, f = experient["p_q_f"]['p'], experient["p_q_f"]['q'], experient["p_q_f"]['f']
    if all(val is not None for val in [p, q, f]):
        p_values.append(p)
        q_values.append(q)
        f_values.append(f)

data = {
    'p': p_values,
    'q': q_values,
    'f': f_values,
}

if data['p']:
    df = pd.DataFrame(data)

    # 四分位圖
    st.markdown("#### p, q, f 四分位圖")
    fig = px.box(df, points="all")
    st.plotly_chart(fig, use_container_width=True)

    # 平均值與標準差
    stats = {
        '平均值': df.mean(),
        '標準差': df.std()
    }
    stat_df = pd.DataFrame(stats).T  # 轉置為列為 avg/std
    st.markdown("#### 平均值 / 標準差")
    st.dataframe(stat_df.style.format("{:.4f}"))
    stp.layout2(5)

 # write: legal/total button: 手動輸入, 全部刪除
for i, column in enumerate(st.columns([2.11, 0.46, 0.43])):
    with column:
        if i == 0:
            legal = sum(st.session_state["experients"][i_objects][p_q_f_key]['f'] is not None 
                for i_objects, (objects_key, p_q_f_key) in enumerate(st.session_state["experients"]))
            total = len(st.session_state["experients"])
            st.markdown(f"##### legal/total: {legal}/{total}")
        if i == 1:
            if st.button("新增一組", key=f"plus_1_{i_objects}"):
                st.session_state["experients"].append({"object": Objects(), "p_q_f": objects_to_p_q_f(get_p_q_f, Objects())})
                st.rerun()
        if i == 2:
            if st.button("全部刪除", key=f"delete_{i_objects}"):
                st.session_state["experients"] = []
                st.rerun()

 # 每experient排版：
 # xyo
 # xy
 # xy
 # xy
 # 複製 刪除
for i_objects, (objects_key, p_q_f_key) in enumerate(st.session_state["experients"]):
    st.markdown(f"### 第{i_objects+1}組")
    for i_coordinate, coordinate in enumerate(st.session_state["experients"][i_objects][objects_key]):
        st.markdown(f"#### {objects_keys[i_coordinate]}")
        for i_value, (value, column) in enumerate(zip(coordinate, st.columns(3))):
            with column:
                def move_func():
                    st.session_state["experients"][i_objects][p_q_f_key] = objects_to_p_q_f(get_p_q_f, st.session_state["experients"][i_objects][objects_key])

                stp.widget_sync(st.number_input, value, 
                    label=coordinate_keys[i_value], 
                    move_func=move_func,
                    value=float(value[0]), 
                    key=f"{i_objects}{objects_keys[i_coordinate]}{coordinate_keys[i_value]}", 
                    step = 0.01
                )
    stp.layout2(1)
    for i, column in enumerate(st.columns([1.14, 1.14, 1.14, 0.79, 0.79])):
        p_q_f = st.session_state["experients"][i_objects][p_q_f_key]
        with column:
            if i == 0:
                if p_q_f['p'] is None:
                    st.markdown(f"##### p = None")
                else:
                    st.markdown(f"##### p = {p_q_f['p']:.4f}")
            if i == 1:
                if p_q_f['q'] is None:
                    st.markdown(f"##### q = None")
                else:
                    st.markdown(f"##### q = {p_q_f['q']:.4f}")
            if i == 2:
                if p_q_f['f'] is None:
                    st.markdown(f"##### f = None")
                else:
                    st.markdown(f"##### f = {p_q_f['f']:.4f}")
            if i == 3:
                if st.button(f"複製第{i_objects+1}組"):
                    st.session_state["experients"].insert(i_objects, copy.deepcopy(st.session_state["experients"][i_objects]))
                    st.rerun()
            if i == 4:
                if st.button(f"刪除第{i_objects+1}組"):
                    del st.session_state["experients"][i_objects]
                    st.rerun()
    stp.layout2(3)
