#!/usr/bin/env python3
"""Draw Thursday's World: one 1024x1024 front page summing up
Thursday 26 November 2026. Local tooling only; the shipped program
(main.ts) never runs this file. Run: python3 draw.py
Writes entry.png next to this file."""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
MARGIN = 26
CONTENT_W = W - 2 * MARGIN

PAPER = (248, 244, 233)
INK = (20, 20, 20)
SOFT = (74, 74, 74)
RULE = (150, 140, 120)
NAVY = (27, 58, 92)
RED = (166, 30, 30)
GOLD = (146, 104, 24)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TAG_COLORS = {
    "MIDDLE EAST": (139, 30, 30),
    "GAZA": (139, 30, 30),
    "IRAN": (139, 30, 30),
    "GULF": (139, 30, 30),
    "SYRIA": (139, 30, 30),
    "EUROPE": (27, 79, 114),
    "BRUSSELS": (27, 79, 114),
    "BRITAIN": (27, 79, 114),
    "SPAIN": (27, 79, 114),
    "GERMANY": (27, 79, 114),
    "GREECE": (27, 79, 114),
    "UNITED STATES": (30, 107, 58),
    "USA": (30, 107, 58),
    "WASHINGTON": (30, 107, 58),
    "NFL": (30, 107, 58),
    "S. AMERICA": (30, 107, 58),
    "VENEZUELA": (30, 107, 58),
    "COLOMBIA": (30, 107, 58),
    "N. KOREA": (122, 74, 18),
    "UKRAINE WAR": (122, 74, 18),
    "SPACE": (122, 74, 18),
    "CHINA": (122, 74, 18),
    "HONG KONG": (122, 74, 18),
    "PACIFIC": (122, 74, 18),
    "BANGLADESH": (122, 74, 18),
    "NEPAL": (122, 74, 18),
    "MYANMAR": (122, 74, 18),
    "AFRICA": (91, 45, 142),
    "MARKETS": (91, 45, 142),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def check_fit(lines, fnt, width, what):
    for line in lines:
        if fnt.getlength(line) > width + 0.5:
            raise SystemExit("OVERFLOW in %s: %r" % (what, line))


def draw_globe(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=color, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=1)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
          start=200, end=340, fill=color, width=1)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
          start=20, end=160, fill=color, width=1)


LEADS = [
    ("MIDDLE EAST · CONFLICT",
     "Drone strike kills 2 Italians in Kuwait; Iran denies role",
     "Two Rheinmetall technicians dead in the attack; Tehran offers a joint inquiry."),
    ("WASHINGTON · TRADE",
     "US proposes tariffs on 14 partners, China up to 40%",
     "Levies target excess capacity; the EU and Japan reject the case."),
    ("UNITED STATES · WEATHER",
     "Storms black out 800,000 on Thanksgiving",
     "Macy's 100th parade put off to Saturday; 1,000+ flights hit."),
]

