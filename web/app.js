async function api(path, options = {}) {
  const res = await fetch(path, {headers: {'Content-Type': 'application/json'}, ...options});
  return await res.json();
}

function pretty(data) { return JSON.stringify(data, null, 2); }

async function refresh() {
  const data = await api('/api/dashboard');
  const counts = data.counts || {};
  document.getElementById('stats').innerHTML = [
    ['Jobs', counts.jobs || 0], ['Traces', counts.traces || 0], ['Skills', counts.skills || 0], ['Versions', counts.skill_versions || 0],
    ['Lessons', counts.lessons || 0], ['Releases', counts.releases || 0], ['Avg score', data.average_trace_score || 0]
  ].map(([label, num]) => `<div class="card"><div class="num">${num}</div><div class="label">${label}</div></div>`).join('');

  document.getElementById('skills').innerHTML = (data.skills || []).map(s => `
    <div class="item">
      <b>${s.name}</b><br/>
      <span class="small">${s.description}</span><br/>
      <span class="pill">current v${s.current_version}</span><span class="pill">${s.visibility}</span>
      <div class="small">Versions: ${(s.versions || []).map(v => `v${v.version} ${v.status} (${v.quality_score})`).join(', ')}</div>
    </div>`).join('') || '<p>No skills yet.</p>';

  document.getElementById('lessons').innerHTML = (data.recent_lessons || []).map(l => `
    <div class="item">
      <b>${l.pattern}</b><br/>
      <span class="small">${l.suggested_change}</span><br/>
      <span class="pill">${l.status}</span><span class="pill">confidence ${Number(l.confidence).toFixed(2)}</span><br/>
      ${l.status === 'ready_to_train' ? `<button onclick="train('${l.lesson_id}')">Train + Test</button>` : ''}
    </div>`).join('') || '<p>No lessons yet. Run several jobs, then click “Find lessons”.</p>';

  document.getElementById('releases').innerHTML = (data.releases || []).map(r => `
    <div class="item">
      <b>${r.skill_id}</b> v${r.from_version} → v${r.to_version}<br/>
      <span class="pill">${r.scope}</span><span class="pill">${r.rollout}</span><span class="pill">rollback v${r.rollback_version}</span>
    </div>`).join('') || '<p>No releases yet.</p>';
}

async function runJob() {
  const payload = {
    goal: document.getElementById('goal').value,
    agent_id: 'sales_agent',
    inputs: {
      prospect_name: document.getElementById('prospect').value,
      company_name: document.getElementById('company').value,
      pain_point: 'manual follow-up work',
      agreed_next_step: document.getElementById('nextStep').value
    },
    human_edits: document.getElementById('edits').value
  };
  const data = await api('/api/jobs', {method: 'POST', body: JSON.stringify(payload)});
  document.getElementById('jobOutput').textContent = pretty(data);
  await refresh();
}

async function learn() {
  const data = await api('/api/learn', {method: 'POST', body: JSON.stringify({min_support: 3})});
  document.getElementById('jobOutput').textContent = pretty(data);
  await refresh();
}

async function train(lessonId) {
  const data = await api('/api/train', {method: 'POST', body: JSON.stringify({lesson_id: lessonId})});
  document.getElementById('jobOutput').textContent = pretty(data);
  if (data.test_result && data.test_result.recommendation === 'approve_canary') {
    const release = await api('/api/approve', {method:'POST', body: JSON.stringify({skill_id:data.candidate.skill_id, version:data.candidate.candidate_version, scope:'team', rollout:'10_percent_canary'})});
    document.getElementById('jobOutput').textContent += '\n\nReleased:\n' + pretty(release);
  }
  await refresh();
}

refresh();
