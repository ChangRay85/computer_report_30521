import itertools
import copy

import streamlit as st

def get_key():
    init("stp_keys", itertools.count())
    return next(st.session_state["stp_keys"])

def init(key, value, mutable=False):
    if key not in st.session_state:
        st.session_state[key] = [value] if mutable else value

def widget_sync(widget_func, value_mutable=None, move_func=None, **karg):
    if value_mutable is None:
        if widget_func(**karg):
            if move_func is not None:
                move_func()
            st.rerun()
    else:
        if value_mutable[0] != widget_func(**karg):
            value_mutable[0] = st.session_state[karg["key"]]
            if move_func is not None:
                move_func()
            st.rerun()

def layout(ratio, func, **karg):
    with st.columns(ratio)[1]:
        func(**karg)

def layout2(i):
    for _ in range(i):
        st.write("")
