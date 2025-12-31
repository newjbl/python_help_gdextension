#ifndef JBL_EXT_H
#define JBL_EXT_H


#include <godot_cpp/classes/control.hpp>
#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/image.hpp>
#include <godot_cpp/classes/input_event_key.hpp>
#include <godot_cpp/classes/tile_map.hpp>
#include <godot_cpp/classes/tile_set.hpp>
#include <godot_cpp/classes/viewport.hpp>
#include <godot_cpp/variant/variant.hpp>

#include <godot_cpp/core/binder_common.hpp>
#include <godot_cpp/core/gdvirtual.gen.inc>

namespace godot {

	class JBL_EXT : public Control {
		GDCLASS(JBL_EXT, Control)

	private:
		

	protected:
		static void _bind_methods();
		void a_test_fun();

	public:
		JBL_EXT();
		~JBL_EXT();

	};

}

#endif