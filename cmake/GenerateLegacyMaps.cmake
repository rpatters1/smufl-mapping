# GenerateLegacyMaps.cmake
#
# This file is safe to use with FetchContent or from top-level CMakeLists

get_filename_component(_gen_script_dir "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
set(SMUFL_MAPPING_ROOT "${_gen_script_dir}/..")

function(generate_legacy_fontmap_headers)
    set(SOURCE_DIR "${SMUFL_MAPPING_ROOT}/source_json/legacy")
    set(FINALE_FILE "${SMUFL_MAPPING_ROOT}/source_json/glyphnamesFinale.json")
    set(VALIDATOR_SCRIPT "${SMUFL_MAPPING_ROOT}/tools/validate_legacy_mappings.py")
    set(DUPLICATE_SCRIPT "${SMUFL_MAPPING_ROOT}/tools/check_duplicate_codepoints.py")
    set(PY_SCRIPT "${SMUFL_MAPPING_ROOT}/tools/generate_legacy_glyphnames_map.py")
    set(OUTPUT_DIR "${SMUFL_MAPPING_ROOT}/src/detail/legacy")

    file(GLOB LEGACY_JSON_FILES "${SOURCE_DIR}/*.json")

    set(LEGACY_VALIDATION_STAMP "${CMAKE_BINARY_DIR}/legacy_mappings_validated.stamp")
    add_custom_command(
        OUTPUT "${LEGACY_VALIDATION_STAMP}"
        COMMAND ${Python3_EXECUTABLE} "${VALIDATOR_SCRIPT}" --legacy-dir "${SOURCE_DIR}"
        COMMAND ${Python3_EXECUTABLE} "${DUPLICATE_SCRIPT}" --std "${SMUFL_MAPPING_ROOT}/source_json/glyphnames.json" --finale "${SMUFL_MAPPING_ROOT}/source_json/glyphnamesFinale.json" --bravura "${SMUFL_MAPPING_ROOT}/source_json/glyphnamesBravura.json"
        COMMAND ${CMAKE_COMMAND} -E touch "${LEGACY_VALIDATION_STAMP}"
        DEPENDS
            ${LEGACY_JSON_FILES}
            "${VALIDATOR_SCRIPT}"
            "${DUPLICATE_SCRIPT}"
            "${SMUFL_MAPPING_ROOT}/source_json/glyphnames.json"
            "${SMUFL_MAPPING_ROOT}/source_json/glyphnamesFinale.json"
            "${SMUFL_MAPPING_ROOT}/source_json/glyphnamesBravura.json"
        COMMENT "Validating legacy mapping JSON"
        VERBATIM
    )
    add_custom_target(validate_legacy_json DEPENDS "${LEGACY_VALIDATION_STAMP}")

    # Derive the expected output headers
    set(OUTPUT_HEADERS "")
    foreach(json_file IN LISTS LEGACY_JSON_FILES)
        get_filename_component(stem_raw "${json_file}" NAME_WE)
        string(REPLACE " " "_" stem "${stem_raw}")
        string(TOLOWER "${stem}" stem)
        list(APPEND OUTPUT_HEADERS "${OUTPUT_DIR}/${stem}_legacy_map.h")
    endforeach()

    list(APPEND OUTPUT_HEADERS "${SMUFL_MAPPING_ROOT}/src/detail/glyphnames_legacy.h")

    file(MAKE_DIRECTORY "${OUTPUT_DIR}")

    add_custom_command(
        OUTPUT ${OUTPUT_HEADERS}
        COMMAND ${Python3_EXECUTABLE} "${PY_SCRIPT}" ${LEGACY_JSON_FILES}
        DEPENDS ${LEGACY_JSON_FILES} "${FINALE_FILE}" "${PY_SCRIPT}" "${LEGACY_VALIDATION_STAMP}"
        COMMENT "Generating legacy SMuFL fontmap headers"
        VERBATIM
    )

    set(GENERATED_LEGACY_HEADERS ${OUTPUT_HEADERS} PARENT_SCOPE)
endfunction()
