#!/usr/bin/env python3
"""
Resume build script — single source of truth.
  Edit resume.json → python build.py → git push
  Produces ONE file: index.html (online resume + chat widget, prints clean)
"""

import json, re, sys, html as _html
from pathlib import Path

DIR = Path(__file__).parent

# ── Helpers ────────────────────────────────────────────────────────────────────

def load():
    return json.loads((DIR / 'resume.json').read_text())

def e(s):
    return _html.escape(str(s)) if s is not None else ''

def get_existing_key():
    p = DIR / 'index.html'
    if p.exists():
        m = re.search(r"SARVAM_API_KEY:\s*'([^']+)'", p.read_text())
        if m and 'YOUR_' not in m.group(1):
            return m.group(1)
    return 'YOUR_SARVAM_API_KEY_HERE'

# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --dark:      #1a1a2e;
    --mid:       #2d3561;
    --accent:    #c84b31;
    --white:     #ffffff;
    --light:     #f7f7f7;
    --text:      #1a1a1a;
    --text2:     #444444;
    --text3:     #777777;
    --border:    #dedede;
    --font-head: 'Merriweather', serif;
    --font-body: 'Lato', sans-serif;
  }

  body {
    font-family: var(--font-body);
    color: var(--text);
    background: #cccccc;
    line-height: 1.5;
  }

  /* ── Print / action bar (hidden when printing) ── */
  .print-bar {
    width: 210mm; margin: 0 auto;
    padding: 14px 0 8px;
    display: flex; justify-content: flex-end; gap: 10px;
  }
  .print-btn {
    background: var(--dark); color: var(--white);
    border: none; padding: 8px 20px; border-radius: 6px;
    font-family: var(--font-body); font-size: 12px;
    cursor: pointer; transition: background 0.2s;
  }
  .print-btn:hover { background: var(--mid); }

  /* ── A4 page shell ── */
  .page {
    width: 210mm;
    min-height: 297mm;
    background: var(--white);
    margin: 0 auto 32px;
    box-shadow: 0 6px 40px rgba(0,0,0,0.25);
  }

  /* ── HEADER ── */
  .resume-header {
    background: var(--white);
    padding: 28px 40px 22px;
    display: flex;
    align-items: center;
    gap: 24px;
    border-bottom: 2.5px solid var(--dark);
  }

  .header-photo {
    width: 88px; height: 88px;
    border-radius: 6px;
    object-fit: cover; object-position: center top;
    border: 1.5px solid var(--border);
    flex-shrink: 0; display: block;
  }

  .header-info { flex: 1; }

  .header-name {
    font-family: var(--font-head);
    font-size: 22pt; font-weight: 700;
    color: var(--dark);
    letter-spacing: 0.01em; margin-bottom: 4px;
    line-height: 1.2;
  }

  .header-title {
    font-size: 10pt; color: var(--text2);
    letter-spacing: 0.05em; text-transform: uppercase;
    margin-bottom: 10px;
  }

  .header-contacts {
    font-size: 10pt; color: var(--text2);
    line-height: 1.6;
  }

  .header-contacts a {
    color: var(--text2); text-decoration: none;
  }
  .header-contacts a:hover { color: var(--dark); text-decoration: underline; }

  /* ── BODY ── */
  .resume-body { padding: 0 40px 28px; }

  .section { padding: 15px 0; border-bottom: 1px solid var(--border); }
  .section:last-child { border-bottom: none; padding-bottom: 0; }

  .section-title {
    font-size: 8pt; font-weight: 900;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--dark);
    border-bottom: 1.5px solid var(--dark);
    padding-bottom: 3px; margin-bottom: 11px;
  }

  /* ── SUMMARY ── */
  .summary-list { padding-left: 16px; }
  .summary-list li {
    font-size: 11pt; color: var(--text);
    margin-bottom: 4px; line-height: 1.6;
  }
  .summary-list li strong { font-weight: 700; }

  /* ── SKILLS ── */
  .skill-row {
    display: flex; gap: 12px;
    margin-bottom: 5px; line-height: 1.5;
  }
  .skill-cat {
    font-size: 10pt; font-weight: 700;
    color: var(--dark); min-width: 190px; flex-shrink: 0;
  }
  .skill-items { font-size: 10pt; color: var(--text2); }

  /* ── EXPERIENCE ── */
  .exp-block { margin-bottom: 15px; }
  .exp-block:last-child { margin-bottom: 0; }

  .exp-top {
    display: flex; justify-content: space-between;
    align-items: baseline; gap: 8px;
  }
  .exp-role {
    font-size: 12pt; font-weight: 700; color: var(--dark);
    line-height: 1.3;
  }
  .exp-dates {
    font-size: 10pt; color: var(--text3);
    white-space: nowrap; flex-shrink: 0;
  }
  .exp-company {
    font-size: 10.5pt; font-weight: 700;
    color: var(--dark); margin: 2px 0 6px;
  }
  .exp-list { padding-left: 16px; }
  .exp-list li {
    font-size: 10.5pt; color: var(--text2);
    margin-bottom: 3px; line-height: 1.55;
  }
  .exp-list li strong { color: var(--text); font-weight: 700; }

  .exp-divider {
    border: none; border-top: 1px dashed var(--border);
    margin: 12px 0;
  }

  .earlier-label {
    font-size: 11pt; font-weight: 700;
    color: var(--dark); margin-bottom: 6px;
  }

  /* ── BOTTOM (edu / certs / patent / awards) ── */
  .bottom-item { margin-bottom: 6px; font-size: 10.5pt; line-height: 1.55; }
  .bottom-item-title { font-weight: 700; color: var(--dark); }
  .bottom-item-sub { color: var(--text); font-size: 10pt; }

  .cert-row { font-size: 10.5pt; margin-bottom: 3px; color: var(--text); }
  .cert-row span { color: var(--text2); }

  .award-row { font-size: 10.5pt; margin-bottom: 3px; color: var(--text); }
  .award-row span { color: var(--text2); }

  /* ── CHAT FAB — pill button ── */
  .chat-fab {
    position: fixed; bottom: 28px; right: 28px;
    background: var(--dark); color: var(--white);
    border: none; border-radius: 50px;
    padding: 10px 20px 10px 8px;
    display: flex; align-items: center; gap: 10px;
    cursor: pointer; z-index: 1000;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    font-family: var(--font-body);
    transition: all 0.2s;
  }
  .chat-fab:hover { background: var(--mid); transform: translateY(-2px); }

  .fab-photo {
    width: 36px; height: 36px; border-radius: 50%;
    object-fit: cover; object-position: center top;
    border: 2px solid var(--accent); flex-shrink: 0;
  }
  .fab-label { font-size: 13px; font-weight: 600; }

  .fab-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #22c55e; position: absolute;
    top: 8px; right: 8px;
    animation: pulse-dot 2s infinite;
  }
  @keyframes pulse-dot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.5; transform:scale(1.4); }
  }

  /* ── CHAT WIDGET ── */
  .chat-widget {
    position: fixed; bottom: 90px; right: 28px;
    width: 370px; height: 520px;
    background: var(--white); border-radius: 16px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.2);
    display: flex; flex-direction: column;
    z-index: 999; overflow: hidden;
    transform: scale(0.92) translateY(14px);
    opacity: 0; pointer-events: none;
    transform-origin: bottom right;
    transition: transform 0.22s ease, opacity 0.22s ease;
  }
  .chat-widget.open {
    transform: scale(1) translateY(0);
    opacity: 1; pointer-events: all;
  }

  .widget-header {
    background: var(--dark); color: var(--white);
    padding: 14px 16px;
    display: flex; align-items: center; gap: 10px;
    flex-shrink: 0;
  }
  .widget-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    border: 2px solid var(--accent); overflow: hidden;
    background: var(--mid); flex-shrink: 0;
  }
  .widget-avatar img {
    width:100%; height:100%;
    object-fit:cover; object-position:center top; display:block;
  }
  .widget-name { font-weight: 700; font-size: 13px; }
  .widget-sub  { font-size: 10px; opacity: 0.7; margin-top: 1px; }
  .widget-close {
    margin-left: auto; background: none; border: none;
    color: rgba(255,255,255,0.7); font-size: 20px;
    cursor: pointer; padding: 2px 6px; line-height:1;
  }
  .widget-close:hover { color: var(--white); }

  .widget-messages {
    flex:1; overflow-y:auto; padding:12px;
    display:flex; flex-direction:column; gap:10px;
  }
  .wmsg { display:flex; gap:8px; align-items:flex-start; }
  .wmsg.user { flex-direction:row-reverse; }

  .wmsg-avatar {
    width:28px; height:28px; border-radius:50%;
    overflow:hidden; flex-shrink:0;
    background:var(--light);
    display:flex; align-items:center; justify-content:center;
    font-size:14px;
  }
  .wmsg-avatar img {
    width:100%; height:100%;
    object-fit:cover; object-position:center top; display:block;
  }
  .wmsg-bubble {
    max-width:80%; padding:9px 12px; border-radius:14px;
    font-size:12.5px; line-height:1.5;
  }
  .wmsg.bot  .wmsg-bubble { background:var(--light); color:var(--text); border-radius:4px 14px 14px 14px; }
  .wmsg.user .wmsg-bubble { background:var(--dark); color:var(--white); border-radius:14px 4px 14px 14px; }
  .wmsg-bubble p { margin-bottom:6px; }
  .wmsg-bubble p:last-child { margin-bottom:0; }
  .wmsg-bubble ul { padding-left:14px; margin:4px 0; }
  .wmsg-bubble li { margin-bottom:2px; }

  .widget-suggestions {
    display:flex; flex-wrap:wrap; gap:6px;
    padding:6px 12px 8px;
  }
  .suggestion-btn {
    background:none; border:1px solid var(--border);
    border-radius:20px; padding:4px 10px;
    font-size:11px; color:var(--text2);
    cursor:pointer; font-family:var(--font-body);
    transition:all 0.15s;
  }
  .suggestion-btn:hover { border-color:var(--dark); color:var(--dark); }

  .widget-input-area {
    border-top:1px solid var(--border);
    padding:10px 12px 12px; flex-shrink:0;
  }
  .widget-input-row {
    display:flex; align-items:flex-end; gap:8px;
    background:var(--light); border:1px solid var(--border);
    border-radius:10px; padding:8px 10px;
  }
  .widget-input {
    flex:1; background:transparent; border:none; outline:none;
    color:var(--text); font-family:var(--font-body);
    font-size:12.5px; line-height:1.5;
    resize:none; max-height:80px; min-height:20px;
  }
  .widget-input::placeholder { color:var(--text3); }

  .widget-send {
    width:30px; height:30px; border-radius:7px; border:none;
    background:var(--dark); color:var(--white);
    cursor:pointer; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    transition:all 0.15s;
  }
  .widget-send:hover:not(:disabled) { background:var(--mid); transform:translateY(-1px); }
  .widget-send:disabled { opacity:0.4; cursor:not-allowed; }

  .widget-powered { text-align:center; font-size:10px; color:var(--text3); margin-top:7px; }

  .widget-welcome { text-align:center; padding:20px 10px 10px; }
  .widget-welcome-title { font-weight:700; font-size:13px; color:var(--dark); margin-bottom:4px; }
  .widget-welcome-sub { font-size:11px; color:var(--text3); line-height:1.5; }

  .typing-dots {
    display:flex; gap:4px; align-items:center;
    padding:10px 14px; background:var(--light);
    border-radius:4px 14px 14px 14px;
  }
  .typing-dots span {
    width:6px; height:6px; border-radius:50%;
    background:var(--text3); animation:blink 1.2s infinite;
  }
  .typing-dots span:nth-child(2) { animation-delay:0.2s; }
  .typing-dots span:nth-child(3) { animation-delay:0.4s; }
  @keyframes blink { 0%,80%,100%{opacity:.2} 40%{opacity:1} }

  /* ── PRINT ── */
  @media print {
    body { background: white; }
    .print-bar, .chat-fab, .chat-widget { display: none !important; }
    .page { box-shadow: none; margin: 0; width: 100%; }
    .resume-body { padding: 0 32px 24px; }
    .resume-header { padding: 22px 32px; }
  }
  @page { size: A4; margin: 0; }
