package com.kaungkyaw.airconsales.ui.dashboard

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.kaungkyaw.airconsales.ui.formatKs

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(vm: DashboardViewModel = hiltViewModel()) {
    val state by vm.state.collectAsState()
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Today") },
                actions = { TextButton(onClick = vm::logout) { Text("Log out") } },
            )
        },
    ) { padding ->
        val modifier = Modifier.padding(padding).padding(16.dp)
        when (val s = state) {
            DashboardState.Loading -> CircularProgressIndicator(modifier)
            is DashboardState.Error -> Text(s.message, modifier)
            is DashboardState.Loaded -> Text(formatKs(s.day.totalAmount), modifier, style = MaterialTheme.typography.displaySmall)
        }
    }
}
