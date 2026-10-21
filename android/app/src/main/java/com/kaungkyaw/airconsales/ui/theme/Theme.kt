package com.kaungkyaw.airconsales.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Cards use surfaceContainerHighest; every container tone gets the same neutral card colour (D32).
private fun ColorScheme.neutral(background: Color, card: Color) = copy(
    background = background,
    surface = background,
    surfaceVariant = card,
    surfaceContainerLowest = card,
    surfaceContainerLow = card,
    surfaceContainer = card,
    surfaceContainerHigh = card,
    surfaceContainerHighest = card,
)

private val LightColorScheme = lightColorScheme(
    primary = BrandBlue,
    onPrimary = Color.White,
    secondary = BrandSky,
    onSecondary = Color.White,
).neutral(BackgroundLight, CardLight)

private val DarkColorScheme = darkColorScheme(
    primary = BrandBlueDark,
    onPrimary = Color(0xFF002D62),
    secondary = BrandSkyDark,
    onSecondary = Color(0xFF00344A),
).neutral(BackgroundDark, CardDark)

// Fixed brand colours, never the phone's wallpaper colours (D28).
@Composable
fun AirconSalesTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme,
        typography = Typography,
        content = content
    )
}
