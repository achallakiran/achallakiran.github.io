#!/usr/bin/env python3
"""
Resume build script — single source of truth.
  python build.py          → generates index.html + resume.html
  python build.py --key sk_xxx  → embed a specific Sarvam API key
"""

import json
import re
import sys
import html as _html
from pathlib import Path

DIR = Path(__file__).parent

# ── Helpers ────────────────────────────────────────────────────────────────────

def load():
    return json.loads((DIR / 'resume.json').read_text())

def e(s):
    return _html.escape(str(s)) if s is not None else ''

def get_existing_key():
    """Preserve existing Sarvam API key from index.html if already set."""
    p = DIR / 'index.html'
    if p.exists():
        m = re.search(r"SARVAM_API_KEY:\s*'([^']+)'", p.read_text())
        if m and 'YOUR_' not in m.group(1):
            return m.group(1)
    return 'YOUR_SARVAM_API_KEY_HERE'

# ── CSS ────────────────────────────────────────────────────────────────────────

RESUME_CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --dark:      #1a1a2e;
      --mid:       #2d3561;
      --accent:    #c84b31;
      --white:     #ffffff;
      --light:     #f7f7f7;
      --text:      #1e1e1e;
      --text2:     #444444;
      --text3:     #888888;
      --border:    #dddddd;
      --sidebar-w: 235px;
      --font-head: 'Merriweather', serif;
      --font-body: 'Lato', sans-serif;
    }

    body {
      font-family: var(--font-body);
      font-size: 12px;
      color: var(--text);
      background: #d8d8d8;
      line-height: 1.5;
    }

    /* Page wrapper — A4, two-column grid */
    .page {
      width: 210mm;
      min-height: 297mm;
      background: var(--white);
      margin: 24px auto;
      box-shadow: 0 4px 32px rgba(0,0,0,0.22);
      display: grid;
      grid-template-columns: var(--sidebar-w) 1fr;
    }

    /* ── SIDEBAR ────────────────────────────── */
    .sidebar {
      background: var(--white);
      border-right: 1px solid var(--border);
      padding: 22px 14px;
      display: flex;
      flex-direction: column;
    }

    /* Profile block */
    .sidebar-profile {
      text-align: center;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 12px;
    }

    .sidebar-photo-wrap {
      width: 110px; height: 110px;
      border-radius: 6px;
      overflow: hidden;
      margin: 0 auto 10px;
      border: 1.5px solid var(--border);
      background: var(--light);
    }

    .sidebar-photo {
      width: 100%; height: 100%;
      object-fit: cover; object-position: center top;
      display: block;
    }

    .photo-fallback {
      width: 100%; height: 100%;
      display: flex; align-items: center; justify-content: center;
      font-size: 30px; font-weight: 700; color: var(--mid);
    }

    .sidebar-name {
      font-family: var(--font-head);
      font-size: 13.5px; font-weight: 700;
      color: var(--dark); margin-bottom: 3px;
      line-height: 1.3;
    }

    .sidebar-role {
      font-size: 10px; color: var(--text3);
      line-height: 1.4;
    }

    /* Section containers */
    .sidebar-section {
      padding: 10px 0;
      border-bottom: 1px solid var(--border);
    }
    .sidebar-section:last-child { border-bottom: none; }

    .s-title {
      font-size: 8.5px; font-weight: 900;
      letter-spacing: 0.13em; text-transform: uppercase;
      color: var(--text3); margin-bottom: 7px;
    }

    /* General info rows */
    .info-row {
      display: flex; gap: 5px;
      margin-bottom: 4px; align-items: flex-start;
    }

    .info-lbl {
      font-size: 8.5px; font-weight: 700;
      color: var(--text3); text-transform: uppercase;
      letter-spacing: 0.05em; flex-shrink: 0;
      width: 50px; padding-top: 1px;
    }

    .info-val {
      font-size: 10px; color: var(--text);
      line-height: 1.4; word-break: break-word;
    }

    a.link { color: var(--mid); text-decoration: none; }
    a.link:hover { color: var(--accent); text-decoration: underline; }

    /* Simple bullet list */
    .bullet-list { font-size: 10.5px; color: var(--text); line-height: 1.7; }
    .bullet-list li { list-style: disc; margin-left: 12px; margin-bottom: 2px; }

    /* Skills */
    .skill-group { margin-bottom: 8px; }
    .skill-group:last-child { margin-bottom: 0; }

    .skill-lbl {
      font-size: 8.5px; font-weight: 700;
      color: var(--mid); text-transform: uppercase;
      letter-spacing: 0.07em; margin-bottom: 4px;
    }

    .skill-list { display: flex; flex-wrap: wrap; gap: 3px; }

    .skill-pill {
      background: var(--light); color: var(--text2);
      border: 1px solid var(--border);
      font-size: 8px; padding: 2px 5px;
      border-radius: 3px; line-height: 1.5;
    }

    /* Patent */
    .patent-name { font-size: 10.5px; font-weight: 700; color: var(--dark); }
    .patent-num  { font-size: 9px; color: var(--accent); margin: 2px 0; }
    .patent-desc { font-size: 9.5px; color: var(--text2); line-height: 1.4; }

    /* Education */
    .edu-degree { font-size: 10.5px; font-weight: 700; color: var(--dark); }
    .edu-meta   { font-size: 9.5px; color: var(--text3); margin-top: 1px; }

    /* Certifications */
    .cert-item {
      font-size: 10px; color: var(--text);
      padding: 3px 0; border-bottom: 1px solid #eee;
      line-height: 1.5;
    }
    .cert-item:last-child { border-bottom: none; }
    .cert-issuer { font-size: 9px; color: var(--text3); }

    /* Awards */
    .award-item {
      display: flex; align-items: flex-start;
      gap: 5px; margin-bottom: 5px; font-size: 10px;
    }
    .award-dot {
      width: 5px; height: 5px; border-radius: 50%;
      background: var(--accent); flex-shrink: 0; margin-top: 4px;
    }
    .award-years { font-size: 9px; color: var(--text3); display: block; }

    /* ── MAIN ────────────────────────────────── */
    .main {
      padding: 22px 24px;
      display: flex; flex-direction: column; gap: 16px;
    }

    .m-title {
      font-size: 11px; font-weight: 700;
      color: var(--text); letter-spacing: 0.02em;
      border-bottom: 1.5px solid var(--text);
      padding-bottom: 3px; margin-bottom: 10px;
    }

    /* Overview bullets */
    .overview-list { padding-left: 16px; }
    .overview-list li {
      font-size: 11.5px; color: var(--text);
      margin-bottom: 5px; line-height: 1.55;
    }
    .overview-list li strong { font-weight: 700; }

    /* Experience */
    .exp-block { margin-bottom: 12px; }
    .exp-block:last-child { margin-bottom: 0; }

    .exp-heading {
      font-size: 11.5px; font-weight: 700;
      color: var(--dark); line-height: 1.4;
      margin-bottom: 5px;
    }

    .exp-achievements { padding-left: 14px; }
    .exp-achievements li {
      font-size: 11px; color: var(--text2);
      margin-bottom: 3px; line-height: 1.5;
    }
    .exp-achievements li strong { color: var(--text); font-weight: 700; }

    .earlier-label {
      font-size: 10.5px; font-weight: 700;
      color: var(--dark); margin-bottom: 5px;
    }

    .exp-divider {
      border: none; border-top: 1px solid var(--border);
      margin: 10px 0;
    }

    /* ── PRINT BAR ─────────────────────────── */
    .print-bar {
      width: 210mm; margin: 0 auto 8px;
      display: flex; justify-content: flex-end; gap: 10px;
    }

    .print-btn {
      background: var(--dark); color: var(--white);
      border: none; padding: 8px 18px;
      border-radius: 6px; font-family: var(--font-body);
      font-size: 12px; cursor: pointer; transition: background 0.2s;
    }
    .print-btn:hover { background: var(--mid); }

    @media print {
      body { background: white; }
      .print-bar, .chat-fab, .chat-widget { display: none !important; }
      .page { margin: 0; box-shadow: none; width: 100%; }
    }
    @page { size: A4; margin: 0; }
