#!/usr/bin/env python3
"""Rebuild activity_calc.xml with bottom-navigation sections."""
import re
from pathlib import Path

SRC = Path('/tmp/activity_calc_original.xml')
OUT = Path('/workspace/android/app/src/main/res/layout/activity_calc.xml')

text = SRC.read_text(encoding='utf-8')
lines = text.splitlines()

# ---------------------------------------------------------------------------
# 1. Parse cards
# ---------------------------------------------------------------------------
cards = []
i = 0
while i < len(lines):
    line = lines[i]
    # Top-level MaterialCardView cards are indented with 12 spaces
    if line.startswith('            <com.google.android.material.card.MaterialCardView'):
        start = i
        depth = 1
        i += 1
        while i < len(lines) and depth > 0:
            l = lines[i]
            if 'com.google.android.material.card.MaterialCardView' in l:
                if l.strip().startswith('<com.google.android.material.card.MaterialCardView'):
                    depth += 1
                elif l.strip().startswith('</com.google.android.material.card.MaterialCardView'):
                    depth -= 1
            i += 1
        end = i  # exclusive
        # Determine title from first TextView text="@string/..."
        title = None
        for j in range(start, min(end, start + 40)):
            m = re.search(r'android:text="@string/([^"]+)"', lines[j])
            if m:
                title = m.group(1)
                break
        cards.append((start, end, title, lines[start:end]))
    else:
        i += 1

# ---------------------------------------------------------------------------
# 2. Classify cards into sections
# ---------------------------------------------------------------------------
SECTION_ASSIGNMENT = {
    # Calculate
    'expr_label': 'calculate',
    'results': 'calculate',
    'quick_select': 'calculate',
    'custom_func_title': 'calculate',
    'history_title': 'calculate',
    'parameters': 'calculate',
    'operations': 'calculate',

    # Plot / Visualisation
    'ode_solver': 'plot',
    'ode_compare': 'plot',
    'direction_field': 'plot',
    'vector_field': 'plot',
    'contour_plot': 'plot',
    'volume_revolution': 'plot',
    'nonlinear_system': 'plot',
    'parametric_label': 'plot',
    'polar_label': 'plot',
    'implicit_label': 'plot',

    # Statistics / Data
    'statistics_calculator': 'stats',
    'function_graph': 'stats',
    'stat_dist_title': 'stats',
    'curve_fitting': 'stats',
    'data_import_title': 'stats',
    'interp_title': 'stats',

    # Tools / Utilities
    'sparse_matrix_title': 'tools',
    'conv_title': 'tools',
    'matrix_operations': 'tools',
    'number_theory': 'tools',
    'bitwise_title': 'tools',
    'base_converter': 'tools',
    'unit_converter': 'tools',
    'cal_title': 'tools',
    'prob_title': 'tools',
    'fin_title': 'tools',
    'laplace_title': 'tools',
}

sections = {'calculate': [], 'plot': [], 'stats': [], 'tools': []}
for card in cards:
    title = card[2]
    section = SECTION_ASSIGNMENT.get(title)
    if section is None:
        print(f"Warning: unclassified card '{title}', defaulting to tools")
        section = 'tools'
    sections[section].append(card)

print(f"Cards: calculate={len(sections['calculate'])}, plot={len(sections['plot'])}, stats={len(sections['stats'])}, tools={len(sections['tools'])}")

# ---------------------------------------------------------------------------
# 3. Rebuild layout
# ---------------------------------------------------------------------------
# Header: line 0 .. first_card.start
header_lines = lines[:cards[0][0]]

# Footer: after last card .. end, then we add BottomNavigationView before final closing tag
footer_start = cards[-1][1]
footer_lines = lines[footer_start:]

# Wrapper templates (12-space indent to match card level)
def section_open(sid):
    return f'''            <LinearLayout
                android:id="@+id/section_{sid}"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical">'''

section_close = '            </LinearLayout>'

new_lines = []
new_lines.extend(header_lines)
for sid in ('calculate', 'plot', 'stats', 'tools'):
    new_lines.append(section_open(sid))
    for card in sections[sid]:
        new_lines.extend(card[3])
    new_lines.append(section_close)
new_lines.extend(footer_lines)

# Add BottomNavigationView before the final </CoordinatorLayout> line in footer.
# Footer should be: blank/empty + </LinearLayout> + </NestedScrollView> + </CoordinatorLayout>
bottom_nav = '''    <com.google.android.material.bottomnavigation.BottomNavigationView
        android:id="@+id/bottom_navigation"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom"
        android:background="@color/void_elevated"
        app:itemIconTint="@color/m3_primary"
        app:itemTextColor="@color/m3_primary"
        app:menu="@menu/bottom_nav_menu" />
'''

# Update paddingBottom in header text before writing
full_text = '\n'.join(new_lines)
full_text = full_text.replace('android:paddingBottom="32dp"', 'android:paddingBottom="80dp"')

# Insert bottom nav before closing CoordinatorLayout
full_text = full_text.rstrip() + '\n'
full_text = full_text[:full_text.rfind('</androidx.coordinatorlayout.widget.CoordinatorLayout>')] \
            + bottom_nav \
            + full_text[full_text.rfind('</androidx.coordinatorlayout.widget.CoordinatorLayout>'):]

OUT.write_text(full_text, encoding='utf-8')
print('Layout rebuilt successfully.')
