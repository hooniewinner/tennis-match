import streamlit as st
import random

# 웹 페이지 설정
st.set_page_config(page_title="테니스 매칭 앱", layout="centered")

# 디자인
st.title("🎾 테니스 복식 팀 생성")
st.write("developed by hooniewinner") 

# 1. 인원 설정
st.header("1. 인원 설정")
num = st.number_input("참석 인원수를 입력하세요", min_value=4, value=8, step=1)
members = [chr(65 + i) for i in range(num)]
st.info(f"선수 명단: {', '.join(members)}")

# --- 데이터 저장소 ---
if 'bad_pairs' not in st.session_state: st.session_state.bad_pairs = []
if 'must_pairs' not in st.session_state: st.session_state.must_pairs = []
if 'counts' not in st.session_state:
    st.session_state.counts = {m: 0 for m in members}
else:
    for m in members:
        if m not in st.session_state.counts: st.session_state.counts[m] = 0

# 2. 페어 설정 (너비를 맞추기 위해 레이아웃 수정)
st.header("2. 팀 밸런스 설정")

# 위쪽 선택 박스 2개를 1:1 비율로 배치
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    p1 = st.selectbox("선수 1", members, key="p1_select")
with col_sel2:
    p2 = st.selectbox("선수 2", members, key="p2_select")

pair = tuple(sorted((p1, p2)))

# 아래쪽 버튼 2개를 1:1 비율로 배치하고 너비를 꽉 채움
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("❌ 페어 불가", use_container_width=True):
        if p1 != p2 and pair not in st.session_state.bad_pairs:
            if pair in st.session_state.must_pairs: st.session_state.must_pairs.remove(pair)
            st.session_state.bad_pairs.append(pair)
        elif p1 == p2: st.error("같은 사람을 고를 수 없습니다.")
with col_btn2:
    if st.button("🤝 무조건 페어", use_container_width=True):
        if p1 != p2 and pair not in st.session_state.must_pairs:
            if pair in st.session_state.bad_pairs: st.session_state.bad_pairs.remove(pair)
            st.session_state.must_pairs.append(pair)
        elif p1 == p2: st.error("같은 사람을 고를 수 없습니다.")

# 설정 목록 표시 (삭제 버튼들도 보기 좋게 정렬)
st.markdown("---")
col_list1, col_list2 = st.columns(2)
with col_list1:
    st.subheader("🚫 페어 불가 목록")
    for i, p in enumerate(st.session_state.bad_pairs):
        if st.button(f"🚫 {p[0]}-{p[1]}", key=f"del_b_{i}", use_container_width=True):
            st.session_state.bad_pairs.pop(i); st.rerun()
with col_list2:
    st.subheader("🤝 무조건 페어 목록")
    for i, p in enumerate(st.session_state.must_pairs):
        if st.button(f"🤝 {p[0]}-{p[1]}", key=f"del_m_{i}", use_container_width=True):
            st.session_state.must_pairs.pop(i); st.rerun()

# 3. 경기 생성 로직
st.divider()
if st.button("🏁 다음 경기 무작위 생성", type="primary", use_container_width=True):
    success = False
    for _ in range(2000): 
        others_sorted = sorted(members, key=lambda x: (st.session_state.counts[x], random.random()))
        selected_players = others_sorted[:4]
        
        valid_selection = True
        for mp in st.session_state.must_pairs:
            p_in = [p for p in mp if p in selected_players]
            if len(p_in) == 1:
                valid_selection = False; break
        
        if not valid_selection: continue

        candidates = selected_players[:]
        random.shuffle(candidates)
        t1 = tuple(sorted((candidates[0], candidates[1])))
        t2 = tuple(sorted((candidates[2], candidates[3])))
        
        is_bad = t1 in st.session_state.bad_pairs or t2 in st.session_state.bad_pairs
        
        must_ok = True
        for mp in st.session_state.must_pairs:
            if mp[0] in selected_players and mp[1] in selected_players:
                if not ((mp[0] in t1 and mp[1] in t1) or (mp[0] in t2 and mp[1] in t2)):
                    must_ok = False; break
        
        if not is_bad and must_ok:
            for p in selected_players: st.session_state.counts[p] += 1
            st.success(f"매칭 완료! 🔥")
            mc1, mc2 = st.columns(2)
            mc1.metric("TEAM 1", f"{t1[0]} & {t1[1]}")
            mc2.metric("TEAM 2", f"{t2[0]} & {t2[1]}")
            success = True; break
            
    if not success:
        st.error("조건이 너무 까다로워 공평한 명단을 짤 수 없습니다. 설정을 조정해주세요.")

with st.expander("📊 선수별 누적 경기 참여 횟수 보기"):
    st.table([st.session_state.counts])