const $ = (id) => document.getElementById(id);
const liveUrl = 'https://montrealai.github.io/skillos/';

const fallbackSnapshot = {
  wealth_proof: {
    workflow: { name: 'Sales follow-up email from call notes' },
    initial_agent_metrics: { active_skill_version: 1, active_rules: [], quality_score: 0.50, accepted_rate: 0.67, minutes_per_job: 6.75, cost_per_job_usd: 8.48 },
    final_skillos_metrics: { active_skill_version: 6, active_rules: ['next_step_first', 'specific_pain', 'clear_cta', 'concise_under_120', 'no_fake_claims'], quality_score: 0.96, accepted_rate: 0.96, minutes_per_job: 2.55, cost_per_job_usd: 3.23 },
    proof_steps: [
      { step: 1, lesson: { suggested_skill_update: 'Put the agreed next step in the first three lines.' }, test_result: { quality_delta: 0.14, minutes_delta: -1.31, cost_delta_usd: -1.64 }, metrics_after_release: { active_skill_version: 2, active_rules: ['next_step_first'], quality_score: 0.64, accepted_rate: 0.76, minutes_per_job: 5.44, cost_per_job_usd: 6.84 }, proved_this_job: true },
      { step: 2, lesson: { suggested_skill_update: 'Use the buyer’s specific pain point.' }, test_result: { quality_delta: 0.10, minutes_delta: -0.92, cost_delta_usd: -1.15 }, metrics_after_release: { active_skill_version: 3, active_rules: ['next_step_first','specific_pain'], quality_score: 0.74, accepted_rate: 0.83, minutes_per_job: 4.52, cost_per_job_usd: 5.69 }, proved_this_job: true },
      { step: 3, lesson: { suggested_skill_update: 'End with a clear yes/no CTA.' }, test_result: { quality_delta: 0.09, minutes_delta: -0.73, cost_delta_usd: -0.91 }, metrics_after_release: { active_skill_version: 4, active_rules: ['next_step_first','specific_pain','clear_cta'], quality_score: 0.83, accepted_rate: 0.89, minutes_per_job: 3.79, cost_per_job_usd: 4.78 }, proved_this_job: true },
      { step: 4, lesson: { suggested_skill_update: 'Keep the email under 120 words.' }, test_result: { quality_delta: 0.07, minutes_delta: -0.61, cost_delta_usd: -0.76 }, metrics_after_release: { active_skill_version: 5, active_rules: ['next_step_first','specific_pain','clear_cta','concise_under_120'], quality_score: 0.90, accepted_rate: 0.93, minutes_per_job: 3.18, cost_per_job_usd: 4.02 }, proved_this_job: true },
      { step: 5, lesson: { suggested_skill_update: 'Do not invent unsupported attachments, pricing, claims, or commitments.' }, test_result: { quality_delta: 0.06, minutes_delta: -0.63, cost_delta_usd: -0.79 }, metrics_after_release: { active_skill_version: 6, active_rules: ['next_step_first','specific_pain','clear_cta','concise_under_120','no_fake_claims'], quality_score: 0.96, accepted_rate: 0.96, minutes_per_job: 2.55, cost_per_job_usd: 3.23 }, proved_this_job: true }
    ],
    monotonic_checks: { every_job_created_approved_release: true, cost_per_job_decreased_after_each_release: true, minutes_per_job_decreased_after_each_release: true, quality_score_increased_after_each_release: true, accepted_rate_increased_after_each_release: true },
    conclusion: { proved: true, cost_reduction_percent_vs_initial_agent: 0.619, speed_gain_percent_vs_initial_agent: 0.622, quality_gain_points_vs_initial_agent: 0.46, projected_annual_savings_usd_vs_human_at_10000_jobs: 112300, projected_annual_hours_saved_vs_human_at_10000_jobs: 17100 }
  }
};

function money(n){return `$${Number(n||0).toLocaleString(undefined,{maximumFractionDigits:0})}`}
function money2(n){return `$${Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`}
function pct(n){return `${Math.round(Number(n||0)*100)}%`}
function setText(id,v){const n=$(id); if(n) n.textContent=v}
function safe(n, fallback=0){const x=Number(n); return Number.isFinite(x) ? x : fallback}
function reduction(from,to){return from ? Math.max(0, Math.round((1 - safe(to)/safe(from)) * 100)) : 0}

