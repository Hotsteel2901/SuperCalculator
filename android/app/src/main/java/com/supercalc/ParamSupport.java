package com.supercalc;

import android.app.Activity;
import android.graphics.Typeface;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Dynamic parameter support shared by every screen with an expression input,
 * mirroring the desktop implementation: free parameters (a, b, ...) are
 * detected in the expression, exposed as live number fields, and substituted
 * back before the expression is evaluated.
 */
public final class ParamSupport {

    private ParamSupport() { }

    private static final Set<String> KNOWN_FUNCS = new HashSet<>(Arrays.asList(
            "sin", "cos", "tan", "log", "ln", "exp", "sqrt", "abs", "floor", "ceil", "mod"));
    private static final Set<String> KNOWN_CONSTS = new HashSet<>(Arrays.asList("pi", "e"));
    private static final Set<String> INDEPENDENT_VARS = new HashSet<>(
            Arrays.asList("x", "y", "t", "theta"));

    /** Same rules as the desktop build: single letters other than x/y/t/theta. */
    public static List<String> detect(String expr) {
        String lower = expr == null ? "" : expr.toLowerCase();
        for (String fn : KNOWN_FUNCS) {
            lower = lower.replaceAll("\\b" + fn + "\\b", " ");
        }
        for (String c : KNOWN_CONSTS) {
            lower = lower.replaceAll("\\b" + c + "\\b", " ");
        }
        Set<String> found = new LinkedHashSet<>();
        Matcher m = Pattern.compile("[a-z]+").matcher(lower);
        while (m.find()) {
            String word = m.group();
            if (word.length() == 1) {
                if (!INDEPENDENT_VARS.contains(word)) found.add(word);
            } else if (!KNOWN_FUNCS.contains(word)
                    && !KNOWN_CONSTS.contains(word)
                    && !INDEPENDENT_VARS.contains(word)) {
                found.add(word);
            }
        }
        return new ArrayList<>(found);
    }

    /** Replace detected parameter names with their current field values. */
    public static String substitute(String expr, Map<String, EditText> fields) {
        if (expr == null) return "";
        String out = expr;
        for (Map.Entry<String, EditText> entry : fields.entrySet()) {
            String value = entry.getValue().getText().toString().trim();
            if (value.isEmpty()) continue;
            out = out.replaceAll("\\b" + Pattern.quote(entry.getKey()) + "\\b", "(" + value + ")");
        }
        return out;
    }

    /**
     * Rebuild the parameter row for {@code expr}. Existing values are kept for
     * parameters that are still present. Returns true when the row changed.
     */
    public static boolean rebuild(Activity activity, LinearLayout row, View hint, View scroll,
                                  Map<String, EditText> fields, String expr) {
        if (row == null || expr == null) return false;
        List<String> params = detect(expr);
        if (params.equals(new ArrayList<>(fields.keySet()))) return false;

        Map<String, String> previous = new HashMap<>();
        for (Map.Entry<String, EditText> entry : fields.entrySet()) {
            previous.put(entry.getKey(), entry.getValue().getText().toString());
        }
        row.removeAllViews();
        fields.clear();

        for (String name : params) {
            LinearLayout cell = new LinearLayout(activity);
            cell.setOrientation(LinearLayout.HORIZONTAL);
            cell.setGravity(Gravity.CENTER_VERTICAL);
            cell.setPadding(0, 0, dp(activity, 12), 0);

            TextView label = new TextView(activity);
            label.setText(name + " =");
            label.setTextSize(13f);
            label.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
            label.setTextColor(activity.getResources()
                    .getColor(R.color.m3_on_surface_variant, activity.getTheme()));
            cell.addView(label);

            EditText field = new EditText(activity);
            field.setText(previous.containsKey(name) ? previous.get(name) : "1");
            field.setTextSize(13f);
            field.setSingleLine(true);
            field.setInputType(InputType.TYPE_CLASS_NUMBER
                    | InputType.TYPE_NUMBER_FLAG_DECIMAL
                    | InputType.TYPE_NUMBER_FLAG_SIGNED);
            field.setTypeface(Typeface.MONOSPACE);
            field.setTextColor(activity.getResources()
                    .getColor(R.color.m3_on_surface, activity.getTheme()));
            field.setBackgroundColor(activity.getResources()
                    .getColor(R.color.result_bg, activity.getTheme()));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    dp(activity, 74), ViewGroup.LayoutParams.WRAP_CONTENT);
            lp.leftMargin = dp(activity, 6);
            field.setLayoutParams(lp);

            cell.addView(field);
            row.addView(cell);
            fields.put(name, field);
        }

        boolean any = !params.isEmpty();
        if (hint != null) hint.setVisibility(any ? View.VISIBLE : View.GONE);
        if (scroll != null) scroll.setVisibility(any ? View.VISIBLE : View.GONE);
        return true;
    }

    private static int dp(Activity activity, float value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
