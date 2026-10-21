package com.kaungkyaw.airconsales.ui.login

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.kaungkyaw.airconsales.data.api.ApiResult
import com.kaungkyaw.airconsales.data.repository.SalesRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(private val repo: SalesRepository) : ViewModel() {
    var username by mutableStateOf("")
    var password by mutableStateOf("")
    var loading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set

    /** Seconds until login is allowed again after a 429 (from `Retry-After`); 0 = not locked. */
    var retryIn by mutableIntStateOf(0)
        private set

    val canSubmit get() = !loading && retryIn == 0 && username.isNotBlank() && password.isNotEmpty()

    /** On success the saved token switches the app to the dashboard (see AirconNavHost). */
    fun login() {
        if (!canSubmit) return
        loading = true
        error = null
        viewModelScope.launch {
            when (val result = repo.login(username.trim(), password)) {
                is ApiResult.Success -> Unit
                is ApiResult.ApiError -> {
                    error = result.message
                    result.retryAfterSeconds?.let { countDown(it) }
                }
                ApiResult.NetworkError -> error = "Can't reach the server. Check the connection and try again."
            }
            loading = false
        }
    }

    private fun countDown(seconds: Int) {
        retryIn = seconds
        viewModelScope.launch {
            while (retryIn > 0) {
                delay(1_000)
                retryIn--
            }
        }
    }
}
