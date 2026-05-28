# SuperCalculator ProGuard rules
# Keep JNI native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep CalcEngine JNI bridge
-keep class com.supercalc.CalcEngine {
    *;
}

# MPAndroidChart
-dontwarn com.github.mikephil.charting.**
-keep class com.github.mikephil.charting.** { *; }
