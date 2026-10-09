#!/usr/bin/env python3
"""Recompute the statement hash printed on each https://pursekeeper.dev/verified/ page.

statement sha256: sha256 over the UTF-8 bytes of the canonical form

    ## Statement\n\n<body>\n\n## What a re-derivation must output to count\n\n<body>\n

where each <body> is that section of the claim file (claims/NN-*.md) with leading and trailing
whitespace removed. These two sections are the text the reviewers worked from.
file sha256: sha256 of the claim file's bytes as committed.

Usage:
    python3 site/statement-hash.py claims/01-*.md [more files]
    python3 site/statement-hash.py --check-issue claims/01-*.md     # also compare the two sections with the GitHub issue body
    git show <snapshot>:claims/01-derangements-avoiding-1234.md | python3 site/statement-hash.py -
No dependencies beyond the standard library.
"""
import hashlib, json, re, sys, urllib.request

SECTIONS = ('Statement', 'What a re-derivation must output to count')
REPO = 'pursekeeper/claims'


def section(text, name):
    m = re.search(r'^## ' + re.escape(name) + r'\s*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    return m.group(1).strip() if m else None


def canonical(text):
    bodies = [section(text, s) for s in SECTIONS]
    if any(b is None for b in bodies):
        raise SystemExit('a required section is missing: ' + ', '.join(s for s, b in zip(SECTIONS, bodies) if b is None))
    return '\n\n'.join(f'## {s}\n\n{b}' for s, b in zip(SECTIONS, bodies)) + '\n'


def issue_number(text):
    m = re.search(r'Issue: \[#(\d+)\]', text)
    return int(m.group(1)) if m else None


def main(argv):
    check = '--check-issue' in argv
    files = [a for a in argv if a != '--check-issue'] or ['-']
    bad = 0
    for f in files:
        raw = sys.stdin.buffer.read() if f == '-' else open(f, 'rb').read()
        text = raw.decode('utf-8')
        print(f'{f}')
        print(f'  statement sha256 {hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()}')
        print(f'  file sha256      {hashlib.sha256(raw).hexdigest()}')
        if check:
            n = issue_number(text)
            if n is None:
                print('  issue: no "Issue: [#N]" line in the file'); bad += 1; continue
            req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/issues/{n}',
                                         headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'statement-hash.py'})
            body = json.load(urllib.request.urlopen(req, timeout=30)).get('body', '')
            same = all(section(body, s) == section(text, s) for s in SECTIONS)
            print(f'  issue #{n}: the two sections are {"byte-identical" if same else "DIFFERENT"}')
            bad += 0 if same else 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
