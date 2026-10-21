package com.kaungkyaw.airconsales.data.api

import com.kaungkyaw.airconsales.data.models.Error
import kotlinx.serialization.SerializationException
import retrofit2.Response
import java.io.IOException

sealed interface ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>
    /** [retryAfterSeconds] comes from the `Retry-After` header (sent with 429 rate_limited). */
    data class ApiError(
        val code: String,
        val message: String,
        val httpStatus: Int,
        val retryAfterSeconds: Int? = null,
    ) : ApiResult<Nothing>
    data object NetworkError : ApiResult<Nothing>
}

/** Runs a Retrofit call and maps every outcome to [ApiResult]; never throws for HTTP or IO failures. */
suspend fun <T : Any> apiCall(call: suspend () -> Response<T>): ApiResult<T> {
    val response = try {
        call()
    } catch (e: IOException) {
        return ApiResult.NetworkError
    } catch (e: SerializationException) {
        return ApiResult.ApiError("bad_response", "The server sent an unexpected response.", 200)
    }
    response.body()?.takeIf { response.isSuccessful }?.let { return ApiResult.Success(it) }
    val error = try {
        ApiJson.decodeFromString<Error>(response.errorBody()?.string().orEmpty()).error
    } catch (e: Exception) {
        // Not the shared error shape (e.g. a proxy page): keep the status, use a generic message.
        Error.Detail("http_${response.code()}", "Server error (${response.code()}).")
    }
    return ApiResult.ApiError(error.code, error.message, response.code(), response.headers()["Retry-After"]?.toIntOrNull())
}
