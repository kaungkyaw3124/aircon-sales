package com.kaungkyaw.airconsales.ui.dashboard

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel

@Composable
fun DashboardScreen(vm: DashboardViewModel = hiltViewModel()) {
    val state by vm.state.collectAsState()
    val refreshing by vm.refreshing.collectAsState()
    DashboardContent(state, refreshing, onRefresh = vm::load, onLogout = vm::logout)
}

private val Green = Color(0xFF2E7D32)
private val Red = Color(0xFFC62828)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardContent(
    state: DashboardState,
    refreshing: Boolean = false,
    onRefresh: () -> Unit = {},
    onLogout: () -> Unit = {},
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Today") },
                actions = { TextButton(onClick = onLogout) { Text("Log out") } },
            )
        },
    ) { padding ->
        PullToRefreshBox(refreshing, onRefresh, Modifier.padding(padding).fillMaxSize()) {
            when (state) {
                DashboardState.Loading -> CircularProgressIndicator(Modifier.align(Alignment.Center))
                is DashboardState.Error -> Column(
                    Modifier.align(Alignment.Center).padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(state.message, style = MaterialTheme.typography.bodyLarge)
                    Button(onClick = onRefresh) { Text("Retry") }
                }
                is DashboardState.Loaded -> Loaded(state.ui, state.offline)
            }
        }
    }
}

@Composable
private fun Loaded(ui: DashboardUi, offline: Boolean) {
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        if (offline) {
            Card(
                Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer,
                    contentColor = MaterialTheme.colorScheme.onErrorContainer,
                ),
            ) {
                Column(Modifier.padding(12.dp)) {
                    Text("Offline — showing saved data", style = MaterialTheme.typography.titleSmall)
                    Text(ui.lastUpdated, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
        Column {
            Text(ui.date, style = MaterialTheme.typography.labelLarge)
            Text(ui.total, style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold)
            Text(ui.invoices, style = MaterialTheme.typography.bodyLarge)
            Text(
                ui.change,
                style = MaterialTheme.typography.titleMedium,
                color = when (ui.trend) {
                    Trend.UP -> Green
                    Trend.DOWN -> Red
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                },
            )
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ui.categories.forEach { row ->
                Card(Modifier.weight(1f)) {
                    Column(Modifier.padding(12.dp)) {
                        Text(row.label, style = MaterialTheme.typography.labelLarge)
                        Text(row.amount, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                        Text(row.detail, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }

        Section("Payment methods") {
            if (ui.payments.isEmpty()) Text("No payments yet", style = MaterialTheme.typography.bodyMedium)
            ui.payments.forEach { LabelValue(it.label, "${it.amount} · ${it.detail}") }
        }

        Section("Not fully paid") {
            LabelValue(ui.unpaidCount, ui.unpaidAmount)
        }

        ui.voided?.let { Section("Voided today") { Text(it, style = MaterialTheme.typography.bodyLarge) } }
    }
}

@Composable
private fun Section(title: String, content: @Composable () -> Unit) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            content()
        }
    }
}

@Composable
private fun LabelValue(label: String, value: String) {
    Box(Modifier.fillMaxWidth()) {
        Text(label, Modifier.align(Alignment.CenterStart), style = MaterialTheme.typography.bodyLarge)
        Text(value, Modifier.align(Alignment.CenterEnd), style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Medium)
    }
}
