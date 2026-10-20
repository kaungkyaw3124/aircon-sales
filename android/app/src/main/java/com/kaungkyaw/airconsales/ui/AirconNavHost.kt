package com.kaungkyaw.airconsales.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.kaungkyaw.airconsales.data.repository.SessionStore
import com.kaungkyaw.airconsales.ui.dashboard.DashboardScreen
import com.kaungkyaw.airconsales.ui.login.LoginScreen
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

@HiltViewModel
class SessionViewModel @Inject constructor(session: SessionStore) : ViewModel() {
    /** null until DataStore has been read. */
    val loggedIn: StateFlow<Boolean?> =
        session.token.map { it != null }.stateIn(viewModelScope, SharingStarted.Eagerly, null)
}

private const val LOGIN = "login"
private const val DASHBOARD = "dashboard"

/** The saved token decides the screen: login, logout and any 401 all just change the token. */
@Composable
fun AirconNavHost(vm: SessionViewModel = hiltViewModel()) {
    val loggedIn by vm.loggedIn.collectAsState()
    val target = when (loggedIn) {
        null -> return
        true -> DASHBOARD
        false -> LOGIN
    }
    val nav = rememberNavController()
    val start = remember { target }
    NavHost(nav, startDestination = start) {
        composable(LOGIN) { LoginScreen() }
        composable(DASHBOARD) { DashboardScreen() }
    }
    LaunchedEffect(target) {
        if (nav.currentDestination?.route != target) {
            // Clear the back stack so Back never returns to the other screen (and its ViewModel is dropped).
            nav.navigate(target) { popUpTo(nav.graph.id) { inclusive = true } }
        }
    }
}
