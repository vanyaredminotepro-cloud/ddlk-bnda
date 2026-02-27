let groupId = null;

const groupInfo = document.getElementById('groupInfo');
const topicsEl = document.getElementById('topics');

async function api(path, options = {}) {
  const r = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`${r.status}: ${txt}`);
  }
  const ct = r.headers.get('content-type') || '';
  return ct.includes('application/json') ? r.json() : null;
}

async function bootstrap() {
  const data = await api('/demo/bootstrap', { method: 'POST' });
  groupId = data.group_id;
  groupInfo.textContent = `group_id: ${groupId} | ${data.title}`;
  await refreshTopics();
}

async function createTopic() {
  if (!groupId) return alert('Сначала нажмите "Создать/получить demo forum"');
  const title = document.getElementById('title').value.trim();
  const icon = document.getElementById('emoji').value.trim();
  if (!title) return alert('Введите название темы');

  await api(`/groups/${groupId}/topics`, {
    method: 'POST',
    body: JSON.stringify({ title, icon_emoji: icon || null }),
  });
  document.getElementById('title').value = '';
  await refreshTopics();
}

async function archiveTopic(topicId, archived) {
  await api(`/groups/${groupId}/topics/${topicId}`, {
    method: 'PATCH',
    body: JSON.stringify({ archived }),
  });
  await refreshTopics();
}

async function deleteTopic(topicId) {
  await api(`/groups/${groupId}/topics/${topicId}`, {
    method: 'DELETE',
    body: JSON.stringify({ delete_for_all: true }),
  });
  await refreshTopics();
}

async function refreshTopics() {
  if (!groupId) return;
  const topics = await api(`/groups/${groupId}/topics`);
  topicsEl.innerHTML = '';
  topics.forEach((t) => {
    const li = document.createElement('li');
    li.className = 'topic';
    li.innerHTML = `<b>#${t.id}</b> ${t.icon_emoji || ''} ${t.title} <span class="status">[${t.status}]</span>`;

    const a = document.createElement('button');
    a.textContent = t.status === 'archived' ? 'Разархивировать' : 'Архивировать';
    a.onclick = () => archiveTopic(t.id, t.status !== 'archived');

    const d = document.createElement('button');
    d.textContent = 'Удалить';
    d.className = 'danger';
    d.onclick = () => deleteTopic(t.id);

    li.append(' ', a, ' ', d);
    topicsEl.appendChild(li);
  });
}

document.getElementById('bootstrapBtn').onclick = () => bootstrap().catch((e) => alert(e.message));
document.getElementById('createBtn').onclick = () => createTopic().catch((e) => alert(e.message));
document.getElementById('refreshBtn').onclick = () => refreshTopics().catch((e) => alert(e.message));
