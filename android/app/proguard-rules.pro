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

# LiquidGlass views are inflated from XML by name and call into JNI
-keep class com.example.liquidglass.** { *; }
-keep class com.example.blur.** { *; }
-dontwarn com.example.liquidglass.**
-dontwarn com.example.blur.**
