package com.kaungkyaw.airconsales.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.kaungkyaw.airconsales.data.api.ApiResult
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.repository.SalesRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed interface DashboardState {
    data object Loading : DashboardState
    data class Error(val message: String) : DashboardState
    data class Loaded(val day: DashboardToday) : DashboardState
}

@HiltViewModel
class DashboardViewModel @Inject constructor(private val repo: SalesRepository) : ViewModel() {
    private val _state = MutableStateFlow<DashboardState>(DashboardState.Loading)
    val state: StateFlow<DashboardState> = _state

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _state.value = when (val result = repo.dashboardToday()) {
                is ApiResult.Success -> DashboardState.Loaded(result.data)
                is ApiResult.ApiError -> DashboardState.Error(result.message)
                ApiResult.NetworkError -> DashboardState.Error("Can't reach the server.")
            }
        }
    }

    fun logout() {
        viewModelScope.launch { repo.logout() }
    }
}
