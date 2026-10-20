package com.kaungkyaw.airconsales

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Proves Robolectric + Compose + Hilt boot the real activity. */
@RunWith(AndroidJUnit4::class)
class SetupTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun appStartsWithLabel() {
        compose.onNodeWithText("Aircon Sales").assertExists()
        if (BuildConfig.DEBUG) assertEquals("http://127.0.0.1:8000/", BuildConfig.API_BASE_URL)
    }
}
