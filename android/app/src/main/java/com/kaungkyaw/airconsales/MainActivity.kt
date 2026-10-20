package com.kaungkyaw.airconsales

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.kaungkyaw.airconsales.ui.AirconNavHost
import com.kaungkyaw.airconsales.ui.theme.AirconSalesTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AirconSalesTheme {
                Surface(Modifier.fillMaxSize()) { AirconNavHost() }
            }
        }
    }
}
