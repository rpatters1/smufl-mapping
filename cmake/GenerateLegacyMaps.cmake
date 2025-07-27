# GenerateLegacyMaps.cmake
#
# This file is safe to use with FetchContent or from top-level CMakeLists

get_filename_component(_gen_script_dir "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
set(SMUFL_MAPPING_ROOT "${_gen_script_dir}/..")
message(STATUS "Directory: ${SMUFL_MAPPING_ROOT}")

function(generate_legacy_fontmap_headers)
    set(SOURCE_DIR "${SMUFL_MAPPING_ROOT}/source_json/legacy")
    set(FINALE_FILE "${SMUFL_MAPPING_ROOT}/source_json/glyphnamesFinale.json")
    set(PY_SCRIPT "${SMUFL_MAPPING_ROOT}/tools/generate_legacy_glyphnames_map.py")
    set(OUTPUT_DIR "${SMUFL_MAPPING_ROOT}/src/detail/legacy")

    message(STATUS "Finale File Directory: ${FINALE_FILE}")

    file(GLOB LEGACY_JSON_FILES "${SOURCE_DIR}/*.json")

    # Derive the expected output headers
    set(OUTPUT_HEADERS "")
    foreach(json_file IN LISTS LEGACY_JSON_FILES)
        get_filename_component(stem "${json_file}" NAME_WE)
        list(APPEND OUTPUT_HEADERS "${OUTPUT_DIR}/${stem}_legacy_map.h")
    endforeach()

    list(APPEND OUTPUT_HEADERS "${SMUFL_MAPPING_ROOT}/src/detail/glyphnames_legacy.h")

    file(MAKE_DIRECTORY "${OUTPUT_DIR}")

    add_custom_command(
        OUTPUT ${OUTPUT_HEADERS}
        COMMAND ${Python3_EXECUTABLE} "${PY_SCRIPT}"
        DEPENDS ${LEGACY_JSON_FILES} "${FINALE_FILE}" "${PY_SCRIPT}"
        COMMENT "Generating legacy SMuFL fontmap headers"
        VERBATIM
    )

    set(GENERATED_LEGACY_HEADERS ${OUTPUT_HEADERS} PARENT_SCOPE)
endfunction()