# (tag, headline, sub) — every story reported on 26 November 2026.
STORIES = [
    ("MIDDLE EAST · CONFLICT",
     "Houthis hit Saudi Jazan refinery; Riyadh strikes Yemen",
     "Nepali worker killed; Saudis say they hit 50 Houthi targets."),
    ("GAZA · CONFLICT",
     "Israeli strikes kill 9 in Gaza, Hamas official among them",
     "Deputy education minister dead; ceasefire officially in force."),
    ("EUROPE · WAR",
     "Russia, Ukraine trade strikes; Trump urges Putin to pull back",
     "Kyiv says 87 missiles and drones downed overnight."),
    ("N. KOREA · SECURITY",
     "Kim Jong Un vows more nuclear weapons",
     "Tours nuclear sites; urges wider use of tactical arms."),
    ("UKRAINE WAR · DATA",
     "Leaked data: Russia has lost nearly 500,000 troops",
     "BBC analysis of leaked figures; Kremlin dismisses counts."),
    ("SYRIA · CONFLICT",
     "ISIL suicide attack kills 2 in northeast Syria",
     "Motorcycle bomber hits checkpoint in Hasakah; 5 wounded."),
    ("IRAN · ENERGY",
     "Iran faces US blockade as oil revenue falls",
     "Exports seen at zero by mid-December; convoy urged."),
    ("GULF · SHIPPING",
     "Mine scare near Hormuz tanker; Iran warns ships",
     "IRGC claims supertanker hit by mine; UK reports blast."),
    ("EUROPE · ECONOMY",
     "Spain's Hernández de Cos picked to lead the ECB",
     "Ex-Bank of Spain chief succeeds Lagarde in February 2027."),
    ("BRUSSELS · POLITICS",
     "EU leaders clash over €2 trillion budget; no deal",
     "Talks resume 17 December; Ukraine loan disputed."),
    ("BRITAIN · MIGRATION",
     "UK net migration falls to 77,000",
     "Lowest since 1997 outside the pandemic years."),
    ("BRITAIN · POLITICS",
     "UK–EU treaties published, with 10-year exit clause",
     "Extra fee to end border checks on some exports."),
    ("SPAIN · POLITICS",
     "Spain votes Sunday with the right favoured",
     "Final debate held Thursday; PP may need the far right."),
    ("GERMANY · POLITICS",
     "Merz defends Ukraine aid: Russia threatens Europe",
     "Chancellor pushes back as EU budget talks stall."),
    ("BRITAIN · DEFENCE",
     "UK contacts 100,000 veterans to boost readiness",
     "Five nations to buy 430 CV90 armoured vehicles."),
    ("GREECE · LABOUR",
     "Greek workers strike over living costs",
     "15,000 march in Athens; ferries, metro and flights hit."),
    ("USA · COURTS",
     "Judge blocks Trump's birthright citizenship limits",
     "Federal judge strikes down narrower rules; second agrees."),
    ("USA · DIPLOMACY",
     "Trump and Rutte warn Russia not to widen war",
     "Leaders meet in Florida; also discuss Iran war."),
    ("USA · MIGRATION",
     "Abrego Garcia leaves US for Spain",
     "After 20 months of litigation; deported in error in 2025."),
    ("S. AMERICA · DIPLOMACY",
     "Brazil withdraws ambassador to Argentina",
     "Milei not invited to Lula's 5 January inauguration."),
    ("VENEZUELA · POLITICS",
     "Venezuela to repeal law barring opponents",
     "Process starts 1 December; González to return from exile."),
    ("COLOMBIA · SECURITY",
     "Colombian police free 76 supermarket hostages",
     "Daylong Cartagena siege ends; one gunman killed."),
    ("NFL · SPORT",
     "Bears beat Lions 39–35 on late touchdown",
     "Williams to Odunze with 3 seconds left; streak ends."),
    ("SPACE · CHINA",
     "First Pakistani astronaut reaches Tiangong station",
     "Muhammad Zeeshan Ali arrives on Shenzhou-24."),
    ("USA · TECH",
     "Huawei found guilty of stealing US trade secrets",
     "Brooklyn jury convicts on 10 of 12 counts."),
    ("CHINA · POLITICS",
     "China investigates Shanghai party chief Chen Jining",
     "Technocrat championed AI and chips; probe opens."),
    ("HONG KONG · SOCIETY",
     "Hong Kong marks year since fire killed 168",
     "Flowers at Wang Fuk Court; families still seek answers."),
    ("PACIFIC · DIPLOMACY",
     "Australia, Solomons sign security treaty",
     "Canberra named primary partner; ends 2022 China pact."),
    ("BANGLADESH · LABOUR",
     "Bangladesh garment workers protest minimum wage",
     "Rise to 17,000 taka; unions want 18,000; 140 factories shut."),
    ("NEPAL · DISASTER",
     "Nepal begins declaring missing flood victims dead",
     "Wait cut from 12 years to about six weeks."),
    ("MYANMAR · JUSTICE",
     "Myanmar rejects parts of ICJ genocide ruling",
     "Will not comply with all measures; court found it responsible."),
    ("AFRICA · HEALTH",
     "DR Congo Ebola cases pass 12,000",
     "About 5,900 dead; second-largest outbreak on record."),
    ("AFRICA · HEALTH",
     "Cheaper HIV prevention jab reaches Africa",
     "Twice-yearly lenacapavir; nearly 100% effective."),
    ("MARKETS · STOCKS",
     "Nasdaq nears bear market in AI sell-off",
     "Fell 4.6% intraday Wednesday; US markets shut Thursday."),
    ("SPACE · TECH",
     "FCC approves SpaceX plan for one million satellites",
     "Orbital data centres; Amazon opposed; debris fears cited."),
    ("BRITAIN · BUSINESS",
     "Poundland collapses into administration",
     "UK discount chain; 11,000 jobs at risk; no buyer found."),
]

TIMELINE = [
    ("02:40", "Kyiv mall"),
    ("05:15", "Ibiza tanker"),
    ("09:00", "UK migration"),
    ("11:30", "ECB pick"),
    ("14:00", "US tariffs"),
    ("16:30", "Kuwait strike"),
    ("20:00", "800k lose power"),
]


