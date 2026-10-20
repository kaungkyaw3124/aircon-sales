package com.kaungkyaw.airconsales.ui.login

import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.PreviewLightDark
import com.kaungkyaw.airconsales.ui.theme.AirconSalesTheme

// Android Studio previews only. Lives in src/debug so it is never in the release build.

@Composable
private fun Themed(content: @Composable () -> Unit) = AirconSalesTheme { Surface(content = content) }

@PreviewLightDark
@Composable
private fun LoginEmptyPreview() = Themed {
    LoginContent(username = "", password = "", error = null, loading = false, canSubmit = false)
}

@PreviewLightDark
@Composable
private fun LoginLoadingPreview() = Themed {
    LoginContent(username = "owner", password = "owner123", error = null, loading = true, canSubmit = false)
}

// Message from the contract fixture invalid_credentials.json.
@PreviewLightDark
@Composable
private fun LoginErrorPreview() = Themed {
    LoginContent(
        username = "owner", password = "wrong", error = "Wrong username or password.",
        loading = false, canSubmit = true,
    )
}
