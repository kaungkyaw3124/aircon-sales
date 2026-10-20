package com.kaungkyaw.airconsales.ui

import androidx.compose.ui.test.assertIsEnabled
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.kaungkyaw.airconsales.MainActivity
import com.kaungkyaw.airconsales.data.repository.SessionStore
import com.kaungkyaw.airconsales.di.ConfigModule
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import dagger.hilt.android.testing.UninstallModules
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Named

@HiltAndroidTest
@UninstallModules(ConfigModule::class)
@Config(application = HiltTestApplication::class)
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @get:Rule(order = 0) val hilt = HiltAndroidRule(this)
    @get:Rule(order = 1) val compose = createEmptyComposeRule()

    private val server = MockWebServer()

    @BindValue @JvmField @Named("apiBaseUrl") val baseUrl: String = server.url("/").toString()
    @BindValue @JvmField val dataStore: DataStore<Preferences> = tempDataStore()

    @Inject lateinit var session: SessionStore

    @After fun tearDown() = server.shutdown()

    private fun launch() {
        hilt.inject()
        ActivityScenario.launch(MainActivity::class.java)
    }

    private fun typeCredentials(password: String = "owner123") {
        compose.onNodeWithText("Username").performTextInput("owner")
        compose.onNodeWithText("Password").performTextInput(password)
    }

    @Test
    fun successfulLoginShowsDashboard() {
        server.enqueue(jsonResponse(200, "owner"))
        server.enqueue(jsonResponse(200, "normal_day"))
        launch()
        typeCredentials()
        compose.onNodeWithText("Log in").performClick()

        compose.waitForText("3,660,000 Ks")
        assertEquals("/auth/login", server.takeRequest().path)
        assertEquals(
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.c2lnbmF0dXJl",
            server.takeRequest().getHeader("Authorization"),
        )
    }

    @Test
    fun wrongPasswordShowsApiMessage() {
        server.enqueue(jsonResponse(401, "invalid_credentials"))
        launch()
        typeCredentials("wrong")
        compose.onNodeWithText("Log in").performClick()

        compose.waitForText("Wrong username or password.")
        assertNull(session.savedToken())
    }

    @Test
    fun buttonDisabledWhenFieldsEmptyAndWhileLoading() {
        server.enqueue(jsonResponse(200, "owner").setHeadersDelay(3, TimeUnit.SECONDS))
        launch()
        val button = compose.onNodeWithText("Log in")
        button.assertIsNotEnabled()
        compose.onNodeWithText("Username").performTextInput("owner")
        button.assertIsNotEnabled()
        compose.onNodeWithText("Password").performTextInput("owner123")
        button.assertIsEnabled()

        button.performClick()
        button.assertIsNotEnabled()
    }

    @Test
    fun savedTokenSkipsLogin() {
        hilt.inject()
        session.saveOwner()
        server.enqueue(jsonResponse(200, "normal_day"))
        ActivityScenario.launch(MainActivity::class.java)

        compose.waitForText("3,660,000 Ks")
        compose.onNodeWithText("Log in").assertDoesNotExist()
    }

    @Test
    fun unauthorizedOnDashboardReturnsToLogin() {
        hilt.inject()
        session.saveOwner()
        server.enqueue(jsonResponse(401, "unauthorized"))
        ActivityScenario.launch(MainActivity::class.java)

        compose.waitForText("Log in")
        assertNull(session.savedToken())
    }

    @Test
    fun logoutClearsTokenAndReturnsToLogin() {
        hilt.inject()
        session.saveOwner()
        server.enqueue(jsonResponse(200, "normal_day"))
        ActivityScenario.launch(MainActivity::class.java)
        compose.waitForText("3,660,000 Ks")

        compose.onNodeWithText("Log out").performClick()
        compose.waitForText("Log in")
        assertNull(session.savedToken())
    }
}
