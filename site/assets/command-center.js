
(function(){
  const fmt = new Intl.NumberFormat("en-US");
  const money = v => {
    const n = Number(v || 0);
    if (!Number.isFinite(n) || n === 0) return "—";
    if (Math.abs(n) >= 1e12) return "$" + (n/1e12).toFixed(2) + "T";
    if (Math.abs(n) >= 1e9) return "$" + (n/1e9).toFixed(2) + "B";
    if (Math.abs(n) >= 1e6) return "$" + (n/1e6).toFixed(2) + "M";
    return "$" + fmt.format(Math.round(n));
  };
  const pct = v => (v === undefined || v === null || v === "") ? "—" : Number(v).toFixed(1).replace(".0","") + "%";
  const safe = s => String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const color = i => ["#7dffb0","#86f8ff","#ffd66b","#d8a7ff","#9da8ff","#ffb86c"][i%6];

  async function loadStatus(){
    try{
      const res = await fetch("public_site_status.json?ts=" + Date.now());
      if(!res.ok) throw new Error("status fetch failed");
      return await res.json();
    }catch(e){
      console.warn(e);
      return null;
    }
  }

  function chartShell(el, title, note, svg){
    el.innerHTML = `<div class="chart-title">${safe(title)}</div>${svg}<div class="chart-note">${safe(note || "")}</div>`;
  }

  function barChart(el, title, rows, note){
    const w=760, h=Math.max(220, 58*rows.length+50), left=220, right=40;
    const max=Math.max(1, ...rows.map(r=>Number(r.value)||0));
    const bars=rows.map((r,i)=>{
      const y=42+i*52, bw=(w-left-right)*(Number(r.value)||0)/max;
      return `<text x="14" y="${y+24}" fill="#b3c0cd" font-size="14">${safe(r.label)}</text>
      <rect x="${left}" y="${y+6}" width="${w-left-right}" height="28" fill="rgba(255,255,255,.06)" rx="8"/>
      <rect x="${left}" y="${y+6}" width="${bw}" height="28" fill="${color(i)}" rx="8"/>
      <text x="${Math.min(left+bw+10,w-85)}" y="${y+25}" fill="#f4fbff" font-size="13" font-weight="700">${safe(r.display ?? r.value)}</text>`;
    }).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 ${w} ${h}" role="img"><rect width="${w}" height="${h}" fill="transparent"/>${bars}</svg>`);
  }

  function polar(cx,cy,r,deg){ const a=(deg-90)*Math.PI/180; return {x:cx+r*Math.cos(a), y:cy+r*Math.sin(a)}; }

  function donutChart(el, title, rows, note){
    const total = rows.reduce((a,r)=>a+(Number(r.value)||0),0) || 1;
    let start=0; const cx=160, cy=142, r=90, sw=28;
    const arcs=rows.map((row,i)=>{
      const val=(Number(row.value)||0)/total; const end=start+val*360; const large=end-start>180?1:0;
      const p1=polar(cx,cy,r,start), p2=polar(cx,cy,r,end);
      const dash=`<path d="M ${p1.x} ${p1.y} A ${r} ${r} 0 ${large} 1 ${p2.x} ${p2.y}" fill="none" stroke="${color(i)}" stroke-width="${sw}" stroke-linecap="round"/>`;
      start=end; return dash;
    }).join("");
    const legend=rows.map((row,i)=>`<g transform="translate(320 ${70+i*30})"><rect width="12" height="12" rx="3" fill="${color(i)}"/><text x="20" y="11" fill="#b3c0cd" font-size="13">${safe(row.label)}: ${safe(row.display ?? row.value)}</text></g>`).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 760 300" role="img"><circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="${sw}"/>${arcs}<text x="${cx}" y="${cy-2}" text-anchor="middle" fill="#f4fbff" font-size="28" font-weight="900">${total}</text><text x="${cx}" y="${cy+24}" text-anchor="middle" fill="#b3c0cd" font-size="12">total</text>${legend}</svg>`);
  }

  function lineChart(el, title, vals, note){
    const w=760,h=300,left=48,bottom=250,top=36,right=28;
    const max=Math.max(100,...vals), min=0;
    const pts=vals.map((v,i)=>({x:left+i*((w-left-right)/Math.max(1,vals.length-1)), y:bottom-((v-min)/(max-min))*(bottom-top), v}));
    const poly=pts.map(p=>`${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
    const circles=pts.map((p,i)=>`<circle cx="${p.x}" cy="${p.y}" r="5" fill="#7dffb0"/><text x="${p.x}" y="276" text-anchor="middle" fill="#b3c0cd" font-size="11">v${i}</text>`).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 ${w} ${h}" role="img"><line x1="${left}" y1="${bottom}" x2="${w-right}" y2="${bottom}" stroke="rgba(255,255,255,.18)"/><line x1="${left}" y1="${top}" x2="${left}" y2="${bottom}" stroke="rgba(255,255,255,.18)"/><polyline points="${poly}" fill="none" stroke="#7dffb0" stroke-width="4"/><path d="M ${poly.replaceAll(" "," L ")} L ${pts[pts.length-1]?.x||left} ${bottom} L ${left} ${bottom} Z" fill="rgba(125,255,176,.08)"/>${circles}</svg>`);
  }

  function radarChart(el, title, rows, note){
    const cx=380,cy=170,r=120,n=rows.length||1;
    const points=rows.map((row,i)=>{ const a=-Math.PI/2+i*2*Math.PI/n; const val=Math.max(0,Math.min(100,Number(row.value)||0))/100; return {x:cx+r*val*Math.cos(a),y:cy+r*val*Math.sin(a), lx:cx+(r+32)*Math.cos(a), ly:cy+(r+32)*Math.sin(a), label:row.label}; });
    const rings=[.25,.5,.75,1].map(fr=>{ const p=rows.map((_,i)=>{const a=-Math.PI/2+i*2*Math.PI/n;return `${cx+r*fr*Math.cos(a)},${cy+r*fr*Math.sin(a)}`}).join(" "); return `<polygon points="${p}" fill="none" stroke="rgba(255,255,255,.11)"/>`; }).join("");
    const poly=points.map(p=>`${p.x},${p.y}`).join(" ");
    const axes=points.map(p=>`<line x1="${cx}" y1="${cy}" x2="${p.lx}" y2="${p.ly}" stroke="rgba(255,255,255,.08)"/><text x="${p.lx}" y="${p.ly}" text-anchor="middle" fill="#b3c0cd" font-size="11">${safe(p.label)}</text>`).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 760 360" role="img">${rings}${axes}<polygon points="${poly}" fill="rgba(134,248,255,.18)" stroke="#86f8ff" stroke-width="3"/><circle cx="${cx}" cy="${cy}" r="3" fill="#fff"/></svg>`);
  }

  function constellation(el, title, roles, note){
    const w=760,h=520,cx=380,cy=260;
    const list=(roles&&roles.length?roles:["capital allocator","compute allocator","energy strategist","data moat","trust","talent","product","distribution","validation","risk","reinvestment","coordination"]);
    const nodes=list.slice(0,80).map((role,i)=>{ const ring=i<24?120:i<52?178:226; const idx=i<24?i:i<52?i-24:i-52; const count=i<24?24:i<52?28:28; const a=-Math.PI/2+idx*2*Math.PI/count+(i<24?0:i<52?.13:.27); const x=cx+ring*Math.cos(a), y=cy+ring*Math.sin(a); return `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="rgba(134,248,255,.08)"/><circle cx="${x}" cy="${y}" r="${i<24?6:5}" fill="${color(i)}"/><title>${safe(role)}</title>`; }).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 ${w} ${h}" role="img"><circle cx="${cx}" cy="${cy}" r="70" fill="rgba(125,255,176,.11)" stroke="#7dffb0"/><text x="${cx}" y="${cy-6}" text-anchor="middle" fill="#f4fbff" font-size="18" font-weight="900">SkillOS</text><text x="${cx}" y="${cy+18}" text-anchor="middle" fill="#b3c0cd" font-size="12">coordination core</text>${nodes}</svg>`);
  }

  function render(status){
    const flagship=status.flagship_raw||{};
    const final=flagship.final||{};
    const single=flagship.single_agent_baseline||{};
    const uncoord=flagship.uncoordinated_pool||{};
    const stat=flagship.static_coordination||{};
    const agentSystem=flagship.agent_system||status.flagship||{};
    const releases=(flagship.rsi_releases||[]).filter(r=>r.released || r.generation===0);
    document.querySelectorAll("[data-live-count]").forEach(el=>{ const key=el.getAttribute("data-live-count"); el.textContent = status[key] ?? "—"; });
    document.querySelectorAll("[data-chart]").forEach(el=>{
      const type=el.getAttribute("data-chart");
      if(type==="proof-status"){ const passed=(status.proved_or_passed_proof_count||0), total=(status.proof_count||0); donutChart(el,"Proof status",[{label:"passed or ready",value:passed},{label:"other entries",value:Math.max(0,total-passed)}],"Autonomously rebuilt from proof JSON, pages, reports, and workflow metadata."); }
      if(type==="workflow-status"){ const rows=status.workflows||[]; const counts={passing:0,running:0,failed:0,other:0}; rows.forEach(w=>{const l=(w.conclusion==="success")?"passing":(["queued","in_progress","requested","waiting"].includes(w.status)?"running":(w.conclusion==="failure"?"failed":"other"));counts[l]++;}); donutChart(el,"Workflow status",Object.entries(counts).map(([k,v])=>({label:k,value:v})),"Latest visible GitHub Actions state."); }
      if(type==="rsi-curve"){ const vals=releases.map(r=>(r.validation||{}).fully_correct_percent ?? 0); lineChart(el,"Recursive self-improvement curve", vals.length?vals:[0,25,50,75,100],"Validation fully-correct rate across released protocol versions."); }
      if(type==="ablation-bars"){ barChart(el,"Ablation: single agent vs pool vs coordination vs RSI",[
        {label:"Single agent", value:single.fully_correct_percent||0, display:pct(single.fully_correct_percent)},
        {label:"Uncoordinated pool", value:uncoord.fully_correct_percent||0, display:pct(uncoord.fully_correct_percent)},
        {label:"Static coordination", value:stat.fully_correct_percent||0, display:pct(stat.fully_correct_percent)},
        {label:"SkillOS RSI", value:final.fully_correct_percent||0, display:pct(final.fully_correct_percent)},
      ],"Shows whether recursive coordination beats both single-agent and uncoordinated multi-agent baselines."); }
      if(type==="capability-radar"){ radarChart(el,"Capability coordination radar",[
        {label:"Coordination", value:final.coordination_protocol_accuracy_percent||0},
        {label:"Risk control", value:final.risk_control_accuracy_percent||0},
        {label:"Role quorum", value:final.role_quorum_accuracy_percent||0},
        {label:"Capability lever", value:final.capability_lever_accuracy_percent||0},
        {label:"Value capture", value:final.value_capture_rate_percent||0},
        {label:"Compounding", value:final.avg_compounding_index||0},
        {label:"Capacity", value:final.avg_productive_capacity_index||0},
      ],"The flagship proof measures coordination quality, risk discipline, compounding, and productive capacity."); }
      if(type==="agent-constellation"){ constellation(el,"Specialist agent organization", (agentSystem.roles||status.flagship.roles||[]), "Visualizes the specialist roles coordinated by the flagship proof."); }
      if(type==="value-bars"){ barChart(el,"Business effect metrics",[
        {label:"Value capture", value:final.value_capture_rate_percent||0, display:pct(final.value_capture_rate_percent)},
        {label:"Compounding index", value:final.avg_compounding_index||0},
        {label:"Productive capacity", value:final.avg_productive_capacity_index||0},
        {label:"Consensus", value:final.avg_consensus_score||0},
        {label:"Risk breach", value:final.risk_breach_rate_percent||0, display:pct(final.risk_breach_rate_percent)},
      ],"Benchmark values, not audited customer revenue."); }
    });
  }

  loadStatus().then(status=>{ if(status) render(status); });
})();
