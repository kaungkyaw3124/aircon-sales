package com.kaungkyaw.airconsales.di

import com.kaungkyaw.airconsales.BuildConfig
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Named

/** Values that tests replace (with @UninstallModules + @BindValue). */
@Module
@InstallIn(SingletonComponent::class)
object ConfigModule {
    @Provides
    @Named("apiBaseUrl")
    fun apiBaseUrl(): String = BuildConfig.API_BASE_URL
}
