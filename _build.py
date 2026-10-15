# -*- coding: utf-8 -*-
"""Build index.html from _data.py + _img/_urls.json"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import _data

urls = json.load(open(os.path.join(HERE, '_img', '_urls.json'), encoding='utf-8'))

groups = []
for g in _data.GROUPS:
    chars = []
    for c, p, m in g['chars']:
        chars.append({"c": c, "p": p, "m": m, "img": urls.get(c, "")})
    groups.append({"name": g['name'], "chars": chars})

data_json = json.dumps(groups, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="描紅練習">
<meta name="theme-color" content="#fdf6ec">
<title>中文描紅練習 · 口訣版</title>
<style>
  :root{
    --ink:#2b2b2b;
    --red:#e74c3c;
    --paper:#fdf6ec;
    --accent:#3b82f6;
    --gold:#f5a623;
  }
  *{box-sizing:border-box; -webkit-tap-highlight-color:transparent;}
  html,body{margin:0; padding:0; background:var(--paper); font-family:"PingFang TC","Noto Sans TC",sans-serif; color:#2b2b2b;}
  body{display:flex; flex-direction:column; align-items:center; min-height:100vh; padding:12px 12px 28px;}
  header{width:100%; max-width:640px; text-align:center; margin-bottom:8px;}
  header h1{font-size:22px; margin:4px 0 2px;}
  header .sub{font-size:14px; color:#888;}
  .catBar{display:flex; flex-wrap:wrap; gap:8px; justify-content:center; padding:4px 2px; width:100%; max-width:640px;}
  .catChip{flex:0 0 auto; border:none; border-radius:20px; padding:8px 14px; font-size:15px; background:#fff; color:#555; border:1px solid #e5e5e5; box-shadow:none; cursor:pointer;}
  .catChip.active{background:var(--accent); color:#fff; border-color:var(--accent); font-weight:700;}
  .charGrid{display:grid; grid-template-columns:repeat(auto-fill,minmax(46px,1fr)); gap:7px; width:100%; max-width:640px; max-height:150px; overflow-y:auto; padding:8px; background:#fff; border-radius:12px; border:1px solid #eee; margin:8px 0 10px; -webkit-overflow-scrolling:touch;}
  .charBtn{aspect-ratio:1/1; border:1px solid #eee; border-radius:10px; background:#fff; font-size:24px; color:#2b2b2b; font-family:"Kaiti TC","TW-Kai","STKaiti","KaiTi","DFKai-SB","Noto Serif TC",serif; padding:0; box-shadow:none; display:flex; align-items:center; justify-content:center; cursor:pointer;}
  .charBtn.active{background:#ffe9e6; border:2px solid var(--red); color:var(--red); font-weight:700;}
  .stage{position:relative; width:100%; max-width:640px; aspect-ratio:1/1; touch-action:none; user-select:none; -webkit-user-select:none;}
  canvas{position:absolute; inset:0; width:100%; height:100%; border-radius:12px;}
  #gridCanvas{z-index:1;}
  #inkCanvas{z-index:2;}
  .pinyin{font-size:15px; color:#b0483c; margin-top:6px; text-align:center;}

  .strokeCard{width:100%; max-width:640px; background:#fff; border:1px solid #eee; border-radius:16px; padding:12px 14px; margin-top:12px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,.05);}
  .strokeHead{display:flex; align-items:center; justify-content:center; gap:8px; margin-bottom:4px;}
  .strokeLabel{background:var(--accent); color:#fff; font-size:13px; font-weight:700; border-radius:999px; padding:3px 12px;}
  .miniBtn{border:none; background:#eef2ff; color:#2b5bd6; border-radius:999px; padding:6px 12px; font-size:14px; cursor:pointer; font-family:inherit;}
  .strokeTarget{width:min(300px,86%); margin:6px auto 0;}
  .strokeTarget svg{width:100%; height:auto; display:block;}
  .strokeControls{display:flex; align-items:center; justify-content:center; gap:8px; margin-top:8px;}
  .strokeCounter{font-size:13px; color:#888;}
  .strokeLoading{font-size:14px; color:#999; padding:20px 0;}
  .strokeErr{font-size:14px; color:#999; padding:20px 0;}

  .mnemonicCard{width:100%; max-width:640px; background:#fff; border:1px solid #eee; border-radius:16px; padding:12px 14px; margin-top:12px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,.05);}
  .mnemonicHead{display:flex; align-items:center; justify-content:center; gap:8px; margin-bottom:6px;}
  .mnemonicLabel{background:var(--gold); color:#fff; font-size:13px; font-weight:700; border-radius:999px; padding:3px 12px;}
  .speakMini{border:none; background:#fff3e0; color:#b06a00; border-radius:999px; padding:6px 12px; font-size:14px; cursor:pointer; font-family:inherit;}
  .mnemonic{font-size:16px; line-height:1.6; color:#333; min-height:24px;}
  .imgWrap{width:min(300px,74%); margin:10px auto 0; border-radius:20px; overflow:hidden; box-shadow:0 6px 16px rgba(0,0,0,.1); background:#f7f7f7; border:1px solid #eee;}
  .imgWrap img{width:100%; display:block; aspect-ratio:1/1; object-fit:cover; animation:float 3.2s ease-in-out infinite;}
  .imgWrap.pop img{animation:pop .5s cubic-bezier(.34,1.56,.64,1);}
  @keyframes pop{0%{transform:scale(.72);opacity:.35}60%{transform:scale(1.06)}100%{transform:scale(1);opacity:1}}
  @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}

  .toolbar{display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:14px; width:100%; max-width:640px;}
  button{border:none; border-radius:14px; padding:12px 18px; font-size:16px; font-family:inherit; cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,.08);}
  .btn-primary{background:var(--accent); color:#fff; font-weight:700;}
  .btn-gold{background:var(--gold); color:#fff; font-weight:700;}
  .btn-red{background:var(--red); color:#fff;}
  .btn-ghost{background:#fff; color:#444; border:1px solid #e5e5e5;}
  .score{width:100%; max-width:640px; text-align:center; margin-top:12px; font-size:17px; min-height:24px; font-weight:600;}
  .score.good{color:#16a34a;} .score.mid{color:#e67e22;} .score.low{color:var(--red);}
  .sectionTitle{width:100%; max-width:640px; text-align:center; margin-top:26px; font-size:19px; font-weight:700; color:var(--ink);}
  .sectionTitle .badge{background:#eef2ff; color:var(--accent); border-radius:999px; padding:4px 14px;}
  .dictHint{width:100%; max-width:640px; text-align:center; font-size:14px; color:#888; margin-top:4px;}
  #dictGridCanvas{z-index:1;}
  #dictInkCanvas{z-index:2;}
  .rewardBar{width:100%; max-width:640px; background:#fff; border:1px solid #eee; border-radius:16px; padding:10px 14px; margin-top:10px; box-shadow:0 2px 10px rgba(0,0,0,.05);}
  .rewardBar .row{display:flex; align-items:center; justify-content:space-between; gap:8px;}
  .rewardBar .label{font-size:13px; color:#666; font-weight:700;}
  .rewardBar .pts{font-size:14px; color:#2b2b2b;}
  .rewardBar .pts strong{font-size:18px; color:var(--accent);}
  .rewardTrack{height:10px; background:#f0ece5; border-radius:999px; overflow:hidden; margin-top:8px;}
  .rewardFill{height:100%; background:linear-gradient(90deg,#f5a623,#e74c3c); width:0%; transition:width .3s;}
  .rewardBar .draws{font-size:13px; color:#888;}
  .cardOverlay{position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index:50; padding:16px;}
  .cardPanel{background:#fff; border-radius:20px; padding:20px; max-width:340px; width:100%; text-align:center; position:relative; box-shadow:0 10px 40px rgba(0,0,0,.25);}
  .cardClose{position:absolute; top:8px; right:12px; border:none; background:none; font-size:22px; color:#999; cursor:pointer; padding:0 4px; box-shadow:none;}
  .cardTitle{font-size:20px; font-weight:800; margin:0 0 4px;}
  .cardSub{font-size:13px; color:#888; margin:0 0 14px;}
  .cardFace{width:180px; height:210px; margin:0 auto 14px; border-radius:16px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; background:#faf6ee; border:2px solid #eee;}
  .cardFace.s5{background:#fff3d6; border-color:#f5a623;}
  .cardFace.s4{background:#fdeef6; border-color:#e67ecf;}
  .cardFace.s3{background:#eaf3ff; border-color:#6aa9f0;}
  .cardFace.s2{background:#eefaf0; border-color:#6fce8a;}
  .cardFace.s1{background:#f7f7f7; border-color:#ccc;}
  .cardEmoji{font-size:72px; line-height:1;}
  .cardName{font-size:17px; font-weight:700; color:#2b2b2b;}
  .cardRarity{font-size:14px; color:#f5a623; letter-spacing:2px;}
  .cardBackMark{font-size:80px; color:#c9bda6; font-weight:800; line-height:1;}
  .cardActions{display:flex; gap:8px; justify-content:center;}
  .footer{width:100%; max-width:640px; text-align:center; margin-top:14px; font-size:12px; color:#aaa;}
</style>
</head>
<body>
<header>
  <h1>中文描紅練習 · 口訣版</h1>
  <div class="sub" id="progress">初小常用正體字 · 口訣 + 粵拼 + 插圖</div>
</header>

<div class="rewardBar">
  <div class="row">
    <span class="label">今日得分</span>
    <span class="pts"><strong id="rewardPoints">0</strong> / 200 分</span>
  </div>
  <div class="rewardTrack"><div class="rewardFill" id="rewardFill" style="width:0%"></div></div>
  <div class="row" style="margin-top:8px;">
    <span class="draws">可抽卡：<strong id="rewardDraws">0</strong> 次</span>
    <button class="btn-primary" id="rewardDrawBtn" disabled>抽卡</button>
  </div>
</div>

<div class="catBar" id="catBar"></div>
<div class="charGrid" id="charGrid"></div>

<div class="toolbar">
  <button class="btn-ghost" id="prevBtn">上一個</button>
  <button class="btn-ghost" id="nextBtn">下一個</button>
</div>

<div class="sectionTitle"><span class="badge">① 筆順（先看）</span></div>
<div class="strokeCard" id="strokeCard">
  <div class="strokeTarget" id="strokeTarget"></div>
  <div class="strokeControls">
    <button class="miniBtn" id="strokePlay">播放</button>
    <button class="miniBtn" id="strokeReplay">重播</button>
    <span class="strokeCounter" id="strokeCounter">已寫 0 / 0 筆</span>
  </div>
</div>

<div class="sectionTitle"><span class="badge">② 口訣、讀音</span></div>
<div class="mnemonicCard" id="mnemonicCard">
  <div class="mnemonicHead">
    <span class="mnemonicLabel">口訣</span>
    <button class="speakMini" id="mnemonicMini">聽口訣</button>
    <button class="speakMini" id="speakBtn">讀音</button>
  </div>
  <div class="pinyin" id="pinyin">粵拼：jat1</div>
  <div class="mnemonic" id="mnemonic">人字一撇一捺，企直似人；軟腳蟹就唔似人。</div>
  <div class="imgWrap" id="imgWrap">
    <img id="charImg" alt="口訣插圖">
  </div>
</div>

<div class="sectionTitle"><span class="badge">③ 跟字練寫</span></div>
<div class="stage">
  <canvas id="gridCanvas"></canvas>
  <canvas id="inkCanvas"></canvas>
</div>
<div class="toolbar">
  <button class="btn-red" id="clearBtn">清除</button>
  <button class="btn-primary" id="checkBtn">檢查</button>
</div>
<div class="score" id="score"></div>

<div class="sectionTitle"><span class="badge">④ 默書</span></div>
<div class="dictHint">唔顯示範字，憑記憶寫返個字出嚟</div>
<div class="stage">
  <canvas id="dictGridCanvas"></canvas>
  <canvas id="dictInkCanvas"></canvas>
</div>
<div class="toolbar">
  <button class="btn-red" id="dictClearBtn">清除</button>
  <button class="btn-primary" id="dictCheckBtn">檢查</button>
</div>
<div class="score" id="dictScore"></div>

<div class="cardOverlay" id="cardOverlay" style="display:none">
  <div class="cardPanel">
    <button class="cardClose" id="cardClose" aria-label="關閉">✕</button>
    <p class="cardTitle">抽卡遊戲</p>
    <p class="cardSub" id="cardSub">可抽卡：0 次・已收藏 0 / 16 種</p>
    <div class="cardFace" id="cardFace">
      <span class="cardBackMark">?</span>
    </div>
    <div class="cardActions">
      <button class="btn-primary" id="cardDrawBtn">抽一張卡</button>
      <button class="btn-ghost" id="cardCloseBtn">關閉</button>
    </div>
  </div>
</div>

<div class="footer">粵語語音依賴裝置內建語音（iOS 對粵語支援有限）· 插圖由 AI 生成</div>

<script>
(function(){
  const GROUPS = __DATA__;

  const SIZE = 720;
  const FONT = 'bold 430px "Kaiti TC","TW-Kai","STKaiti","KaiTi","DFKai-SB","Noto Serif TC","PingFang TC",serif';
  const PEN = '#2b2b2b';
  const PEN_WIDTH = 22;
  let catIdx = 0;
  let charIdx = 0;
  let templateMask = null;

  const curList = () => GROUPS[catIdx].chars;
  const curChar = () => curList()[charIdx];

  const gridCanvas = document.getElementById('gridCanvas');
  const inkCanvas = document.getElementById('inkCanvas');
  gridCanvas.width = SIZE; gridCanvas.height = SIZE;
  inkCanvas.width = SIZE; inkCanvas.height = SIZE;
  const gctx = gridCanvas.getContext('2d');
  const ictx = inkCanvas.getContext('2d');
  const charImg = document.getElementById('charImg');
  const imgWrap = document.getElementById('imgWrap');
  const dictGridCanvas = document.getElementById('dictGridCanvas');
  const dictInkCanvas = document.getElementById('dictInkCanvas');
  dictGridCanvas.width = SIZE; dictGridCanvas.height = SIZE;
  dictInkCanvas.width = SIZE; dictInkCanvas.height = SIZE;
  const dgctx = dictGridCanvas.getContext('2d');
  const dictIctx = dictInkCanvas.getContext('2d');

  function drawGridOn(ctx){
    ctx.clearRect(0,0,SIZE,SIZE);
    ctx.fillStyle = '#fff'; ctx.fillRect(0,0,SIZE,SIZE);
    const m = 46;
    ctx.strokeStyle = '#e74c3c'; ctx.lineWidth = 5;
    ctx.strokeRect(m,m,SIZE-2*m,SIZE-2*m);
    ctx.strokeStyle = 'rgba(231,76,60,0.42)'; ctx.lineWidth = 2;
    ctx.setLineDash([10,9]);
    ctx.beginPath();
    ctx.moveTo(m,SIZE/2); ctx.lineTo(SIZE-m,SIZE/2);
    ctx.moveTo(SIZE/2,m); ctx.lineTo(SIZE/2,SIZE-m);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  function drawGrid(){ drawGridOn(gctx); }

  function drawDictGrid(){ drawGridOn(dgctx); }

  function drawTemplate(){
    drawGrid();
    gctx.font = FONT;
    gctx.textAlign = 'center'; gctx.textBaseline = 'middle';
    gctx.fillStyle = 'rgba(231,76,60,0.30)';
    gctx.fillText(curChar().c, SIZE/2, SIZE/2 + SIZE*0.015);
  }

  function buildTemplateMask(){
    const off = document.createElement('canvas');
    off.width = SIZE; off.height = SIZE;
    const c = off.getContext('2d');
    c.font = FONT; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = '#000';
    c.fillText(curChar().c, SIZE/2, SIZE/2 + SIZE*0.015);
    const d = c.getImageData(0,0,SIZE,SIZE).data;
    const mask = new Uint8Array(SIZE*SIZE);
    for(let i=0;i<SIZE*SIZE;i++){ if(d[i*4+3]>40) mask[i]=1; }
    return mask;
  }

  function renderChips(){
    const bar = document.getElementById('catBar');
    bar.innerHTML = '';
    GROUPS.forEach(function(cat,i){
      const b = document.createElement('button');
      b.className = 'catChip' + (i===catIdx ? ' active' : '');
      b.textContent = cat.name;
      b.onclick = function(){ loadChar(i, 0); };
      bar.appendChild(b);
    });
  }

  function renderGrid(){
    const grid = document.getElementById('charGrid');
    grid.innerHTML = '';
    curList().forEach(function(ch, ci){
      const b = document.createElement('button');
      b.className = 'charBtn' + (ci===charIdx ? ' active' : '');
      b.textContent = ch.c;
      b.onclick = function(){ loadChar(catIdx, ci); };
      grid.appendChild(b);
    });
  }

  let strokeDataPromise = null;
  let strokeTimer = null;
  let strokePlaying = false;
  let strokeIndex = 0;
  let strokeInfo = null;

  function getStrokeData(){
    if(!strokeDataPromise){
      strokeDataPromise = fetch('data/strokeData.json').then(function(r){
        if(!r.ok){ throw new Error('stroke data load failed'); }
        return r.json();
      });
    }
    return strokeDataPromise;
  }

  function setPlayBtn(label){
    const btn = document.getElementById('strokePlay');
    if(btn){ btn.textContent = label; }
  }

  function stopStrokeTimer(){
    if(strokeTimer){ clearInterval(strokeTimer); strokeTimer = null; }
    strokePlaying = false;
    setPlayBtn('播放');
  }

  function updateStrokeFrame(){
    if(!strokeInfo) return;
    const total = strokeInfo.strokes.length;
    const paths = document.querySelectorAll('#strokeTarget .s-path');
    for(let i=0;i<paths.length;i++){
      if(i < strokeIndex){
        paths[i].setAttribute('visibility','visible');
        paths[i].setAttribute('fill', (strokePlaying && i === strokeIndex-1) ? '#e74c3c' : '#2b2b2b');
      }else{
        paths[i].setAttribute('visibility','hidden');
      }
    }
    const marker = document.querySelector('#strokeTarget .s-marker');
    if(marker){
      if(strokeIndex < total && strokeInfo.starts && strokeInfo.starts[strokeIndex]){
        marker.setAttribute('visibility','visible');
        marker.setAttribute('cx', strokeInfo.starts[strokeIndex][0]);
        marker.setAttribute('cy', strokeInfo.starts[strokeIndex][1]);
      }else{
        marker.setAttribute('visibility','hidden');
      }
    }
    const counter = document.getElementById('strokeCounter');
    if(counter){ counter.textContent = '已寫 ' + Math.min(strokeIndex, total) + ' / ' + total + ' 筆'; }
  }

  function startStroke(){
    if(!strokeInfo) return;
    stopStrokeTimer();
    strokeIndex = 0;
    strokePlaying = true;
    setPlayBtn('暫停');
    updateStrokeFrame();
    strokeTimer = setInterval(function(){
      if(!strokeInfo){ stopStrokeTimer(); return; }
      if(strokeIndex >= strokeInfo.strokes.length){
        stopStrokeTimer();
        return;
      }
      strokeIndex++;
      updateStrokeFrame();
    }, 1680);
  }

  function pauseStroke(){
    stopStrokeTimer();
    updateStrokeFrame();
  }

  function toggleStrokePlay(){
    if(strokePlaying){ pauseStroke(); }
    else { startStroke(); }
  }

  function renderStroke(ch){
    stopStrokeTimer();
    strokeInfo = null;
    const target = document.getElementById('strokeTarget');
    const counter = document.getElementById('strokeCounter');
    target.innerHTML = '<div class="strokeLoading">筆順載入中…</div>';
    if(counter){ counter.textContent = '已寫 0 / 0 筆'; }
    getStrokeData().then(function(data){
      const info = data[ch];
      if(!info || !info.strokes || !info.strokes.length){
        target.innerHTML = '<div class="strokeErr">此字暫無筆順資料</div>';
        return;
      }
      strokeInfo = info;
      let pathsHtml = '';
      for(let i=0;i<info.strokes.length;i++){
        pathsHtml += '<path class="s-path" d="' + info.strokes[i] + '" fill="#2b2b2b" visibility="hidden"></path>';
      }
      target.innerHTML =
        '<svg viewBox="0 0 1024 1024" class="stroke-svg" role="img" aria-label="' + ch + '的筆順示範">' +
          '<g class="s-grid" aria-hidden="true">' +
            '<rect x="46" y="46" width="932" height="932" fill="#ffffff" stroke="#e74c3c" stroke-width="5"/>' +
            '<line x1="46" y1="341.3" x2="978" y2="341.3" stroke="rgba(231,76,60,0.42)" stroke-width="2"/>' +
            '<line x1="46" y1="682.7" x2="978" y2="682.7" stroke="rgba(231,76,60,0.42)" stroke-width="2"/>' +
            '<line x1="341.3" y1="46" x2="341.3" y2="978" stroke="rgba(231,76,60,0.42)" stroke-width="2"/>' +
            '<line x1="682.7" y1="46" x2="682.7" y2="978" stroke="rgba(231,76,60,0.42)" stroke-width="2"/>' +
          '</g>' +
          '<g class="s-flip" transform="translate(0,900) scale(1,-1)">' +
            pathsHtml +
            '<circle class="s-marker" r="16" fill="#e74c3c" visibility="hidden"></circle>' +
          '</g>' +
        '</svg>';
      startStroke();
    }).catch(function(){
      target.innerHTML = '<div class="strokeErr">筆順資料載入失敗</div>';
    });
  }

  function loadChar(cat, ci){
    catIdx = (cat + GROUPS.length) % GROUPS.length;
    const list = curList();
    charIdx = (ci + list.length) % list.length;
    const ch = curChar();
    ictx.clearRect(0,0,SIZE,SIZE);
    dictIctx.clearRect(0,0,SIZE,SIZE);
    writeScored = false;
    dictScored = false;
    drawDictGrid();
    templateMask = buildTemplateMask();
    drawTemplate();
    document.getElementById('progress').textContent = '「' + GROUPS[catIdx].name + '」第 ' + (charIdx+1) + ' / ' + list.length + ' 個字';
    document.getElementById('pinyin').textContent = '粵拼：' + ch.p;
    document.getElementById('mnemonic').textContent = ch.m;
    charImg.onerror = function(){ this.style.display='none'; };
    charImg.style.display = '';
    charImg.src = ch.img || '';
    renderStroke(ch.c);
    const el = document.getElementById('score');
    el.textContent = ''; el.className = 'score';
    const dEl = document.getElementById('dictScore');
    dEl.textContent = ''; dEl.className = 'score';
    renderChips();
    renderGrid();
  }

  function getPos(e){
    const r = inkCanvas.getBoundingClientRect();
    return { x:(e.clientX-r.left)*SIZE/r.width, y:(e.clientY-r.top)*SIZE/r.height };
  }

  let drawing = false, last = null;
  inkCanvas.addEventListener('pointerdown', function(e){
    e.preventDefault();
    drawing = true; last = getPos(e);
    ictx.fillStyle = PEN;
    ictx.beginPath(); ictx.arc(last.x,last.y,PEN_WIDTH/2,0,Math.PI*2); ictx.fill();
    if(inkCanvas.setPointerCapture) inkCanvas.setPointerCapture(e.pointerId);
  });
  inkCanvas.addEventListener('pointermove', function(e){
    if(!drawing) return;
    e.preventDefault();
    const p = getPos(e);
    ictx.strokeStyle = PEN; ictx.lineWidth = PEN_WIDTH;
    ictx.lineCap = 'round'; ictx.lineJoin = 'round';
    ictx.beginPath(); ictx.moveTo(last.x,last.y); ictx.lineTo(p.x,p.y); ictx.stroke();
    last = p;
  });
  function stopDraw(){ drawing = false; last = null; }
  inkCanvas.addEventListener('pointerup', stopDraw);
  inkCanvas.addEventListener('pointercancel', stopDraw);

  function getDictPos(e){
    const r = dictInkCanvas.getBoundingClientRect();
    return { x:(e.clientX-r.left)*SIZE/r.width, y:(e.clientY-r.top)*SIZE/r.height };
  }
  let dictDrawing = false, dictLast = null;
  dictInkCanvas.addEventListener('pointerdown', function(e){
    e.preventDefault();
    dictDrawing = true; dictLast = getDictPos(e);
    dictIctx.fillStyle = PEN;
    dictIctx.beginPath(); dictIctx.arc(dictLast.x, dictLast.y, PEN_WIDTH/2, 0, Math.PI*2); dictIctx.fill();
    if(dictInkCanvas.setPointerCapture) dictInkCanvas.setPointerCapture(e.pointerId);
  });
  dictInkCanvas.addEventListener('pointermove', function(e){
    if(!dictDrawing) return;
    e.preventDefault();
    const p = getDictPos(e);
    dictIctx.strokeStyle = PEN; dictIctx.lineWidth = PEN_WIDTH;
    dictIctx.lineCap = 'round'; dictIctx.lineJoin = 'round';
    dictIctx.beginPath(); dictIctx.moveTo(dictLast.x, dictLast.y); dictIctx.lineTo(p.x, p.y); dictIctx.stroke();
    dictLast = p;
  });
  function stopDictDraw(){ dictDrawing = false; dictLast = null; }
  dictInkCanvas.addEventListener('pointerup', stopDictDraw);
  dictInkCanvas.addEventListener('pointercancel', stopDictDraw);

  function dilate(mask, r){
    const out = new Uint8Array(SIZE*SIZE);
    for(let y=0;y<SIZE;y++){
      const row = y*SIZE;
      for(let x=0;x<SIZE;x++){
        if(!mask[row+x]) continue;
        const y0 = Math.max(0,y-r), y1 = Math.min(SIZE-1,y+r);
        const x0 = Math.max(0,x-r), x1 = Math.min(SIZE-1,x+r);
        for(let yy=y0;yy<=y1;yy++){
          const orow = yy*SIZE;
          for(let xx=x0;xx<=x1;xx++) out[orow+xx] = 1;
        }
      }
    }
    return out;
  }

  // ===== 獎勵系統：累積分數 + 抽卡 =====
  const REWARD_KEY = 'chinese_tracing_rewards_v1';
  const DRAW_POINTS = 200;
  const CARDS = [
    {id:'fire-dragon', name:'火焰龍', emoji:'🐉', stars:5},
    {id:'ice-unicorn', name:'冰晶獨角獸', emoji:'🦄', stars:4},
    {id:'storm-wolf', name:'雷風狼', emoji:'🐺', stars:4},
    {id:'forest-fox', name:'森林狐狸', emoji:'🦊', stars:3},
    {id:'thunder-eagle', name:'雷電鷹', emoji:'🦅', stars:3},
    {id:'ocean-turtle', name:'海洋龜', emoji:'🐢', stars:3},
    {id:'lava-tiger', name:'岩漿虎', emoji:'🐯', stars:2},
    {id:'moon-owl', name:'月光貓頭鷹', emoji:'🦉', stars:2},
    {id:'sun-butterfly', name:'太陽蝴蝶', emoji:'🦋', stars:2},
    {id:'wave-dolphin', name:'波浪海豚', emoji:'🐬', stars:2},
    {id:'bamboo-panda', name:'竹林熊貓', emoji:'🐼', stars:1},
    {id:'meadow-bee', name:'花田蜜蜂', emoji:'🐝', stars:1},
    {id:'pond-frog', name:'池塘青蛙', emoji:'🐸', stars:1},
    {id:'garden-rabbit', name:'花園兔子', emoji:'🐰', stars:1},
    {id:'desert-snake', name:'沙漠蛇', emoji:'🐍', stars:1},
    {id:'pearl-fish', name:'珍珠魚', emoji:'🐠', stars:1}
  ];
  const RARITY_WEIGHT = {1:40, 2:25, 3:15, 4:10, 5:5};

  function todayStr(){
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  }

  let reward = loadReward();
  function loadReward(){
    try{
      const raw = localStorage.getItem(REWARD_KEY);
      const t = raw ? JSON.parse(raw) : {};
      const r = {
        date: t.date || todayStr(),
        points: Number(t.points) || 0,
        draws: Number(t.draws) || 0,
        collection: Array.isArray(t.collection) ? t.collection : []
      };
      if(r.date !== todayStr()){ r.date = todayStr(); r.points = 0; }
      return r;
    }catch(e){ return {date: todayStr(), points: 0, draws: 0, collection: []}; }
  }

  function saveReward(){
    try{ localStorage.setItem(REWARD_KEY, JSON.stringify(reward)); }catch(e){}
  }

  function addPoints(pts){
    if(pts > 0){
      reward.points += pts;
      while(reward.points >= DRAW_POINTS){
        reward.draws += 1;
        reward.points -= DRAW_POINTS;
      }
    }
    saveReward();
    updateRewardBar();
  }

  function consumeDraw(){
    if(reward.draws <= 0) return false;
    reward.draws -= 1;
    saveReward();
    updateRewardBar();
    return true;
  }

  function collectCard(id){
    if(reward.collection.indexOf(id) < 0){
      reward.collection.push(id);
      saveReward();
    }
  }

  function pickCard(){
    const total = CARDS.reduce(function(s,c){ return s + (RARITY_WEIGHT[c.stars] || 10); }, 0);
    let r = Math.random() * total;
    for(let i=0;i<CARDS.length;i++){
      r -= (RARITY_WEIGHT[CARDS[i].stars] || 10);
      if(r <= 0) return CARDS[i];
    }
    return CARDS[0];
  }

  function starStr(n){ return '★'.repeat(n) + '☆'.repeat(5-n); }

  function updateRewardBar(){
    const ptsEl = document.getElementById('rewardPoints');
    const fillEl = document.getElementById('rewardFill');
    const drawsEl = document.getElementById('rewardDraws');
    const btnEl = document.getElementById('rewardDrawBtn');
    if(ptsEl){ ptsEl.textContent = reward.points; }
    if(fillEl){ fillEl.style.width = Math.min(100, Math.round(reward.points / DRAW_POINTS * 100)) + '%'; }
    if(drawsEl){ drawsEl.textContent = reward.draws; }
    if(btnEl){ btnEl.disabled = reward.draws <= 0; }
    const sub = document.getElementById('cardSub');
    if(sub){ sub.textContent = '可抽卡：' + reward.draws + ' 次・已收藏 ' + reward.collection.length + ' / ' + CARDS.length + ' 種'; }
  }

  function openCardDialog(){
    updateRewardBar();
    document.getElementById('cardOverlay').style.display = 'flex';
  }

  function closeCardDialog(){
    document.getElementById('cardOverlay').style.display = 'none';
  }

  function doDrawCard(){
    if(!consumeDraw()) return;
    const card = pickCard();
    collectCard(card.id);
    const face = document.getElementById('cardFace');
    face.className = 'cardFace s' + card.stars;
    face.innerHTML =
      '<span class="cardEmoji">' + card.emoji + '</span>' +
      '<span class="cardName">' + card.name + '</span>' +
      '<span class="cardRarity">' + starStr(card.stars) + '</span>';
    document.getElementById('cardDrawBtn').textContent = '再抽一次';
    document.getElementById('cardDrawBtn').disabled = reward.draws <= 0;
  }

  function speakText(text, rate){
    if(!('speechSynthesis' in window)){ alert('你的裝置不支援語音'); return; }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'zh-HK'; u.rate = (rate == null ? 0.85 : rate);
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  }

  function speak(){ speakText(curChar().c); }

  function playImage(){
    imgWrap.classList.remove('pop');
    void imgWrap.offsetWidth;
    imgWrap.classList.add('pop');
    setTimeout(function(){ imgWrap.classList.remove('pop'); }, 600);
  }

  function speakMnemonic(){
    speakText(curChar().m, 0.8);
    playImage();
  }

  function speakPraise(){
    speakText('波仔，叻仔，繼續努力！', 0.9);
  }

  function computeScore(ctx, mask){
    const d = ctx.getImageData(0,0,SIZE,SIZE).data;
    const ink = new Uint8Array(SIZE*SIZE);
    let inkCount = 0;
    for(let i=0;i<SIZE*SIZE;i++){ if(d[i*4+3]>40){ ink[i]=1; inkCount++; } }
    if(!inkCount) return null;

    const r = 14;
    const inkNear = dilate(ink, r);
    const tmpNear = dilate(mask, r);

    let tCount = 0, covered = 0, inkOn = 0;
    for(let i=0;i<SIZE*SIZE;i++){
      if(mask[i]){ tCount++; if(inkNear[i]) covered++; }
      if(ink[i] && tmpNear[i]) inkOn++;
    }
    const coverage = tCount ? covered/tCount : 0;
    const precision = inkCount ? inkOn/inkCount : 0;
    const score = Math.round((coverage*0.6 + precision*0.4)*100);
    return {score: score, coverage: coverage, precision: precision};
  }

  let writeScored = false;
  let dictScored = false;

  function doCheck(ctx, el, emptyMsg, done){
    const res = computeScore(ctx, templateMask);
    if(!res){ el.textContent = emptyMsg; el.className = 'score low'; return done; }
    const d10 = Math.round(res.score / 10);
    let msg;
    if(res.score>=90){ msg = '寫得好好！'; el.className = 'score good'; }
    else if(res.score>=70){ msg = '不錯，繼續加油！'; el.className = 'score good'; }
    else if(res.score>=50){ msg = '加油，再寫一次！'; el.className = 'score mid'; }
    else { msg = '再試一次，慢慢寫！'; el.className = 'score low'; }
    let tail = '得分 ' + d10 + ' / 10（覆蓋 ' + Math.round(res.coverage*100) + '% · 準確 ' + Math.round(res.precision*100) + '%）';
    if(!done && d10 > 0){ addPoints(d10); done = true; }
    else if(done){ tail += '・清除再寫可再加分'; }
    el.textContent = msg + ' ' + tail;
    if(res.score >= 70){ speakPraise(); }
    return done;
  }

  function check(){
    writeScored = doCheck(ictx, document.getElementById('score'), '還未寫字，先在格內描一描吧！', writeScored);
  }

  function checkDict(){
    dictScored = doCheck(dictIctx, document.getElementById('dictScore'), '還未默寫，先在格內寫字吧！', dictScored);
  }

  document.getElementById('prevBtn').onclick = function(){ loadChar(catIdx, charIdx-1); };
  document.getElementById('nextBtn').onclick = function(){ loadChar(catIdx, charIdx+1); };
  document.getElementById('clearBtn').onclick = function(){
    ictx.clearRect(0,0,SIZE,SIZE);
    writeScored = false;
    const el = document.getElementById('score');
    el.textContent = ''; el.className = 'score';
  };
  document.getElementById('checkBtn').onclick = check;
  document.getElementById('dictCheckBtn').onclick = checkDict;
  document.getElementById('dictClearBtn').onclick = function(){
    dictIctx.clearRect(0,0,SIZE,SIZE);
    dictScored = false;
    const el = document.getElementById('dictScore');
    el.textContent = ''; el.className = 'score';
  };
  document.getElementById('speakBtn').onclick = speak;
  document.getElementById('mnemonicMini').onclick = speakMnemonic;
  document.getElementById('strokePlay').onclick = toggleStrokePlay;
  document.getElementById('strokeReplay').onclick = startStroke;
  imgWrap.addEventListener('click', speakMnemonic);
  document.getElementById('rewardDrawBtn').onclick = openCardDialog;
  document.getElementById('cardDrawBtn').onclick = doDrawCard;
  document.getElementById('cardClose').onclick = closeCardDialog;
  document.getElementById('cardCloseBtn').onclick = closeCardDialog;
  updateRewardBar();

  loadChar(0, 0);
})();
</script>
</body>
</html>
"""

html = HTML.replace('__DATA__', data_json)

out = os.path.join(HERE, 'index.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

print('Wrote', out, len(html), 'chars')
print('Groups:', len(groups), '| Total entries:', sum(len(g['chars']) for g in groups))