"""

# ── Section builders ───────────────────────────────────────────────────────────


def header_html(d):
    p  = d['personal']
    cr = d['current_role']
    li_handle = p['links']['linkedin'].replace('https://www.', '').replace('https://', '')
    gh_handle = p['links']['github'].replace('https://', '')
    return f"""  <header class="resume-header">
    <img src="{e(p['photo'])}" class="header-photo" alt="{e(p['name']['full'])}"
         onerror="this.style.display='none'"/>
    <div class="header-info">
      <div class="header-name">{e(p['name']['full'])}</div>
      <div class="header-title">{e(cr['title'])} &mdash; {e(cr['department'])}, {e(cr['company'])}</div>
      <div class="header-contacts">
        <a href="mailto:{e(p['email'])}">{e(p['email'])}</a> &nbsp;|&nbsp;
        {e(p['phone'])} &nbsp;|&nbsp;
        {e(p['location']['city'])}, {e(p['location']['country'])} &nbsp;|&nbsp;
        <a href="{e(p['links']['linkedin'])}" target="_blank">{e(li_handle)}</a> &nbsp;|&nbsp;
        <a href="{e(p['links']['github'])}" target="_blank">{e(gh_handle)}</a>
      </div>
    </div>
  </header>"""

def summary_section(d):
    lis = '\n      '.join(f'<li>{e(h)}</li>' for h in d['summary']['highlights'])
    return f"""    <div class="section">
      <div class="section-title">Professional Summary</div>
      <ul class="summary-list">
      {lis}
      </ul>
    </div>"""

def skills_section(d):
    rows = '\n      '.join(
        f'<div class="skill-row"><span class="skill-cat">{e(g["label"])}</span><span class="skill-items">{e(", ".join(g["items"]))}</span></div>'
        for g in d['skills'].values()
    )
    return f"""    <div class="section">
      <div class="section-title">Core Skills</div>
      {rows}
    </div>"""

def experience_section(d):
    detailed = [x for x in d['experience'] if x['period']['start'] >= '2018-02']
    earlier  = [x for x in d['experience'] if x['period']['start'] <  '2018-02']

    blocks = []
    for i, exp in enumerate(detailed):
        lis = '\n          '.join(
            '<li>' + e(a['description']) + (f' &mdash; <strong>{e(a["impact"])}</strong>' if a.get('impact') else '') + '</li>'
            for a in exp['achievements']
        )
        dept = f', {e(exp["department"])}' if exp.get('department') else ''
        loc  = f' &nbsp;&middot;&nbsp; {e(exp["location"])}' if exp.get('location') else ''
        blocks.append(f"""      <div class="exp-block">
        <div class="exp-top">
          <span class="exp-role">{e(exp['title'])}{dept}</span>
          <span class="exp-dates">{e(exp['period']['display'])}</span>
        </div>
        <div class="exp-company">{e(exp['company'])}{loc}</div>
        <ul class="exp-list">
          {lis}
        </ul>
      </div>""")
        if i < len(detailed) - 1:
            blocks.append('      <hr class="exp-divider"/>')

    earlier_lis = '\n          '.join(
        '<li><strong>' + e(x['title']) + ', ' + e(x['company']) + ' (' + e(x['period']['display']) + '):</strong> '
        + e(x['achievements'][0]['description'])
        + (f' &mdash; <strong>{e(x["achievements"][0]["impact"])}</strong>' if x['achievements'][0].get('impact') else '')
        + '</li>'
        for x in earlier
    )

    blocks.append(f"""      <hr class="exp-divider"/>
      <div class="exp-block">
        <div class="earlier-label">Earlier Career (2009 &ndash; 2018)</div>
        <ul class="exp-list">
          {earlier_lis}
        </ul>
      </div>""")

    return f"""    <div class="section">
      <div class="section-title">Professional Experience</div>
{chr(10).join(blocks)}
    </div>"""

def bottom_sections(d):
    edu = d['education'][0]
    pat = d['patents'][0]

    certs = '\n      '.join(
        f'<div class="cert-row"><strong>{e(c["name"])}</strong> <span>&mdash; {e(c["issuer"])}</span></div>'
        for c in d['certifications']
    )

    awards = '\n      '.join(
        f'<div class="award-row"><strong>{e(a["name"])}</strong> <span>&mdash; {e(a["issuer"])}, {", ".join(str(y) for y in a["years"])}</span></div>'
        for a in d['awards']
    )

    return f"""    <div class="section">
      <div class="section-title">Education</div>
      <div class="bottom-item">
        <span class="bottom-item-title">{e(edu['degree'])}, {e(edu['field'])}</span><br>
        <span class="bottom-item-sub">{e(edu['institution_full'])}, {e(edu['location'])} &mdash; {e(edu['year_graduation'])} &nbsp;&middot;&nbsp; CGPA: {e(edu['cgpa'])}/10</span>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Certifications</div>
      {certs}
    </div>

    <div class="section">
      <div class="section-title">Patent</div>
      <div class="bottom-item">
        <span class="bottom-item-title"><a href="{e(pat['url'])}" target="_blank" style="color:var(--dark);text-decoration:none">{e(pat['name'])}</a></span>
        <span class="bottom-item-sub"> &mdash; {e(pat['number'])}</span><br>
        <span class="bottom-item-sub">{e(pat['description'])}</span>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Awards</div>
      {awards}
    </div>"""

# ── Chat widget ────────────────────────────────────────────────────────────────

def chat_widget_html(d, sarvam_key):
    p   = d['personal']
    cr  = d['current_role']
    exp = d['experience']
    edu = d['education'][0]
    pat = d['patents'][0]

    current = next(x for x in exp if x['period']['is_current'])
    current_bullets = '\n'.join(
        '- ' + a['description'] + (f' — {a["impact"]}' if a.get('impact') else '')
        for a in current['achievements']
    )
    all_skills = ', '.join(item for g in d['skills'].values() for item in g['items'])
    all_certs  = ', '.join(c['name'] for c in d['certifications'])
    all_awards = ', '.join(
        f'{a["name"]} ({", ".join(str(y) for y in a["years"])})' for a in d['awards']
    )
    prev_roles = '\n'.join(
        f'- {x["title"]}, {x["company"]} ({x["period"]["display"]}): {x["achievements"][0]["description"]}'
        + (f' — {x["achievements"][0]["impact"]}' if x['achievements'][0].get('impact') else '')
        for x in exp if not x['period']['is_current']
    )

    system_prompt = (
        f'You are an AI assistant representing {p["name"]["full"]}, '
        f'a {cr["title"]} with {d["summary"]["years_experience"]} years of experience '
        f'in Data Engineering, Big Data, and Cloud Analytics at {cr["company"]}.\n\n'
        f'Answer questions about {p["name"]["first"]} based on this:\n\n'
        f'CURRENT ROLE: {cr["title"]}, {cr["department"]} at {cr["company"]} ({current["period"]["display"]})\n'
        f'{current_bullets}\n\n'
        f'PREVIOUS ROLES:\n{prev_roles}\n\n'
        f'SKILLS: {all_skills}\n\n'
        f'EDUCATION: {edu["degree"]} {edu["field_short"]}, {edu["institution_full"]}, {edu["year_graduation"]} (CGPA {edu["cgpa"]})\n\n'
        f'PATENT: {pat["name"]} ({pat["number"]}) — {pat["description"]}\n\n'
        f'AWARDS: {all_awards}\n\n'
        f'CERTIFICATIONS: {all_certs}\n\n'
        f'Keep answers concise and professional. If asked something not covered, '
        f'suggest contacting {p["name"]["first"]} at {p["email"]}.'
    )

    return f"""<!-- ═══ FLOATING CHAT WIDGET ═══ -->
