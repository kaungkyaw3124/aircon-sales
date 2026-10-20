package com.kaungkyaw.airconsales.ui

import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.kaungkyaw.airconsales.MainActivity
import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.fixture
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.repository.SessionStore
import com.kaungkyaw.airconsales.di.ConfigModule
import dagger.hilt.android.testing.BindValue
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import dagger.hilt.android.testing.UninstallModules
import kotlinx.coroutines.runBlocking
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import javax.inject.Inject
import javax.inject.Named

/** Error, Retry and offline states of the dashboard, through the real activity. */
@HiltAndroidTest
@UninstallModules(ConfigModule::class)
@Config(application = HiltTestApplication::class)
@RunWith(AndroidJUnit4::class)
class DashboardStatesTest {
    @get:Rule(order = 0) val hilt = HiltAndroidRule(this)
    @get:Rule(order = 1) val compose = createEmptyComposeRule()

    private val server = MockWebServer()

    @BindValue @JvmField @Named("apiBaseUrl") val baseUrl: String = server.url("/").toString()
    @BindValue @JvmField val dataStore: DataStore<Preferences> = tempDataStore()

    @Inject lateinit var session: SessionStore

    @Before fun setUp() {
        hilt.inject()
        session.saveOwner()
    }

    @After fun tearDown() = server.shutdown()

    @Test
    fun serverErrorShowsMessageAndRetryReloads() {
        server.enqueue(
            MockResponse().setResponseCode(500).setHeader("Content-Type", "application/json")
                .setBody("""{"error":{"code":"internal_error","message":"Something went wrong on the server."}}"""),
        )
        server.enqueue(jsonResponse(200, "normal_day"))
        ActivityScenario.launch(MainActivity::class.java)

        compose.waitForText("Something went wrong on the server.")
        compose.onNodeWithText("Retry").performClick()
        compose.waitForText("3,660,000 Ks")
        compose.onNodeWithText("Offline — showing saved data").assertDoesNotExist()
    }

    @Test
    fun networkDownWithCacheShowsBannerAndSavedNumbers() {
        runBlocking { session.saveDashboard(ApiJson.decodeFromString<DashboardToday>(fixture("normal_day"))) }
        server.shutdown()
        ActivityScenario.launch(MainActivity::class.java)

        compose.waitForText("Offline — showing saved data")
        compose.onNodeWithText("Last updated 15:42").assertExists()
        compose.onNodeWithText("3,660,000 Ks").assertExists()
    }

    @Test
    fun networkDownWithoutCacheShowsErrorState() {
        server.shutdown()
        ActivityScenario.launch(MainActivity::class.java)

        compose.waitForText("Can't reach the server. Check the connection and try again.")
        compose.onNodeWithText("Retry").assertExists()
    }

    @Test
    fun successfulLoadIsCachedForOffline() {
        server.enqueue(jsonResponse(200, "normal_day"))
        ActivityScenario.launch(MainActivity::class.java)
        compose.waitForText("3,660,000 Ks")

        assertEquals(3660000L, runBlocking { session.cachedDashboard() }?.totalAmount)
    }
}
