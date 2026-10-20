package com.kaungkyaw.airconsales.data

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import org.junit.Assert.assertEquals
import org.junit.Test
import org.yaml.snakeyaml.Yaml
import java.io.File

fun fixture(name: String): String =
    requireNotNull(object {}.javaClass.getResource("/contract/$name.json")) { "missing fixture $name.json" }.readText()

/** Fails when a fixture in test/resources/contract drifts from its response example in docs/openapi.yaml. */
class ContractFixturesTest {
    private val examples: Map<String, JsonElement> by lazy {
        val path = System.getProperty("openapi.path") ?: "../../docs/openapi.yaml"
        val spec = File(path).also { require(it.exists()) { "contract not found at ${it.absolutePath}" } }
        mutableMapOf<String, JsonElement>().also { collect(Yaml().load<Any>(spec.readText()), false, it) }
    }

    // Response examples live under any "responses" key (paths and components); request examples are skipped.
    private fun collect(node: Any?, inResponses: Boolean, out: MutableMap<String, JsonElement>) {
        when (node) {
            is Map<*, *> -> node.forEach { (k, v) ->
                if (inResponses && k == "examples" && v is Map<*, *>) {
                    v.forEach { (name, ex) ->
                        check(out.put(name.toString(), toJson((ex as Map<*, *>)["value"])) == null) { "duplicate example name $name" }
                    }
                } else {
                    collect(v, inResponses || k == "responses", out)
                }
            }
            is List<*> -> node.forEach { collect(it, inResponses, out) }
        }
    }

    private fun toJson(v: Any?): JsonElement = when (v) {
        null -> JsonNull
        is Map<*, *> -> JsonObject(v.entries.associate { it.key.toString() to toJson(it.value) })
        is List<*> -> JsonArray(v.map(::toJson))
        is String -> JsonPrimitive(v)
        is Boolean -> JsonPrimitive(v)
        is Number -> JsonPrimitive(v)
        else -> error("unexpected YAML value ${v::class}: $v")
    }

    @Test
    fun everyResponseExampleHasAnIdenticalFixture() {
        val fixtureNames = File(object {}.javaClass.getResource("/contract")!!.toURI())
            .listFiles()!!.map { it.nameWithoutExtension }.toSet()
        assertEquals("fixture files vs contract examples", examples.keys, fixtureNames)
        examples.forEach { (name, expected) ->
            assertEquals("fixture $name.json differs from openapi.yaml", expected, Json.parseToJsonElement(fixture(name)))
        }
    }
}