"""

CHAT_CSS = """
    /* ── CHAT FAB (pill) ─────────────────────── */
    .chat-fab {
      position: fixed; bottom: 28px; right: 28px;
      background: var(--dark); color: var(--white);
      border: none; border-radius: 50px;
      padding: 10px 18px 10px 8px;
      display: flex; align-items: center; gap: 10px;
      cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      z-index: 1000; transition: all 0.2s;
      font-family: var(--font-body);
    }
    .chat-fab:hover { background: var(--mid); transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.35); }

    .fab-photo {
      width: 36px; height: 36px; border-radius: 50%;
      object-fit: cover; object-position: center top;
      border: 2px solid var(--accent); flex-shrink: 0;
    }

    .fab-text { font-size: 13px; font-weight: 600; letter-spacing: 0.01em; }

    .fab-badge {
      width: 8px; height: 8px; border-radius: 50%;
      background: #22c55e; position: absolute; top: 8px; right: 8px;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.6; transform: scale(1.3); }
    }

    /* ── CHAT WIDGET ─────────────────────────── */
    .chat-widget {
      position: fixed; bottom: 90px; right: 28px;
      width: 370px; height: 520px;
      background: var(--white);
      border-radius: 16px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.2);
      display: flex; flex-direction: column;
      z-index: 999; overflow: hidden;
      transform: scale(0.92) translateY(12px);
      opacity: 0; pointer-events: none;
      transform-origin: bottom right;
      transition: transform 0.22s ease, opacity 0.22s ease;
    }
    .chat-widget.open { transform: scale(1) translateY(0); opacity: 1; pointer-events: all; }

    .widget-header {
      background: var(--dark); color: var(--white);
      padding: 14px 16px; display: flex; align-items: center; gap: 10px;
      flex-shrink: 0;
    }

    .widget-avatar {
      width: 40px; height: 40px; border-radius: 50%;
      border: 2px solid var(--accent); overflow: hidden;
      background: var(--mid); flex-shrink: 0;
    }
    .widget-avatar img { width: 100%; height: 100%; object-fit: cover; object-position: center top; display: block; }

    .widget-name { font-weight: 700; font-size: 13px; }
    .widget-sub  { font-size: 10px; opacity: 0.7; margin-top: 1px; }
    .widget-close {
      margin-left: auto; background: none; border: none;
      color: rgba(255,255,255,0.7); font-size: 20px;
      cursor: pointer; line-height: 1; padding: 2px 6px;
    }
    .widget-close:hover { color: var(--white); }

    .widget-messages {
      flex: 1; overflow-y: auto; padding: 12px;
      display: flex; flex-direction: column; gap: 10px;
    }

    .wmsg { display: flex; gap: 8px; align-items: flex-start; }
    .wmsg.user { flex-direction: row-reverse; }

    .wmsg-avatar {
      width: 28px; height: 28px; border-radius: 50%;
      overflow: hidden; flex-shrink: 0;
      background: var(--light); display: flex;
      align-items: center; justify-content: center;
      font-size: 14px;
    }
    .wmsg-avatar img { width: 100%; height: 100%; object-fit: cover; object-position: center top; display: block; }

    .wmsg-bubble {
      max-width: 80%; padding: 9px 12px;
      border-radius: 14px; font-size: 12.5px; line-height: 1.5;
    }
    .wmsg.bot  .wmsg-bubble { background: var(--light); color: var(--text); border-radius: 4px 14px 14px 14px; }
    .wmsg.user .wmsg-bubble { background: var(--dark); color: var(--white); border-radius: 14px 4px 14px 14px; }
    .wmsg-bubble p { margin-bottom: 6px; }
    .wmsg-bubble p:last-child { margin-bottom: 0; }
    .wmsg-bubble ul { padding-left: 14px; margin: 4px 0; }
    .wmsg-bubble li { margin-bottom: 2px; }

    .widget-suggestions {
      display: flex; flex-wrap: wrap; gap: 6px;
      padding: 6px 12px 8px;
    }
    .suggestion-btn {
      background: none; border: 1px solid var(--border);
      border-radius: 20px; padding: 4px 10px;
      font-size: 11px; color: var(--text2); cursor: pointer;
      font-family: var(--font-body); transition: all 0.15s;
    }
    .suggestion-btn:hover { border-color: var(--dark); color: var(--dark); }

    .widget-input-area {
      border-top: 1px solid var(--border); padding: 10px 12px 12px;
      flex-shrink: 0;
    }

    .widget-input-row {
      display: flex; align-items: flex-end; gap: 8px;
      background: var(--light); border: 1px solid var(--border);
      border-radius: 10px; padding: 8px 10px;
    }

    .widget-input {
      flex: 1; background: transparent; border: none; outline: none;
      color: var(--text); font-family: var(--font-body);
      font-size: 12.5px; line-height: 1.5;
      resize: none; max-height: 80px; min-height: 20px;
    }
    .widget-input::placeholder { color: var(--text3); }

    .widget-send {
      width: 30px; height: 30px; border-radius: 7px; border: none;
      background: var(--dark); color: var(--white);
      cursor: pointer; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.15s;
    }
    .widget-send:hover:not(:disabled) { background: var(--mid); transform: translateY(-1px); }
    .widget-send:disabled { opacity: 0.4; cursor: not-allowed; }

    .widget-powered { text-align: center; font-size: 10px; color: var(--text3); margin-top: 7px; }

    .widget-welcome { text-align: center; padding: 20px 10px 10px; }
    .widget-welcome-title { font-weight: 700; font-size: 13px; color: var(--dark); margin-bottom: 4px; }
    .widget-welcome-sub { font-size: 11px; color: var(--text3); line-height: 1.5; }

    .typing-dots {
      display: flex; gap: 4px; align-items: center;
      padding: 10px 14px; background: var(--light);
      border-radius: 4px 14px 14px 14px;
    }
    .typing-dots span {
      width: 6px; height: 6px; border-radius: 50%;
      background: var(--text3); animation: blink 1.2s infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink { 0%,80%,100% { opacity: 0.2; } 40% { opacity: 1; } }
"""

# ── HTML Generators ────────────────────────────────────────────────────────────

def skills_html(skills):
    parts = []
    for g in skills.values():
        pills = ''.join(f'<span class="skill-pill">{e(i)}</span>' for i in g['items'])
        parts.append(f'<div class="skill-group"><div class="skill-lbl">{e(g["label"])}</div><div class="skill-list">{pills}</div></div>')
    return '\n'.join(parts)

def sidebar_html(d):
    p = d['personal']
    pat = d['patents'][0]
    edu = d['education'][0]

    certs = '\n'.join(
        f'<div class="cert-item">{e(c["name"])}<div class="cert-issuer">{e(c["issuer"])}</div></div>'
        for c in d['certifications']
    )

    awards = '\n'.join(
        f'<div class="award-item"><div class="award-dot"></div><div>{e(a["name"])}<span class="award-years">{" · ".join(str(y) for y in a["years"])}</span></div></div>'
        for a in d['awards']
    )

    return f"""  <aside class="sidebar">

    <div class="sidebar-profile">
      <div class="sidebar-photo-wrap">
        <img src="{e(p['photo'])}" alt="{e(p['name']['full'])}" class="sidebar-photo"
             onerror="this.style.display='none';this.parentElement.innerHTML='<div class=&quot;photo-fallback&quot;>RK</div>'"/>
      </div>
      <div class="sidebar-name">{e(p['name']['full'])}</div>
      <div class="sidebar-role">{e(d['current_role']['title'])}, {e(d['current_role']['company'])}</div>
    </div>

    <div class="sidebar-section">
      <div class="s-title">General Information</div>
      <div class="info-row"><span class="info-lbl">Email</span><a href="mailto:{e(p['email'])}" class="info-val link">{e(p['email'])}</a></div>
      <div class="info-row"><span class="info-lbl">Phone</span><span class="info-val">{e(p['phone'])}</span></div>
      <div class="info-row"><span class="info-lbl">LinkedIn</span><a href="{e(p['links']['linkedin'])}" target="_blank" class="info-val link">ravikiran-achalla</a></div>
      <div class="info-row"><span class="info-lbl">GitHub</span><a href="{e(p['links']['github'])}" target="_blank" class="info-val link">achallakiran</a></div>
      <div class="info-row"><span class="info-lbl">City</span><span class="info-val">{e(p['location']['city'])}, {e(p['location']['country'])}</span></div>
      <div class="info-row"><span class="info-lbl">Address</span><span class="info-val">{e(p['location']['address'])}</span></div>
      <div class="info-row"><span class="info-lbl">DOB</span><span class="info-val">{e(p['dob'])}</span></div>
    </div>

    <div class="sidebar-section">
      <div class="s-title">Industry Experience</div>
      <ul class="bullet-list">{"".join(f"<li>{e(i)}</li>" for i in d['summary']['industry'])}</ul>
    </div>

    <div class="sidebar-section">
      <div class="s-title">Current Role</div>
      <ul class="bullet-list"><li>{e(d['current_role']['title'])}, {e(d['current_role']['department'])}</li></ul>
    </div>

    <div class="sidebar-section">
      <div class="s-title">Skills</div>
      {skills_html(d['skills'])}
    </div>

    <div class="sidebar-section">
      <div class="s-title">Patents</div>
      <div class="patent-name"><a href="{e(pat['url'])}" target="_blank" class="link">{e(pat['name'])}</a></div>
      <div class="patent-num">{e(pat['number'])}</div>
      <div class="patent-desc">{e(pat['description'])}</div>
    </div>

    <div class="sidebar-section">
      <div class="s-title">Education</div>
      <div class="edu-degree">{e(edu['degree'])}, {e(edu['field_short'])}, {e(edu['institution'])}, {e(edu['location'].split(',')[0])}</div>
      <div class="edu-meta">({e(edu['cgpa'])} CGPA), {e(edu['year_graduation'])}</div>
    </div>

    <div class="sidebar-section">
      <div class="s-title">Certifications</div>
      {certs}
    </div>

    <div class="sidebar-section">
      <div class="s-title">Awards</div>
      {awards}
    </div>

  </aside>"""

def achievement_li(a):
    desc = e(a['description'])
    if a.get('impact'):
        return f'<li>{desc} — <strong>{e(a["impact"])}</strong></li>'
    return f'<li>{desc}</li>'

def experience_html(experience):
    detailed = [x for x in experience if x['period']['start'] >= '2018-02']
    earlier  = [x for x in experience if x['period']['start'] <  '2018-02']

    blocks = []
    for i, exp in enumerate(detailed):
        lis = '\n          '.join(achievement_li(a) for a in exp['achievements'])
        dept = f" – {e(exp['department'])}" if exp.get('department') else ''
        blocks.append(f"""      <div class="exp-block">
        <div class="exp-heading"><strong>{e(exp['title'])}{dept}, {e(exp['company'])}</strong> ({e(exp['period']['display'])})</div>
        <ul class="exp-achievements">
          {lis}
        </ul>
      </div>""")
        if i < len(detailed) - 1:
            blocks.append('      <hr class="exp-divider"/>')

    earlier_lis = '\n          '.join(
        f'<li><strong>{e(x["company"])} ({e(x["period"]["display"])})</strong>: {e(x["achievements"][0]["description"])}'
        + (f' — <strong>{e(x["achievements"][0]["impact"])}</strong>' if x["achievements"][0].get("impact") else '')
        + '</li>'
        for x in earlier
    )
    blocks.append(f"""      <hr class="exp-divider"/>
      <div class="exp-block">
        <div class="earlier-label">Earlier Career (2009 – 2018)</div>
        <ul class="exp-achievements">
          {earlier_lis}
        </ul>
      </div>""")

    return '\n\n'.join(blocks)

def main_html(d):
    highlights = '\n      '.join(
        f'<li>{e(h)}</li>' for h in d['summary']['highlights']
    )
    return f"""  <main class="main">

    <section>
      <div class="m-title">Overview</div>
      <ul class="overview-list">
      {highlights}
      </ul>
    </section>

    <section>
      <div class="m-title">Professional Experience</div>

{experience_html(d['experience'])}

    </section>

  </main>"""

# ── Chat widget (index.html only) ──────────────────────────────────────────────

def chat_widget_html(d, sarvam_key):
    p = d['personal']
    cr = d['current_role']
    exp = d['experience']

    # Build system prompt from JSON data
    current = next(x for x in exp if x['period']['is_current'])
    current_bullets = '\n'.join(
        f"- {a['description']}" + (f" — {a['impact']}" if a.get('impact') else '')
        for a in current['achievements']
    )
    skill_items = ', '.join(
        item for g in d['skills'].values() for item in g['items']
    )
    certs = ', '.join(c['name'] for c in d['certifications'])
    awards = ', '.join(
        f"{a['name']} ({', '.join(str(y) for y in a['years'])})" for a in d['awards']
    )
    pat = d['patents'][0]
    edu = d['education'][0]

    system_prompt = f"""You are an AI assistant representing {e(p['name']['full'])}, a {e(cr['title'])} with {d['summary']['years_experience']} years of experience in Data Engineering, Big Data, and Cloud Analytics at {e(cr['company'])}.

Answer questions about {e(p['name']['first'])} based on this information:

CURRENT ROLE: {e(cr['title'])}, {e(cr['department'])} at {e(cr['company'])} ({e(current['period']['display'])})
{current_bullets}

PREVIOUS ROLES:
{chr(10).join(
    f"- {x['title']}, {x['company']} ({x['period']['display']}): {x['achievements'][0]['description']}"
    + (f" — {x['achievements'][0]['impact']}" if x['achievements'][0].get('impact') else '')
    for x in exp if not x['period']['is_current']
)}

SKILLS: {skill_items}

EDUCATION: {edu['degree']} {edu['field_short']}, {edu['institution']} {edu['location'].split(',')[0]}, {edu['year_graduation']} (CGPA {edu['cgpa']})

PATENT: {pat['name']} ({pat['number']}) — {pat['description']}

AWARDS: {awards}

CERTIFICATIONS: {certs}

CONTACT: {e(p['email'])}

Keep answers concise, professional, and factual. If asked something not covered above, suggest contacting {e(p['name']['first'])} at {e(p['email'])}.
"""

    return f"""
<!-- ═══════════════ FLOATING CHAT WIDGET ═══════════════ -->

<button class="chat-fab" id="chatFab" title="Chat with Ravi's AI">
  <img src="{e(p['photo'])}" class="fab-photo" alt="{e(p['name']['first'])}"
       onerror="this.style.display='none'"/>
  <span class="fab-text">Chat with {e(p['name']['first'])}</span>
  <div class="fab-badge"></div>
</button>

<div class="chat-widget" id="chatWidget">
  <div class="widget-header">
    <div class="widget-avatar">
      <img src="{e(p['photo'])}" alt="{e(p['name']['first'])}"
           onerror="this.style.display='none';this.parentElement.textContent='👨‍💻'"/>
    </div>
    <div>
      <div class="widget-name">{e(p['name']['first'])}'s AI Assistant</div>
      <div class="widget-sub">Ask me about {e(p['name']['first'])}'s experience &amp; skills</div>
    </div>
    <button class="widget-close" id="chatClose" title="Close">×</button>
  </div>

  <div class="widget-messages" id="widgetMessages">
    <div class="widget-welcome" id="widgetWelcome">
      <div class="widget-welcome-title">Hi there! 👋</div>
      <div class="widget-welcome-sub">I can answer questions about {e(p['name']['first'])}'s background, skills, projects, and achievements.</div>
    </div>
  </div>

  <div class="widget-suggestions" id="widgetSuggestions">
    <button class="suggestion-btn">Current role?</button>
    <button class="suggestion-btn">Key achievements?</button>
    <button class="suggestion-btn">Agentic AI work?</button>
    <button class="suggestion-btn">Patent details</button>
    <button class="suggestion-btn">Cloud cost savings?</button>
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
const closeBtn = document.getElementById('chatClose');

fab.addEventListener('click', () => {{
  widget.classList.toggle('open');
  if (widget.classList.contains('open')) {{
    document.getElementById('widgetInput').focus();
    fab.querySelector('.fab-badge').style.display = 'none';
  }}
}});
closeBtn.addEventListener('click', () => widget.classList.remove('open'));

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
input.addEventListener('keydown', e => {{
  if (e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(input.value); }}
}});

