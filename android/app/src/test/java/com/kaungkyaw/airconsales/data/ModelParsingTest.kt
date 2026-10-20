package com.kaungkyaw.airconsales.data

import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.models.Error
import com.kaungkyaw.airconsales.data.models.LoginResponse
import kotlinx.serialization.Serializable
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class ModelParsingTest {
    @Serializable
    private data class Health(val status: String)

    @Test
    fun everyFixtureParsesIntoItsModel() {
        assertEquals("ok", ApiJson.decodeFromString<Health>(fixture("ok")).status)
        assertEquals("U Kyaw Kyaw", ApiJson.decodeFromString<LoginResponse>(fixture("owner")).user.fullName)
        listOf("invalid_credentials", "unauthorized", "missing_field").forEach {
            ApiJson.decodeFromString<Error>(fixture(it))
        }
        assertNull(ApiJson.decodeFromString<DashboardToday>(fixture("empty_day")).changePercent)
    }

    @Test
    fun normalDayTotal() {
        val day = ApiJson.decodeFromString<DashboardToday>(fixture("normal_day"))
        assertEquals(3660000L, day.totalAmount)
        assertEquals(20.0, day.changePercent!!, 0.0)
        assertEquals(listOf("aircon", "accessory", "service"), day.byCategory.map { it.category })
    }
}
