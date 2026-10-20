package com.kaungkyaw.airconsales.ui.dashboard

import com.kaungkyaw.airconsales.data.models.DashboardToday
import com.kaungkyaw.airconsales.ui.formatKs
import java.time.LocalDate
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale
import kotlin.math.abs

enum class Trend { UP, DOWN, FLAT, NONE }

data class Row(val label: String, val amount: String, val detail: String)

/** Everything the dashboard shows, already formatted; built from the API model in one place so it is easy to test. */
data class DashboardUi(
    val date: String,
    val total: String,
    val invoices: String,
    val change: String,
    val trend: Trend,
    val categories: List<Row>,
    val payments: List<Row>,
    val unpaidCount: String,
    val unpaidAmount: String,
    val voided: String?,
    val lastUpdated: String,
)

private val CATEGORY_LABELS = mapOf("aircon" to "Aircon", "accessory" to "Accessories", "service" to "Service")
private val METHOD_LABELS = mapOf(
    "cash" to "Cash", "bank" to "Bank", "kbzpay" to "KBZPay", "wavepay" to "WavePay", "other" to "Other",
)
private val DATE_FORMAT = DateTimeFormatter.ofPattern("EEE, d MMM yyyy", Locale.US)
private val TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm", Locale.US)

private fun count(n: Int, one: String, many: String) = "$n ${if (n == 1) one else many}"

fun DashboardToday.toUi(): DashboardUi {
    val p = changePercent
    return DashboardUi(
        date = LocalDate.parse(date).format(DATE_FORMAT),
        total = formatKs(totalAmount),
        invoices = count(invoiceCount, "invoice", "invoices"),
        change = when {
            p == null -> "No sales yesterday"
            p > 0 -> "▲ ${percent(p)} vs yesterday"
            p < 0 -> "▼ ${percent(p)} vs yesterday"
            else -> "${percent(p)} vs yesterday"
        },
        trend = when {
            p == null -> Trend.NONE
            p > 0 -> Trend.UP
            p < 0 -> Trend.DOWN
            else -> Trend.FLAT
        },
        categories = byCategory.map {
            Row(CATEGORY_LABELS[it.category] ?: it.category, formatKs(it.amount), "Qty ${it.quantity}")
        },
        payments = byPaymentMethod.map {
            Row(METHOD_LABELS[it.paymentMethod] ?: it.paymentMethod, formatKs(it.amount), count(it.invoiceCount, "invoice", "invoices"))
        },
        unpaidCount = count(unpaidCount, "invoice", "invoices"),
        unpaidAmount = formatKs(unpaidAmount),
        voided = if (voidCount > 0) count(voidCount, "sale", "sales") else null,
        // generated_at carries the Yangon offset, so this is Yangon time whatever the phone's timezone.
        lastUpdated = "Last updated " + OffsetDateTime.parse(generatedAt).format(TIME_FORMAT),
    )
}

private fun percent(p: Double) = String.format(Locale.US, "%.1f%%", abs(p))
