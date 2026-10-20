package com.kaungkyaw.airconsales.ui.dashboard

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.github.takahirom.roborazzi.captureRoboImage
import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.fixture
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.ui.theme.AirconSalesTheme
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** Record: .\gradlew recordRoborazziDebug   Verify: .\gradlew verifyRoborazziDebug */
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w411dp-h891dp-xhdpi")
class DashboardScreenshotTest {
    @get:Rule val compose = createComposeRule()

    private fun day(name: String) = ApiJson.decodeFromString<DashboardToday>(fixture(name))

    private fun capture(state: DashboardState, file: String) {
        compose.setContent { AirconSalesTheme { DashboardContent(state) } }
        compose.onRoot().captureRoboImage("src/test/screenshots/$file.png")
    }

    @Test fun normalDay() = capture(DashboardState.Loaded(day("normal_day").toUi()), "dashboard_normal_day")

    @Test fun emptyDay() = capture(DashboardState.Loaded(day("empty_day").toUi()), "dashboard_empty_day")

    @Test fun negativeChange() = capture(
        DashboardState.Loaded(day("normal_day").copy(yesterdayTotalAmount = 4182857, changePercent = -12.5).toUi()),
        "dashboard_negative_change",
    )
}
