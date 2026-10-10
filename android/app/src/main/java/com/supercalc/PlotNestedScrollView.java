package com.supercalc;

import android.content.Context;
import android.graphics.Rect;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;

import androidx.core.widget.NestedScrollView;

/**
 * NestedScrollView used by the plot screen.
 *
 * A normal NestedScrollView can decide to intercept a mostly-vertical MOVE
 * before a chart's gesture listener has a chance to process it.  Once a touch
 * starts inside the chart, this view keeps the stream with the chart until all
 * pointers are released.  Touches that start outside the chart retain normal
 * page scrolling.
 */
public class PlotNestedScrollView extends NestedScrollView {

    private boolean chartTouchActive;
    private View chartView;

    public PlotNestedScrollView(Context context) {
        super(context);
    }

    public PlotNestedScrollView(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public PlotNestedScrollView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    @Override
    protected void onFinishInflate() {
        super.onFinishInflate();
        chartView = findInteractiveChart(this);
    }

    @Override
    public boolean onInterceptTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();

        if (action == MotionEvent.ACTION_DOWN) {
            chartTouchActive = isInsideChart(event);
        }

        if (chartTouchActive) {
            // Do this from the parent as well as from InteractiveLineChart:
            // it closes the race between the parent's DOWN dispatch and its
            // first MOVE interception attempt.
            requestDisallowInterceptTouchEvent(true);
            if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                chartTouchActive = false;
                requestDisallowInterceptTouchEvent(false);
            }
            return false;
        }

        return super.onInterceptTouchEvent(event);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (chartTouchActive) {
            // The chart child owns this stream.  Returning false here allows
            // dispatch to continue to the child while preventing this scroll
            // container from turning the same MOVE into page scrolling.
            if (event.getActionMasked() == MotionEvent.ACTION_UP
                    || event.getActionMasked() == MotionEvent.ACTION_CANCEL) {
                chartTouchActive = false;
                requestDisallowInterceptTouchEvent(false);
            }
            return false;
        }
        return super.onTouchEvent(event);
    }

    private boolean isInsideChart(MotionEvent event) {
        if (chartView == null || !chartView.isShown()) return false;

        Rect bounds = new Rect();
        chartView.getGlobalVisibleRect(bounds);
        return bounds.contains(Math.round(event.getRawX()), Math.round(event.getRawY()));
    }

    private static View findInteractiveChart(ViewGroup root) {
        for (int i = 0; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            if (child instanceof InteractiveLineChart) return child;
            if (child instanceof ViewGroup) {
                View found = findInteractiveChart((ViewGroup) child);
                if (found != null) return found;
            }
        }
        return null;
    }
}