<button class="chat-fab" id="chatFab" title="Chat with {e(p['name']['first'])}'s AI">
  <img src="{e(p['photo'])}" class="fab-photo" alt="{e(p['name']['first'])}"
       onerror="this.style.display='none'"/>
  <span class="fab-label">Chat with {e(p['name']['first'])}</span>
  <div class="fab-dot"></div>
</button>

<div class="chat-widget" id="chatWidget">
  <div class="widget-header">
    <div class="widget-avatar">
      <img src="{e(p['photo'])}" alt="{e(p['name']['first'])}"
           onerror="this.style.display='none';this.parentElement.textContent='👨‍💻'"/>
    </div>
    <div>
      <div class="widget-name">{e(p['name']['first'])}'s AI Assistant</div>
      <div class="widget-sub">Ask about experience &amp; skills</div>
    </div>
    <button class="widget-close" id="chatClose">×</button>
  </div>

  <div class="widget-messages" id="widgetMessages">
    <div class="widget-welcome" id="widgetWelcome">
      <div class="widget-welcome-title">Hi there! 👋</div>
      <div class="widget-welcome-sub">Ask me anything about {e(p['name']['first'])}'s background, projects, and achievements.</div>
    </div>
  </div>

  <div class="widget-suggestions" id="widgetSuggestions">
    <button class="suggestion-btn">Current role?</button>
    <button class="suggestion-btn">Agentic AI work?</button>
    <button class="suggestion-btn">Cloud cost savings?</button>
    <button class="suggestion-btn">Patent details</button>
  </div>

  <div class="widget-input-area">
    <div class="widget-input-row">
      <textarea class="widget-input" id="widgetInput"
        placeholder="Ask anything about {e(p['name']['first'])}..." rows="1"></textarea>
      <button class="widget-send" id="widgetSend">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
    <div class="widget-powered">Powered by Sarvam AI</div>
  </div>
