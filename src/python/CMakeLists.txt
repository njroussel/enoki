pybind11_add_module(
  enoki-python
  THIN_LTO OPT_SIZE

  bind.h
  common.h
  loop.h
  random.h
  tensor.h
  texture.h
  main.cpp
  implicit.cpp
  reinterpret.cpp
  bind_scalar.cpp
  bind_packet.cpp
  bind_cuda.cpp
  bind_cuda_ad.cpp
  bind_llvm.cpp
  bind_llvm_ad.cpp
  dlpack.cpp
)

target_link_libraries(enoki-python PRIVATE enoki)

if (MSVC)
  target_compile_options(enoki-python PRIVATE /wd4714) # function marked as __forceinline not inlined
endif()

# macOS: Avoid warnings about loop unrolling being disabled with -Os
target_compile_definitions(enoki-python PRIVATE "-DENOKI_UNROLL= ")

if (ENOKI_ENABLE_JIT)
  target_link_libraries(enoki-python PRIVATE enoki-jit)
  target_compile_definitions(enoki-python PRIVATE -DENOKI_ENABLE_JIT=1)

  if (NOT APPLE)
    target_compile_definitions(enoki-python PRIVATE -DENOKI_ENABLE_CUDA=1)
  endif()
endif()

if (ENOKI_ENABLE_AUTODIFF)
  target_link_libraries(enoki-python PRIVATE enoki-autodiff)
  target_compile_definitions(enoki-python PRIVATE -DENOKI_ENABLE_AUTODIFF=1)
endif()


if (ENOKI_ENABLE_PYTHON_PACKET)
  target_compile_definitions(enoki-python PRIVATE -DENOKI_ENABLE_PYTHON_PACKET=1)
endif()

set_target_properties(enoki-python PROPERTIES
  OUTPUT_NAME enoki_ext ${ENOKI_OUTPUT_DIRECTORY})

target_compile_options(enoki-python PRIVATE ${ENOKI_NATIVE_FLAGS})

if (ENOKI_MASTER_PROJECT)
  # Adapt to variations in rpath handling on Linux and macOS
  if (APPLE)
    set(ENOKI_ORIGIN "@loader_path")
  elseif(UNIX)
    set(ENOKI_ORIGIN "$ORIGIN")
  endif()

  install(TARGETS enoki-python LIBRARY DESTINATION enoki)
  set_target_properties(enoki-python PROPERTIES INSTALL_RPATH "${ENOKI_ORIGIN}")
endif()

if (ENOKI_MASTER_PROJECT AND NOT "${CMAKE_CURRENT_SOURCE_DIR}" STREQUAL "${CMAKE_CURRENT_BINARY_DIR}")
  set(ENOKI_PYTHON_FILES
     __init__.py const.py detail.py generic.py
     matrix.py router.py traits.py
  )

  set(ENOKI_COPY_FILES "")
  foreach(file ${ENOKI_PYTHON_FILES})
    set(IN_FILE ${CMAKE_CURRENT_SOURCE_DIR}/../../enoki/${file})
    set(OUT_FILE ${CMAKE_CURRENT_BINARY_DIR}/../../enoki/${file})

    add_custom_command(
      OUTPUT ${OUT_FILE} DEPENDS ${IN_FILE}
      COMMAND ${CMAKE_COMMAND} -E copy ${IN_FILE} ${OUT_FILE})
    list(APPEND ENOKI_COPY_FILES ${OUT_FILE})
    install(FILES ${IN_FILE} DESTINATION enoki)
  endforeach(file)

  add_custom_target(copy-python-files ALL DEPENDS ${ENOKI_COPY_FILES})
endif()
