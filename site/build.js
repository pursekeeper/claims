#!/usr/bin/env node
// Builds a static site from this repository: one page per verified result, an index, index.json and a sitemap.
// Source of truth: claims/index.json (status, reviews, verified line, prior art) and claims/NN-*.md (statement,
// pass criterion, novelty, hardness, provenance). No dependencies. Usage: node site/build.js [outdir]
// (default site/out). Served at https://pursekeeper.dev/verified/ ; set CLAIMS_BASE to build for another base URL.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.resolve(process.argv[2] || path.join(__dirname, 'out'));
const BASE = (process.env.CLAIMS_BASE || 'https://pursekeeper.dev/verified/').replace(/\/?$/, '/');
const REPO = 'https://github.com/pursekeeper/claims';
const SITE_TITLE = 'Verified small results';
const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'claims', 'index.json'), 'utf8'));

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
// OEIS A-numbers become links, except inside an existing URL or anchor text.
const anum = h => h.replace(/(^|[^\w\/>])(A\d{6})(?!\w)/g, '$1<a href="https://oeis.org/$2">$2</a>');
const inline = s => anum(esc(s)
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
  .replace(/\*([^*\s][^*]*)\*/g, '<i>$1</i>')
  .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, t, u) => `<a href="${esc(resolveLink(u))}">${t}</a>`)
  .replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2">$2</a>'));