</div>

<script>
const CONFIG = {{
  SARVAM_API_KEY: '{sarvam_key}',
  SARVAM_API_URL: 'https://api.sarvam.ai/v1/chat/completions',
  SARVAM_MODEL:   'sarvam-m',
  SYSTEM_PROMPT:  {json.dumps(system_prompt)}
}};

const fab    = document.getElementById('chatFab');
const widget = document.getElementById('chatWidget');
fab.addEventListener('click', () => {{
  widget.classList.toggle('open');
  if (widget.classList.contains('open')) document.getElementById('widgetInput').focus();
}});
document.getElementById('chatClose').addEventListener('click', () => widget.classList.remove('open'));

document.querySelectorAll('.suggestion-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    sendMessage(btn.textContent);
    document.getElementById('widgetSuggestions').style.display = 'none';
  }});
}});

const input = document.getElementById('widgetInput');
input.addEventListener('input', () => {{
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 80) + 'px';
}});
input.addEventListener('keydown', ev => {{
  if (ev.key === 'Enter' && !ev.shiftKey) {{ ev.preventDefault(); sendMessage(input.value); }}
}});

const history = [];
let loading = false;

function scrollBottom() {{
  const m = document.getElementById('widgetMessages');
  m.scrollTop = m.scrollHeight;
}}

