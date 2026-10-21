package com.kaungkyaw.airconsales.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.kaungkyaw.airconsales.R
import java.util.Locale

@Composable
fun LoginScreen(vm: LoginViewModel = hiltViewModel()) {
    LoginContent(
        username = vm.username,
        password = vm.password,
        error = vm.error,
        loading = vm.loading,
        canSubmit = vm.canSubmit,
        retryIn = vm.retryIn,
        onUsernameChange = { vm.username = it },
        onPasswordChange = { vm.password = it },
        onLogin = vm::login,
    )
}

@Composable
fun LoginContent(
    username: String,
    password: String,
    error: String?,
    loading: Boolean,
    canSubmit: Boolean,
    retryIn: Int = 0,
    onUsernameChange: (String) -> Unit = {},
    onPasswordChange: (String) -> Unit = {},
    onLogin: () -> Unit = {},
) {
    Column(
        Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
    ) {
        Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)
        OutlinedTextField(
            value = username,
            onValueChange = onUsernameChange,
            label = { Text("Username") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = password,
            onValueChange = onPasswordChange,
            label = { Text("Password") },
            singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
            modifier = Modifier.fillMaxWidth(),
        )
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        if (retryIn > 0) Text(String.format(Locale.US, "Try again in %d:%02d", retryIn / 60, retryIn % 60))
        Button(onClick = onLogin, enabled = canSubmit, modifier = Modifier.fillMaxWidth()) {
            Text("Log in")
        }
        if (loading) LinearProgressIndicator(Modifier.fillMaxWidth())
    }
}
