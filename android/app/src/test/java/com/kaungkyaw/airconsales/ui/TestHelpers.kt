package com.kaungkyaw.airconsales.ui

import androidx.compose.ui.test.junit4.ComposeTestRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import androidx.datastore.preferences.core.Preferences
import com.kaungkyaw.airconsales.data.api.ApiJson
import com.kaungkyaw.airconsales.data.fixture
import com.kaungkyaw.airconsales.data.models.LoginResponse
import com.kaungkyaw.airconsales.data.repository.SessionStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import okhttp3.mockwebserver.MockResponse
import java.io.File

/** A fresh DataStore file per test, so Hilt test components never share one. */
fun tempDataStore(): DataStore<Preferences> =
    PreferenceDataStoreFactory.create { File.createTempFile("session", ".preferences_pb").apply { delete() } }

fun jsonResponse(code: Int, fixtureName: String): MockResponse =
    MockResponse().setResponseCode(code).setHeader("Content-Type", "application/json").setBody(fixture(fixtureName))

fun SessionStore.saveOwner() = runBlocking { save(ApiJson.decodeFromString<LoginResponse>(fixture("owner"))) }

fun SessionStore.savedToken(): String? = runBlocking { token.first() }

fun ComposeTestRule.waitForText(text: String, timeoutMs: Long = 5_000) =
    waitUntil(timeoutMs) { onAllNodesWithText(text).fetchSemanticsNodes().isNotEmpty() }