function fmt(text) {{
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^[-•] (.+)/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    .split('\\n\\n')
    .map(b => b.trim() ? (b.startsWith('<') ? b : `<p>${{b.replace(/\\n/g,'<br>')}}</p>`) : '')
    .join('');
}}

function appendMsg(role, text) {{
  const welcome = document.getElementById('widgetWelcome');
  if (welcome) welcome.remove();
  const wrap   = document.createElement('div'); wrap.className = `wmsg ${{role}}`;
  const avatar = document.createElement('div'); avatar.className = 'wmsg-avatar';
  if (role === 'bot') avatar.innerHTML = '<img src="{e(p["photo"])}" onerror="this.style.display=\\'none\\'">';
  else avatar.textContent = '👤';
  const bubble = document.createElement('div'); bubble.className = 'wmsg-bubble';
  if (role === 'bot') bubble.innerHTML = fmt(text); else bubble.textContent = text;
  wrap.appendChild(avatar); wrap.appendChild(bubble);
  document.getElementById('widgetMessages').appendChild(wrap);
  scrollBottom();
}}

function showTyping() {{
  const wrap = document.createElement('div'); wrap.className = 'wmsg bot'; wrap.id = 'typingWrap';
  const av   = document.createElement('div'); av.className = 'wmsg-avatar';
  av.innerHTML = '<img src="{e(p["photo"])}" onerror="this.style.display=\\'none\\'">';
  const dots = document.createElement('div'); dots.className = 'typing-dots';
  dots.innerHTML = '<span></span><span></span><span></span>';
  wrap.appendChild(av); wrap.appendChild(dots);
  document.getElementById('widgetMessages').appendChild(wrap);
  scrollBottom();
}}

