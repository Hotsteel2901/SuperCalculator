package com.supercalc;

import android.content.Context;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.ViewParent;

import com.github.mikephil.charting.charts.LineChart;

/**
 * A LineChart that claims the complete touch stream before any ancestor can
 * interpret it as a scroll gesture.
 *
 * MPAndroidChart handles the actual one-finger translation and two-finger
 * pinch transform.  The important part here is the dispatch boundary: a
 * NestedScrollView/CoordinatorLayout must not receive a chart MOVE event and
 * start moving the page while MPAndroidChart is updating its viewport.
 */
public class InteractiveLineChart extends LineChart {

    public InteractiveLineChart(Context context) {
        super(context);
    }

    public InteractiveLineChart(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public InteractiveLineChart(Context context, AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
    }

    @Override
    public boolean dispatchTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN
                || action == MotionEvent.ACTION_MOVE
                || action == MotionEvent.ACTION_POINTER_DOWN
                || action == MotionEvent.ACTION_POINTER_UP) {
            disallowAncestorInterception(true);
        }

        boolean handled = super.dispatchTouchEvent(event);

        // Keep ancestors locked until the final finger leaves.  Releasing on
        // POINTER_UP would let a NestedScrollView steal the remaining finger
        // in the middle of a pinch gesture.
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
            disallowAncestorInterception(false);
        }
        return handled;
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // dispatchTouchEvent is normally sufficient, but this also covers
        // callers/frameworks that invoke the view's touch method directly.
        int action = event.getActionMasked();
        if (action != MotionEvent.ACTION_UP && action != MotionEvent.ACTION_CANCEL) {
            disallowAncestorInterception(true);
        }
        boolean handled = super.onTouchEvent(event);
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
            disallowAncestorInterception(false);
        }
        return handled;
    }

    @Override
    protected void onDetachedFromWindow() {
        // Do not leave a coordinator or scroll parent locked if the activity is
        // closed while a pointer is still down.
        disallowAncestorInterception(false);
        super.onDetachedFromWindow();
    }

    private void disallowAncestorInterception(boolean disallow) {
        ViewParent parent = getParent();
        while (parent != null) {
            parent.requestDisallowInterceptTouchEvent(disallow);
            parent = parent.getParent();
        }
    }
}