const history = [];
let loading = false;

function scrollBottom() {{
  const m = document.getElementById('widgetMessages');
  m.scrollTop = m.scrollHeight;
}}

function formatText(text) {{
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
  const wrap   = document.createElement('div');
  wrap.className = `wmsg ${{role}}`;
  const avatar = document.createElement('div');
  avatar.className = 'wmsg-avatar';
  if (role === 'bot') {{
    avatar.innerHTML = '<img src="{e(p["photo"])}" alt="{e(p["name"]["first"])}" onerror="this.style.display=\\'none\\';this.parentElement.textContent=\\'👨\\u200d💻\\'">';
  }} else {{
    avatar.textContent = '👤';
  }}
  const bubble = document.createElement('div');
  bubble.className = 'wmsg-bubble';
  if (role === 'bot') bubble.innerHTML = formatText(text);
  else bubble.textContent = text;
  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  document.getElementById('widgetMessages').appendChild(wrap);
  scrollBottom();
}}

function showTyping() {{
  const wrap = document.createElement('div');
  wrap.className = 'wmsg bot'; wrap.id = 'typingWrap';
  const avatar = document.createElement('div');
  avatar.className = 'wmsg-avatar';
  avatar.innerHTML = '<img src="{e(p["photo"])}" alt="{e(p["name"]["first"])}" onerror="this.style.display=\\'none\\'">';
  const dots = document.createElement('div');
  dots.className = 'typing-dots';
  dots.innerHTML = '<span></span><span></span><span></span>';
  wrap.appendChild(avatar); wrap.appendChild(dots);
  document.getElementById('widgetMessages').appendChild(wrap);
  scrollBottom();
}}