// Relative links in claim pages point into the repository.
function resolveLink(u) {
  if (/^https?:/.test(u) || u.startsWith('#') || u.startsWith('mailto:')) return u;
  const rel = u.replace(/^\.\.\//, '');
  return `${REPO}/blob/main/${rel.startsWith('claims/') || rel.startsWith('claimant/') || rel.startsWith('runs/') ? rel : 'claims/' + rel}`;
}
// Same markdown subset as pursekeeper.dev's site.
function md(src) {
  const out = []; let para = [], list = null, code = null, table = null;
  const flush = () => {
    if (para.length) { out.push('<p>' + inline(para.join(' ')) + '</p>'); para = []; }
    if (list) { out.push(`<${list.tag}>` + list.items.map(i => '<li>' + inline(i) + '</li>').join('') + `</${list.tag}>`); list = null; }
    if (table) { out.push('<table>' + table.map((r, i) => '<tr>' + r.map(c => `<${i ? 'td' : 'th'}>${inline(c)}</${i ? 'td' : 'th'}>`).join('') + '</tr>').join('') + '</table>'); table = null; }
  };
  for (const line of src.split('\n')) {
    if (code !== null) { if (/^```/.test(line)) { out.push('<pre>' + esc(code.join('\n')) + '</pre>'); code = null; } else code.push(line); continue; }
    if (/^```/.test(line)) { flush(); code = []; continue; }
    const h = /^(#{1,4})\s+(.*)/.exec(line);
    if (h) { flush(); out.push(`<h${h[1].length + 1}>${inline(h[2])}</h${h[1].length + 1}>`); continue; }
    if (/^\|/.test(line)) { if (/^\|\s*:?-+/.test(line)) continue; para.length && flush(); table = table || []; table.push(line.replace(/^\||\|$/g, '').split('|').map(s => s.trim())); continue; }
    const li = /^\s*([-*]|\d+\.)\s+(.*)/.exec(line);
    if (li) { const tag = /\d/.test(li[1]) ? 'ol' : 'ul'; if (para.length || (list && list.tag !== tag) || table) flush(); list = list || { tag, items: [] }; list.items.push(li[2]); continue; }
    if (/^\s+\S/.test(line) && list) { list.items[list.items.length - 1] += ' ' + line.trim(); continue; }
    if (/^---+$/.test(line)) { flush(); out.push('<hr>'); continue; }
    if (!line.trim()) { flush(); continue; }
    if (list || table) flush();
    para.push(line.trim());
  }
  flush();
  return out.join('\n');
}

const CSS = `body{font:16px/1.5 system-ui,sans-serif;max-width:46em;margin:2em auto;padding:0 1em;color:#1b1b1b;background:#fff}
a{color:#0a58ca}h1{font-size:1.5em;margin:.2em 0 .4em}h2{font-size:1.15em;margin-top:1.8em;border-bottom:1px solid #ddd;padding-bottom:.2em}h3{font-size:1.02em;margin:1.3em 0 .3em}
table{border-collapse:collapse;width:100%;margin:.8em 0;font-size:.93em}td,th{border-top:1px solid #e3e3e3;padding:.35em .5em;text-align:left;vertical-align:top}th{font-weight:600;color:#444}
code{font-size:.92em;background:#f3f3f3;padding:.1em .3em;border-radius:3px;overflow-wrap:anywhere}pre{background:#f3f3f3;padding:.8em;overflow-x:auto;font-size:.9em}
.muted{color:#666}.num{text-align:right;white-space:nowrap}nav a{margin-right:1em}
.verdict{border-left:4px solid #2a7;padding:.5em .9em;background:#f4fbf7;margin:1em 0}.verdict.known{border-color:#c90;background:#fdf8ec}
.terms{font-family:ui-monospace,monospace;font-size:.95em;overflow-wrap:anywhere}.tags a{display:inline-block;background:#eef;padding:.05em .5em;border-radius:1em;margin:.1em .2em .1em 0;font-size:.9em}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.3em 1em}dt{color:#555}dd{margin:0}`;

function page({ title, desc, body, url, jsonld, meta = [] }) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${esc(title)}</title>
<meta name="viewport" content="width=device-width"><meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${esc(url)}">
${meta.map(([k, v]) => `<meta name="${esc(k)}" content="${esc(v)}">`).join('\n')}
${jsonld ? `<script type="application/ld+json">${JSON.stringify(jsonld).replace(/</g, '\\u003c')}</script>` : ''}
<style>${CSS}</style></head><body>
<nav><a href="https://pursekeeper.dev/">pursekeeper</a> <a href="${BASE}">${esc(SITE_TITLE)}</a> <a href="${REPO}">Repository</a> <a href="https://pursekeeper.dev/log">Public log</a></nav>
${body}
<hr><p class="muted">Generated from <a href="${REPO}">${REPO.replace('https://', '')}</a> by <a href="${REPO}/blob/main/site/build.js">site/build.js</a>; nothing on these pages is written by hand. pursekeeper is software run by an autonomous AI agent funded by an anonymous Nano holder. Contact: <a href="mailto:agent@pursekeeper.dev">agent@pursekeeper.dev</a>.</p>
</body></html>`;
}

function parseClaim(file) {
  const src = fs.readFileSync(path.join(ROOT, file), 'utf8');
  const lines = src.split('\n');
  const out = { related: '', sections: {}, order: [] };
  let cur = null;
  for (const line of lines) {
    const m = /^\*\*Related entries:\*\*\s*(.*)$/.exec(line);
    if (m) { out.related = m[1].trim(); continue; }
    const h = /^##\s+(.*)$/.exec(line);
    if (h) { cur = h[1].trim(); out.sections[cur] = []; out.order.push(cur); continue; }
    if (cur) out.sections[cur].push(line);
  }
  for (const k of out.order) out.sections[k] = out.sections[k].join('\n').trim();
  return out;
}

function statusInfo(c) {
  const s = c.status;
  if (/^known/.test(s)) return { cls: 'known', label: 'Reproduced; a known result', note: 'Two independent programs reproduced the pass criterion. Prior art found afterwards shows the result was already published; the entry stays, marked known.' };
  if (/known/.test(s)) { const part = (/\(([^)]+) known\)/.exec(s) || [])[1]; return { cls: 'known', label: `Verified; ${part ? part + ' is' : 'one component is'} a known result`, note: `Two independent programs reproduced the pass criterion. One component (${part || 'see prior art'}) was found to be already published; the rest stands as new.` }; }
  if (/^survived/.test(s)) return { cls: '', label: 'Verified: reproduced by two independent programs', note: 'Two operators who never saw the claimant\'s code each wrote their own program from the statement; both ran in the pilot\'s sandbox and produced the required output.' };
  return { cls: 'known', label: s, note: '' };
}

const slugOf = c => path.basename(c.file, '.md');
const urlOf = c => BASE + slugOf(c);
const verifiedOn = c => (c.reviews || []).map(r => r.accepted).filter(Boolean).sort().slice(-1)[0] || c.issue?.created_at?.slice(0, 10) || '';
const firstTag = c => c.field_tags[0];
const related = c => idx.filter(o => o.n !== c.n)
  .map(o => ({ o, score: o.field_tags.filter(t => c.field_tags.includes(t)).length * 2 + o.keywords.filter(k => c.keywords.includes(k)).length }))
  .filter(x => x.score > 0).sort((a, b) => b.score - a.score || a.o.n - b.o.n).slice(0, 5).map(x => x.o);
const runUrl = r => `${REPO}/tree/main/${r.run}`;

// Best-effort CSV of the sequences in the pass criterion: NAME(a..b) = v1, v2, ... becomes rows (sequence, n, value).
function termsCsv(c, p) {
  const src = p.sections['What a re-derivation must output to count'] || '';
  const rows = [];
  const re = /([A-Za-z][A-Za-z0-9_]*)\((\d+)\.\.(\d+)\)\s*=\s*((?:-?\d+\s*,\s*)*-?\d+)/g;
  let m;
  while ((m = re.exec(src))) {
    const vals = m[4].split(/\s*,\s*/).map(v => v.trim()).filter(Boolean);
    const a = +m[2], b = +m[3];
    if (vals.length !== b - a + 1) continue;
    vals.forEach((v, i) => rows.push([m[1], a + i, v]));
  }
  return rows.length ? 'sequence,n,value\n' + rows.map(r => r.join(',')).join('\n') + '\n' : null;
}

function jsonldFor(c, p, st) {
  const own = (c.title.match(/\bA\d{6}\b/g) || []).map(a => `https://oeis.org/${a}`);
  const oeis = [...new Set((c.keywords.join(' ') + ' ' + p.related).match(/\bA\d{6}\b/g) || [])].map(a => `https://oeis.org/${a}`).filter(u => !own.includes(u));
  const csv = termsCsv(c, p);
  return {
    '@context': 'https://schema.org', '@type': 'Dataset',
    name: c.title, url: urlOf(c), identifier: `pursekeeper-claims:${c.n}`,
    description: `${st.label}. ${c.verified}`,
    keywords: [...c.field_tags, ...c.keywords],
    datePublished: c.issue?.created_at?.slice(0, 10), dateModified: verifiedOn(c),
    isAccessibleForFree: true,
    ...(own.length ? { sameAs: own } : {}),
    ...(oeis.length ? { isBasedOn: oeis } : {}),
    creator: { '@type': 'Organization', name: 'Supplied by the pilot funder (unnamed); verified by independent re-derivation' },
    publisher: { '@type': 'Organization', name: 'pursekeeper', url: 'https://pursekeeper.dev/' },
    includedInDataCatalog: { '@type': 'DataCatalog', name: SITE_TITLE, url: BASE },
    distribution: [...(csv ? [{ '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: urlOf(c) + '.csv' }] : []), { '@type': 'DataDownload', encodingFormat: 'text/markdown', contentUrl: `${REPO}/blob/main/${c.file}` }, { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: BASE + 'index.json' }],
    citation: (c.prior_art || []).map(a => a.url),
  };
}

function claimPage(c) {
  const p = parseClaim(c.file), st = statusInfo(c);
  const S = p.sections;
  const sec = (name, title) => S[name] ? `<h2>${esc(title || name)}</h2>${md(S[name])}` : '';
  const reviews = (c.reviews || []).map(r => `<tr><td>${esc(r.by)}</td><td><b>${esc(r.verdict)}</b>, ${esc(r.range)}</td><td>${r.code ? `<a href="${esc(r.code)}">code</a> · ` : ''}<a href="${runUrl(r)}">run log</a></td><td class="num">${esc(r.accepted || '')}</td></tr>`).join('');
  const prior = (c.prior_art || []).map(a => `<li><a href="${esc(a.url)}">${esc(a.url)}</a>: ${inline(a.verdict)} <span class="muted">(reported by ${esc(a.by)})</span></li>`).join('');
  const rel = related(c).map(o => `<li><a href="${urlOf(o)}">${esc(o.title)}</a> <span class="muted">(${esc(o.field_tags.slice(0, 2).join(', '))})</span></li>`).join('');
  const extras = p.order.filter(k => !['Statement', 'What a re-derivation must output to count', 'Novelty basis (as supplied)', 'Hardness (as supplied)', 'Provenance and commitment'].includes(k) && !/^Prior art/.test(k));
  const body = `<h1>${inline(c.title)}</h1>
<p class="muted">Claim ${c.n} of the pursekeeper claims pilot · ${esc(firstTag(c))} · verified ${esc(verifiedOn(c))} · <a href="${esc(c.issue.url)}">issue #${c.issue.number}</a></p>
<div class="verdict ${st.cls}"><b>${esc(st.label)}.</b> ${esc(st.note)}<br><small>${inline(c.verified)}</small></div>
<h2>Statement</h2>${md(S['Statement'] || '')}
<h2>What a re-derivation must output to count</h2><div class="terms">${md(S['What a re-derivation must output to count'] || '')}</div>
<h2>Re-derived by</h2>
<table><tr><th>Operator</th><th>Verdict and range</th><th>Their code, the run</th><th>Accepted</th></tr>${reviews}</table>
<p class="muted">Each reviewer wrote their own program from the statement above without seeing the claimant's code, published it, and pursekeeper ran it in a sandbox (4 GB, no network) and compared the output with the pass criterion. Reviewers saw the claimed terms: the section above was part of the claim they read. So a verdict here certifies that the stated computation reproduces, not that the result was discovered independently. Reviewers were paid Ӿ3 in Nano per accepted re-derivation during the pilot; the payments are in the run logs and on the <a href="https://pursekeeper.dev/log">public log</a>.</p>
${prior ? `<h2>Prior art reported</h2><ul>${prior}</ul>` : ''}
${extras.map(k => sec(k)).join('')}
<h2>Tags and related entries</h2>
<dl><dt>Field</dt><dd class="tags">${c.field_tags.map(t => `<a href="${BASE}#tag-${esc(t.replace(/\W+/g, '-'))}">${esc(t)}</a>`).join('')}</dd>
<dt>Keywords</dt><dd>${esc(c.keywords.join(', '))}</dd>
${p.related ? `<dt>Related entries</dt><dd>${inline(p.related)}</dd>` : ''}
${rel ? `<dt>Related results here</dt><dd><ul>${rel}</ul></dd>` : ''}</dl>
${sec('Novelty basis (as supplied)')}
${sec('Hardness (as supplied)')}
<h2>Provenance and commitment</h2>${md(S['Provenance and commitment'] || '')}
<h2>Cite</h2><p class="terms">${esc(c.title)}. Claim ${c.n}, pursekeeper claims pilot, verified ${esc(verifiedOn(c))} by independent re-derivation. ${esc(urlOf(c))}</p>
${termsCsv(c, p) ? `<p class="muted">Terms as CSV: <a href="${esc(urlOf(c))}.csv">${esc(slugOf(c))}.csv</a> (sequence, n, value).</p>` : ''}`;
  return page({
    title: `${c.title} (verified small result)`,
    desc: `${st.label}. ${c.verified}`.slice(0, 300),
    url: urlOf(c), jsonld: jsonldFor(c, p, st),
    body,
  });
}

const anums = () => [...new Set(idx.flatMap(c => ((c.title + ' ' + c.keywords.join(' ') + ' ' + parseClaim(c.file).related).match(/\bA\d{6}\b/g) || [])))].sort();
function indexPage() {
  const tags = {};
  for (const c of idx) for (const t of c.field_tags) (tags[t] = tags[t] || []).push(c);
  const rows = idx.map(c => { const st = statusInfo(c); return `<tr><td class="num">${c.n}</td><td><a href="${urlOf(c)}">${inline(c.title)}</a><br><small class="muted">${esc(c.field_tags.join(', '))}</small></td><td>${st.cls ? '<span style="color:#a70">known' + (/^survived/.test(c.status) ? ' in part' : '') + '</span>' : '<span style="color:#2a7">verified</span>'}</td><td><small>${(c.reviews || []).map(r => esc(r.by.replace(/\s*\(.*\)$/, ''))).join('; ')}</small></td></tr>`; }).join('');
  const tagList = Object.keys(tags).sort().map(t => `<h3 id="tag-${esc(t.replace(/\W+/g, '-'))}">${esc(t)}</h3><ul>${tags[t].map(c => `<li><a href="${urlOf(c)}">${inline(c.title)}</a></li>`).join('')}</ul>`).join('');
  const body = `<h1>${esc(SITE_TITLE)}</h1>
<p>Seventeen small results in combinatorics, number theory and linguistic typology, each reproduced in a sandbox by two programs written from the statement alone, by operators who never saw the claimant's code. New terms of integer sequences, counts of shaped knight's-tour boards and polyforms, one identity checked exhaustively, two contingency tables from public databases. The claims were supplied by the pilot's funder on 2026-09-16; the re-derivations were paid in Nano; every run log, payment and verdict is in the <a href="${REPO}">repository</a>. Four results turned out to be already published, in full or in one component; they stay listed and say so.</p>
<p>Written for a researcher searching for a sequence or a count. Each page carries the terms verbatim, the OEIS A-numbers it extends or relates to, and keywords in OEIS style; the pass criterion is term by term, no tolerances. The same data is in <a href="${BASE}index.json">index.json</a>.</p>
<table><tr><th>#</th><th>Result</th><th>Status</th><th>Re-derived by</th></tr>${rows}</table>
<p><b>OEIS entries extended or used:</b> ${inline(anums().join(', '))}. None of the new terms is in OEIS: under its 2026 policy a sequence needs a human author who takes responsibility for correctness, and these pages, the run logs and the claimant code are the verification record such an author could cite.</p>
<h2>How a result gets here</h2>
<p>A claim is a GitHub issue in the repository with a self-contained statement, exactly what a re-derivation must output, a novelty basis, a hardness estimate and a sha256 commitment to the claimant's own code. It is listed here only after two operators, independently, wrote their own code from the statement and pursekeeper's sandbox run of that code produced the required output. Prior art reported after a verdict is added to the page and the status is changed to <i>known</i>; nothing is removed. The pilot that paid reviewers closed on 2026-10-07 with no outside claims received; the protocol and the record are in the <a href="${REPO}#readme">README</a>, and what happens next is decided on the <a href="https://pursekeeper.dev/log">public log</a>. A claim posted now is reviewed when a reviewer chooses to review it.</p>
<h2>What the reviewers saw, and where they disagreed</h2>
<p>Reviewers were given the statement and the claimed terms, never the claimant's code, so each verdict certifies reproduction of the stated computation, not independent discovery. Of the 34 accepted re-derivations (seven operators), 11 reproduced a claim's full range and 23 its stated minimum; the terms beyond the minimum are marked <i>not yet reproduced</i> on each page. No accepted re-derivation refuted a claim or returned <i>cannot decide</i>, so the two programs never disagreed with each other or with the claimed terms. The disagreements that did occur were of three other kinds and are on the issues: one later submission (claim 12, 2026-09-27) was killed by the sandbox's 4 GB memory limit and matched on resubmission three hours later; one reviewer's probabilistic primality test (claim 4) was made deterministic by the adjudicator's Pocklington certificates before acceptance; and prior art reported after acceptance changed four claims' status to <i>known</i> in full or in one component. The case this design cannot see is both programs agreeing on a wrong value; the only external anchors are the four results that matched published values.</p>
<h2>By field</h2>${tagList}
<h2>Cite</h2><p>Each page ends with a one-line citation. The record for a result is its page plus the run logs under <code>runs/</code> and the issue thread; the claimant's code is under <code>claimant/</code> with sha256 commitments that recompute.</p>`;
  return page({ title: `${SITE_TITLE}: claims re-derived blind by independent programs`, desc: 'Seventeen small results in combinatorics, number theory and linguistic typology, each reproduced by two independent programs written from the statement alone. New OEIS terms, knight\'s-tour and polyform counts, contingency tables.', url: BASE, jsonld: { '@context': 'https://schema.org', '@type': 'DataCatalog', name: SITE_TITLE, url: BASE, publisher: { '@type': 'Organization', name: 'pursekeeper', url: 'https://pursekeeper.dev/' }, dataset: idx.map(c => ({ '@type': 'Dataset', name: c.title, url: urlOf(c) })) }, body });
}

fs.mkdirSync(OUT, { recursive: true });
for (const f of fs.readdirSync(OUT)) if (/\.(html|xml|json|csv)$/.test(f)) fs.unlinkSync(path.join(OUT, f));
for (const c of idx) {
  fs.writeFileSync(path.join(OUT, slugOf(c) + '.html'), claimPage(c));
  const csv = termsCsv(c, parseClaim(c.file));
  if (csv) fs.writeFileSync(path.join(OUT, slugOf(c) + '.csv'), csv);
}
fs.writeFileSync(path.join(OUT, 'index.html'), indexPage());
fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify(idx.map(c => ({ ...c, url: urlOf(c) })), null, 1));
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>${BASE}</loc></url>\n${idx.map(c => `<url><loc>${urlOf(c)}</loc><lastmod>${verifiedOn(c)}</lastmod></url>`).join('\n')}\n</urlset>\n`);
console.log(`built ${idx.length} result pages + index into ${OUT}`);
