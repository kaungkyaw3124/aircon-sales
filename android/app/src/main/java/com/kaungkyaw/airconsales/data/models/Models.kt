package com.kaungkyaw.airconsales.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// Mirrors docs/openapi.yaml. Money is Long kyat, never Double.

@Serializable
data class LoginRequest(val username: String, val password: String)

@Serializable
data class LoginResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String,
    @SerialName("expires_in") val expiresIn: Long,
    val user: User,
)

@Serializable
data class User(
    val id: Long,
    val username: String,
    @SerialName("full_name") val fullName: String,
    val role: String,
)

@Serializable
data class DashboardToday(
    val date: String,
    val currency: String,
    @SerialName("total_amount") val totalAmount: Long,
    @SerialName("invoice_count") val invoiceCount: Int,
    @SerialName("void_count") val voidCount: Int,
    @SerialName("yesterday_total_amount") val yesterdayTotalAmount: Long,
    @SerialName("change_percent") val changePercent: Double?,
    @SerialName("by_category") val byCategory: List<CategoryTotal>,
    @SerialName("by_payment_method") val byPaymentMethod: List<PaymentMethodTotal>,
    @SerialName("unpaid_count") val unpaidCount: Int,
    @SerialName("unpaid_amount") val unpaidAmount: Long,
    @SerialName("generated_at") val generatedAt: String,
)

@Serializable
data class CategoryTotal(val category: String, val amount: Long, val quantity: Int)

@Serializable
data class PaymentMethodTotal(
    @SerialName("payment_method") val paymentMethod: String,
    val amount: Long,
    @SerialName("invoice_count") val invoiceCount: Int,
)

@Serializable
data class Error(val error: Detail) {
    @Serializable
    data class Detail(val code: String, val message: String)
}