function hideTyping() {{
  const el = document.getElementById('typingWrap');
  if (el) el.remove();
}}

async function callSarvam(userMessage) {{
  if (!CONFIG.SARVAM_API_KEY || CONFIG.SARVAM_API_KEY.startsWith('YOUR_')) {{
    return '⚠️ API key not configured. Update SARVAM_API_KEY in index.html to enable AI responses.';
  }}
  history.push({{ role: 'user', content: userMessage }});
  const resp = await fetch(CONFIG.SARVAM_API_URL, {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      'api-subscription-key': CONFIG.SARVAM_API_KEY
    }},
    body: JSON.stringify({{
      model: CONFIG.SARVAM_MODEL,
      messages: [
        {{ role: 'system', content: CONFIG.SYSTEM_PROMPT }},
        ...history
      ],
      max_tokens: 600
    }})
  }});
  if (!resp.ok) throw new Error(`API error ${{resp.status}}`);
  const data = await resp.json();
  const reply = data.choices[0].message.content;
  history.push({{ role: 'assistant', content: reply }});
  return reply;
}}

async function sendMessage(text) {{
  text = text.trim();
  if (!text || loading) return;
  input.value = ''; input.style.height = 'auto';
  appendMsg('user', text);
  loading = true;
  document.getElementById('widgetSend').disabled = true;
  showTyping();
  try {{
    const reply = await callSarvam(text);
    hideTyping(); appendMsg('bot', reply);
  }} catch(err) {{
    hideTyping(); appendMsg('bot', '⚠️ Something went wrong. Please try again.');
    console.error(err);
  }} finally {{
    loading = false;
    document.getElementById('widgetSend').disabled = false;
  }}
}}

