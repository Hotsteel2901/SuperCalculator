plugins {
    id("com.android.application")
}

android {
    namespace = "com.supercalc"
    compileSdk = 34
    ndkVersion = "27.0.12077973"

    defaultConfig {
        applicationId = "com.supercalc"
        minSdk = 26
        targetSdk = 34
        versionCode = 2
        versionName = "1.0.1"
        ndk {
            // LiquidGlass ships prebuilt JNI code for ARM only, and its native
            // loader is not guarded, so restrict the APK to the ABIs it supports.
            abiFilters += listOf("arm64-v8a", "armeabi-v7a")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.core:core:1.13.1")
    implementation("androidx.coordinatorlayout:coordinatorlayout:1.2.0")
    // Use actively maintained fork of MPAndroidChart
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
    // iOS 26 style liquid glass for the Android View system (no Compose needed)
    implementation("com.github.QWEA0:liquidglass:v2.0.10")
}
