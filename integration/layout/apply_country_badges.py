#!/usr/bin/env python3
"""Proportional country badges and centered icon/name grouping in the TV strip."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'app/src/main/java/com/infomak/moailite/BrowseStrip.java'
s=p.read_text(encoding='utf-8')
checks=[
 ('earth icon', 'earth.setTextSize(21);', 'earth.setTextSize(18);'),
 ('earth width', 'new LayoutParams(dp(26),dp(26));', 'new LayoutParams(dp(20),dp(20));'),
 ('flag dimensions', 'new LayoutParams(dp(22),dp(16))', 'new LayoutParams(dp(20),dp(14))'),
 ('flag spacing', 'bp.setMargins(0,0,dp(4),0);', 'bp.setMargins(0,0,dp(5),0);'),
 ('country text', 'text.setTextSize(countries?12:13);', 'text.setTextSize(countries?12:13);'),
 ('text layout', 'card.addView(text,new LayoutParams(0,-2,1));', 'card.addView(text,countries?new LayoutParams(-2,-2):new LayoutParams(0,-2,1));'),
 ('card padding','card.setPadding(dp(countries?4:8),0,dp(countries?4:8),0);','card.setPadding(dp(countries?7:8),0,dp(countries?7:8),0);')
]
for name,a,b in checks:
    assert a in s,name+' anchor missing'
    s=s.replace(a,b,1)
# Prevent labels from forcing chip overflow while preserving two-line long country names.
needle='text.setMaxLines(countries?2:1);if(!countries)text.setEllipsize(android.text.TextUtils.TruncateAt.END);'
assert needle in s
s=s.replace(needle,'''text.setMaxLines(countries?2:1);
            text.setIncludeFontPadding(false);
            if(countries) {
                text.setSingleLine(false);
                text.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_SIMPLE);
                text.setEllipsize(android.text.TextUtils.TruncateAt.END);
            } else text.setEllipsize(android.text.TextUtils.TruncateAt.END);''',1)
# Keep outer edges symmetrical. The entire country badge+text group is now centered
# because the text occupies only its natural width (instead of weight=1).
p.write_text(s,encoding='utf-8')
print('MOAI country chips centered; globe 20dp, flags 20x14dp, label wraps at two lines')
