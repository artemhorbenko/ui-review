#!/usr/bin/env python3
"""Turn a ui-review audit.json into a hands-off file for an AI agent or a developer.

Usage: python build_handoff.py audit.json handoff.md [--json tasks.json]

The report page is for people; this file is for whoever implements the fixes.
Plain Markdown, no design: context, sources, design tokens, rules, then one
task per issue in priority order (ICE, dependencies first) with evidence,
where (page/URL, viewport, selector, screenshot mark), current -> target
values, steps, acceptance criteria and a way to verify. Optional tasks.json
carries the same tasks for a tracker or an agent loop. Standard library only.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_audit import validate  # noqa: E402

TOKENS = re.compile(r"\{(health|qw|n|conf|crit)\}")
L = {
    "en": dict(title="Hands-off", intro="Implementation brief generated from the UI review. Work top to bottom: tasks are ordered by ICE, and a task always comes after the ones it depends on. Each task says where the change happens (page, viewport, selector, screenshot mark) and what the values are now and should become. Treat \"hypothesis\" tasks as experiments: test before building fully.",
               context="Context", finding="Main finding", maturity="UI maturity", answers="Owner answers and assumptions", skipped="skipped",
               sources="Sources", missing="Missing, so lower confidence", tokens="Design tokens", tok_name="Token", tok_val="Value", tok_use="Use",
               shots="Screenshots", shot="Screenshot", marks="marks", rules="Rules for the implementer", tasks="Tasks",
               order="Suggested order", type_o="fix", type_x="rethink", ev_o="observed", ev_h="hypothesis",
               lens="Lens", ice="ICE", type="Type", evidence="Evidence", sev="Severity", why="Evidence", steps="Steps", accept="Acceptance criteria",
               verify="How to verify", metric="Metric", effort="Effort", risk="Risk / guardrail", alt="Alternatives rejected",
               pm="Pre-mortem", hypo="Hypothesis", copy="Copy variants", top="top 3", dep="Depends on", task="Task", conf="Confidence", glossary="Glossary",
               where="Where", page="Page", vp="Viewport", sel="Selector", mark="mark", change="Current → target", prop="Property", cur="Current", tgt="Target", token="Token",
               sevs=["", "cosmetic", "minor", "major", "critical"],
               stages=["Broken", "Usable", "Consistent", "Polished", "Delightful"],
               set_to="{prop}{on} is {tgt} at {vp}",on=" of `{sel}`",every="every viewport",
               verify_default="Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.",
               default_rules=["Use the design tokens listed here; do not hard-code new colours, sizes or spacing values.",
                              "Change only the elements named under Where; check that the same component elsewhere does not break.",
                              "Verify at every viewport listed (desktop 1280×800, phone 390×844 unless stated) and in dark mode if the product has one.",
                              "Keep text contrast ≥ 4.5:1 (large text ≥ 3:1), touch targets ≥ 24×24 px (aim for 44×44), visible focus on every control.",
                              "Do not submit real forms, payments or messages while testing.",
                              "Record before/after screenshots and measured values for each task.",
                              "When a task is a hypothesis, run the cheapest test first and stop if the threshold is not met."]),
    "uk": dict(title="Hands-off", intro="Бриф на впровадження, згенерований з UI-рев'ю. Ідіть згори донизу: задачі впорядковано за ICE, і кожна стоїть після тих, від яких залежить. Для кожної задачі вказано, де зміна (сторінка, в'юпорт, селектор, позначка на скріншоті), і які значення зараз та якими мають стати. Задачі з позначкою «гіпотеза» — це експерименти: спершу перевірка, потім повна реалізація.",
               context="Контекст", finding="Головна знахідка", maturity="Зрілість UI", answers="Відповіді власника й припущення", skipped="пропущено",
               sources="Джерела", missing="Бракує, тому впевненість нижча", tokens="Дизайн-токени", tok_name="Токен", tok_val="Значення", tok_use="Де",
               shots="Скріншоти", shot="Скріншот", marks="позначки", rules="Правила для виконавця", tasks="Задачі",
               order="Рекомендований порядок", type_o="виправлення", type_x="переосмислення", ev_o="спостережено", ev_h="гіпотеза",
               lens="Лінза", ice="ICE", type="Тип", evidence="Доказ", sev="Серйозність", why="Доказ", steps="Кроки", accept="Критерії приймання",
               verify="Як перевірити", metric="Метрика", effort="Зусилля", risk="Ризик / запобіжник", alt="Відкинуті альтернативи",
               pm="Pre-mortem", hypo="Гіпотеза", copy="Варіанти тексту", top="топ-3", dep="Залежить від", task="Задача", conf="Впевненість", glossary="Глосарій",
               where="Де", page="Сторінка", vp="В'юпорт", sel="Селектор", mark="позначка", change="Зараз → ціль", prop="Властивість", cur="Зараз", tgt="Ціль", token="Токен",
               sevs=["", "косметична", "незначна", "серйозна", "критична"],
               stages=["Ламається", "Придатний", "Цілісний", "Відшліфований", "Приємний"],
               set_to="{prop}{on} = {tgt} ({vp})",on=" у `{sel}`",every="усі в'юпорти",
               verify_default="Відкрити сторінку в кожному в'юпорті з розділу «Де», зробити скріншот тієї самої області, порівняти з позначкою й повторно виміряти (scripts/inspect_ui.py --sel) кожну властивість із «Зараз → ціль».",
               default_rules=["Використовувати перелічені дизайн-токени; не вписувати нових кольорів, розмірів чи відступів вручну.",
                              "Змінювати лише елементи з розділу «Де»; перевірити, що той самий компонент деінде не зламався.",
                              "Перевіряти в кожному вказаному в'юпорті (desktop 1280×800, phone 390×844, якщо не сказано інше) і в темній темі, якщо вона є.",
                              "Контраст тексту ≥ 4.5:1 (великий текст ≥ 3:1), зони дотику ≥ 24×24 px (краще 44×44), видимий фокус на кожному елементі керування.",
                              "Не відправляти справжні форми, платежі чи повідомлення під час тестів.",
                              "Для кожної задачі зберегти скріншоти й виміряні значення до і після.",
                              "Якщо задача — гіпотеза, спершу найдешевший тест; зупинитися, якщо поріг не досягнуто."]),
}


def clean(s, ctx):
    s = TOKENS.sub(lambda m: str(ctx.get(m.group(1), m.group(0))), str(s))
    return s.replace("[[", "**").replace("]]", "**")


TAG = re.compile(r"(</?[A-Za-z][^<>]*>)")


def md(s):
    """Keep HTML tags and CSS asterisks visible: wrap tags in backticks, escape stray *."""
    parts = str(s or "").split("`")
    for i in range(0, len(parts), 2):  # outside existing code spans
        parts[i] = TAG.sub(lambda m: "`" + m.group(1) + "`", parts[i].replace("*", "\\*"))
    return "`".join(parts)


def code(s):
    v = str(s or "").replace("|", "\\|").replace("\n", " ")
    return "``" + v + "``" if "`" in v else "`" + v + "`"


def cell(s):
    return md(s).replace("|", "\\|").replace("\n", " ")


def build(a):
    lang = (a.get("lang") or "en")[:2]
    t = L.get(lang, L["en"])
    ops = a.get("ops") or []
    detail, plans = a.get("detail") or {}, a.get("plans") or {}
    lenses = a.get("lenses") or []
    sources = a.get("sources") or []
    shots = {s.get("id"): s for s in a.get("shots") or []}
    health = round(sum(l.get("s", 0) for l in lenses) / len(lenses)) if lenses else 0
    conf = round(sum({"ok": 1, "demo": .6}.get(s.get("status"), 0) for s in sources) / len(sources) * 100) if sources else 0
    qw = sum(1 for o in ops if o.get("I", 0) >= 6 and 11 - o.get("E", 0) <= 5)
    crit = sum(1 for o in ops if o.get("sev") == 4)
    ctx = dict(health=health, qw=qw, n=len(ops), conf=conf, crit=crit)
    text = a.get("text") or {}

    def shot_ref(w, oid):
        sid = w.get("shot")
        if not sid:
            return ""
        s = shots.get(sid, {})
        src = s.get("src", "")
        src = "" if src.startswith("data:") else src
        return f"{sid}" + (f" ({src})" if src else "") + f", {t['mark']} {w.get('mark') or oid}"

    tasks = []
    for i, o in enumerate(ops, 1):
        d = detail.get(str(i), {})
        p = plans.get(str(i), {})
        where = [dict(page=w.get("page", ""), url=w.get("url", ""), viewport=w.get("vp", ""), selector=w.get("sel", ""),
                      shot=w.get("shot", ""), shot_file=(lambda s: "" if s.startswith("data:") else s)(shots.get(w.get("shot"), {}).get("src", "")) if w.get("shot") else "",
                      mark=(w.get("mark") or i) if w.get("shot") else None, ref=shot_ref(w, i)) for w in d.get("where") or []]
        change = [dict(property=c.get("prop", ""), current=c.get("cur", ""), target=c.get("tgt", ""), token=c.get("token", ""), measured_by=c.get("src", "")) for c in d.get("change") or []]
        accept = list(d.get("accept") or [])
        if not accept:
            sels = list(dict.fromkeys(w["selector"] for w in where if w["selector"]))
            vps = ", ".join(dict.fromkeys(t["every"] if w["viewport"] in ("all", "усі") else w["viewport"] for w in where if w["viewport"])) or t["every"]
            for c in change:
                tgt = c["target"] + (f" ({c['token']})" if c["token"] else "")
                on = t["on"].format(sel=sels[0]) if len(sels) == 1 and re.fullmatch(r"[\w-]+", c["property"]) else ""
                accept.append(t["set_to"].format(prop=c["property"], on=on, vp=vps, tgt=tgt))
            if d.get("thr"):
                accept.append(d["thr"])
            if d.get("metric"):
                accept.append(f"{t['metric']}: {d['metric']}")
        tasks.append(dict(
            id=f"T{i:02d}", n=i, title=o.get("t"), lens=o.get("ln"), lens_id=o.get("l"),
            type="rethink" if o.get("x") == "ex" else "fix",
            evidence_type="hypothesis" if o.get("ev") == "hyp" else "observed",
            severity=o.get("sev"), impact=o.get("I"), confidence=o.get("C"), ease=o.get("E"),
            ice=o.get("I", 0) * o.get("C", 0) * o.get("E", 0),
            evidence=d.get("why", ""), where=where, change=change, steps=d.get("steps") or [], acceptance=accept,
            verify=p.get("t") or d.get("verify") or t["verify_default"], hypothesis=p.get("h", ""),
            metric=d.get("metric", ""), effort=d.get("effort", ""), risk=d.get("risk", ""),
            alternatives=d.get("alt") or [], risk_type=d.get("rtype", ""), pre_mortem=d.get("pm", ""),
            copy=d.get("copy") or [], depends_on=d.get("depends") or [],
        ))
    tasks.sort(key=lambda x: (-x["ice"], x["n"]))
    by_id, done, ordered = {tk["id"]: tk for tk in tasks}, set(), []

    def place(tk, seen=()):
        if tk["id"] in done or tk["id"] in seen:
            return
        for dep in tk["depends_on"]:
            if dep in by_id:
                place(by_id[dep], seen + (tk["id"],))
        done.add(tk["id"])
        ordered.append(tk)
    for tk in tasks:
        place(tk)
    tasks = ordered
    for rank, tk in enumerate(tasks, 1):
        tk["rank"] = rank

    out = []
    w = out.append
    tp = lambda tk: t["type_x"] if tk["type"] == "rethink" else t["type_o"]
    ev = lambda tk: t["ev_h"] if tk["evidence_type"] == "hypothesis" else t["ev_o"]
    w(f"# {t['title']}: {a.get('title', '')}".rstrip(": "))
    w("")
    w(t["intro"])
    w("")
    w(f"## {t['context']}")
    w("")
    if text.get("headline"):
        w(f"- **{t['finding']}:** {clean(text['headline'], ctx).replace('**', '')}")
    if text.get("lead"):
        w(f"- {md(clean(text['lead'], ctx))}")
    m = a.get("maturity")
    if m:
        w(f"- **{t['maturity']}:** {t['stages'][m.get('cur', 0)]}. {md(m.get('note', ''))}")
    w(f"- **{t['conf']}:** {conf}%")
    w("")
    if a.get("answers"):
        w(f"### {t['answers']}")
        w("")
        for q in a["answers"]:
            mark = f" ({t['skipped']})" if q.get("skipped") else ""
            w(f"- {q.get('q')}{mark}: {q.get('a')}")
        w("")
    if sources:
        w(f"### {t['sources']}")
        w("")
        for s in sources:
            w(f"- [{s.get('status')}] {s.get('name')}" + (f" — {s['note']}" if s.get("note") else ""))
        miss = [s.get("name") for s in sources if s.get("status") == "no"]
        if miss:
            w("")
            w(f"{t['missing']}: {', '.join(miss)}.")
        w("")
    if a.get("tokens"):
        w(f"### {t['tokens']}")
        w("")
        w(f"| {t['tok_name']} | {t['tok_val']} | {t['tok_use']} |")
        w("|---|---|---|")
        for tok in a["tokens"]:
            w(f"| {code(tok.get('name'))} | {code(tok.get('value'))} | {cell(tok.get('use'))} |")
        w("")
    if shots:
        w(f"### {t['shots']}")
        w("")
        for sid, s in shots.items():
            src = s.get("src", "")
            src = "" if src.startswith("data:") else src
            nums = ", ".join(str(mk.get("n")) for mk in s.get("marks") or [])
            w(f"- `{sid}` — {s.get('cap', '')}" + (f" · {s['vp']}" if s.get("vp") else "") + (f" · {s['url']}" if s.get("url") else "") + (f" · `{src}`" if src else "") + (f" · {t['marks']}: {nums}" if nums else ""))
        w("")
    w(f"## {t['rules']}")
    w("")
    for r in (a.get("rules") or t["default_rules"]):
        w(f"- {r}")
    w("")
    w(f"## {t['order']}")
    w("")
    w(f"| # | ID | {t['task']} | {t['sev']} | {t['ice']} | {t['type']} | {t['evidence']} |")
    w("|---|---|---|---|---|---|---|")
    for tk in tasks:
        top = f" ({t['top']})" if tk["rank"] <= 3 else ""
        w(f"| {tk['rank']} | {tk['id']} | {cell(tk['title'])}{top} | {tk['severity']} {t['sevs'][tk['severity'] or 0]} | {tk['ice']} | {tp(tk)} | {ev(tk)} |")
    w("")
    w(f"## {t['tasks']}")
    for tk in tasks:
        w("")
        w(f"### {tk['rank']}. {tk['id']} — {md(tk['title'])}")
        w("")
        w(f"- {t['lens']}: {tk['lens']} · {t['sev']}: {tk['severity']} {t['sevs'][tk['severity'] or 0]} · {t['ice']} {tk['ice']} = {tk['impact']}×{tk['confidence']}×{tk['ease']} · {t['type']}: {tp(tk)} · {ev(tk)}")
        if tk["effort"]:
            w(f"- {t['effort']}: {tk['effort']}")
        if tk["depends_on"]:
            w(f"- {t['dep']}: {', '.join(tk['depends_on'])}")
        w("")
        if tk["evidence"]:
            w(f"**{t['why']}.** {md(tk['evidence'])}")
            w("")
        if tk["hypothesis"]:
            w(f"**{t['hypo']}.** {md(tk['hypothesis'])}")
            w("")
        if tk["where"]:
            w(f"**{t['where']}:**")
            w("")
            w(f"| {t['page']} | {t['vp']} | {t['sel']} | {t['shot']} |")
            w("|---|---|---|---|")
            for x in tk["where"]:
                pg = " · ".join(v for v in (x["page"], x["url"]) if v)
                w(f"| {cell(pg)} | {cell(x['viewport'])} | {code(x['selector']) if x['selector'] else '—'} | {cell(x['ref']) or '—'} |")
            w("")
        if tk["change"]:
            w(f"**{t['change']}:**")
            w("")
            w(f"| {t['prop']} | {t['cur']} | {t['tgt']} | {t['token']} |")
            w("|---|---|---|---|")
            for c in tk["change"]:
                w(f"| {code(c['property'])} | {cell(c['current'])} | {cell(c['target'])} | {code(c['token']) if c['token'] else '—'} |")
            w("")
        if tk["steps"]:
            w(f"**{t['steps']}:**")
            w("")
            for j, s in enumerate(tk["steps"], 1):
                w(f"{j}. {md(s)}")
            w("")
        if tk["acceptance"]:
            w(f"**{t['accept']}:**")
            w("")
            for c in tk["acceptance"]:
                w(f"- [ ] {md(c)}")
            w("")
        if tk["verify"]:
            w(f"**{t['verify']}:** {md(tk['verify'])}")
            w("")
        if tk["risk"]:
            w(f"**{t['risk']}:** {md(tk['risk'])}")
            w("")
        if tk["alternatives"]:
            w(f"**{t['alt']}:**")
            w("")
            for x in tk["alternatives"]:
                w(f"- {md(x)}")
            w("")
        if tk["pre_mortem"]:
            w(f"**{t['pm']}:** {md(tk['pre_mortem'])}")
            w("")
        if tk["copy"]:
            w(f"**{t['copy']}:**")
            w("")
            for x in tk["copy"]:
                w(f"- {md(x)}")
            w("")
    gl = a.get("glossary") or {}
    if gl:
        w(f"## {t['glossary']}")
        w("")
        for k, v in gl.items():
            w(f"- **{k}** ({v.get('g')}): {v.get('d')}")
        w("")
    return "\n".join(out).rstrip() + "\n", tasks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audit")
    ap.add_argument("out")
    ap.add_argument("--json", help="also write tasks as JSON for a tracker or an agent loop")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    with open(a.audit, encoding="utf-8") as f:
        audit = json.load(f)
    err, _ = validate(audit)
    if err and not a.force:
        for e in err:
            print("[ERROR]", e)
        print("Not built. Fix audit.json or pass --force.")
        return 1
    md, tasks = build(audit)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(md)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"title": audit.get("title"), "lang": audit.get("lang"), "tokens": audit.get("tokens") or [], "rules": audit.get("rules") or L.get((audit.get("lang") or "en")[:2], L["en"])["default_rules"], "tasks": tasks}, f, ensure_ascii=False, indent=1)
    print(f"Written {a.out} ({len(tasks)} tasks)" + (f" and {a.json}" if a.json else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
