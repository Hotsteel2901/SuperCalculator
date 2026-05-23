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
        versionCode = 1
        versionName = "AlphaV1"
        ndk {
            abiFilters += listOf("arm64-v8a")
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
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
}
