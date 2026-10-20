package com.kaungkyaw.airconsales.data

import com.kaungkyaw.airconsales.data.api.ApiResult
import com.kaungkyaw.airconsales.data.api.AuthInterceptor
import com.kaungkyaw.airconsales.data.api.apiCall
import com.kaungkyaw.airconsales.data.api.createApi
import com.kaungkyaw.airconsales.data.models.LoginRequest
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ApiClientTest {
    private val server = MockWebServer()
    private var token: String? = null
    private var unauthorizedCalls = 0
    private val api = createApi(server.url("/").toString(), AuthInterceptor({ token }, { unauthorizedCalls++ }))

    @After fun tearDown() = server.shutdown()

    private fun json(code: Int, name: String) =
        MockResponse().setResponseCode(code).setHeader("Content-Type", "application/json").setBody(fixture(name))

    @Test
    fun login200() = runTest {
        server.enqueue(json(200, "owner"))
        val result = apiCall { api.login(LoginRequest("owner", "pw")) }
        assertEquals("owner", (result as ApiResult.Success).data.user.username)
        val request = server.takeRequest()
        assertEquals("/auth/login", request.path)
        assertEquals("""{"username":"owner","password":"pw"}""", request.body.readUtf8())
        assertNull(request.getHeader("Authorization"))
    }

    @Test
    fun login401MapsToApiError() = runTest {
        server.enqueue(json(401, "invalid_credentials"))
        val result = apiCall { api.login(LoginRequest("owner", "bad")) }
        assertEquals(ApiResult.ApiError("invalid_credentials", "Wrong username or password.", 401), result)
        assertEquals("no token was sent, so no logout", 0, unauthorizedCalls)
    }

    @Test
    fun dashboardSendsBearerToken() = runTest {
        token = "abc.def.ghi"
        server.enqueue(json(200, "normal_day"))
        val result = apiCall { api.dashboardToday() }
        assertEquals(3660000L, (result as ApiResult.Success).data.totalAmount)
        val request = server.takeRequest()
        assertEquals("/dashboard/today", request.path)
        assertEquals("Bearer abc.def.ghi", request.getHeader("Authorization"))
    }

    @Test
    fun dashboard401CallsOnUnauthorized() = runTest {
        token = "expired"
        server.enqueue(json(401, "unauthorized"))
        assertEquals(ApiResult.ApiError("unauthorized", "Missing or invalid token.", 401), apiCall { api.dashboardToday() })
        assertEquals(1, unauthorizedCalls)
    }

    @Test
    fun nonJsonErrorBodyKeepsStatus() = runTest {
        server.enqueue(MockResponse().setResponseCode(502).setBody("<html>Bad Gateway</html>"))
        val result = apiCall { api.dashboardToday() } as ApiResult.ApiError
        assertEquals(502, result.httpStatus)
    }

    @Test
    fun serverDownIsNetworkError() = runTest {
        server.shutdown()
        assertTrue(apiCall { api.dashboardToday() } is ApiResult.NetworkError)
    }
}
