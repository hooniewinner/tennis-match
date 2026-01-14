import streamlit as st
import random

# 웹 페이지 설정
st.set_page_config(page_title="테니스 매칭 앱", layout="centered")

# 디자인
st.title("🎾 테니스 복식 팀 생성기")
st.write("developed by hooniewinner") 

# 1. 인원 및 코트 설정
st.header("1. 모임 설정")
col_setting1, col_setting2 = st.columns(2)
with col_setting1:
    num = st.number_input("참석 인원수", min_value=4, value=8, step=1)
with col_setting2:
    court_num = st.number_input("사용 코트 수", min_value=1, value=1, step=1)

members = [chr(65 + i) for i in range(num)]
st.info(f"선수 명단: {', '.join(members)}")

# 최대 가능 코트 수 계산
max_courts = num // 4
current_courts = min(court_num, max_courts)

# --- 데이터 저장소 ---
if 'bad_pairs' not in st.session_state: st.session_state.bad_pairs = []
if 'must_pairs' not in st.session_state: st.session_state.must_pairs = []
if 'counts' not in st.session_state:
    st.session_state.counts = {m: 0 for m in members}
else:
    for m in members:
        if m not in st.session_state.counts: st.session_state.counts[m] = 0

# 2. 페어 설정
st.header("2. 팀 밸런스 설정")
col_sel1, col_sel2 = st.columns(2)
with col_sel1: p1 = st.selectbox("선수 1", members, key="p1_select")
with col_sel2: p2 = st.selectbox("선수 2", members, key="p2_select")

pair = tuple(sorted((p1, p2)))
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("❌ 페어 불가", use_container_width=True):
        if p1 != p2 and pair not in st.session_state.bad_pairs:
            if pair in st.session_state.must_pairs: st.session_state.must_pairs.remove(pair)
            st.session_state.bad_pairs.append(pair)
with col_btn2:
    if st.button("🤝 무조건 페어", use_container_width=True):
        if p1 != p2 and pair not in st.session_state.must_pairs:
            if pair in st.session_state.bad_pairs: st.session_state.bad_pairs.remove(pair)
            st.session_state.must_pairs.append(pair)

# 설정 목록
st.markdown("---")
col_list1, col_list2 = st.columns(2)
with col_list1:
    st.subheader("🚫 페어 불가")
    for i, p in enumerate(st.session_state.bad_pairs):
        if st.button(f"🚫 {p[0]}-{p[1]}", key=f"del_b_{i}", use_container_width=True):
            st.session_state.bad_pairs.pop(i); st.rerun()
with col_list2:
    st.subheader("🤝 무조건 페어")
    for i, p in enumerate(st.session_state.must_pairs):
        if st.button(f"🤝 {p[0]}-{p[1]}", key=f"del_m_{i}", use_container_width=True):
            st.session_state.must_pairs.pop(i); st.rerun()

# 3. 경기 생성 및 대기자 로직
st.divider()
if st.button("🏁 다치지 말고 화이팅", type="primary", use_container_width=True):
    temp_counts = st.session_state.counts.copy()
    all_matches = []
    used_in_round = set()
    
    success_all_courts = True
    for c in range(int(current_courts)):
        success_this_court = False
        available = [m for m in members if m not in used_in_round]
        
        for _ in range(2000):
            # 경기수 적은 사람 우선 추출
            candidates = sorted(available, key=lambda x: (temp_counts[x], random.random()))[:4]
            if len(candidates) < 4: break
            
            # 규칙 체크
            valid_sel = True
            for mp in st.session_state.must_pairs:
                p_in = [p for p in mp if p in candidates]
                if len(p_in) == 1: valid_sel = False; break
            if not valid_sel: continue
            
            random.shuffle(candidates)
            t1, t2 = tuple(sorted(candidates[:2])), tuple(sorted(candidates[2:]))
            
            is_bad = t1 in st.session_state.bad_pairs or t2 in st.session_state.bad_pairs
            must_ok = True
            for mp in st.session_state.must_pairs:
                if mp[0] in candidates and mp[1] in candidates:
                    if not ((mp[0] in t1 and mp[1] in t1) or (mp[0] in t2 and mp[1] in t2)):
                        must_ok = False; break
            
            if not is_bad and must_ok:
                all_matches.append((t1, t2))
                used_in_round.update(candidates)
                for p in candidates: temp_counts[p] += 1
                success_this_court = True; break
        
        if not success_this_court:
            success_all_courts = False; break

    if success_all_courts:
        st.session_state.counts = temp_counts
        # 1. 코트별 매칭 표시
        for i, m in enumerate(all_matches):
            st.success(f"🎾 {i+1} 코트 매칭")
            mc1, mc2 = st.columns(2)
            mc1.metric("TEAM 1", f"{m[0][0]} & {m[0][1]}")
            mc2.metric("TEAM 2", f"{m[1][0]} & {m[1][1]}")
        
        # 2. 대기자 명단 표시 (중요!)
        waiting_players = [m for m in members if m not in used_in_round]
        if waiting_players:
            st.divider()
            st.subheader("⏳ 몸 푸세요")
            # 대기자들을 보기 좋게 쉼표로 나열
            st.warning(f"대기 명단: {', '.join(waiting_players)}")
    else:
        st.error("조건을 만족하는 매칭을 찾지 못했습니다. 설정을 조정해 주세요.")

with st.expander("📊 선수별 누적 경기 참여 횟수 보기"):
    st.table([st.session_state.counts])