function hideTyping() {{ const el = document.getElementById('typingWrap'); if (el) el.remove(); }}

async function callSarvam(msg) {{
  if (!CONFIG.SARVAM_API_KEY || CONFIG.SARVAM_API_KEY.startsWith('YOUR_'))
    return '⚠️ API key not configured. Update SARVAM_API_KEY in index.html.';
  history.push({{ role: 'user', content: msg }});
  const r = await fetch(CONFIG.SARVAM_API_URL, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json', 'api-subscription-key': CONFIG.SARVAM_API_KEY }},
    body: JSON.stringify({{
      model: CONFIG.SARVAM_MODEL,
      messages: [{{ role: 'system', content: CONFIG.SYSTEM_PROMPT }}, ...history],
      max_tokens: 600
    }})
  }});
  if (!r.ok) throw new Error(`${{r.status}}`);
  const data = await r.json();
  const reply = data.choices[0].message.content;
  history.push({{ role: 'assistant', content: reply }});
  return reply;
}}

async function sendMessage(text) {{
  text = text.trim();
  if (!text || loading) return;
  input.value = ''; input.style.height = 'auto';
  appendMsg('user', text); loading = true;
  document.getElementById('widgetSend').disabled = true;
  showTyping();
  try {{
    const reply = await callSarvam(text);
    hideTyping(); appendMsg('bot', reply);
  }} catch(err) {{
    hideTyping(); appendMsg('bot', '⚠️ Something went wrong. Please try again.');
  }} finally {{
    loading = false; document.getElementById('widgetSend').disabled = false;
  }}
}}
document.getElementById('widgetSend').addEventListener('click', () => sendMessage(input.value));
</script>"""

# ── Page render ────────────────────────────────────────────────────────────────

GFONTS = '<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&family=Merriweather:wght@400;700&display=swap" rel="stylesheet">'

def render_index(d, sarvam_key):
    p = d['personal']
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{e(p['name']['full'])} — {e(d['current_role']['title'])}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  {GFONTS}
  <style>
{CSS}
  </style>
</head>
<body>

<div class="print-bar">
  <button class="print-btn" onclick="window.print()">⬇ Download PDF</button>
</div>

<div class="page">

{header_html(d)}

  <div class="resume-body">
{summary_section(d)}
{skills_section(d)}
{experience_section(d)}
{bottom_sections(d)}
  </div>

</div>

{chat_widget_html(d, sarvam_key)}

</body>
</html>
"""

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    d = load()

    sarvam_key = get_existing_key()
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg.startswith('--key='):
            sarvam_key = arg.split('=', 1)[1]
        elif arg == '--key' and i + 1 < len(args):
            sarvam_key = args[i + 1]

    (DIR / 'index.html').write_text(render_index(d, sarvam_key))
    print('✅  index.html — single-column resume + chat widget (prints clean to PDF)')
    print(f"🔑  Sarvam key — {'preserved from existing file' if sarvam_key != 'YOUR_SARVAM_API_KEY_HERE' else 'PLACEHOLDER — update manually'}")
