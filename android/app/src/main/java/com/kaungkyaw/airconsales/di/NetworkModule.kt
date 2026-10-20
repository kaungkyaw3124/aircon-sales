package com.kaungkyaw.airconsales.di

import com.kaungkyaw.airconsales.data.api.AirconApi
import com.kaungkyaw.airconsales.data.api.AuthInterceptor
import com.kaungkyaw.airconsales.data.api.createApi
import com.kaungkyaw.airconsales.data.repository.SessionStore
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import javax.inject.Named
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun api(@Named("apiBaseUrl") baseUrl: String, session: SessionStore): AirconApi =
        // OkHttp interceptors run on OkHttp's background threads, so blocking on DataStore is fine here.
        // A 401 on a call that carried a token clears the session; the UI follows and shows login.
        createApi(
            baseUrl,
            AuthInterceptor(
                token = { runBlocking { session.token.first() } },
                onUnauthorized = { runBlocking { session.clear() } },
            ),
        )
}
