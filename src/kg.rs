use std::collections::HashMap;
use std::hash::{BuildHasherDefault, DefaultHasher};
use std::sync::Mutex;
pub use ctor_bare::register_ctor;

mod str;

// https://doc.rust-lang.org/std/collections/struct.HashMap.html
static NODE_MAP: Mutex<HashMap<String, String, BuildHasherDefault<DefaultHasher>>> =
    Mutex::new(HashMap::with_hasher(BuildHasherDefault::new()));


fn register_node(name: String, builder: String) {
    println!("---- register {name}");
    NODE_MAP.lock().unwrap().insert(name, builder);
}

#[macro_export]
macro_rules! register {
    ($node_name:expr, $node_builder:expr) => {
        use $crate::kg::{register_ctor, register_node};
        #[register_ctor]
        fn register() {
            register_node($node_name, $node_builder);
        }
    };
}