package com.kaungkyaw.airconsales.data.api

import kotlinx.serialization.json.Json
import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Response
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

/** Unknown fields are ignored so a newer API does not break an older app. */
val ApiJson = Json { ignoreUnknownKeys = true }

/** Adds `Authorization: Bearer <token>` when a token is saved; calls [onUnauthorized] if that token gets a 401. */
class AuthInterceptor(
    private val token: () -> String?,
    private val onUnauthorized: () -> Unit = {},
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = token() ?: return chain.proceed(chain.request())
        val response = chain.proceed(
            chain.request().newBuilder().header("Authorization", "Bearer $token").build()
        )
        if (response.code == 401) onUnauthorized()
        return response
    }
}

fun createApi(baseUrl: String, authInterceptor: AuthInterceptor, client: OkHttpClient.Builder = OkHttpClient.Builder()): AirconApi =
    Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(client.addInterceptor(authInterceptor).build())
        .addConverterFactory(ApiJson.asConverterFactory("application/json".toMediaType()))
        .build()
        .create(AirconApi::class.java)
