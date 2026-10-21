package com.kaungkyaw.airconsales.ui.login

import androidx.compose.material3.Surface
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.github.takahirom.roborazzi.captureRoboImage
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
class LoginScreenshotTest {
    @get:Rule val compose = createComposeRule()

    // Message from the contract fixture rate_limited.json.
    @Test fun rateLimited() {
        compose.setContent {
            AirconSalesTheme {
                Surface {
                    LoginContent(
                        username = "owner", password = "owner123",
                        error = "Too many login attempts. Try again in 15 minutes.",
                        loading = false, canSubmit = false, retryIn = 892,
                    )
                }
            }
        }
        compose.onRoot().captureRoboImage("src/test/screenshots/login_rate_limited.png")
    }
}
