use std::collections::HashMap;
use std::hash::{BuildHasherDefault, DefaultHasher};
use std::sync::{RwLock};
use yaml_rust::{YamlLoader, Yaml};
pub use ctor_bare::register_ctor;

mod str;
mod num;

#[allow(dead_code)]
pub struct Node {
    name: &'static str,
    yaml: &'static str,
    data: Yaml    
}

type NodeMap = HashMap<String, Node, BuildHasherDefault<DefaultHasher>>;
type RwNodeMap = RwLock<NodeMap>;

// https://doc.rust-lang.org/std/collections/struct.HashMap.html
static NODE_MAP: RwNodeMap =
    RwLock::new(HashMap::with_hasher(BuildHasherDefault::new()));


fn register_node(name: &'static str, yaml: &'static str) {
    println!("register: {name}\n{yaml}");
    let docs = YamlLoader::load_from_str(yaml).unwrap();
    let data = docs[0].clone();
    let node = Node {name, yaml, data};
    println!("{:?}", node.data);
    NODE_MAP.write().unwrap().insert(name.to_string(), node);
}

#[macro_export]
macro_rules! register {
    ($registration_fn_name:ident, $yaml_file:literal) => {
        use $crate::kg::{register_ctor, register_node};
        #[register_ctor]
        fn $registration_fn_name() {
            let this_file = &file!()[7 .. (file!().len() - 3)];
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
        
    //fn get(node_name: &str) -> Option<&Node> {
    //    let map = Self::get_map().read().unwrap();
    //    map.get(node_name)
    //}
    
    pub fn exists(node_name: &str) -> Option<()> {
        let map = Graph::get().read().unwrap();
        match map.get(node_name) {
            None => None,
            Some(_) => Some(())
        }
    }
    
    pub fn get_links(&self) -> Vec<String> {
        //let mut links: Vec<String> = vec![];
        let top = self.data.as_hash().unwrap();
        let top = top.get(&Yaml::from_str(self.name)).unwrap();
        let keys = top.as_hash().unwrap().keys();
        let links = keys
            .map(|k| k.clone().into_string().unwrap())
            .collect::<Vec<String>>();
        println!("links: {:?}", links);
        links
    }

}

#[allow(dead_code)]
pub struct Graph {
   
}

#[allow(dead_code)]
impl Graph {
    
    fn get() -> &'static RwNodeMap {
        &NODE_MAP
    }
    
    pub fn check() -> Result<bool, Box<dyn std::error::Error>> {
        let map = Self::get().read().unwrap();
        for (node_name, node) in map.iter() {
            println!("name: {}, node: {:?}", node_name, node.data);
            let links = node.get_links();
            for link_name in links {
                // [[label], node_name]
                let link_node_name = link_name.clone(); //FIXME
                if Node::exists(&link_node_name).is_none() {
                    println!("node: '{}' does not exist, in '{}:{}'",
                        link_node_name, node_name, link_name);
                    return Ok(false);
                }
            }
        }
        Ok(true)
    }
}
