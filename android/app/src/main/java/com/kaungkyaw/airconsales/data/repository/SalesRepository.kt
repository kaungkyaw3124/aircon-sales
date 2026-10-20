package com.kaungkyaw.airconsales.data.repository

import com.kaungkyaw.airconsales.data.api.AirconApi
import com.kaungkyaw.airconsales.data.api.ApiResult
import com.kaungkyaw.airconsales.data.api.apiCall
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.models.LoginRequest
import com.kaungkyaw.airconsales.data.models.LoginResponse
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SalesRepository @Inject constructor(
    private val api: AirconApi,
    private val session: SessionStore,
) {
    suspend fun login(username: String, password: String): ApiResult<LoginResponse> =
        apiCall { api.login(LoginRequest(username, password)) }
            .also { if (it is ApiResult.Success) session.save(it.data) }

    suspend fun dashboardToday(): ApiResult<DashboardToday> =
        apiCall { api.dashboardToday() }
            .also { if (it is ApiResult.Success) session.saveDashboard(it.data) }

    suspend fun cachedDashboard(): DashboardToday? = session.cachedDashboard()

    suspend fun logout() = session.clear()
}