def tag_color(tag):
    region = tag.split(" · ")[0]
    return TAG_COLORS.get(region, NAVY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    f_kicker = font(SANS_B, 11)
    f_title = font(SERIF, 57)
    f_date = font(SANS_B, 19)
    f_stats = font(SANS, 11)

    kicker = "THE WORLD IN ONE DAY  ·  A FRONT PAGE OF THE DAY'S NEWS"
    d.text((W / 2, 18), kicker, font=f_kicker, fill=GOLD, anchor="ma")
    check_fit([kicker], f_kicker, CONTENT_W, "kicker")

    draw_globe(d, 78, 62, 24, NAVY)
    draw_globe(d, W - 78, 62, 24, NAVY)

    title = "THURSDAY'S WORLD"
    d.text((W / 2, 34), title, font=f_title, fill=INK, anchor="ma")
    check_fit([title], f_title, CONTENT_W - 220, "title")

    d.line([MARGIN, 106, W - MARGIN, 106], fill=INK, width=2)
    date_line = "THURSDAY, 26 NOVEMBER 2026"
    d.text((W / 2, 114), date_line, font=f_date, fill=RED, anchor="ma")
    check_fit([date_line], f_date, CONTENT_W, "date")

    stats = "39 STORIES  ·  5 REGIONS  ·  20+ FIELDS  —  EVERY STORY REPORTED ON THIS DAY"
    d.text((W / 2, 140), stats, font=f_stats, fill=SOFT, anchor="ma")
    check_fit([stats], f_stats, CONTENT_W, "stats")
    d.line([MARGIN, 158, W - MARGIN, 158], fill=INK, width=2)

    # ---- Lead stories ----
    lead_y = 170
    lead_h = 130
    lead_w = (CONTENT_W - 2 * 12) // 3
    f_lead_num = font(SERIF, 26)
    f_lead_head = font(SANS_B, 15)
    f_lead_sub = font(SANS, 10)
    for i, (tag, head, sub) in enumerate(LEADS):
        x = MARGIN + i * (lead_w + 12)
        d.rectangle([x, lead_y, x + lead_w, lead_y + lead_h],
                    outline=RULE, width=1)
        d.rectangle([x, lead_y, x + lead_w, lead_y + 4],
                    fill=tag_color(tag))
        d.text((x + 10, lead_y + 12), "%02d" % (i + 1),
               font=f_lead_num, fill=RED)
        f_tag = font(SANS_B, 9)
        d.text((x + 52, lead_y + 22), tag, font=f_tag,
               fill=tag_color(tag))
        head_lines = wrap(head, f_lead_head, lead_w - 20)
        check_fit(head_lines, f_lead_head, lead_w - 20, "lead head %d" % i)
        y = lead_y + 46
        for line in head_lines[:3]:
            d.text((x + 10, y), line, font=f_lead_head, fill=INK)
            y += 18
        sub_lines = wrap(sub, f_lead_sub, lead_w - 20)
        check_fit(sub_lines, f_lead_sub, lead_w - 20, "lead sub %d" % i)
        y = lead_y + 100
        for line in sub_lines[:2]:
            d.text((x + 10, y), line, font=f_lead_sub, fill=SOFT)
            y += 13

    # ---- Story grid: 3 columns x 12 rows ----
    grid_y = 310
    row_h = 54
    col_w = (CONTENT_W - 2 * 12) // 3
    f_tag = font(SANS_B, 9)
    f_head = font(SANS_B, 11)
    f_sub = font(SANS, 9)
    for i, (tag, head, sub) in enumerate(STORIES):
        row, col = divmod(i, 3)
        x = MARGIN + col * (col_w + 12)
        y = grid_y + row * row_h
        d.text((x, y), tag, font=f_tag, fill=tag_color(tag))
        head_lines = wrap(head, f_head, col_w - 4)
        check_fit(head_lines, f_head, col_w - 4, "head %d" % i)
        hy = y + 12
        for line in head_lines[:2]:
            d.text((x, hy), line, font=f_head, fill=INK)
            hy += 13
        sub_lines = wrap(sub, f_sub, col_w - 4)
        check_fit(sub_lines, f_sub, col_w - 4, "sub %d" % i)
        if sub_lines:
            d.text((x, y + 39), sub_lines[0], font=f_sub, fill=SOFT)
        if row < 11:
            d.line([x, y + row_h - 6, x + col_w, y + row_h - 6],
                   fill=(214, 206, 188), width=1)

    grid_bottom = grid_y + 12 * row_h  # 958

    # ---- UTC timeline strip ----
    strip_y = 964
    strip_h = 34
    d.rectangle([MARGIN, strip_y, W - MARGIN, strip_y + strip_h],
                fill=NAVY)
    f_tl_head = font(SANS_B, 9)
    f_tl = font(SANS, 9)
    head_txt = "THE DAY IN UTC — TIMES APPROX."
    d.text((MARGIN + 10, strip_y + 11), head_txt,
           font=f_tl_head, fill=(255, 255, 255))
    head_w = f_tl_head.getlength(head_txt)
    items = ["%s  %s" % (t, label) for t, label in TIMELINE]
    tl_text = "   ·   ".join(items)
    avail = CONTENT_W - 20 - head_w - 16
    check_fit([tl_text], f_tl, avail, "timeline")
    tw = f_tl.getlength(tl_text)
    d.text((W - MARGIN - 10 - tw, strip_y + 11), tl_text,
           font=f_tl, fill=(214, 226, 240))

    # ---- Footer ----
    f_foot = font(SANS, 9)
    foot = ("All 39 stories were reported on Thursday 26 November 2026.  "
            "Sources: BBC · Reuters · Al Jazeera · The Guardian · France 24 · "
            "AP · UPI · Sky News · UN News · DW")
    d.text((W / 2, 1006), foot, font=f_foot, fill=SOFT, anchor="ma")
    check_fit([foot], f_foot, CONTENT_W, "footer")

    img.save(OUT, optimize=True)
    print("wrote %s  %dx%d  %d bytes  stories=%d"
          % (OUT, W, H, os.path.getsize(OUT), len(LEADS) + len(STORIES)))


if __name__ == "__main__":
    main()
