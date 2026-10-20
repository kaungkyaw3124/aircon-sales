package com.kaungkyaw.airconsales.ui

import java.util.Locale

/** 3660000 -> "3,660,000 Ks" */
fun formatKs(kyat: Long): String = String.format(Locale.US, "%,d Ks", kyat)
