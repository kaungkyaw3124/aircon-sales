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
    data class Loaded(val ui: DashboardUi) : DashboardState
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
                ApiResult.NetworkError -> DashboardState.Error("Can't reach the server.")
            }
            _refreshing.value = false
        }
    }

    fun logout() {
        viewModelScope.launch { repo.logout() }
    }
}
