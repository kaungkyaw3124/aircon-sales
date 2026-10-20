package com.kaungkyaw.airconsales.data.repository

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.models.LoginResponse
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/** Token, user and (task 2.5) the last dashboard, in DataStore. */
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

    private companion object {
        val TOKEN = stringPreferencesKey("token")
        val USER = stringPreferencesKey("user")
    }
}
