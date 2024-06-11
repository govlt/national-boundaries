plugins {
    application
}

group = "lt.startupgov"
version = "1.0-SNAPSHOT"

repositories {
    maven {
        url = uri("https://repo.osgeo.org/repository/release/")
    }
    mavenCentral()
}

dependencies {
    implementation("com.onthegomap.planetiler:planetiler-core:0.7.0")

    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}

tasks.test {
    useJUnitPlatform()
}

application {
    mainClass = "lt.startupgov.boundaries.Main"
}