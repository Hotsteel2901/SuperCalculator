package com.supercalc;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;

/**
 * Custom Canvas-based 3D surface renderer for z = f(x,y).
 * Renders a wireframe mesh with simple perspective projection.
 * Supports touch-drag rotation and pinch-to-zoom.
 */
public class Surface3DView extends View {

    private float[][] zValues;
    private float xMin = -10f, xMax = 10f;
    private float yMin = -10f, yMax = 10f;
    private float zMin = -10f, zMax = 10f;

    private float rotX = 25f; // rotation around X axis (degrees)
    private float rotY = -35f; // rotation around Y axis (degrees)
    private float scale = 1.0f;
    private static final float MIN_SCALE = 0.3f;
    private static final float MAX_SCALE = 3.0f;

    private Paint gridPaint;
    private Paint axisPaint;
    private Paint textPaint;

    private float lastTouchX, lastTouchY;
    private static final float ROT_SENSITIVITY = 0.5f;

    private ScaleGestureDetector scaleDetector;
    private boolean isZooming = false;

    public Surface3DView(Context context) {
        super(context);
        init();
    }

    public Surface3DView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        gridPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        gridPaint.setStrokeWidth(2f);

        axisPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        axisPaint.setColor(Color.parseColor("#cdd6f4"));
        axisPaint.setStrokeWidth(3f);

        textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setColor(Color.parseColor("#cdd6f4"));
        textPaint.setTextSize(28f);