document.getElementById('widgetSend').addEventListener('click', () => sendMessage(input.value));
</script>"""

# ── Page assembler ─────────────────────────────────────────────────────────────

GOOGLE_FONTS = '<link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&family=Merriweather:wght@400;700&display=swap" rel="stylesheet">'

def render_index(d, sarvam_key):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{e(d['personal']['name']['full'])} — {e(d['current_role']['title'])}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  {GOOGLE_FONTS}
  <style>
{RESUME_CSS}
{CHAT_CSS}
  </style>
</head>
<body>

<div class="print-bar">
  <button class="print-btn" onclick="window.print()">⬇ Download PDF</button>
</div>

<div class="page">

{sidebar_html(d)}

{main_html(d)}

</div>

{chat_widget_html(d, sarvam_key)}

</body>
</html>
"""

def render_resume(d):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{e(d['personal']['name']['full'])} — Resume</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  {GOOGLE_FONTS}
  <style>
{RESUME_CSS}
  </style>
</head>
<body>

<div class="print-bar">
  <a href="index.html" style="background:none;border:1px solid #ddd;color:#555;padding:8px 18px;border-radius:6px;text-decoration:none;font-size:12px;font-family:var(--font-body)">← Back</a>
  <button class="print-btn" onclick="window.print()">⬇ Download PDF</button>
