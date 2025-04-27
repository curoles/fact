use std::collections::HashMap;
use std::hash::{BuildHasherDefault, DefaultHasher};
use std::sync::Mutex;
pub use ctor_bare::register_ctor;

mod str;
mod num;

// https://doc.rust-lang.org/std/collections/struct.HashMap.html
static NODE_MAP: Mutex<HashMap<String, String, BuildHasherDefault<DefaultHasher>>> =
    Mutex::new(HashMap::with_hasher(BuildHasherDefault::new()));


fn register_node(name: String, builder: String) {
    println!("---- register: {name}, {builder}");
    NODE_MAP.lock().unwrap().insert(name, builder);
}

#[macro_export]
macro_rules! register {
    ($registration_fn_name:ident, $yaml_file:literal) => {
        use $crate::kg::{register_ctor, register_node};
        #[register_ctor]
        fn $registration_fn_name() {
            let this_file = file!();
            let yaml_string = include_str!($yaml_file);
            register_node(this_file.to_string(), yaml_string.to_string());
        }
    };
}

#[allow(dead_code)]
trait Node {

    // `Self` refers to the implementor type.
    fn new() -> Self;
    
    // Like new() but returns trait
    fn create() -> impl Node;

    /*fn create() -> impl Node {
        let node = Self::new();
        node
    }*/

    // Method signatures; these will return a string.
    //fn name(&self) -> &'static str;
    //fn noise(&self) -> &'static str;

    // Traits can provide default method definitions.
    //fn talk(&self) {
    //    println!("{} says {}", self.name(), self.noise());
    //}
}