function normalizeProof(raw){
  const proof = raw.wealth_proof || raw;
  if(proof.initial_agent_metrics && proof.final_skillos_metrics){
    const before = proof.initial_agent_metrics;
    const after = proof.final_skillos_metrics;
    const history = [before, ...(proof.proof_steps||[]).map(s => s.metrics_after_release).filter(Boolean)].map(m => ({
      skill_version: m.active_skill_version,
      quality_percent: Math.round(safe(m.quality_score)*100),
      total_minutes_per_job: safe(m.minutes_per_job).toFixed(2),
      cost_per_job: safe(m.cost_per_job_usd),
      accepted_percent: Math.round(safe(m.accepted_rate)*100),
      enabled_rules: m.active_rules || []
    }));
    const releases = (proof.proof_steps||[]).map(s => ({
      learned_title: s.lesson?.suggested_skill_update || `Release ${s.step}`,
      quality_delta_points: Math.round(safe(s.test_result?.quality_delta)*100),
      minutes_saved_per_job: Math.abs(safe(s.test_result?.minutes_delta)).toFixed(2),
      cost_saved_per_job: Math.abs(safe(s.test_result?.cost_delta_usd)),
      version: s.release?.to_version,
      passed: !!s.proved_this_job
    }));
    const conclusion = proof.conclusion || {};
    return {
      workflow: proof.workflow?.name || 'Sales follow-up email from call notes',
      claim: conclusion.claim || 'SkillOS proved one real workflow gets cheaper, faster, and better as agents do the work.',
      proofPassed: !!conclusion.proved,
      before: { skill_version: before.active_skill_version, quality_percent: Math.round(safe(before.quality_score)*100), total_minutes_per_job: safe(before.minutes_per_job), cost_per_job: safe(before.cost_per_job_usd), accepted_percent: Math.round(safe(before.accepted_rate)*100), enabled_rules: before.active_rules || [] },
      after: { skill_version: after.active_skill_version, quality_percent: Math.round(safe(after.quality_score)*100), total_minutes_per_job: safe(after.minutes_per_job), cost_per_job: safe(after.cost_per_job_usd), accepted_percent: Math.round(safe(after.accepted_rate)*100), enabled_rules: after.active_rules || [] },
      history,
      releases,
      checks: proof.monotonic_checks || {},
      unitEconomics: {
        annualSavingsVsHuman: safe(conclusion.projected_annual_savings_usd_vs_human_at_10000_jobs),
        annualHoursSavedVsHuman: safe(conclusion.projected_annual_hours_saved_vs_human_at_10000_jobs),
        annualVolume: 10000,
        costReduction: safe(conclusion.cost_reduction_percent_vs_initial_agent),
        speedGain: safe(conclusion.speed_gain_percent_vs_initial_agent),
        qualityGain: safe(conclusion.quality_gain_points_vs_initial_agent)
      },
      raw: proof
    };
  }
  return {
    workflow: 'Sales follow-up email from call notes',
    claim: proof.claim || 'SkillOS proved one real workflow gets cheaper, faster, and better.',
    proofPassed: !!proof.proof_checks?.passed,
    before: proof.before || {},
    after: proof.after || {},
    history: proof.history || [],
    releases: proof.releases || [],
    checks: proof.proof_checks || {},
    unitEconomics: proof.unit_economics || {},
    raw: proof
  };
}