</div>

<div class="page">

{sidebar_html(d)}

{main_html(d)}

</div>

</body>
</html>
"""

# ── ATS-safe renderer ─────────────────────────────────────────────────────────

ATS_CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Calibri', 'Arial', sans-serif;
    font-size: 11pt;
    color: #000;
    background: #fff;
    line-height: 1.45;
    padding: 0;
  }

  /* Print wrapper — A4 */
  .ats-page {
    max-width: 780px;
    margin: 0 auto;
    padding: 36px 48px;
    background: #fff;
  }

  /* Name block */
  .ats-name {
    font-size: 22pt;
    font-weight: 700;
    color: #000;
    margin-bottom: 2px;
    line-height: 1.2;
  }

  .ats-headline {
    font-size: 11pt;
    color: #333;
    margin-bottom: 8px;
  }

  .ats-contact {
    font-size: 10pt;
    color: #222;
    margin-bottom: 20px;
    line-height: 1.7;
  }

  .ats-contact a { color: #000; text-decoration: none; }

  /* Section */
  .ats-section { margin-bottom: 16px; }

  .ats-section-title {
    font-size: 11pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1.5px solid #000;
    padding-bottom: 2px;
    margin-bottom: 9px;
    color: #000;
  }

  /* Experience */
  .ats-job { margin-bottom: 12px; }

  .ats-job-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 2px;
  }

  .ats-job-title { font-weight: 700; font-size: 11pt; }
  .ats-job-dates { font-size: 10pt; color: #333; white-space: nowrap; }
  .ats-job-company { font-size: 10.5pt; color: #333; margin-bottom: 5px; }

  .ats-bullets { padding-left: 18px; }

  .ats-bullets li {
    font-size: 10.5pt;
    color: #111;
    margin-bottom: 3px;
    line-height: 1.5;
  }

  /* Skills */
  .ats-skill-row { margin-bottom: 5px; font-size: 10.5pt; }
  .ats-skill-cat { font-weight: 700; }

  /* Education / Certs / Awards */
  .ats-item { margin-bottom: 5px; font-size: 10.5pt; }
  .ats-item-title { font-weight: 700; }
  .ats-item-sub { color: #333; }

  /* Print bar (hidden when printing) */
  .ats-print-bar {
    max-width: 780px;
    margin: 0 auto;
    padding: 12px 48px 0;
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }

  .ats-btn {
    padding: 7px 16px;
    border-radius: 5px;
    font-size: 11pt;
    cursor: pointer;
    font-family: inherit;
  }

  .ats-btn-primary { background: #1a1a2e; color: #fff; border: none; }
  .ats-btn-secondary { background: #fff; color: #444; border: 1px solid #ccc; text-decoration: none; display: inline-block; }

  @media print {
    .ats-print-bar { display: none; }
    body { padding: 0; }
    .ats-page { padding: 20mm 18mm; max-width: 100%; }
  }

  @page { size: A4; margin: 0; }
"""

