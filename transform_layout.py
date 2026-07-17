#!/usr/bin/env python3
"""Wrap activity_calc.xml cards into bottom-navigation sections."""
import pathlib
import re

SRC = pathlib.Path("/workspace/android/app/src/main/res/layout/activity_calc.xml")
OUT = pathlib.Path("/workspace/android/app/src/main/res/layout/activity_calc.xml")

text = SRC.read_text(encoding="utf-8")
lines = text.splitlines()

# Container wrapper template
WRAPPER_OPEN = '            <LinearLayout\n                android:id="@+id/{}"\n                android:layout_width="match_parent"\n                android:layout_height="wrap_content"\n                android:orientation="vertical">\n'
WRAPPER_CLOSE = "            </LinearLayout>\n"

# Boundary line numbers (1-based, inclusive ranges of original card content)
SECTIONS = [
    ("section_calculate", 55, 259),
    ("section_plot", 260, 611),
    ("section_stats", 612, 708),
    ("section_tools", 709, 1155),
]


def line_start(line_no):
    """Return the character index at the start of line_no (1-based)."""
    idx = 0
    for i, line in enumerate(lines, start=1):
        if i == line_no:
            return idx
        idx += len(line) + 1  # +1 for the newline
    raise ValueError(f"line {line_no} not found")


def line_end(line_no):
    """Return the character index right after the end of line_no (1-based)."""
    idx = 0
    for i, line in enumerate(lines, start=1):
        idx += len(line) + 1
        if i == line_no:
            return idx
    raise ValueError(f"line {line_no} not found")


insertions = []
for name, start, end in SECTIONS:
    insertions.append((line_start(start), WRAPPER_OPEN.format(name)))
    insertions.append((line_end(end), WRAPPER_CLOSE))

# Apply insertions from the end of the file toward the start so positions stay valid.
insertions.sort(key=lambda x: x[0], reverse=True)
for pos, snippet in insertions:
    text = text[:pos] + snippet + text[pos:]

# Update NestedScrollView paddingBottom to leave room for bottom nav
text = text.replace('android:paddingBottom="32dp"', 'android:paddingBottom="80dp"')

# BottomNavigationView to insert before closing CoordinatorLayout
bottom_nav = """    <com.google.android.material.bottomnavigation.BottomNavigationView
        android:id="@+id/bottom_navigation"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom"
        android:background="@color/void_elevated"
        app:itemIconTint="@color/m3_primary"
        app:itemTextColor="@color/m3_primary"
        app:menu="@menu/bottom_nav_menu" />
"""

# Insert before last line (</androidx.coordinatorlayout.widget.CoordinatorLayout>)
text = text.rstrip() + "\n"
text = text[:text.rfind("</androidx.coordinatorlayout.widget.CoordinatorLayout>")] + bottom_nav + text[text.rfind("</androidx.coordinatorlayout.widget.CoordinatorLayout>"):]

OUT.write_text(text, encoding="utf-8")
print("Transformed layout written.")
