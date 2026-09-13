package com.supercalc;

import android.animation.ArgbEvaluator;
import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Typeface;
import android.text.TextUtils;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;
import android.view.animation.DecelerateInterpolator;
import android.view.animation.OvershootInterpolator;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

/**
 * Glass tab bar whose indicator can be dragged and snaps to the nearest tab.
 *
 * The library's own tab bar draws a refractive lens <em>over</em> the selected
 * label, which bends the glyphs and leaves them off-centre. Here the row is
 * laid out explicitly — equal cells, centre-gravity labels — and a translucent
 * indicator slides underneath the text, so the label stays crisp and centred
 * while the indicator keeps the draggable "liquid ball" behaviour.
 */
public class DraggableTabBar extends FrameLayout {

    public interface OnTabSelectedListener {
        void onTabSelected(int index);
    }

    private static final int COLOR_ACTIVE = 0xFFFFFFFF;
    private static final int COLOR_INACTIVE = 0xB8FFFFFF;

    private View indicator;
    private LinearLayout row;
    private final List<TextView> labels = new ArrayList<>();
    private final ArgbEvaluator argbEvaluator = new ArgbEvaluator();

    private OnTabSelectedListener listener;
    private int selected = 0;
    private int touchSlop;
    private float downX;
    private boolean dragging;

    public DraggableTabBar(Context context) {
        this(context, null);
    }

    public DraggableTabBar(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public DraggableTabBar(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        touchSlop = ViewConfiguration.get(context).getScaledTouchSlop();
    }

    @Override
    protected void onFinishInflate() {
        super.onFinishInflate();
        indicator = findViewById(R.id.category_indicator);
        row = findViewById(R.id.category_row);
    }

    public void setOnTabSelectedListener(OnTabSelectedListener listener) {
        this.listener = listener;
    }

    public int getSelectedIndex() {
        return selected;
    }

    /** Programmatic selection; notifies the listener when the index changes. */
    public void setSelectedIndex(int index, boolean animate) {
        applySelection(index, animate);
    }

    /** Build one equal-width, centre-aligned cell per title. */
    public void setTabs(CharSequence[] titles) {
        if (row == null) {
            return;
        }
        row.removeAllViews();
        labels.clear();
        int count = titles == null ? 0 : titles.length;
        for (int i = 0; i < count; i++) {
            final int index = i;
            TextView label = new TextView(getContext());
            label.setText(titles[i]);
            label.setTextSize(13f);
            label.setGravity(Gravity.CENTER);
            label.setSingleLine(true);
            label.setEllipsize(TextUtils.TruncateAt.END);
            label.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
            label.setTextColor(COLOR_INACTIVE);
            label.setLayoutParams(new LinearLayout.LayoutParams(
                    0, LayoutParams.MATCH_PARENT, 1f));
            label.setOnClickListener(v -> applySelection(index, true));
            row.addView(label);
            labels.add(label);
        }
        selected = 0;
        post(() -> {
            placeIndicator(selected);
            updateLabelColors(false);
        });
    }

    // ------------------------------------------------------------------
    //  Geometry
    // ------------------------------------------------------------------

    private int cellWidth() {
        if (row == null || labels.isEmpty()) {
            return 0;
        }
        return row.getWidth() / labels.size();
    }

    private int indicatorWidth(int cell) {
        return Math.max(dp(28), cell - dp(12));
    }

    private float indicatorLeftFor(int index, int cell, int width) {
        return index * cell + (cell - width) / 2f;
    }

    private int nearestIndex(float x) {
        int cell = cellWidth();
        if (cell <= 0 || labels.isEmpty()) {
            return selected;
        }
        int index = Math.round((x - cell / 2f) / cell);
        return Math.max(0, Math.min(index, labels.size() - 1));
    }

    private void ensureIndicatorSize(int cell) {
        if (indicator == null) {
            return;
        }
        int width = indicatorWidth(cell);
        LayoutParams lp = (LayoutParams) indicator.getLayoutParams();
        if (lp.width != width) {
            lp.width = width;
            indicator.setLayoutParams(lp);
        }
    }

    private void placeIndicator(int index) {
        int cell = cellWidth();
        if (cell <= 0 || indicator == null) {
            return;
        }
        ensureIndicatorSize(cell);
        indicator.animate().cancel();
        indicator.setScaleX(1f);
        indicator.setScaleY(1f);
        indicator.setTranslationX(indicatorLeftFor(index, cell, indicator.getWidth()));
    }

    private void animateIndicatorTo(int index) {
        int cell = cellWidth();
        if (cell <= 0 || indicator == null) {
            return;
        }
        ensureIndicatorSize(cell);
        indicator.animate().cancel();
        indicator.animate()
                .translationX(indicatorLeftFor(index, cell, indicator.getWidth()))
                .scaleX(1f)
                .scaleY(1f)
                .setDuration(300)
                .setInterpolator(new OvershootInterpolator(0.9f))
                .start();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        post(() -> placeIndicator(selected));
    }

    // ------------------------------------------------------------------
    //  Selection
    // ------------------------------------------------------------------

    private void applySelection(int index, boolean animate) {
        if (labels.isEmpty()) {
            return;
        }
        int clamped = Math.max(0, Math.min(index, labels.size() - 1));
        boolean changed = clamped != selected;
        selected = clamped;
        updateLabelColors(animate);
        if (animate) {
            animateIndicatorTo(selected);
        } else {
            placeIndicator(selected);
        }
        if (changed && listener != null) {
            listener.onTabSelected(selected);
        }
    }

    private void updateLabelColors(boolean animate) {
        for (int i = 0; i < labels.size(); i++) {
            TextView label = labels.get(i);
            int to = (i == selected) ? COLOR_ACTIVE : COLOR_INACTIVE;
            int from = label.getCurrentTextColor();
            if (!animate || from == to) {
                label.setTextColor(to);
                continue;
            }
            ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f);
            animator.setDuration(220);
            animator.setInterpolator(new DecelerateInterpolator());
            animator.addUpdateListener(a -> label.setTextColor(
                    (int) argbEvaluator.evaluate((float) a.getAnimatedValue(), from, to)));
            animator.start();
        }
    }

