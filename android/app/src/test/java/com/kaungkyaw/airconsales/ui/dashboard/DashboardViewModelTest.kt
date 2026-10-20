package com.kaungkyaw.airconsales.ui.dashboard

import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.api.AuthInterceptor
import com.kaungkyaw.airconsales.data.fixture
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.api.createApi
import com.kaungkyaw.airconsales.data.repository.SalesRepository
import com.kaungkyaw.airconsales.data.repository.SessionStore
import com.kaungkyaw.airconsales.ui.jsonResponse
import com.kaungkyaw.airconsales.ui.tempDataStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import kotlinx.coroutines.withTimeout
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Before
import org.junit.Test

class DashboardViewModelTest {
    private val server = MockWebServer()

    @Before fun setUp() = Dispatchers.setMain(UnconfinedTestDispatcher())

    @After fun tearDown() {
        Dispatchers.resetMain()
        server.shutdown()
    }

    private fun loadedUi(fixtureName: String): DashboardUi = runBlocking {
        server.enqueue(jsonResponse(200, fixtureName))
        val repo = SalesRepository(
            createApi(server.url("/").toString(), AuthInterceptor({ "token" })),
            SessionStore(tempDataStore()),
        )
        val vm = DashboardViewModel(repo)
        withTimeout(5_000) { (vm.state.first { it !is DashboardState.Loading } as DashboardState.Loaded).ui }
    }

    @Test
    fun normalDay() {
        val ui = loadedUi("normal_day")
        assertEquals("Tue, 20 Oct 2026", ui.date)
        assertEquals("3,660,000 Ks", ui.total)
        assertEquals("5 invoices", ui.invoices)
        assertEquals("▲ 20.0% vs yesterday", ui.change)
        assertEquals(Trend.UP, ui.trend)
        assertEquals(
            listOf(
                Row("Aircon", "3,300,000 Ks", "Qty 2"),
                Row("Accessories", "150,000 Ks", "Qty 5"),
                Row("Service", "210,000 Ks", "Qty 3"),
            ),
            ui.categories,
        )
        assertEquals(
            listOf(
                Row("Cash", "1,600,000 Ks", "2 invoices"),
                Row("KBZPay", "1,870,000 Ks", "1 invoice"),
                Row("WavePay", "70,000 Ks", "1 invoice"),
            ),
            ui.payments,
        )
        assertEquals("2 invoices", ui.unpaidCount)
        assertEquals("1,990,000 Ks", ui.unpaidAmount)
        assertEquals("1 sale", ui.voided)
    }

    @Test
    fun emptyDay() {
        val ui = loadedUi("empty_day")
        assertEquals("Wed, 21 Oct 2026", ui.date)
        assertEquals("0 Ks", ui.total)
        assertEquals("0 invoices", ui.invoices)
        assertEquals("No sales yesterday", ui.change)
        assertEquals(Trend.NONE, ui.trend)
        assertEquals(listOf("0 Ks", "0 Ks", "0 Ks"), ui.categories.map { it.amount })
        assertEquals(emptyList<Row>(), ui.payments)
        assertEquals("0 Ks", ui.unpaidAmount)
        assertNull("no 'Voided today' when void_count is 0", ui.voided)
    }

    @Test
    fun negativeAndZeroChange() {
        val day = ApiJson.decodeFromString<DashboardToday>(fixture("normal_day"))
        day.copy(changePercent = -12.5).toUi().let {
            assertEquals("▼ 12.5% vs yesterday", it.change)
            assertEquals(Trend.DOWN, it.trend)
        }
        day.copy(changePercent = 0.0).toUi().let {
            assertEquals("0.0% vs yesterday", it.change)
            assertEquals(Trend.FLAT, it.trend)
        }
    }
}
