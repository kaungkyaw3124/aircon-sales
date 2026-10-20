package com.kaungkyaw.airconsales.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.kaungkyaw.airconsales.data.api.ApiResult
import com.kaungkyaw.airconsales.data.repository.SalesRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed interface DashboardState {
    data object Loading : DashboardState
    data class Error(val message: String) : DashboardState
    /** [offline]: the server could not be reached and [ui] is the last saved dashboard. */
    data class Loaded(val ui: DashboardUi, val offline: Boolean = false) : DashboardState
}

@HiltViewModel
class DashboardViewModel @Inject constructor(private val repo: SalesRepository) : ViewModel() {
    private val _state = MutableStateFlow<DashboardState>(DashboardState.Loading)
    val state: StateFlow<DashboardState> = _state
    private val _refreshing = MutableStateFlow(false)
    val refreshing: StateFlow<Boolean> = _refreshing

    init {
        load()
    }

    /** First load shows a spinner; later loads (pull to refresh) keep the numbers on screen. */
    fun load() {
        if (_state.value is DashboardState.Loaded) _refreshing.value = true else _state.value = DashboardState.Loading
        viewModelScope.launch {
            _state.value = when (val result = repo.dashboardToday()) {
                is ApiResult.Success -> DashboardState.Loaded(result.data.toUi())
                is ApiResult.ApiError -> DashboardState.Error(result.message)
                ApiResult.NetworkError -> repo.cachedDashboard()
                    ?.let { DashboardState.Loaded(it.toUi(), offline = true) }
                    ?: DashboardState.Error("Can't reach the server. Check the connection and try again.")
            }
            _refreshing.value = false
        }
    }

    fun logout() {
        viewModelScope.launch { repo.logout() }
    }
}
