package com.kaungkyaw.airconsales.ui.dashboard

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.PreviewLightDark
import com.kaungkyaw.airconsales.data.models.CategoryTotal
import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.data.models.PaymentMethodTotal
import com.kaungkyaw.airconsales.ui.theme.AirconSalesTheme

// Android Studio previews only. Lives in src/debug so it is never in the release build.

// Same values as the contract fixture normal_day.json.
private val normalDay = DashboardToday(
    date = "2026-10-20",
    currency = "MMK",
    totalAmount = 3660000,
    invoiceCount = 5,
    voidCount = 1,
    yesterdayTotalAmount = 3050000,
    changePercent = 20.0,
    byCategory = listOf(
        CategoryTotal("aircon", 3300000, 2),
        CategoryTotal("accessory", 150000, 5),
        CategoryTotal("service", 210000, 3),
    ),
    byPaymentMethod = listOf(
        PaymentMethodTotal("cash", 1600000, 2),
        PaymentMethodTotal("kbzpay", 1870000, 1),
        PaymentMethodTotal("wavepay", 70000, 1),
    ),
    unpaidCount = 2,
    unpaidAmount = 1990000,
    generatedAt = "2026-10-20T15:42:10+06:30",
)

// Same values as the contract fixture empty_day.json.
private val emptyDay = DashboardToday(
    date = "2026-10-21",
    currency = "MMK",
    totalAmount = 0,
    invoiceCount = 0,
    voidCount = 0,
    yesterdayTotalAmount = 0,
    changePercent = null,
    byCategory = listOf(
        CategoryTotal("aircon", 0, 0),
        CategoryTotal("accessory", 0, 0),
        CategoryTotal("service", 0, 0),
    ),
    byPaymentMethod = emptyList(),
    unpaidCount = 0,
    unpaidAmount = 0,
    generatedAt = "2026-10-21T08:05:00+06:30",
)

@Composable
private fun Preview(state: DashboardState) = AirconSalesTheme { DashboardContent(state) }

@PreviewLightDark
@Composable
private fun DashboardNormalDayPreview() = Preview(DashboardState.Loaded(normalDay.toUi()))

@PreviewLightDark
@Composable
private fun DashboardEmptyDayPreview() = Preview(DashboardState.Loaded(emptyDay.toUi()))

@PreviewLightDark
@Composable
private fun DashboardNegativeChangePreview() = Preview(
    DashboardState.Loaded(normalDay.copy(yesterdayTotalAmount = 4182857, changePercent = -12.5).toUi()),
)

@PreviewLightDark
@Composable
private fun DashboardLoadingPreview() = Preview(DashboardState.Loading)

@PreviewLightDark
@Composable
private fun DashboardErrorPreview() = Preview(DashboardState.Error("Server error (500)."))

@PreviewLightDark
@Composable
private fun DashboardOfflinePreview() = Preview(DashboardState.Loaded(normalDay.toUi(), offline = true))
