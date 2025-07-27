# GenerateSmuflMaps.cmake
#
# Safe to use via FetchContent

# Locate base path relative to this file (e.g., /cmake/ → /src/)
get_filename_component(_gen_script_dir "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
set(SMUFL_MAPPING_BASE_DIR "${_gen_script_dir}/../src")

function(generate_smuflmap_headers)
    set(FONTMAP_SOURCES_DIR "${SMUFL_MAPPING_BASE_DIR}/../source_json")
    set(OUTPUT_DIR "${SMUFL_MAPPING_BASE_DIR}/detail")
    set(PY_SCRIPT "${SMUFL_MAPPING_BASE_DIR}/../tools/generate_glyphnames_map.py")

    file(MAKE_DIRECTORY "${OUTPUT_DIR}")

    set(INPUTS
        "${FONTMAP_SOURCES_DIR}/glyphnames.json|${OUTPUT_DIR}/glyphnames_smufl.h"
        "${FONTMAP_SOURCES_DIR}/glyphnamesFinale.json|${OUTPUT_DIR}/glyphnames_finale.h"
        "${FONTMAP_SOURCES_DIR}/glyphnamesBravura.json|${OUTPUT_DIR}/glyphnames_bravura.h"
    )

    foreach(entry IN LISTS INPUTS)
        string(REPLACE "|" ";" entry_parts "${entry}")

        list(GET entry_parts 0 input_json)
        list(GET entry_parts 1 output_header)

        add_custom_command(
            OUTPUT ${output_header}
            COMMAND ${CMAKE_COMMAND} -E echo "Generating ${output_header}"
            COMMAND ${Python3_EXECUTABLE} ${PY_SCRIPT} ${input_json} ${output_header}
            DEPENDS ${input_json} ${PY_SCRIPT}
            COMMENT "Generating ${output_header} from ${input_json}"
            VERBATIM
        )

        list(APPEND GENERATED_HEADERS ${output_header})
    endforeach()

    set(SMUFL_MAPPING_GENERATED_HEADERS ${GENERATED_HEADERS} PARENT_SCOPE)
endfunction()
