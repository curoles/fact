use std::collections::HashMap;
use std::hash::{BuildHasherDefault, DefaultHasher};
use std::sync::Mutex;
use yaml_rust::{YamlLoader, Yaml};
pub use ctor_bare::register_ctor;

mod str;
mod num;

#[allow(dead_code)]
struct Node {
    name: &'static str,
    yaml: &'static str,
    data: Yaml    
}

type NodeMap = Mutex<HashMap<String, Node, BuildHasherDefault<DefaultHasher>>>;

// https://doc.rust-lang.org/std/collections/struct.HashMap.html
static NODE_MAP: NodeMap =
    Mutex::new(HashMap::with_hasher(BuildHasherDefault::new()));


fn register_node(name: &'static str, yaml: &'static str) {
    println!("register: {name}\n{yaml}");
    let docs = YamlLoader::load_from_str(yaml).unwrap();
    let data = docs[0].clone();
    let node = Node {name, yaml, data};
    println!("{:?}", node.data);
    NODE_MAP.lock().unwrap().insert(name.to_string(), node);
}

#[macro_export]
macro_rules! register {
    ($registration_fn_name:ident, $yaml_file:literal) => {
        use $crate::kg::{register_ctor, register_node};
        #[register_ctor]
        fn $registration_fn_name() {
            let this_file = &file!()[4 .. (file!().len() - 3)];
            let yaml_string = include_str!($yaml_file);
            register_node(this_file, yaml_string);
        }
    };
}


#[allow(dead_code)]
impl Node {

    fn name(&self) -> &'static str {
        self.name
    }

    fn yaml(&self) -> &'static str {
        self.yaml
    }
    
    fn get_map() -> &'static NodeMap {
        &NODE_MAP
    }
}