    // ------------------------------------------------------------------
    //  Drag to slide the indicator, release to snap
    // ------------------------------------------------------------------

    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        switch (ev.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                downX = ev.getX();
                dragging = false;
                break;
            case MotionEvent.ACTION_MOVE:
                if (Math.abs(ev.getX() - downX) > touchSlop) {
                    dragging = true;
                    requestParentDisallow(true);
                    return true;
                }
                break;
            default:
                break;
        }
        return false;
    }

    @Override
    public boolean onTouchEvent(MotionEvent ev) {
        int cell = cellWidth();
        if (cell <= 0 || indicator == null) {
            return super.onTouchEvent(ev);
        }
        switch (ev.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                downX = ev.getX();
                dragging = false;
                return true;
            case MotionEvent.ACTION_MOVE:
                dragging = true;
                dragIndicatorTo(ev.getX(), cell);
                return true;
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                requestParentDisallow(false);
                applySelection(nearestIndex(ev.getX()), true);
                dragging = false;
                return true;
            default:
                return super.onTouchEvent(ev);
        }
    }

    private void dragIndicatorTo(float fingerX, int cell) {
        int width = indicator.getWidth();
        if (width <= 0) {
            return;
        }
        float min = indicatorLeftFor(0, cell, width);
        float max = indicatorLeftFor(labels.size() - 1, cell, width);
        float target = Math.max(min, Math.min(max, fingerX - width / 2f));
        indicator.animate().cancel();
        indicator.setTranslationX(target);

        // Liquid stretch: the further the droplet is from the nearest cell, the
        // more it elongates towards its destination.
        float home = indicatorLeftFor(nearestIndex(fingerX), cell, width);
        float stretch = 1f + Math.min(0.22f, Math.abs(target - home) / (width * 1.6f));
        indicator.setScaleX(stretch);
        indicator.setScaleY(1f - (stretch - 1f) * 0.45f);
    }

    private void requestParentDisallow(boolean disallow) {
        if (getParent() != null) {
            getParent().requestDisallowInterceptTouchEvent(disallow);
        }
    }

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