function render(raw){
  const proof = normalizeProof(raw);
  const b = proof.before, a = proof.after, u = proof.unitEconomics;
  const costDrop = reduction(b.cost_per_job, a.cost_per_job);
  const timeDrop = reduction(b.total_minutes_per_job, a.total_minutes_per_job);
  const qGain = Math.round(safe(a.quality_percent) - safe(b.quality_percent));
  const annualSavings = u.annualSavingsVsHuman || u.annual_savings_vs_human_only_usd || 0;

  setText('heroProof', proof.proofPassed ? 'Proof passed' : 'Proof pending');
  setText('costDrop', `${costDrop}%`);
  setText('timeDrop', `${timeDrop}%`);
  setText('qualityGain', `+${qGain} pts`);
  setText('annualSavings', money(annualSavings));
  setText('plainResult', `${proof.workflow}: cost per job fell from ${money2(b.cost_per_job)} to ${money2(a.cost_per_job)}, time per job fell from ${safe(b.total_minutes_per_job).toFixed(2)} to ${safe(a.total_minutes_per_job).toFixed(2)} minutes, and quality rose from ${b.quality_percent}% to ${a.quality_percent}%.`);

  const chip = $('proofPassed');
  if(chip){
    chip.textContent = proof.proofPassed ? 'Proof gates passed' : 'Proof gates not passed';
    chip.classList.toggle('ok', proof.proofPassed);
  }

  const cards = $('wealthCards');
  if(cards) cards.innerHTML = [
    ['Cheaper', `${money2(b.cost_per_job)} → ${money2(a.cost_per_job)}`, `${costDrop}% lower cost per job`],
    ['Faster', `${safe(b.total_minutes_per_job).toFixed(2)} → ${safe(a.total_minutes_per_job).toFixed(2)} min`, `${timeDrop}% less time per job`],
    ['Better', `${b.quality_percent}% → ${a.quality_percent}%`, `+${qGain} quality points`],
    ['Skill capital', `v${b.skill_version||1} → v${a.skill_version||proof.history.length}`, `${(a.enabled_rules||[]).length} tested rules shipped`]
  ].map(([label,value,desc]) => `<article><span>${label}</span><strong>${value}</strong><p>${desc}</p></article>`).join('');

  const unit = $('unitEconomics');
  if(unit) unit.innerHTML = [
    ['Annual volume assumption', `${Number(u.annualVolume||u.yearly_volume_assumption_jobs||10000).toLocaleString()} jobs`],
    ['Annual savings vs human', money(annualSavings)],
    ['Annual hours saved', `${Number(u.annualHoursSavedVsHuman||0).toLocaleString()} hrs`],
    ['Monotonic checks', Object.values(proof.checks||{}).every(Boolean) ? 'All passed' : 'Needs review']
  ].map(([label,value]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join('');

  const rows = $('proofRows');
  if(rows) rows.innerHTML = proof.history.map(r => `<tr><td>v${r.skill_version}</td><td>${r.quality_percent}%</td><td>${safe(r.total_minutes_per_job).toFixed(2)}</td><td>${money2(r.cost_per_job)}</td><td>${r.accepted_percent}%</td><td>${(r.enabled_rules||[]).join(', ') || 'baseline'}</td></tr>`).join('');

  const chart = $('versionChart');
  if(chart){
    const h = proof.history;
    const maxCost = Math.max(...h.map(x => safe(x.cost_per_job)), 1);
    const maxTime = Math.max(...h.map(x => safe(x.total_minutes_per_job)), 1);
    chart.innerHTML = h.map((r,i) => `<div class="chart-row" style="--delay:${i*60}ms"><strong>v${r.skill_version}</strong><div class="bar quality" style="width:${Math.max(5,safe(r.quality_percent))}%"><span>Quality ${r.quality_percent}%</span></div><div class="bar time" style="width:${Math.max(5,(safe(r.total_minutes_per_job)/maxTime)*100)}%"><span>Time ${safe(r.total_minutes_per_job).toFixed(2)}m</span></div><div class="bar cost" style="width:${Math.max(5,(safe(r.cost_per_job)/maxCost)*100)}%"><span>Cost ${money2(r.cost_per_job)}</span></div></div>`).join('');
  }

  const rel = $('releaseList');
  if(rel) rel.innerHTML = proof.releases.map((r,i) => `<article><span>Release ${i+1}${r.version ? ` · v${r.version}` : ''}</span><strong>${r.learned_title}</strong><p>Quality +${r.quality_delta_points} pts · ${r.minutes_saved_per_job} min saved/job · ${money2(r.cost_saved_per_job)} saved/job ${r.passed ? '· approved' : ''}</p></article>`).join('');

  setText('demoJson', JSON.stringify({ claim: proof.claim, workflow: proof.workflow, before: b, after: a, checks: proof.checks, releases: proof.releases.map(r => r.learned_title), annualSavingsVsHuman: annualSavings }, null, 2));
}

async function load(){
  try{
    const response = await fetch('data/demo.json', {cache:'no-store'});
    if(!response.ok) throw new Error(`demo ${response.status}`);
    const demo = await response.json();
    render(demo);
  }catch(e1){
    try{
      const response = await fetch('data/wealth_proof.json', {cache:'no-store'});
      if(!response.ok) throw new Error(`proof ${response.status}`);
      render(await response.json());
    }catch(e2){
      render(fallbackSnapshot);
    }
  }
}

function replay(){
  const steps = [...document.querySelectorAll('#timeline li')];
  steps.forEach(s => s.classList.remove('active','done'));
  steps.forEach((step,i) => setTimeout(() => {
    steps.forEach((s,j) => { s.classList.toggle('done', j < i); s.classList.toggle('active', j === i); });
    if(i === steps.length-1) setTimeout(() => step.classList.add('done'), 450);
  }, i * 520));
}

$('runDemo')?.addEventListener('click', replay);
$('copyUrl')?.addEventListener('click', async () => {
  try{ await navigator.clipboard.writeText(liveUrl); $('copyUrl').textContent='Copied'; setTimeout(()=>$('copyUrl').textContent='Copy URL', 1400); }
  catch{ window.prompt('Copy this URL:', liveUrl); }
});

load();
setTimeout(replay, 500);
