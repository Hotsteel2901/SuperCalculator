plugins {
    id("com.android.application")
}

android {
    namespace = "com.supercalc"
    compileSdk = 34
    // NDK version - use a flexible approach
    // If a specific version is needed, uncomment and set:
    // ndkVersion = "27.0.12077973"

    defaultConfig {
        applicationId = "com.supercalc"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "AlphaV1"
        ndk {
            // Support multiple ABIs for broader device compatibility
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
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
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.coordinatorlayout:coordinatorlayout:1.2.0")
    // Use actively maintained fork of MPAndroidChart
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
}