def render_ats(d):
    p  = d['personal']
    cr = d['current_role']
    sm = d['summary']

    # Contact line
    contact_parts = [
        p['email'],
        p['phone'],
        p['links']['linkedin'].replace('https://www.linkedin.com/in/', 'linkedin.com/in/'),
        p['links']['github'].replace('https://github.com/', 'github.com/'),
        f"{p['location']['city']}, {p['location']['country']}",
    ]
    contact_line = ' | '.join(e(x) for x in contact_parts)

    # Skills — flat grouped rows
    skill_rows = '\n'.join(
        f'<div class="ats-skill-row"><span class="ats-skill-cat">{e(g["label"])}:</span> {e(", ".join(g["items"]))}</div>'
        for g in d['skills'].values()
    )

    # Summary bullets
    summary_lis = '\n'.join(f'<li>{e(h)}</li>' for h in sm['highlights'])

    # Experience — detailed (2018+)
    detailed = [x for x in d['experience'] if x['period']['start'] >= '2018-02']
    earlier  = [x for x in d['experience'] if x['period']['start'] <  '2018-02']

    def job_block(exp):
        lis = '\n'.join(
            '<li>' + e(a['description']) + (f' {e(a["impact"])}.' if a.get('impact') else '') + '</li>'
            for a in exp['achievements']
        )
        dept = f', {e(exp["department"])}' if exp.get('department') else ''
        return f"""    <div class="ats-job">
      <div class="ats-job-header">
        <span class="ats-job-title">{e(exp['title'])}{dept}</span>
        <span class="ats-job-dates">{e(exp['period']['display'])}</span>
      </div>
      <div class="ats-job-company">{e(exp['company'])}{(' · ' + e(exp['location'])) if exp.get('location') else ''}</div>
      <ul class="ats-bullets">{lis}</ul>
    </div>"""

    exp_blocks = '\n'.join(job_block(x) for x in detailed)

    earlier_lis = '\n'.join(
        '<li><b>' + e(x['title']) + ', ' + e(x['company']) + '</b> (' + e(x['period']['display']) + '): '
        + e(x['achievements'][0]['description'])
        + (f' {e(x["achievements"][0]["impact"])}.' if x['achievements'][0].get('impact') else '')
        + '</li>'
        for x in earlier
    )

    # Education
    edu = d['education'][0]
    edu_block = f"""    <div class="ats-item">
      <span class="ats-item-title">{e(edu['degree'])}, {e(edu['field'])}</span><br>
      <span class="ats-item-sub">{e(edu['institution_full'])}, {e(edu['location'])} — {e(edu['year_graduation'])} (CGPA: {e(edu['cgpa'])}/10)</span>
    </div>"""

    # Certifications
    cert_items = '\n'.join(
        f'<div class="ats-item"><span class="ats-item-title">{e(c["name"])}</span> — <span class="ats-item-sub">{e(c["issuer"])}</span></div>'
        for c in d['certifications']
    )

    # Patents
    pat = d['patents'][0]
    patent_block = f"""    <div class="ats-item">
      <span class="ats-item-title">{e(pat['name'])}</span> ({e(pat['number'])})<br>
      <span class="ats-item-sub">{e(pat['description'])}</span>
    </div>"""

    # Awards
    award_items = '\n'.join(
        f'<div class="ats-item"><span class="ats-item-title">{e(a["name"])}</span> — <span class="ats-item-sub">{e(a["issuer"])}, {", ".join(str(y) for y in a["years"])}</span></div>'
        for a in d['awards']
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{e(p['name']['full'])} — ATS Resume</title>
  <style>
{ATS_CSS}
  </style>
</head>
<body>

<div class="ats-print-bar">
  <a href="index.html" class="ats-btn ats-btn-secondary">← Back</a>
  <button class="ats-btn ats-btn-primary" onclick="window.print()">⬇ Save as PDF</button>
</div>

<div class="ats-page">

  <div class="ats-name">{e(p['name']['full'])}</div>
  <div class="ats-headline">{e(cr['title'])}, {e(cr['department'])} · {e(cr['company'])}</div>
  <div class="ats-contact">{contact_line}</div>

  <div class="ats-section">
    <div class="ats-section-title">Professional Summary</div>
    <ul class="ats-bullets">{summary_lis}</ul>
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Skills</div>
    {skill_rows}
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Work Experience</div>
    {exp_blocks}
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Earlier Career (2009 – 2018)</div>
    <ul class="ats-bullets">{earlier_lis}</ul>
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Education</div>
    {edu_block}
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Certifications</div>
    {cert_items}
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Patents</div>
    {patent_block}
  </div>

  <div class="ats-section">
    <div class="ats-section-title">Awards</div>
    {award_items}
  </div>

</div>
</body>
</html>
"""

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    d = load()

    sarvam_key = get_existing_key()
    for arg in sys.argv[1:]:
        if arg.startswith('--key='):
            sarvam_key = arg.split('=', 1)[1]
        elif arg.startswith('--key'):
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                sarvam_key = sys.argv[idx + 1]

    (DIR / 'index.html').write_text(render_index(d, sarvam_key))
    (DIR / 'resume.html').write_text(render_resume(d))
    (DIR / 'ats.html').write_text(render_ats(d))
    print(f"✅  index.html   — resume + chat widget")
    print(f"✅  resume.html  — clean printable version")
    print(f"✅  ats.html     — ATS-safe single-column (open in browser → Save as PDF)")
    print(f"🔑  Sarvam key   — {'(from existing file)' if sarvam_key != 'YOUR_SARVAM_API_KEY_HERE' else 'PLACEHOLDER — update manually'}")
