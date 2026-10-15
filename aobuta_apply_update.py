from pathlib import Path

p=Path('index.html')
for fname in ('icon-192.png','icon-512.png','icon.jpg'):
    if not Path(fname).is_file():
        raise RuntimeError(f'{fname} が見つかりません。ZIPを先に展開してください。')
s=p.read_text(encoding='utf-8')

def put(old,new):
    global s
    count=s.count(old)
    if count!=1:
        raise RuntimeError(f'更新対象の一致数が想定外: {count}; {old[:80]}')
    s=s.replace(old,new,1)

marker='<div class="info">高確・リラックス中は全設定共通：スイカ30.1%・チェリー50.0%・チャンス目85.2%。参考表示のみで設定推定には使用しません。</div>'
html='''<h3>アオハルCHANCE当選率：実戦カウント（通常状態のみ）</h3>
<div class="info">役が成立して非当選なら「非当選＋」、その役から当選なら「当選＋」を押してください。各1タップで成立回数も集計します。</div>
<div class="grid2">
  <div class="statbox">
    <div class="label">チェリー → アオハルCHANCE</div>
    <div class="value" id="roleCherryRate">—</div>
    <div class="compare" id="roleCherryCount">当選 0 / 成立 0</div>
    <div class="row pointBtns">
      <button class="btn secondary small" data-role="roleCherryMissV2" data-d="1">非当選＋</button>
      <button class="btn good small" data-role="roleCherryHitV2" data-d="1">当選＋</button>
      <button class="btn small" data-role="roleCherryMissV2" data-d="-1">非当選−</button>
      <button class="btn small" data-role="roleCherryHitV2" data-d="-1">当選−</button>
    </div>
  </div>
  <div class="statbox">
    <div class="label">チャンス目 → アオハルCHANCE</div>
    <div class="value" id="roleChanceRate">—</div>
    <div class="compare" id="roleChanceCount">当選 0 / 成立 0</div>
    <div class="row pointBtns">
      <button class="btn secondary small" data-role="roleChanceMissV2" data-d="1">非当選＋</button>
      <button class="btn good small" data-role="roleChanceHitV2" data-d="1">当選＋</button>
      <button class="btn small" data-role="roleChanceMissV2" data-d="-1">非当選−</button>
      <button class="btn small" data-role="roleChanceHitV2" data-d="-1">当選−</button>
    </div>
  </div>
</div>
<div class="toggle"><input type="checkbox" id="use_roleAoharuV2"><label for="use_roleAoharuV2">小役からのアオハルCHANCE当選率を設定推定に使う</label></div>
<div class="info" id="roleEstimateMode"></div>
<div class="notice warn" style="margin-top:8px">内部状態が通常と判断できる試行だけ入力してください。状態不明・高確・リラックス中、契機を特定できない当選は含めません。小役別の当選率を使うときは、重複計上防止のためアオハルCHANCE全体出現率を推定から外します。</div>
'''
put(marker,html+marker)
put('  bonus:0,aoharu:0,dreamCollection:0,','  bonus:0,aoharu:0,dreamCollection:0,\n  roleCherryHitV2:0,roleCherryMissV2:0,roleChanceHitV2:0,roleChanceMissV2:0,use_roleAoharuV2:true,')
put('function calc(){\n  const g=n(st.games), c=constraint();','function calc(){\n  const g=n(st.games), c=constraint();\n  const chTrials=n(st.roleCherryHitV2)+n(st.roleCherryMissV2);\n  const caTrials=n(st.roleChanceHitV2)+n(st.roleChanceMissV2);\n  const useRole=!!st.use_roleAoharuV2&&(chTrials+caTrials>0);')
put('    if(st.use_aoharu&&g>0)ll[s]+=pLL(n(st.aoharu),g,RATE.aoharu[s]);', '''    if(st.use_aoharu&&g>0&&!useRole)ll[s]+=pLL(n(st.aoharu),g,RATE.aoharu[s]);
    if(useRole){
      if(chTrials)ll[s]+=bLL(n(st.roleCherryHitV2),chTrials,RATE.cherryAoharu[s]);
      if(caTrials)ll[s]+=bLL(n(st.roleChanceHitV2),caTrials,RATE.chanceAoharu[s]);
    }''')
put('  document.getElementById("pt300Txt").textContent=', '''  const cherryTrials=n(st.roleCherryHitV2)+n(st.roleCherryMissV2);
  const chanceTrials=n(st.roleChanceHitV2)+n(st.roleChanceMissV2);
  document.getElementById("roleCherryRate").textContent=ratio(n(st.roleCherryHitV2),cherryTrials);
  document.getElementById("roleChanceRate").textContent=ratio(n(st.roleChanceHitV2),chanceTrials);
  document.getElementById("roleCherryCount").textContent=`当選 ${n(st.roleCherryHitV2)} / 成立 ${cherryTrials}`;
  document.getElementById("roleChanceCount").textContent=`当選 ${n(st.roleChanceHitV2)} / 成立 ${chanceTrials}`;
  document.getElementById("use_roleAoharuV2").checked=!!st.use_roleAoharuV2;
  const useRole=!!st.use_roleAoharuV2&&(cherryTrials+chanceTrials>0);
  document.getElementById("roleEstimateMode").textContent=useRole
    ? "役別の当選率を設定推定に使用中（アオハル全体出現率は除外）"
    : "役別当選率は設定推定に未使用（全体出現率は従来の設定に従います）";
  document.getElementById("pt300Txt").textContent=''')
put('    const any=g>0||c.min>2||n(st.pt400trial)>0;', '    const any=g>0||c.min>2||n(st.pt400trial)>0||useRole;')
put('      st.use_aoharu&&g>0,', '      st.use_aoharu&&g>0&&!useRole,\n      useRole,')
put('document.addEventListener("click",e=>{\n  const b=e.target.closest("[data-count]");', '''document.addEventListener("click",e=>{
  const r=e.target.closest("[data-role]");
  if(r){
    const k=r.dataset.role, d=Number(r.dataset.d);
    if(["roleCherryHitV2","roleCherryMissV2","roleChanceHitV2","roleChanceMissV2"].includes(k)){
      st[k]=n(st[k]+d);save();render();return;
    }
  }
  const b=e.target.closest("[data-count]");''')
put('document.getElementById("setting1Confirmed").addEventListener("change",e=>{', '''document.getElementById("use_roleAoharuV2").addEventListener("change",e=>{
  st.use_roleAoharuV2=e.target.checked;save();render();
});
document.getElementById("setting1Confirmed").addEventListener("change",e=>{''')

q=Path('sw.js')
t=q.read_text(encoding='utf-8')
old='aobuta-setting-pro-v8-public'
if t.count(old)!=1:raise RuntimeError('sw.jsのキャッシュ名が想定と異なります')
t=t.replace(old,'aobuta-setting-pro-v9-role-count-icon',1)
# Install-time cache should include the favicon as well.
if "  './icon.jpg'," not in t:
    t=t.replace("  './icon-512.png'", "  './icon-512.png',\n  './icon.jpg'")

p.write_text(s,encoding='utf-8')
q.write_text(t,encoding='utf-8')
print('PATCH_OK: 小役当選率の入力・推定処理、キャッシュ更新が完了')
