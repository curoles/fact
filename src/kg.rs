use std::collections::HashMap;
use std::hash::{BuildHasherDefault, DefaultHasher};
use std::sync::{RwLock};
use yaml_rust::{/*YamlLoader,*/ Yaml};
//pub use ctor_bare::register_ctor;

use crate::display::{KgDisplay};

#[allow(dead_code)]
pub struct Node {
    pub name: &'static str,
    pub yaml: &'static str,
    data: Yaml    
}

type NodeMap = HashMap<String, Node, BuildHasherDefault<DefaultHasher>>;
type RwNodeMap = RwLock<NodeMap>;

// https://doc.rust-lang.org/std/collections/struct.HashMap.html
static NODE_MAP: RwNodeMap =
    RwLock::new(HashMap::with_hasher(BuildHasherDefault::new()));


/*#[allow(dead_code)]
fn register_node(name: &'static str, yaml: &'static str) {
    //println!("register: {name}\n{yaml}");
    let docs = YamlLoader::load_from_str(yaml).unwrap();
    let data = docs[0].clone();
    let node = Node {name, yaml, data};
    //println!("{:?}", node.data);
    NODE_MAP.write().unwrap().insert(name.to_string(), node);
}*/

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
    
    pub fn get_links_name(&self) -> Vec<String> {
        let top = self.data.as_hash().unwrap();
        let top = top.get(&Yaml::from_str(self.name)).unwrap();
        let keys = top.as_hash().unwrap().keys();
        let links = keys
            .map(|k| k.clone().into_string().unwrap())
            .collect::<Vec<String>>();
        //println!("links: {:?}", links);
        #[allow(clippy::let_and_return)]
        links
    }

    pub fn check_links(&self) -> Result<bool, Box<dyn std::error::Error>> {
        let top = self.data.as_hash().ok_or("node top is not hash")?;
        let top = top.get(&Yaml::from_str(self.name)).ok_or("wrong node name")?;
        let links = top.as_hash().ok_or("links not hash")?;
        for (link_name, link_data) in links {
            //println!("link: {:?}, data: {:?}", link_name.as_str().unwrap(), link_data);
            let data = link_data.as_vec().ok_or("link data not array")?;
            let target_node = &data[1].as_str().ok_or("target node not string")?;
            //println!("link: {:?}, target: {:?}", link_name.as_str().unwrap(), target_node);
            if Node::exists(target_node).is_none() {
                println!("Error: target node: '{}' does not exist, in '{}:{}'",
                    target_node, self.name, link_name.as_str().unwrap());
                return Ok(false);
            }
        }
        Ok(true)
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
    
    pub fn init() -> Result<bool, Box<dyn std::error::Error>> {
        println!("Init...");
        //let mut map = Self::get().write()?;
        //map.insert("val".to_string(),
        //    Node {name: "val", yaml: "", data: Yaml::from_str("")});
        Ok(true)
    }

    pub fn check() -> Result<bool, Box<dyn std::error::Error>> {
        println!("Checking...");
        let map = Self::get().read()?;
        for (_node_name, node) in map.iter() {
            println!("name: {}, node: {:?}", _node_name, node.data);
            let ok = node.check_links()?;
            if !ok {
                return Ok(false);
            }
        }
        Ok(true)
    }
    
    pub fn display_node(dsp: &dyn KgDisplay, node_name: &str) {
        let map = Graph::get().read().unwrap();
        if let Some(node) = map.get(node_name) {
            dsp.node(node);
        }
        else {
            dsp.no_node(node_name);
        }
    }
}
