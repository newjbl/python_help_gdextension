#include "jbl_ext.h"
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/utility_functions.hpp>


using namespace godot;

void JBL_EXT::_bind_methods() {
	ClassDB::bind_method(D_METHOD("a_test_fun"), &JBL_EXT::a_test_fun);
}

JBL_EXT::JBL_EXT() {
	
}

JBL_EXT::~JBL_EXT() {
	// Add your cleanup here.
}

void JBL_EXT::a_test_fun() {
	UtilityFunctions::print("i am a test for jbl!");
}