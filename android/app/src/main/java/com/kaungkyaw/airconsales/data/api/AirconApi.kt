package com.kaungkyaw.airconsales.data.api

import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.models.LoginRequest
import com.kaungkyaw.airconsales.data.models.LoginResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AirconApi {
    @POST("auth/login")
    suspend fun login(@Body body: LoginRequest): Response<LoginResponse>

    /** The bearer token is added by [AuthInterceptor]. */
    @GET("dashboard/today")
    suspend fun dashboardToday(): Response<DashboardToday>
}
