package com.kaungkyaw.airconsales.data.repository

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.models.LoginResponse
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/** Token, user and the last loaded dashboard, in DataStore. */
@Singleton
class SessionStore @Inject constructor(private val store: DataStore<Preferences>) {
    val token: Flow<String?> = store.data.map { it[TOKEN] }

    suspend fun save(login: LoginResponse) {
        store.edit {
            it[TOKEN] = login.accessToken
            it[USER] = ApiJson.encodeToString(login.user)
        }
    }

    /** Logout: drops everything, so the next user never sees the previous user's data. */
    suspend fun clear() {
        store.edit { it.clear() }
    }

    suspend fun saveDashboard(day: DashboardToday) {
        store.edit { it[DASHBOARD] = ApiJson.encodeToString(day) }
    }

    /** The last dashboard loaded, for offline use; null if none or unreadable (e.g. after an app update). */
    suspend fun cachedDashboard(): DashboardToday? =
        store.data.first()[DASHBOARD]?.let { runCatching { ApiJson.decodeFromString<DashboardToday>(it) }.getOrNull() }

    private companion object {
        val TOKEN = stringPreferencesKey("token")
        val USER = stringPreferencesKey("user")
        val DASHBOARD = stringPreferencesKey("dashboard_today")
    }
}
