/* godot-cpp integration testing project.
 *
 * This is free and unencumbered software released into the public domain.
 */

#ifndef JBL_EXT_REGISTER_TYPES_H
#define JBL_EXT_REGISTER_TYPES_H

#include <godot_cpp/core/class_db.hpp>

using namespace godot;

void initialize_jbl_ext_module(ModuleInitializationLevel p_level);
void uninitialize_jbl_ext_module(ModuleInitializationLevel p_level);

#endif // JBL_EXT_REGISTER_TYPES_H