        scaleDetector = new ScaleGestureDetector(getContext(), new ScaleGestureDetector.SimpleOnScaleGestureListener() {
            @Override
            public boolean onScale(ScaleGestureDetector detector) {
                scale *= detector.getScaleFactor();
                scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, scale));
                invalidate();
                return true;
            }
        });
    }

    public void setData(float[][] zValues, float xMin, float xMax, float yMin, float yMax, float zMin, float zMax) {
        this.zValues = zValues;
        this.xMin = xMin;
        this.xMax = xMax;
        this.yMin = yMin;
        this.yMax = yMax;
        this.zMin = zMin;
        this.zMax = zMax;
        invalidate();
    }

    public void resetRotation() {
        rotX = 25f;
        rotY = -35f;
        scale = 1.0f;
        invalidate();
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        scaleDetector.onTouchEvent(event);

        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                isZooming = false;
                lastTouchX = event.getX();
                lastTouchY = event.getY();
                return true;
            case MotionEvent.ACTION_POINTER_DOWN:
                isZooming = true;
                break;
            case MotionEvent.ACTION_MOVE:
                if (!isZooming && !scaleDetector.isInProgress()) {
                    float dx = event.getX() - lastTouchX;
                    float dy = event.getY() - lastTouchY;
                    rotY += dx * ROT_SENSITIVITY;
                    rotX -= dy * ROT_SENSITIVITY;
                    rotX = Math.max(-90f, Math.min(90f, rotX));
                    lastTouchX = event.getX();
                    lastTouchY = event.getY();
                    invalidate();
                }
                return true;
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_POINTER_UP:
                if (event.getPointerCount() <= 1) {
                    isZooming = false;
                    if (event.getPointerCount() == 1) {
                        lastTouchX = event.getX();
                        lastTouchY = event.getY();
                    }
                }
                break;
        }
        return super.onTouchEvent(event);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(Color.parseColor("#181825"));

        if (zValues == null || zValues.length == 0 || zValues[0].length == 0) {
            canvas.drawText("No 3D data", getWidth() / 2f - 60, getHeight() / 2f, textPaint);
            return;
        }

        int rows = zValues.length;
        int cols = zValues[0].length;

        float cx = getWidth() / 2f;
        float cy = getHeight() / 2f;
        float baseScale = Math.min(getWidth(), getHeight()) / 3.5f * scale;

        // Precompute projected points
        float[][] projX = new float[rows][cols];
        float[][] projY = new float[rows][cols];

        float radX = (float) Math.toRadians(rotX);
        float radY = (float) Math.toRadians(rotY);
        float cosX = (float) Math.cos(radX);
        float sinX = (float) Math.sin(radX);
        float cosY = (float) Math.cos(radY);
        float sinY = (float) Math.sin(radY);

        float xRange = xMax - xMin;
        float yRange = yMax - yMin;
        float zRange = zMax - zMin;
        if (zRange == 0) zRange = 1f;

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                float x = ((j / (float) Math.max(cols - 1, 1)) * xRange + xMin) / Math.max(xRange, 1f);
                float y = ((i / (float) Math.max(rows - 1, 1)) * yRange + yMin) / Math.max(yRange, 1f);
                float z = (zValues[i][j] - zMin) / zRange;

                // Rotation around Y then X
                float xr = x * cosY - z * sinY;
                float zr = x * sinY + z * cosY;
                float yr = y * cosX - zr * sinX;
                float zr2 = y * sinX + zr * cosX;

                // Perspective projection
                float distance = 2.5f;
                float persp = distance / (distance - zr2);
                projX[i][j] = cx + xr * baseScale * persp;
                projY[i][j] = cy + yr * baseScale * persp;
            }
        }

        // Draw grid lines (back to front ordering based on average depth)
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                float zNorm = (zValues[i][j] - zMin) / zRange;
                int color = heightToColor(zNorm);
                gridPaint.setColor(color);

                if (j + 1 < cols) {
                    canvas.drawLine(projX[i][j], projY[i][j], projX[i][j + 1], projY[i][j + 1], gridPaint);
                }
                if (i + 1 < rows) {
                    canvas.drawLine(projX[i][j], projY[i][j], projX[i + 1][j], projY[i + 1][j], gridPaint);
                }
            }
        }

        // Draw axes
        drawAxes(canvas, baseScale, cx, cy, cosX, sinX, cosY, sinY);
    }

    private void drawAxes(Canvas canvas, float baseScale, float cx, float cy,
                          float cosX, float sinX, float cosY, float sinY) {
        float axisLen = 1.2f;
        float[][] axes = {
            {0, 0, 0}, {axisLen, 0, 0}, // X
            {0, 0, 0}, {0, axisLen, 0}, // Y
            {0, 0, 0}, {0, 0, axisLen}  // Z
        };
        String[] labels = {"X", "Y", "Z"};
        float[] textOffsetX = {10, -10, -10};
        float[] textOffsetY = {0, -10, 10};

        for (int a = 0; a < 3; a++) {
            float[] start = axes[a * 2];
            float[] end = axes[a * 2 + 1];

            float[] p1 = projectPoint(start[0], start[1], start[2], baseScale, cx, cy, cosX, sinX, cosY, sinY);
            float[] p2 = projectPoint(end[0], end[1], end[2], baseScale, cx, cy, cosX, sinX, cosY, sinY);

            canvas.drawLine(p1[0], p1[1], p2[0], p2[1], axisPaint);
            canvas.drawText(labels[a], p2[0] + textOffsetX[a], p2[1] + textOffsetY[a], textPaint);
        }
    }

    private float[] projectPoint(float x, float y, float z, float baseScale, float cx, float cy,
                                 float cosX, float sinX, float cosY, float sinY) {
        float xr = x * cosY - z * sinY;
        float zr = x * sinY + z * cosY;
        float yr = y * cosX - zr * sinX;
        float zr2 = y * sinX + zr * cosX;
        float distance = 2.5f;
        float persp = distance / (distance - zr2);
        return new float[]{cx + xr * baseScale * persp, cy + yr * baseScale * persp};
    }

    private int heightToColor(float t) {
        // t in [0,1] -> blue (low) to cyan to green to yellow to red (high)
        t = Math.max(0f, Math.min(1f, t));
        int r, g, b;
        if (t < 0.25f) {
            // blue -> cyan
            float s = t / 0.25f;
            r = 0; g = (int) (s * 255); b = 255;
        } else if (t < 0.5f) {
            // cyan -> green
            float s = (t - 0.25f) / 0.25f;
            r = 0; g = 255; b = (int) ((1 - s) * 255);
        } else if (t < 0.75f) {
            // green -> yellow
            float s = (t - 0.5f) / 0.25f;
            r = (int) (s * 255); g = 255; b = 0;
        } else {
            // yellow -> red
            float s = (t - 0.75f) / 0.25f;
            r = 255; g = (int) ((1 - s) * 255); b = 0;
        }
        return Color.argb(255, r, g, b);
    }
}
